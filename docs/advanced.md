# Advanced Usage

## Working with DNSSEC Proofs

### Constructing Proofs Manually

```python
from dns_prove import DnsProver
from dns_prove.utils import build_proof

# Initialize prover
prover = DnsProver("0x123...789")

# Get DNS record
record = prover.lookup_dns_record("TXT", "example.com")

# Construct proof manually
proof = build_proof(
    name="example.com",
    rrsig={
        "algorithm": 13,  # ECDSAP256SHA256
        "key": "your_key",
        "signature": "your_signature"
    },
    rrset={
        "name": "example.com",
        "type": "TXT",
        "ttl": 300,
        "data": record
    }
)

# Submit proof
prover.submit_proof(proof)
```

### Working with ENS Domains

```python
# Resolve ENS domain
owner = prover.resolve_eth_domain("vitalik.eth")

# Verify ENS domain ownership
is_owner = prover.verify_signed_text_record(
    "vitalik.eth",
    "0x123...789"
)
```

## Error Handling

```python
try:
    proof = prover.construct_proof("TXT", "example.com")
    prover.submit_proof(proof)
except Exception as e:
    print(f"Error: {e}") 