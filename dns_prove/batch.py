from pathlib import Path
from dns_prove.progress import ProgressTracker
from dns_prove.cache import ProofCache
import csv
import json

class BatchProcessor:
    def __init__(self, prover, cache_enabled=True):
        self.prover = prover
        self.progress = ProgressTracker()
        self.cache = ProofCache() if cache_enabled else None
        
    def process_file(self, file_path, output_file=None):
        """Process domains from a file with progress tracking"""
        domains = self._read_domains(file_path)
        results = []
        
        self.progress.start_task("Processing Domains", len(domains))
        
        for domain in domains:
            # Check cache first
            if self.cache:
                proof = self.cache.get(domain, "TXT")
                if proof:
                    results.append({"domain": domain, "status": "cached", "proof": proof})
                    continue
            
            # Generate new proof
            try:
                proof = self.prover.construct_proof("TXT", domain)
                if proof:
                    if self.cache:
                        self.cache.set(domain, "TXT", proof)
                    results.append({"domain": domain, "status": "success", "proof": proof})
                else:
                    results.append({"domain": domain, "status": "failed", "proof": None})
            except Exception as e:
                results.append({"domain": domain, "status": "error", "error": str(e)})
            
            self.progress.update("Processing Domains")
        
        self.progress.complete("Processing Domains")
        
        if output_file:
            self._save_results(results, output_file)
        
        return results
    
    def _read_domains(self, file_path):
        """Read domains from various file formats"""
        path = Path(file_path)
        if path.suffix == '.csv':
            with open(path) as f:
                return [row[0] for row in csv.reader(f)]
        elif path.suffix == '.json':
            with open(path) as f:
                data = json.load(f)
                return [d.get('domain') for d in data if 'domain' in d]
        else:
            with open(path) as f:
                return [line.strip() for line in f if line.strip()] 

    def _save_results(self, results, output_file):
        """Save batch processing results to file"""
        path = Path(output_file)
        if path.suffix == '.json':
            with open(path, 'w') as f:
                json.dump(results, f, indent=2)
        elif path.suffix == '.csv':
            with open(path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['domain', 'status', 'proof', 'error'])
                writer.writeheader()
                for result in results:
                    writer.writerow(result)
        else:
            with open(path, 'w') as f:
                for result in results:
                    f.write(f"{result['domain']}: {result['status']}\n") 