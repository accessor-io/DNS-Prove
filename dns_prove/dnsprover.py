import dns.resolver
import dns.rdatatype
import dns.query
from web3 import Web3
import eth_utils
from .crypto.initEth import *
from .utils import *
from .abi import dnssec_oracle_abi

class DnsProver:
    def __init__(self, oracle_address, provider_url=None):
        self.oracle_address = oracle_address
        self.provider = Web3.HTTPProvider(provider_url) if provider_url else Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID")
        self.w3 = Web3(self.provider)
        self.oracle = self.w3.eth.contract(address=oracle_address, abi=dnssec_oracle_abi)

    def lookup_dns_record(self, record_type, domain):
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.query(domain, record_type)
            for rdata in answers:
                return rdata.to_text()
        except dns.resolver.NXDOMAIN:
            return None
        except Exception as e:
            print(f"Error looking up DNS record: {e}")
            return None

    def construct_proof(self, record_type, domain):
        record = self.lookup_dns_record(record_type, domain)
        if record is None:
            return None
        proof = construct_proof_from_record(record, domain)
        return proof

    def submit_proof(self, proof):
        tx_hash = self.oracle.functions.verifySignedTextRecord(proof).transact()
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Proof submitted. Transaction hash: {tx_hash.hex()}")

    def verify_signed_text_record(self, domain, address):
        record = self.lookup_dns_record("TXT", domain)
        if record is None:
            return False
        proof = construct_proof_from_record(record, domain)
        result = self.oracle.functions.verifySignedTextRecord(proof).call()
        return result

def main():
    import argparse

    parser = argparse.ArgumentParser(description='DNSSEC Proof Tool')
    parser.add_argument('record_type', choices=['A', 'AAAA', 'TXT'],
                        help='Type of DNS record to fetch')
    parser.add_argument('domain', help='Domain name to fetch DNS information for')
    parser.add_argument('--oracle', required=True, help='Address of the DNSSEC Oracle contract')
    parser.add_argument('--provider', help='Web3 provider URL (optional)')

    args = parser.parse_args()

    prover = DnsProver(args.oracle, args.provider)

    proof = prover.construct_proof(args.record_type, args.domain)
    if proof is not None:
        prover.submit_proof(proof)

if __name__ == "__main__":
    main()