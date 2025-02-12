import json
from pathlib import Path
from datetime import datetime, timedelta

class ProofCache:
    def __init__(self, cache_dir=".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.hits = 0
        self.misses = 0
        self._stats = {}  # Cache statistics
    
    def get(self, domain, record_type):
        cache_file = self.cache_dir / f"{domain}_{record_type}.json"
        if cache_file.exists():
            data = json.loads(cache_file.read_text())
            if datetime.fromisoformat(data['timestamp']) > datetime.now() - timedelta(hours=1):
                self.hits += 1
                return data['proof']
        self.misses += 1
        return None
    
    def set(self, domain, record_type, proof):
        cache_file = self.cache_dir / f"{domain}_{record_type}.json"
        data = {
            'timestamp': datetime.now().isoformat(),
            'proof': proof
        }
        cache_file.write_text(json.dumps(data))

    def get_all(self):
        """Get all cached proofs"""
        results = []
        for cache_file in self.cache_dir.glob('*.json'):
            data = json.loads(cache_file.read_text())
            results.append({
                'domain': cache_file.stem.split('_')[0],
                'type': cache_file.stem.split('_')[1],
                'proof': data['proof'],
                'timestamp': data['timestamp']
            })
        return results

    @property
    def stats(self):
        """Get cache statistics (cached property)"""
        if not self._stats:
            files = list(self.cache_dir.glob('*.json'))
            self._stats = {
                'entries': len(files),
                'size': sum(f.stat().st_size for f in files),
                'hit_rate': round((self.hits / (self.hits + self.misses) * 100) 
                                    if (self.hits + self.misses) > 0 else 0, 2)
            }
        return self._stats

    def clear(self):
        """Clear all cached proofs"""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
        self.hits = 0
        self.misses = 0 