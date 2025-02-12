from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from dns_prove.dnsprover import DnsProver
from dns_prove.batch import BatchProcessor
from dns_prove.cache import ProofCache
from dns_prove.logger import setup_logging
import logging
from datetime import datetime
import asyncio
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure logging
logger = setup_logging()

# Initialize metrics
REQUESTS = Counter('dns_prove_requests_total', 'Total requests processed', ['endpoint', 'status'])
LATENCY = Histogram('dns_prove_request_latency_seconds', 'Request latency', ['endpoint'])
CACHE_HITS = Counter('dns_prove_cache_hits_total', 'Total cache hits')
ACTIVE_REQUESTS = Gauge('dns_prove_active_requests', 'Number of active requests')

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI(
    title="DNS Prove API",
    description="API for verifying DNS records with blockchain proofs and ENS domain resolution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add instrumentation
FastAPIInstrumentor.instrument_app(app)

# Add CORS middleware with more restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*.example.com"],  # Replace with actual domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600
)

# Rate limiting middleware
from fastapi_limiter import FastAPILimiter
import aioredis

@app.on_event("startup")
async def startup():
    redis = await aioredis.create_redis_pool('redis://localhost')
    await FastAPILimiter.init(redis)

# Initialize services with dependency injection
class Services:
    def __init__(self):
        self._prover = None
        self._batch_processor = None
        self._cache = None
    
    @property
    def prover(self):
        if not self._prover:
            self._prover = DnsProver()
        return self._prover
    
    @property
    def batch_processor(self):
        if not self._batch_processor:
            self._batch_processor = BatchProcessor(self.prover)
        return self._batch_processor
    
    @property
    def cache(self):
        if not self._cache:
            self._cache = ProofCache()
        return self._cache

services = Services()

class DomainRequest(BaseModel):
    domain: str = Field(..., description="Domain name to verify", min_length=3, max_length=253)
    record_type: str = Field(default="TXT", description="DNS record type")
    check_ens: bool = Field(default=False, description="Check ENS resolution for .eth domains")
    priority: int = Field(default=1, description="Request priority (1-5)", ge=1, le=5)

    @validator('domain')
    def validate_domain(cls, v):
        if not v or len(v) > 253:
            raise ValueError('Invalid domain name')
        if not all(c.isalnum() or c in '.-' for c in v):
            raise ValueError('Domain contains invalid characters')
        return v.lower()

    @validator('record_type')
    def validate_record_type(cls, v):
        valid_types = ['A', 'AAAA', 'TXT', 'CNAME', 'MX', 'NS', 'SOA', 'SRV']
        if v not in valid_types:
            raise ValueError(f'Invalid record type. Must be one of: {", ".join(valid_types)}')
        return v

class BatchRequest(BaseModel):
    domains: List[str] = Field(..., description="List of domains to verify", max_items=100)
    record_type: str = Field(default="TXT", description="DNS record type")
    check_ens: bool = Field(default=False, description="Check ENS resolution for .eth domains")
    parallel: bool = Field(default=True, description="Process domains in parallel")
    priority: int = Field(default=1, description="Batch priority (1-5)", ge=1, le=5)

    @validator('domains')
    def validate_domains(cls, v):
        if not v:
            raise ValueError('Domain list cannot be empty')
        if len(v) > 100:
            raise ValueError('Maximum 100 domains per batch')
        if not all(all(c.isalnum() or c in '.-' for c in domain) for domain in v):
            raise ValueError('One or more domains contain invalid characters')
        return [domain.lower() for domain in v]

async def process_domain(domain: str, record_type: str, check_ens: bool, prover: DnsProver, cache: ProofCache) -> Dict[str, Any]:
    with ACTIVE_REQUESTS.track_inprogress(), \
         LATENCY.labels(endpoint='process_domain').time(), \
         tracer.start_as_current_span("process_domain") as span:
        
        span.set_attribute("domain", domain)
        span.set_attribute("record_type", record_type)
        
        cache_key = f"{domain}_{record_type}"
        cached_proof = cache.get(domain, record_type)
        
        if cached_proof:
            CACHE_HITS.inc()
            logger.info("Cache hit for domain: %s", domain)
            return {
                "domain": domain,
                "status": "success",
                "proof": cached_proof,
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }

        try:
            proof = await asyncio.shield(prover.construct_proof(record_type, domain))
            
            if check_ens and domain.endswith('.eth'):
                eth_address = await asyncio.shield(prover.resolve_eth_domain(domain))
                if eth_address:
                    proof = {"eth_address": eth_address, "dns_proof": proof}
            
            if proof:
                await asyncio.shield(cache.set(domain, record_type, proof))
                REQUESTS.labels(endpoint='process_domain', status='success').inc()
                logger.info("Successfully processed domain: %s", domain)
                return {
                    "domain": domain,
                    "status": "success",
                    "proof": proof,
                    "cached": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            REQUESTS.labels(endpoint='process_domain', status='failed').inc()
            logger.warning("No proof generated for domain: %s", domain)
            return {
                "domain": domain,
                "status": "failed",
                "error": "No proof generated",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            REQUESTS.labels(endpoint='process_domain', status='error').inc()
            logger.error("Error processing domain %s: %s", domain, str(e), exc_info=True)
            return {
                "domain": domain,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

@app.post("/verify", response_model=Dict[str, Any], tags=["Verification"])
@FastAPILimiter.limit("100/minute")
async def verify_domain(
    request: DomainRequest,
    background_tasks: BackgroundTasks,
    prover: DnsProver = Depends(lambda: services.prover),
    cache: ProofCache = Depends(lambda: services.cache)
):
    """
    Verify a single domain's DNS records with optional ENS resolution
    
    - Supports standard DNS records and ENS domains
    - Includes DNSSEC validation
    - Caches results for improved performance
    - Rate limited to 100 requests per minute
    """
    with tracer.start_as_current_span("verify_domain") as span:
        span.set_attribute("domain", request.domain)
        logger.info("Processing verification request for domain: %s", request.domain)
        
        result = await process_domain(request.domain, request.record_type, request.check_ens, prover, cache)
        
        if result["status"] == "error":
            logger.error("Verification failed for domain: %s", request.domain)
            raise HTTPException(
                status_code=400,
                detail={"error": result["error"], "domain": request.domain}
            )
        
        return result

@app.post("/batch", response_model=List[Dict[str, Any]], tags=["Batch Processing"])
@FastAPILimiter.limit("20/minute")
async def process_batch(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
    prover: DnsProver = Depends(lambda: services.prover),
    cache: ProofCache = Depends(lambda: services.cache)
):
    """
    Process multiple domains in batch with parallel processing support
    
    - Supports parallel processing for improved performance
    - Includes caching and ENS resolution
    - Returns detailed results for each domain
    - Rate limited to 20 batches per minute
    """
    with tracer.start_as_current_span("process_batch") as span:
        span.set_attribute("domain_count", len(request.domains))
        logger.info("Processing batch request for %d domains", len(request.domains))
        
        if request.parallel:
            tasks = [
                process_domain(domain, request.record_type, request.check_ens, prover, cache)
                for domain in request.domains
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for domain in request.domains:
                result = await process_domain(domain, request.record_type, request.check_ens, prover, cache)
                results.append(result)
        
        return results