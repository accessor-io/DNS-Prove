import unittest
from unittest.mock import patch, Mock
from dns_prove.dnsprover import DnsProver
import dns.resolver

class TestDnsProver(unittest.TestCase):
    def setUp(self):
        # Using a valid Ethereum address format (40 hex characters after 0x)
        self.dnsprover = DnsProver("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")

    @patch('dns.resolver.Resolver.query')
    def test_successful_lookup_dns_record(self, mock_query):
        # Mock DNS response
        mock_response = Mock()
        mock_response.to_text.return_value = "1.2.3.4"
        mock_query.return_value = [mock_response]

        # Test domain and record type
        domain = "example.com"
        record_type = "A"

        result = self.dnsprover.lookup_dns_record(record_type, domain)
        
        # Verify the resolver was called with correct parameters
        mock_query.assert_called_once_with(domain, record_type)
        
        # Verify result contains expected data
        self.assertIsNotNone(result)
        self.assertEqual(result, "1.2.3.4")

    @patch('dns.resolver.Resolver.query')
    def test_lookup_with_invalid_domain(self, mock_query):
        # Mock DNS resolution failure
        mock_query.side_effect = dns.resolver.NXDOMAIN()

        result = self.dnsprover.lookup_dns_record("A", "invalid.domain")
        self.assertIsNone(result)

    @patch('dns.resolver.Resolver.query')
    def test_lookup_with_invalid_record_type(self, mock_query):
        # Mock DNS resolution failure for invalid record type
        mock_query.side_effect = dns.resolver.NoAnswer()

        result = self.dnsprover.lookup_dns_record("INVALID", "example.com")
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
