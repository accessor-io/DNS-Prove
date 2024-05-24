import dns.resolver
from web3 import Web3
from ensdomains.dnsprovejs import DnsProve, DNSRegistrarJs

class DnsProver:
    def __init__(self, provider=None):
        self.provider = provider
        self.dnsprove = DnsProve(provider)
        self.web3 = Web3(provider)

    def lookup_and_submit(self, record_type, domain, oracle_address, non_owner, dnsregistrar_address=None, account=None):
        # Lookup DNS information
        resolver = dns.resolver.Resolver()
        try:
            answers = resolver.resolve(domain, record_type)
        except dns.resolver.NoAnswer:
            raise Exception(f"No DNS records found for {domain}")
        except dns.resolver.NXDOMAIN:
            raise Exception(f"Domain {domain} does not exist")

        records = []
        for rdata in answers:
            record = {
                "name": domain,
                "type": record_type,
                "ttl": rdata.ttl,
                "class": "IN",
                "flush": False,
                "data": {
                    "flags": 257,  # Example flag
                    "algorithm": 253,  # Example algorithm
                    "key": rdata.to_text()
                }
            }
            records.append(record)

        # Get Oracle
        oracle = self.dnsprove.getOracle(oracle_address)

        # fetch
      
        proofs = []

        # Submit to Oracle or handle based on DNSSEC proof status
        if proofs:
            oracle.submitAll({'proofs': proofs}, {'from': non_owner})
        else:
            raise Exception("No DNSSEC proofs found")

        # If dnsregistrar_address and account are provided, also interact with DNSRegistrar
        if dnsregistrar_address and account:
            dnsregistrar = DNSRegistrarJs(self.provider, dnsregistrar_address)
            claim = dnsregistrar.claim('foo.test')
            claim.submit({'from': account})

# Example usage
provider = Web3.HTTPProvider('http://localhost:8545')  # provider
dns_prover = DnsProver(provider)
dns_prover.lookup_and_submit('TXT',  Example Web3 provider'_ens.matoken.xyz', '0x123...', 'nonOwner', 'dnsregistraraddress', 'account')
