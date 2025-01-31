import unittest
from dns_prove.dnsprover import DnsProver
import dns.resolver
from dns_prove.utils import build_proof

class TestDnsProver(unittest.TestCase):
    def setUp(self):
        # Using a valid Ethereum address format for testing
        self.oracle_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        self.provider_url = "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
        self.dnsprover = DnsProver(self.oracle_address, self.provider_url)

    def test_successful_lookup_dns_record(self):
        """Test successful DNS record lookup"""
        # Test with a known stable domain
        domain = "google.com"
        record_type = "A"

        result = self.dnsprover.lookup_dns_record(record_type, domain)
        
        # Verify result is a valid IP address
        self.assertIsNotNone(result)
        # Basic IP address format validation (x.x.x.x)
        self.assertRegex(result, r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    def test_lookup_with_invalid_domain(self):
        """Test DNS lookup with invalid domain"""
        result = self.dnsprover.lookup_dns_record("A", "thisdomain.definitely.does.not.exist.example")
        self.assertIsNone(result)

    def test_lookup_with_invalid_record_type(self):
        """Test DNS lookup with invalid record type"""
        result = self.dnsprover.lookup_dns_record("INVALID", "google.com")
        self.assertIsNone(result)

    def test_invalid_input_validation(self):
        """Test input validation for DNS lookups"""
        # Test with empty domain
        result = self.dnsprover.lookup_dns_record("A", "")
        self.assertIsNone(result)

        # Test with None values
        result = self.dnsprover.lookup_dns_record("A", None)
        self.assertIsNone(result)
        
        result = self.dnsprover.lookup_dns_record(None, "example.com")
        self.assertIsNone(result)

    def test_construct_proof(self):
        """Test proof construction"""
        domain = "google.com"
        record_type = "A"
        
        # First get a DNS record
        record = self.dnsprover.lookup_dns_record(record_type, domain)
        self.assertIsNotNone(record)
        
        # Then construct a proof
        proof = build_proof(domain, {
            "name": domain,
            "type": "RRSIG",
            "ttl": 300,
            "algorithm": 13,
            "key": "test_key",
            "signature": "test_signature"
        }, {
            "name": domain,
            "type": record_type,
            "ttl": 300,
            "data": record
        })
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof["name"], domain)
        self.assertIn("rrsig", proof)
        self.assertIn("rrset", proof)

if __name__ == '__main__':
    unittest.main()
