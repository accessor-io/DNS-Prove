import unittest
from dns_prove.dnsprover import DnsProver
import dns.resolver

class TestDnsProver(unittest.TestCase):
    def setUp(self):
        # Using a valid Ethereum address format (40 hex characters after 0x)
        self.dnsprover = DnsProver("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")

    def test_successful_lookup_dns_record(self):
        # Test with a known stable domain
        domain = "google.com"
        record_type = "A"

        result = self.dnsprover.lookup_dns_record(record_type, domain)
        
        # Verify result is a valid IP address
        self.assertIsNotNone(result)
        # Basic IP address format validation (x.x.x.x)
        self.assertRegex(result, r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    def test_lookup_with_invalid_domain(self):
        # Test with a non-existent domain
        result = self.dnsprover.lookup_dns_record("A", "thisdomain.definitely.does.not.exist.example")
        self.assertIsNone(result)

    def test_lookup_with_invalid_record_type(self):
        # Test with an invalid record type
        result = self.dnsprover.lookup_dns_record("INVALID", "google.com")
        self.assertIsNone(result)

    def test_invalid_input_validation(self):
        # Test with empty domain
        result = self.dnsprover.lookup_dns_record("A", "")
        self.assertIsNone(result)

        # Test with None values
        result = self.dnsprover.lookup_dns_record("A", None)
        self.assertIsNone(result)
        
        result = self.dnsprover.lookup_dns_record(None, "example.com")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
