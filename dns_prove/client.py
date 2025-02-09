"""
DNS Prove - A tool for creating and verifying DNSSEC proofs on Ethereum

Usage:
    dns_prove <record_type> <domain> --oracle ADDRESS [--provider URL]

Example:
    dns_prove TXT example.com --oracle 0x1234... --provider https://mainnet.infura.io
"""

from .dnsprover import DnsProver
from .oracle import Oracle
from .utils import build_proof
import argparse

def main():
    """Main entry point for the DNS Prove CLI tool."""
    parser = argparse.ArgumentParser(
        description='Fetches DNS information and submits proofs to DNSSEC Oracle.',
        epilog='''
Examples:
    # Verify TXT record for a domain using Mainnet:
    dns_prove TXT example.com --oracle 0x4B1488B7a6B320d2D721406204aBc3eeAa9AD329 --provider https://mainnet.infura.io/v3/YOUR-PROJECT-ID

    # Verify A record using local node:
    dns_prove A example.com --oracle 0x4B1488B7a6B320d2D721406204aBc3eeAa9AD329 --provider http://localhost:8545

    # Verify AAAA record:
    dns_prove AAAA example.com --oracle 0x4B1488B7a6B320d2D721406204aBc3eeAa9AD329
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('record_type', 
                       choices=['A', 'AAAA', 'TXT'],
                       help='Type of DNS record to fetch (e.g., A for IPv4, AAAA for IPv6, TXT for text records)')
    
    parser.add_argument('domain', 
                       help='Domain name to fetch DNS information for (e.g., example.com)')
    
    parser.add_argument('--oracle', 
                       required=True,
                       help='Address of the DNSSEC Oracle contract (e.g., 0x4B1488B7a6B320d2D721406204aBc3eeAa9AD329)')
    
    parser.add_argument('--provider', 
                       help='Web3 provider URL (default: https://mainnet.infura.io/v3/YOUR-PROJECT-ID)')

    args = parser.parse_args()

    try:
        # Initialize DnsProver and Oracle
        dnsprover = DnsProver(args.oracle, args.provider)

        # Fetch DNS information
        records = dnsprover.lookup_dns_record(args.record_type, args.domain)

        if not records:
            print(f"No {args.record_type} records found for {args.domain}")
            return

        # Construct and submit proofs
        for record in records:
            try:
                proof = build_proof(record['name'], record['rrsig'], record['rrset'])
                dnsprover.submit_proof(proof)
                print(f"Successfully submitted proof for {record['name']}")
            except Exception as e:
                print(f"Error submitting proof for {record['name']}: {e}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == '__main__':
    main()
