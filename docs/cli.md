# Command Line Interface

DNS-Prove provides a command-line interface for easy interaction with DNS records and DNSSEC proofs.

## Basic Commands

### Look up DNS Records

```bash
dns-prove <record_type> <domain> --oracle <oracle_address> [--provider <provider_url>]
```

#### Arguments:
- `record_type`: Type of DNS record (A, AAAA, TXT)
- `domain`: Domain name to query
- `--oracle`: Ethereum address of the DNSSEC Oracle contract
- `--provider`: (Optional) Web3 provider URL

### Examples

Look up TXT record:
```bash
dns-prove TXT example.com --oracle 0x123...789
```

Verify domain ownership:
```bash
dns-prove TXT example.com --oracle 0x123...789 --verify 0x456...abc
```

Use custom provider:
```bash
dns-prove A example.com --oracle 0x123...789 --provider https://mainnet.infura.io/v3/YOUR-PROJECT-ID
``` 