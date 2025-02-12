#!/usr/bin/env python3

from dns_prove.dnsprover import DnsProver
from dns_prove.oracle import Oracle
from web3 import Web3
import argparse
import sys
import logging
from pathlib import Path
import json
import os

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_config(config_path):
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load config
    config_path = Path.home() / '.dns-prove' / 'config.json'
    config = load_config(config_path)

    parser = argparse.ArgumentParser(
        description='''
DNS-Prove: Create and verify DNSSEC proofs on Ethereum

This tool allows you to:
- Look up DNS records and submit DNSSEC proofs to Ethereum
- Verify domain ownership using DNSSEC proofs
- Batch process multiple domains
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Actions:
  lookup       Look up a DNS record and submit its DNSSEC proof to Ethereum
  verify       Verify domain ownership using DNSSEC proofs
  batch        Process multiple domains from a file

Record Types:
  A           IPv4 address record
  AAAA        IPv6 address record
  TXT         Text record
  NS          Nameserver record
  MX          Mail exchange record
  CNAME       Canonical name record

Examples:
    # Look up and submit proof for an A record
    python main.py lookup A example.com --oracle 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

    # Look up and submit proof for a TXT record
    python main.py lookup TXT example.com --oracle 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

    # Verify a domain's ownership
    python main.py verify example.com 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

    # Batch process multiple domains
    python main.py batch domains.txt --oracle 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

Network Options:
    --provider          Ethereum provider URL (default: Sepolia testnet)
    --network          Select network: mainnet, sepolia, or goerli (default: sepolia)
    --gas-limit        Gas limit for transactions (default: 500000)
    --max-gas-price    Maximum gas price in Gwei
    --dry-run          Simulate operations without submitting transactions

Other Options:
    --retry-count      Number of retry attempts for failed operations (default: 3)
    --timeout          Timeout in seconds for network operations (default: 30)
    --output          Path to save output results
    --verbose, -v     Enable verbose logging
    --config          Path to custom config file
'''
    )

    # Required arguments
    parser.add_argument('action', choices=['lookup', 'verify', 'batch'],
                      help='Action to perform (lookup DNS record, verify ownership, or batch process)')
    parser.add_argument('record_type', nargs='?', choices=['A', 'AAAA', 'TXT', 'NS', 'MX', 'CNAME'],
                      help='Type of DNS record to fetch')
    parser.add_argument('domain',
                      help='Domain name to fetch DNS information for')
    parser.add_argument('--oracle', required=True,
                      help='Ethereum address of the DNSSEC Oracle contract')

    # Optional arguments with defaults from config
    parser.add_argument('--provider', default=config.get('provider', "https://sepolia.infura.io/v3/6686de2244c54a0dbefb2e19ce334199"),
                      help='Ethereum provider URL (default: Sepolia testnet)')
    parser.add_argument('--gas-limit', type=int, default=config.get('gas_limit', 500000),
                      help='Gas limit for transactions')
    parser.add_argument('--retry-count', type=int, default=config.get('retry_count', 3),
                      help='Number of retry attempts for failed operations')
    parser.add_argument('--output', type=Path,
                      help='Path to save output results')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose logging')
    parser.add_argument('--timeout', type=int, default=config.get('timeout', 30),
                      help='Timeout in seconds for network operations')
    parser.add_argument('--max-gas-price', type=int, default=config.get('max_gas_price', None),
                      help='Maximum gas price in Gwei to use for transactions')
    parser.add_argument('--dry-run', action='store_true',
                      help='Simulate operations without submitting transactions')
    parser.add_argument('--network', choices=['mainnet', 'sepolia', 'goerli'], 
                      default=config.get('network', 'sepolia'),
                      help='Ethereum network to use')
    parser.add_argument('--config', type=Path,
                      help='Path to custom config file')
    
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize DnsProver with retry mechanism
        for attempt in range(args.retry_count):
            try:
                prover = DnsProver(args.oracle, args.provider, gas_limit=args.gas_limit)
                break
            except Exception as e:
                if attempt == args.retry_count - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
        
        if args.action == 'lookup':
            # Lookup DNS record and construct proof
            record = prover.lookup_dns_record(args.record_type, args.domain)
            if record is None:
                logger.error(f"No {args.record_type} record found for {args.domain}")
                return 1
                
            logger.info(f"Found {args.record_type} record for {args.domain}:")
            print(record)
            
            # Construct and submit proof
            proof = prover.construct_proof(args.record_type, args.domain)
            if proof is None:
                logger.error("Failed to construct proof")
                return 1
                
            logger.info("\nConstructed proof:")
            print(proof)
            
            # Submit proof to Oracle
            try:
                oracle = Oracle(args.oracle, args.provider)
                tx_receipt = oracle.submit_proof(proof)
                logger.info("\nProof submitted successfully!")
                logger.info(f"Transaction hash: {tx_receipt['transactionHash'].hex()}")
                
                if args.output:
                    result = {
                        'domain': args.domain,
                        'record_type': args.record_type,
                        'record': record,
                        'tx_hash': tx_receipt['transactionHash'].hex()
                    }
                    args.output.write_text(json.dumps(result, indent=2))
                    
            except Exception as e:
                logger.error(f"\nFailed to submit proof: {e}")
                return 1
                
        elif args.action == 'verify':
            # Verify domain ownership
            result = prover.verify_signed_text_record(args.domain, args.oracle)
            if result:
                logger.info(f"✓ Domain {args.domain} is owned by {args.oracle}")
            else:
                logger.error(f"✗ Domain {args.domain} ownership verification failed")
                return 1

        elif args.action == 'batch':
            # Batch process domains from file
            with open(args.domain) as f:
                domains = f.read().splitlines()
            
            results = []
            for domain in domains:
                try:
                    result = prover.verify_signed_text_record(domain, args.oracle)
                    results.append({'domain': domain, 'verified': result})
                except Exception as e:
                    logger.error(f"Error processing {domain}: {e}")
                    results.append({'domain': domain, 'error': str(e)})
            
            if args.output:
                args.output.write_text(json.dumps(results, indent=2))
    
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            logger.exception("Detailed error trace:")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())