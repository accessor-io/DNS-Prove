from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
import os
from pathlib import Path
import json
from getpass import getpass
import secrets
from typing import Optional, Union

class WalletManager:
    def __init__(self, keystore_path: str = None):
        """Initialize wallet manager with optional keystore path"""
        self.keystore_path = Path(keystore_path or Path.home() / '.dns-prove' / 'keystore')
        self.keystore_path.parent.mkdir(parents=True, exist_ok=True)
        self.account: Optional[LocalAccount] = None
        
    def create_wallet(self, password: str = None) -> dict:
        """Create a new wallet and save to keystore"""
        if not password:
            password = getpass("Enter password for new wallet: ")
        
        # Generate private key and create account
        private_key = secrets.token_hex(32)
        account: LocalAccount = Account.from_key(private_key)
        
        # Create keystore file
        keystore = Account.encrypt(private_key, password)
        
        # Save keystore
        wallet_file = self.keystore_path / f'wallet_{account.address}.json'
        wallet_file.write_text(json.dumps(keystore))
        
        return {
            'address': account.address,
            'private_key': private_key,
            'keystore_file': str(wallet_file)
        }
    
    def load_wallet(self, keystore_file: Union[str, Path], password: str = None) -> str:
        """Load wallet from keystore file"""
        if not password:
            password = getpass("Enter wallet password: ")
            
        keystore_file = Path(keystore_file)
        if not keystore_file.exists():
            raise FileNotFoundError(f"Keystore file not found: {keystore_file}")
            
        # Load and decrypt keystore
        keystore = json.loads(keystore_file.read_text())
        private_key = Account.decrypt(keystore, password)
        
        self.account = Account.from_key(private_key)
        return self.account.address
    
    def sign_transaction(self, transaction_dict: dict) -> str:
        """Sign a transaction with loaded wallet"""
        if not self.account:
            raise ValueError("No wallet loaded. Call load_wallet() first")
            
        signed = self.account.sign_transaction(transaction_dict)
        return signed.rawTransaction.hex()
    
    def get_balance(self, w3: Web3) -> int:
        """Get wallet balance in Wei"""
        if not self.account:
            raise ValueError("No wallet loaded")
        return w3.eth.get_balance(self.account.address) 