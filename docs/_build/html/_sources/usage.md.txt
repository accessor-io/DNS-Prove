# Usage Guide

## Basic Usage

```python
from dns_prove import DnsProver

# Initialize with DNSSEC Oracle contract address
prover = DnsProver("0x123...789")

# Look up DNS records
record = prover.lookup_dns_record("TXT", "example.com")

# Verify domain ownership
is_owner = prover.verify_signed_text_record("example.com", "0x123...789")
```

## Command Line Interface

```bash
# Look up TXT record
dns-prove TXT example.com --oracle 0x123...789

# Verify domain ownership
dns-prove TXT example.com --oracle 0x123...789 --verify 0x456...abc
``` 