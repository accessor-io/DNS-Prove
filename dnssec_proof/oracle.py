from web3 import Web3

class Oracle:
    def __init__(self, contract_address, web3_instance):
        self.contract_address = Web3.toChecksumAddress(contract_address)
        self.web3 = web3_instance
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.get_abi())

    def get_abi(self):
        # Replace iwth ABI
        return []

    def submit_proof(self, proof):
        tx_hash = self.contract.functions.submitProof(proof).transact()
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        return tx_receipt

    def get_proof(self, proof_id):
        return self.contract.functions.getProof(proof_id).call()

