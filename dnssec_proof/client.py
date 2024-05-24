from dnssec_proof.dnsprover import DnsProver
from dnssec_proof.oracle import Oracle
from dnssec_proof.utils import build_proof
import argparse

def main():
    parser = argparse.ArgumentParser(description='Fetches DNS information and submits proofs to DNSSEC Oracle.')
    parser.add_argument('record_type', help='Type of DNS record to fetch (e.g., A, AAAA, TXT)')
    parser.add_argument('domain', help='Domain name to fetch DNS information for')
    parser.add_argument('--oracle', help='Address of the DNSSEC Oracle contract', required=True)
    parser.add_argument('--provider', help='Web3 provider URL')
    args = parser.parse_args()

    # Initialize DnsProver and Oracle
    dnsprover = DnsProver(args.provider)
    oracle = Oracle(args.oracle)

    # Fetch DNS information
    records = dnsprover.lookup(args.record_type, args.domain)

    # Construct and submit proofs
    for record in records:
        proof = build_proof(record['name'], record['rrsig'], record['rrset'])
        oracle.submit_proof(proof)

if __name__ == '__main__':
    main()
