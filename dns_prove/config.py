import yaml
from pathlib import Path

class Config:
    def __init__(self, config_file="config.yml"):
        self.config_file = Path(config_file)
        self.load()
    
    def load(self):
        if self.config_file.exists():
            self.settings = yaml.safe_load(self.config_file.read_text())
        else:
            self.settings = self.default_settings()
            self.save()
    
    def default_settings(self):
        return {
            'networks': {
                'mainnet': {
                    'provider': 'https://mainnet.infura.io/v3/${INFURA_API_KEY}',
                    'oracle': '0x226159d592E2b063810a10Ebf6cF7A7bAD0193a6'
                },
                'testnet': {
                    'provider': 'https://sepolia.infura.io/v3/${INFURA_API_KEY}',
                    'oracle': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
                }
            },
            'cache': {
                'enabled': True,
                'ttl': 3600
            }
        } 

    def save(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(self.settings, f, default_flow_style=False)

    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key, value):
        """Set configuration value"""
        keys = key.split('.')
        target = self.settings
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        self.save() 