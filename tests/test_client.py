import unittest
from dns_prove.client import main
from dns_prove.dnsprover import DnsProver
from dns_prove.oracle import Oracle
import argparse

class TestClient(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.oracle_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        self.provider_url = "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"

    def test_argument_parsing(self):
        """Test command line argument parsing"""
        parser = argparse.ArgumentParser()
        parser.add_argument('record_type', choices=['A', 'AAAA', 'TXT'])
        parser.add_argument('domain')
        parser.add_argument('--oracle', required=True)
        parser.add_argument('--provider')

        # Test valid arguments
        args = parser.parse_args(['A', 'example.com', '--oracle', self.oracle_address])
        self.assertEqual(args.record_type, 'A')
        self.assertEqual(args.domain, 'example.com')
        self.assertEqual(args.oracle, self.oracle_address)
        self.assertIsNone(args.provider)

    def test_dnsprover_creation(self):
        """Test DnsProver instance creation"""
        prover = DnsProver(self.oracle_address, self.provider_url)
        self.assertIsNotNone(prover)
        self.assertEqual(prover.oracle_address, self.oracle_address)

    def test_oracle_creation(self):
        """Test Oracle instance creation"""
        oracle = Oracle(self.oracle_address, self.provider_url)
        self.assertIsNotNone(oracle)
        self.assertEqual(oracle.address, self.oracle_address)

if __name__ == '__main__':
    unittest.main() 