import unittest
from web3 import Web3
from dns_prove.oracle import Oracle

class TestOracle(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.oracle_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        self.provider_url = "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
        self.oracle = Oracle(self.oracle_address, self.provider_url)

    def test_oracle_initialization(self):
        """Test Oracle initialization"""
        self.assertIsNotNone(self.oracle)
        self.assertEqual(self.oracle.address, self.oracle_address)
        self.assertTrue(Web3.is_address(self.oracle.address))

    def test_oracle_connection(self):
        """Test Oracle connection to Ethereum network"""
        self.assertTrue(self.oracle.w3.is_connected())

    def test_oracle_contract(self):
        """Test Oracle contract interface"""
        self.assertIsNotNone(self.oracle.contract)
        self.assertEqual(self.oracle.contract.address, self.oracle_address)

if __name__ == '__main__':
    unittest.main()
