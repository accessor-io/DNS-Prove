import unittest
from unittest.mock import Mock, patch
from dns_prove.dnsprover import DnsProver
import dns.resolver
from dns_prove.utils import build_proof
from web3 import Web3
import sys

class TestDnsProver(unittest.TestCase):
    def setUp(self):
        # Mock Web3 provider
        self.w3_patcher = patch('web3.Web3')
        self.mock_w3 = self.w3_patcher.start()
        
        # Mock chain_id
        self.mock_w3.eth.chain_id = 1  # Mainnet
        
        # Setup test instance
        self.oracle_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        self.provider_url = "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
        
        # Mock Web3 instance
        self.mock_w3_instance = Mock()
        self.mock_w3.HTTPProvider.return_value = self.mock_w3_instance
        self.mock_w3.return_value = self.mock_w3_instance
        
        self.dnsprover = DnsProver(self.oracle_address, self.provider_url)

    def tearDown(self):
        self.w3_patcher.stop()

    @patch('dns.resolver.Resolver')
    def test_successful_lookup_dns_record(self, mock_resolver):
        """Test successful DNS record lookup with mock"""
        # Mock DNS response
        mock_answer = Mock()
        mock_answer.to_text.return_value = "192.168.1.1"
        mock_resolver.return_value.resolve.return_value = [mock_answer]

        result = self.dnsprover.lookup_dns_record("A", "example.com")
        self.assertEqual(result, "192.168.1.1")
        mock_resolver.return_value.resolve.assert_called_once_with("example.com", "A")

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

    @patch('dns.resolver.Resolver')
    def test_lookup_dns_record_txt(self, mock_resolver):
        # Mock DNS response
        mock_answer = Mock()
        mock_answer.to_text.return_value = '"eth-address=0x742d35Cc6634C0532925a3b844Bc454e4438f44e"'
        mock_resolver.return_value.resolve.return_value = [mock_answer]

        result = self.dnsprover.lookup_dns_record("TXT", "example.com")
        self.assertEqual(result, "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")

    @patch('dns.resolver.Resolver')
    def test_lookup_dns_record_a(self, mock_resolver):
        # Mock DNS response
        mock_answer = Mock()
        mock_answer.to_text.return_value = "192.168.1.1"
        mock_resolver.return_value.resolve.return_value = [mock_answer]

        result = self.dnsprover.lookup_dns_record("A", "example.com")
        self.assertEqual(result, "192.168.1.1")

    def test_namehash(self):
        # Test ENS namehash function
        test_cases = [
            ("", "0x0000000000000000000000000000000000000000000000000000000000000000"),
            ("eth", "0x93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae"),
            ("alice.eth", "0x787192fc5378cc32aa956ddfdedbf26b24e8d78e40109add0eea2c1a012c3dec"),
        ]
        
        for name, expected in test_cases:
            result = self.dnsprover.namehash(name)
            self.assertEqual(Web3.to_hex(result), expected)

    def test_verify_signed_text_record(self):
        with patch.object(self.dnsprover, 'lookup_dns_record') as mock_lookup:
            # Test successful verification
            mock_lookup.return_value = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
            result = self.dnsprover.verify_signed_text_record(
                "example.com",
                "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
            )
            self.assertTrue(result)

            # Test failed verification
            result = self.dnsprover.verify_signed_text_record(
                "example.com",
                "0x0000000000000000000000000000000000000000"
            )
            self.assertFalse(result)

    def test_invalid_inputs(self):
        # Test invalid record type
        result = self.dnsprover.lookup_dns_record("INVALID", "example.com")
        self.assertIsNone(result)

        # Test empty domain
        result = self.dnsprover.lookup_dns_record("TXT", "")
        self.assertIsNone(result)

        # Test None values
        result = self.dnsprover.lookup_dns_record("TXT", None)
        self.assertIsNone(result)
        result = self.dnsprover.lookup_dns_record(None, "example.com")
        self.assertIsNone(result)

class TestCLI(unittest.TestCase):
    @patch('dns_prove.client.DnsProver')
    def test_cli_txt_lookup(self, mock_dnsprover):
        from dns_prove.client import main
        from io import StringIO

        # Mock DNS response
        mock_instance = Mock()
        mock_instance.lookup_dns_record.return_value = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        mock_dnsprover.return_value = mock_instance

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Test CLI
        sys.argv = [
            "dns-prove-py",
            "TXT",
            "example.com",
            "--oracle",
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        ]
        
        try:
            main()
        except SystemExit:
            pass

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        self.assertIn("0x742d35Cc6634C0532925a3b844Bc454e4438f44e", output)

    def tearDown(self):
        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    unittest.main()
