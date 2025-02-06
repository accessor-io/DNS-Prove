#!/usr/bin/env python3

from dns_prove.dnsprover import DnsProver
from dns_prove.oracle import Oracle
from web3 import Web3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description='DNS-Prove: Create and verify DNSSEC proofs on Ethereum',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Look up and submit proof for an A record
    python main.py lookup A example.com --oracle 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

    # Look up and submit proof for a TXT record
    python main.py lookup TXT example.com --oracle 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

    # Verify a domain's ownership
    python main.py verify example.com 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
    """
    )

    parser.add_argument('action', choices=['lookup', 'verify'],
                      help='Action to perform (lookup DNS record or verify ownership)')
    parser.add_argument('record_type', nargs='?', choices=['A', 'AAAA', 'TXT'],
                      help='Type of DNS record to fetch')
    parser.add_argument('domain',
                      help='Domain name to fetch DNS information for')
    parser.add_argument('--oracle', required=True,
                      help='Ethereum address of the DNSSEC Oracle contract')
    parser.add_argument('--provider', default="https://sepolia.infura.io/v3/6686de2244c54a0dbefb2e19ce334199",
                      help='Ethereum provider URL (default: Sepolia testnet)')
    
    args = parser.parse_args()

    try:
        # Initialize DnsProver
        prover = DnsProver(args.oracle, args.provider)
        
        if args.action == 'lookup':
            # Lookup DNS record and construct proof
            record = prover.lookup_dns_record(args.record_type, args.domain)
            if record is None:
                print(f"No {args.record_type} record found for {args.domain}")
                return 1
                
            print(f"Found {args.record_type} record for {args.domain}:")
            print(record)
            
            # Construct and submit proof
            proof = prover.construct_proof(args.record_type, args.domain)
            if proof is None:
                print("Failed to construct proof")
                return 1
                
            print("\nConstructed proof:")
            print(proof)
            
            # Submit proof to Oracle
            try:
                oracle = Oracle(args.oracle, args.provider)
                tx_receipt = oracle.submit_proof(proof)
                print("\nProof submitted successfully!")
                print(f"Transaction hash: {tx_receipt['transactionHash'].hex()}")
            except Exception as e:
                print(f"\nFailed to submit proof: {e}")
                return 1
                
        elif args.action == 'verify':
            # Verify domain ownership
            result = prover.verify_signed_text_record(args.domain, args.oracle)
            if result:
                print(f"✓ Domain {args.domain} is owned by {args.oracle}")
            else:
                print(f"✗ Domain {args.domain} ownership verification failed")
                return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 