from web3 import Web3

class Oracle:
    def __init__(self, contract_address, web3_instance):
        self.contract_address = Web3.to_checksum_address(contract_address)
        if isinstance(web3_instance, str):
            self.w3 = Web3(Web3.HTTPProvider(web3_instance))
        else:
            self.w3 = web3_instance
        self.contract = self.w3.eth.contract(address=self.contract_address)

    @property
    def address(self):
        return self.contract_address

    def get_abi(self):
        # Replace with actual ABI
        return []

    def submit_proof(self, proof):
        tx_hash = self.contract.functions.submitProof(proof).transact()
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        return tx_receipt

    def get_proof(self, proof_id):
        return self.contract.functions.getProof(proof_id).call()

    # Add more functions as needed...
