import unittest
from unittest.mock import MagicMock
from dnssec_proof.oracle import Oracle

class TestOracle(unittest.TestCase):
    def setUp(self):
        self.web3_mock = MagicMock()
        self.oracle = Oracle(contract_address='0x123456', web3_instance=self.web3_mock)

    def test_submit_proof(self):
        proof = {"name": ".", "rrsig": {}, "rrset": []}
        self.oracle.contract.functions.submitProof = MagicMock(return_value='0x123')
        self.web3_mock.eth.waitForTransactionReceipt = MagicMock(return_value=True)
        result = self.oracle.submit_proof(proof)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
