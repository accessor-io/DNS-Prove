from web3 import Web3
from eth_account import Account
import os

# ENS DNSSEC Oracle ABI
ORACLE_ABI = [
    {
        "constant": False,
        "inputs": [
            {
                "name": "input",
                "type": "bytes"
            },
            {
                "name": "sig",
                "type": "bytes"
            }
        ],
        "name": "submitRRSet",
        "outputs": [
            {
                "name": "",
                "type": "bytes32"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "name",
                "type": "bytes32"
            },
            {
                "name": "rrset",
                "type": "uint16"
            }
        ],
        "name": "rrsets",
        "outputs": [
            {
                "name": "inception",
                "type": "uint32"
            },
            {
                "name": "expiration",
                "type": "uint32"
            },
            {
                "name": "hash",
                "type": "bytes32"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "name",
                "type": "bytes"
            },
            {
                "name": "proof",
                "type": "bytes"
            }
        ],
        "name": "verifyDNSProof",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

class Oracle:
    def __init__(self, contract_address, web3_instance):
        self.contract_address = Web3.to_checksum_address(contract_address)
        if isinstance(web3_instance, str):
            self.w3 = Web3(Web3.HTTPProvider(web3_instance))
        else:
            self.w3 = web3_instance
            
        # Set up account from private key if available
        private_key = os.environ.get('ETH_PRIVATE_KEY')
        if private_key:
            self.account = Account.from_key(private_key)
            self.w3.eth.default_account = self.account.address
        else:
            print("Warning: No ETH_PRIVATE_KEY environment variable found. Transactions will fail.")
            
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=ORACLE_ABI)

    @property
    def address(self):
        return self.contract_address

    def submit_proof(self, proof):
        """Submit a DNSSEC proof to the Oracle contract"""
        if not hasattr(self, 'account'):
            raise Exception("No Ethereum account configured. Set ETH_PRIVATE_KEY environment variable.")
            
        try:
            # Convert the proof components to proper format
            rrset_data = Web3.to_bytes(hexstr=Web3.to_hex(text=str(proof['rrset'])))
            sig_data = Web3.to_bytes(hexstr=Web3.to_hex(text=str(proof['rrsig'])))
            
            # Build the transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Estimate gas for the transaction
            gas_estimate = self.contract.functions.submitRRSet(rrset_data, sig_data).estimate_gas({
                'from': self.account.address,
                'nonce': nonce
            })
            
            transaction = self.contract.functions.submitRRSet(rrset_data, sig_data).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'gas': gas_estimate,
                'maxFeePerGas': self.w3.eth.max_priority_fee + (2 * self.w3.eth.get_block('latest')['baseFeePerGas']),
                'maxPriorityFeePerGas': self.w3.eth.max_priority_fee,
                'nonce': nonce,
            })
            
            # Sign and send the transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"\nTransaction sent: {Web3.to_hex(tx_hash)}")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt
            
        except Exception as e:
            print(f"\nFailed to submit proof: {str(e)}")
            return None

    def verify_dns_proof(self, name, proof):
        """Verify a DNS proof without submitting it to the blockchain"""
        name_bytes = Web3.to_bytes(text=name)
        proof_bytes = Web3.to_bytes(text=str(proof))
        return self.contract.functions.verifyDNSProof(name_bytes, proof_bytes).call()

    def get_rrset(self, name, rrset_type):
        """Get an RRSet from the Oracle contract"""
        name_hash = Web3.keccak(text=name)
        return self.contract.functions.rrsets(name_hash, rrset_type).call()

    # Add more functions as needed...
