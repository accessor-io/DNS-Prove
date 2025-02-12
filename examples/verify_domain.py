"""Example script showing how to verify domain ownership."""
from dns_prove.dnsprover import DnsProver

def main():
    prover = DnsProver()
    domain = "example.eth"
    record_type = "TXT"
    
    # Construct and submit proof
    proof = prover.construct_proof(record_type, domain)
    if proof:
        prover.submit_proof(proof)

if __name__ == "__main__":
    main() 