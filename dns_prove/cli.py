import cmd
from dns_prove.dnsprover import DnsProver
from dns_prove.batch import BatchProcessor
from dns_prove.cache import ProofCache
import yaml
from dns_prove.config import Config
from dns_prove.wallet import WalletManager

class DNSProveCLI(cmd.Cmd):
    intro = 'Welcome to DNS Prove. Type help or ? to list commands.\n'
    prompt = '(dns-prove) '
    
    # Command aliases
    aliases = {
        'v': 'verify',
        'b': 'batch',
        'n': 'network',
        's': 'status',
        'c': 'config',
        'r': 'resolve',
        'e': 'export',
        'q': 'quit',
        'clear': 'cache clear',
        'stats': 'cache stats'
    }
    
    def __init__(self):
        super().__init__()
        self.config = Config()  # Initialize config
        self.prover = DnsProver()
        self.batch_processor = BatchProcessor(self.prover)
        self.cache = ProofCache()
        self.network = 'mainnet'  # Default network
        self.wallet_manager = WalletManager()
        self.wallet_loaded = False
    
    def precmd(self, line):
        """Pre-process command line to handle aliases"""
        if not line:
            return line
        
        cmd, *args = line.split(maxsplit=1)
        if cmd in self.aliases:
            return f"{self.aliases[cmd]} {args[0] if args else ''}"
        return line
    
    def do_verify(self, arg):
        """Verify a domain: verify example.eth"""
        domain = arg.strip()
        proof = self.prover.construct_proof("TXT", domain)
        if proof:
            self.prover.submit_proof(proof)
    
    def do_batch(self, arg):
        """Process multiple domains from a file: batch domains.txt [output.json]"""
        args = arg.strip().split()
        input_file = args[0]
        output_file = args[1] if len(args) > 1 else None
        results = self.batch_processor.process_file(input_file, output_file)
        print(f"Processed {len(results)} domains")

    def do_config(self, arg):
        """View or modify configuration: config [key] [value]"""
        args = arg.strip().split()
        if not args:
            print(yaml.dump(self.config.settings, default_flow_style=False))
            return
        
        if len(args) == 1:
            value = self.config.get(args[0])
            print(f"{args[0]}: {value}")
        else:
            key, value = args[0], ' '.join(args[1:])
            self.config.set(key, value)
            print(f"Updated {key} = {value}")

    def do_cache(self, arg):
        """Cache management: cache [clear|stats]"""
        cmd = arg.strip()
        if cmd == 'clear':
            self.cache.clear()
            print("Cache cleared")
        elif cmd == 'stats':
            stats = self.cache.stats
            print(f"Cache entries: {stats['entries']}")
            print(f"Cache size: {stats['size']} bytes")
            print(f"Hit rate: {stats['hit_rate']}%")

    def do_network(self, arg):
        """Switch between networks: network [mainnet|testnet]"""
        network = arg.strip().lower()
        if network in ['mainnet', 'testnet']:
            try:
                self.network = network
                self.prover = DnsProver(network=network)
                self.batch_processor = BatchProcessor(self.prover)  # Recreate with new prover
                print(f"Switched to {network}")
            except Exception as e:
                print(f"Error switching network: {e}")
                self.network = 'mainnet'  # Fallback to mainnet
        else:
            print("Invalid network. Use 'mainnet' or 'testnet'")

    def do_status(self, arg):
        """Show current status and settings"""
        print(f"Network: {self.network}")
        print(f"Provider: {self.prover.provider_url}")
        print(f"Oracle Address: {self.prover.oracle.address}")
        if self.cache:
            stats = self.cache.get_stats()
            print(f"Cache Status: Enabled ({stats['entries']} entries)")
        print(f"Chain ID: {self.prover.w3.eth.chain_id}")

    def do_resolve(self, arg):
        """Resolve ENS domain to address: resolve vitalik.eth"""
        domain = arg.strip()
        if not domain.endswith('.eth'):
            print("Error: Only .eth domains supported")
            return
        try:
            address = self.prover.resolve_eth_domain(domain)
            print(f"Resolved {domain} to {address}")
        except Exception as e:
            print(f"Error resolving domain: {e}")

    def do_export(self, arg):
        """Export proofs to file: export output.json"""
        if not arg:
            print("Error: Please specify output file")
            return
        try:
            self.batch_processor._save_results(
                self.cache.get_all(),
                arg.strip()
            )
            print(f"Exported proofs to {arg}")
        except Exception as e:
            print(f"Error exporting: {e}")

    def do_quit(self, arg):
        """Exit the DNS Prove CLI"""
        print("Goodbye!")
        return True

    def do_help(self, arg):
        """List available commands with "help" or detailed help with "help cmd"."""
        if arg:
            # Handle alias help requests
            if arg in self.aliases:
                arg = self.aliases[arg]
            super().do_help(arg)
        else:
            print("\nAvailable commands:")
            commands = {
                'verify': 'Verify a domain\'s DNS records',
                'batch': 'Process multiple domains from file',
                'network': 'Switch network (mainnet/testnet)',
                'status': 'Show current status',
                'config': 'View/edit configuration',
                'cache': 'Cache management',
                'resolve': 'Resolve ENS domain',
                'export': 'Export proofs',
                'quit': 'Exit the program'
            }
            
            # Generate help text from commands dict
            for cmd, desc in commands.items():
                aliases = [k for k, v in self.aliases.items() if v == cmd]
                alias_str = f" ({','.join(aliases)})" if aliases else ""
                print(f"  {cmd}{alias_str:<15} - {desc}")

    def complete_network(self, text, line, begidx, endidx):
        """Tab completion for network command"""
        networks = ['mainnet', 'testnet']
        if text:
            return [n for n in networks if n.startswith(text)]
        return networks

    def complete_verify(self, text, line, begidx, endidx):
        """Tab completion for verify command"""
        if text.endswith('.eth'):
            # Could suggest common ENS domains
            suggestions = ['vitalik.eth', 'ens.eth', 'nick.eth']
            return [s for s in suggestions if s.startswith(text)]
        return []

    def do_wallet(self, arg):
        """Wallet management: wallet [create|load|balance|address]"""
        args = arg.strip().split()
        if not args:
            print("Usage: wallet [create|load|balance|address]")
            return
        
        cmd = args[0]
        if cmd == 'create':
            try:
                wallet = self.wallet_manager.create_wallet()
                print(f"Created new wallet: {wallet['address']}")
                print(f"Keystore saved to: {wallet['keystore_file']}")
                self.wallet_loaded = True
            except Exception as e:
                print(f"Error creating wallet: {e}")
        
        elif cmd == 'load':
            if len(args) < 2:
                print("Usage: wallet load <keystore_file>")
                return
            try:
                address = self.wallet_manager.load_wallet(args[1])
                print(f"Loaded wallet: {address}")
                self.wallet_loaded = True
            except Exception as e:
                print(f"Error loading wallet: {e}")
        
        elif cmd == 'balance':
            if not self.wallet_loaded:
                print("No wallet loaded. Use 'wallet load' first")
                return
            balance = self.wallet_manager.get_balance(self.prover.w3)
            eth_balance = self.prover.w3.from_wei(balance, 'ether')
            print(f"Balance: {eth_balance} ETH")
        
        elif cmd == 'address':
            if not self.wallet_loaded:
                print("No wallet loaded")
                return
            print(f"Current wallet: {self.wallet_manager.account.address}")

    def default(self, line):
        """Handle unknown commands"""
        print(f"Unknown command: {line}")
        print("Type 'help' for list of commands") 