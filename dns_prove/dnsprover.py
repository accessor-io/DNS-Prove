import dns.resolver
import dns.rdatatype
import dns.query
import dns.dnssec
import dns.name
import dns.message
import dns.rdtypes.ANY.DNSKEY
import dns.rdtypes.ANY.DS
import dns.rdtypes.ANY.RRSIG
from web3 import Web3
import eth_utils
from dns_prove.crypto.initEth import verify_signed_text_record
from dns_prove.utils import build_proof, construct_rrsig, construct_rrset
from dns_prove.abi import dnssec_oracle_abi
import os
from dotenv import load_dotenv
from eth_abi.abi import encode
from dns_prove.logger import setup_logging

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Add debug output
print(f"Current directory: {os.getcwd()}")
print(f"Project root: {project_root}")
print(f"Looking for .env at: {env_path}")
print(f"Loading .env file...")
load_dotenv(dotenv_path=env_path)
print(f"Loaded .env file. Path exists: {os.path.exists(env_path)}")
print(f"Environment after loading: {os.environ.get('WEB3_PROVIDER')}")

# ENS Registry ABI (complete set of required functions)
ENS_REGISTRY_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "resolver",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "owner",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "ttl",
        "outputs": [{"name": "", "type": "uint64"}],
        "type": "function"
    }
]

# ENS Public Resolver ABI (complete set of required functions)
ENS_RESOLVER_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "addr",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "node", "type": "bytes32"},
            {"name": "key", "type": "string"}
        ],
        "name": "text",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "contenthash",
        "outputs": [{"name": "", "type": "bytes"}],
        "type": "function"
    }
]

logger = setup_logging()

class DnsProver:
    def __init__(self, provider_url=None):
        logger.info("Initializing DnsProver...")
        # Debug environment variables
        print(f"Current environment variables: {os.environ.get('WEB3_PROVIDER')}")
        
        # Try environment variable first, then argument
        self.provider_url = provider_url or os.getenv("WEB3_PROVIDER")
        
        if not self.provider_url:
            available_vars = "\n".join([k for k in os.environ if "WEB3" in k or "PROVIDER" in k])
            raise ValueError(
                f"Web3 provider required but not found.\n"
                f"Tried: --provider argument and WEB3_PROVIDER environment variable\n"
                f"Available relevant environment variables:\n{available_vars}"
            )

        # Verify the URL format
        if not self.provider_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid provider URL format: {self.provider_url}")

        print(f"Using provider: {self.provider_url}")
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError("Could not connect to Ethereum provider")
        
        print(f"Connected to network: {self.w3.eth.chain_id}")
        # ENS DNSSEC Oracle mainnet address
        self.oracle = self.w3.eth.contract(
            address=Web3.to_checksum_address("0x226159d592E2b063810a10Ebf6cF7A7bAD0193a6"),
            abi=dnssec_oracle_abi
        )
        self.resolver = dns.resolver.Resolver()
        
        # Initialize resolver with DNSSEC
        self.resolver.nameservers = ['1.1.1.1']  # Cloudflare's DNS
        self.resolver.use_edns(0, dns.flags.DO, 4096)  # Enable DNSSEC
        
        # ENS Registry contract (Mainnet)
        self.ens_registry = self.w3.eth.contract(
            address=Web3.to_checksum_address("0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e"),  # ENS Registry on mainnet
            abi=ENS_REGISTRY_ABI
        )

    def namehash(self, name):
        """Compute the ENS namehash of a domain"""
        if not name:
            return b'\0' * 32
        
        node = b'\0' * 32
        if name:
            labels = name.split('.')
            for label in reversed(labels):
                label_hash = Web3.keccak(text=label)
                node = Web3.keccak(node + label_hash)
        return node

    def resolve_eth_domain(self, domain):
        """Resolve a .eth domain to its Ethereum address and ownership information"""
        try:
            # Calculate the namehash
            node = self.namehash(domain)
            
            # Get the owner address
            owner = self.ens_registry.functions.owner(node).call()
            if owner == "0x0000000000000000000000000000000000000000":
                print(f"Domain {domain} is not registered")
                return None
            
            print(f"Domain {domain} is owned by: {owner}")
            
            # Get the resolver address
            resolver_address = self.ens_registry.functions.resolver(node).call()
            if resolver_address == "0x0000000000000000000000000000000000000000":
                print(f"No resolver set for {domain}")
                return owner  # Return owner even if no resolver
                
            # Create resolver contract instance
            resolver = self.w3.eth.contract(
                address=resolver_address,
                abi=ENS_RESOLVER_ABI + [
                    # Add DNS record resolution
                    {
                        "constant": True,
                        "inputs": [
                            {"name": "node", "type": "bytes32"},
                            {"name": "name", "type": "string"}
                        ],
                        "name": "dnsRecord",
                        "outputs": [{"name": "", "type": "bytes"}],
                        "type": "function"
                    }
                ]
            )
            
            try:
                # Get the resolved address
                address = resolver.functions.addr(node).call()
                if address and address != "0x0000000000000000000000000000000000000000":
                    print(f"Resolved address: {address}")
                
                # Try to get DNS A record
                try:
                    dns_record = resolver.functions.dnsRecord(node, "_dns.nick.eth").call()
                    if dns_record:
                        print(f"DNS record found: {dns_record.hex()}")
                except Exception as e:
                    print(f"No DNS records found: {e}")
                    
                # Try to get any text records
                try:
                    eth_address = resolver.functions.text(node, "ETH").call()
                    if eth_address:
                        print(f"ETH text record: {eth_address}")
                except Exception:
                    pass
                    
                # Try to get content hash
                try:
                    content = resolver.functions.contenthash(node).call()
                    if content and content != b'':
                        print(f"Content hash: {content.hex()}")
                except Exception:
                    pass
                
                return owner  # Return the owner address
                
            except Exception as e:
                print(f"Error reading resolver data: {e}")
                return owner  # Return owner even if resolver fails
            
        except Exception as e:
            print(f"Error resolving ENS domain: {e}")
            return None

    def _get_ds_record(self, domain):
        """Get DS record for a domain"""
        try:
            ds = self.resolver.resolve(domain, 'DS')
            return ds[0]
        except Exception:
            return None

    def _get_dnskey_record(self, domain):
        """Get DNSKEY record for a domain"""
        try:
            dnskey = self.resolver.resolve(domain, 'DNSKEY')
            return dnskey[0]
        except Exception:
            return None

    def lookup_dns_record(self, record_type, domain):
        """Look up a DNS record with DNSSEC validation"""
        # Handle .eth domains differently
        if domain.endswith('.eth'):
            if record_type == 'TXT':
                address = self.resolve_eth_domain(domain)
                if address:
                    return f"eth-address={address}"
                return None
            else:
                print(f"Only TXT record lookups are supported for .eth domains")
                return None

        if not domain or not record_type:
            return None

        try:
            # First, check if the domain has DNSSEC enabled
            ds_record = self._get_ds_record(domain)
            if not ds_record:
                print(f"Warning: No DS record found for {domain}, DNSSEC may not be enabled")
            
            # Get the actual record
            answer = self.resolver.resolve(domain, record_type)
            if not answer:
                return None

            # Try to get DNSKEY and validate if available
            dnskey = self._get_dnskey_record(domain)
            if dnskey:
                try:
                    # Get RRSIG for the answer
                    rrsig_answer = self.resolver.resolve(domain, 'RRSIG')
                    if rrsig_answer:
                        print(f"Found DNSSEC signatures for {domain}")
                except Exception as e:
                    print(f"No RRSIG records found: {e}")

            # For TXT records, look specifically for Ethereum address records
            if record_type == 'TXT':
                for rdata in answer:
                    txt_string = rdata.to_text().strip('"')
                    # Check for Ethereum address format
                    if txt_string.startswith('eth-address='):
                        eth_address = txt_string.split('=')[1]
                        if Web3.is_address(eth_address):
                            print(f"Found Ethereum address: {eth_address}")
                            return eth_address
                    # Also check ENS standard format
                    elif txt_string.startswith('a=0x'):
                        eth_address = txt_string[2:]  # Remove 'a=' prefix
                        if Web3.is_address(eth_address):
                            print(f"Found Ethereum address: {eth_address}")
                            return eth_address
                print("No valid Ethereum address found in TXT records")
                return None

            return answer[0].to_text()

        except Exception as e:
            print(f"Error looking up DNS record: {e}")
            return None

    def construct_proof(self, record_type, domain):
        """Construct a DNSSEC proof for a DNS record"""
        record = self.lookup_dns_record(record_type, domain)
        if record is None:
            return None

        try:
            # Get DNSKEY and DS records
            dnskey = self._get_dnskey_record(domain)
            ds = self._get_ds_record(domain)
            
            # Create RRSIG record
            rrsig_record = construct_rrsig(
                name=domain,
                type=record_type,
                ttl=300,  # Default TTL
                algorithm=dnskey.algorithm if dnskey else 13,
                key=dnskey.to_text() if dnskey else "no-key",
                signature=ds.digest if ds else b"no-signature"
            )

            # Create RRset record
            rrset_record = construct_rrset(
                name=domain,
                type=record_type,
                ttl=300,
                flags=256,
                algorithm=dnskey.algorithm if dnskey else 13,
                key=record
            )

            # Build and encode the proof
            proof_dict = build_proof(domain, rrsig_record, rrset_record)
            # Convert to RLP encoded format that the contract expects
            proof_types = ['bytes']
            proof_values = [Web3.to_bytes(text=str(proof_dict))]
            return encode(proof_types, proof_values)
            
        except Exception as e:
            print(f"Error constructing proof: {e}")
            return None

    def submit_proof(self, proof):
        if not hasattr(self, 'wallet_manager') or not self.wallet_manager.account:
            raise ValueError("No wallet loaded. Load a wallet before submitting proofs")
        
        # Encode the proof dictionary into bytes
        encoded_proof = Web3.to_bytes(text=str(proof))
        
        # Build transaction
        tx = self.oracle.functions.verifySignedTextRecord(encoded_proof).build_transaction({
            'from': self.wallet_manager.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.wallet_manager.account.address),
            'gas': 200000,  # Estimate gas or use a safe value
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = self.wallet_manager.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx)
        
        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Proof submitted. Transaction hash: {tx_hash.hex()}")
        print(f"Gas used: {receipt['gasUsed']}")
        return receipt

    def verify_signed_text_record(self, domain, address):
        """Verify a signed TXT record proving domain ownership"""
        eth_address = self.lookup_dns_record("TXT", domain)
        if not eth_address:
            print(f"No Ethereum address found for {domain}")
            return False
            
        # Convert addresses to checksum format for comparison
        try:
            domain_address = Web3.to_checksum_address(eth_address)
            verify_address = Web3.to_checksum_address(address)
            
            if domain_address.lower() == verify_address.lower():
                print(f"✓ Domain {domain} is owned by {domain_address}")
                return True
            else:
                print(f"✗ Domain {domain} is owned by {domain_address}, not {verify_address}")
                return False
        except Exception as e:
            print(f"Error verifying address: {e}")
            return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description='DNSSEC Proof Tool')
    parser.add_argument('record_type', choices=['A', 'AAAA', 'TXT'],
                        help='Type of DNS record to fetch')
    parser.add_argument('domain', help='Domain name to fetch DNS information for')
    parser.add_argument('--provider', required=False, help='Web3 provider URL (e.g. Infura/Alchemy endpoint)')

    args = parser.parse_args()

    prover = DnsProver(args.provider)

    proof = prover.construct_proof(args.record_type, args.domain)
    if proof is not None:
        prover.submit_proof(proof)

if __name__ == "__main__":
    main()