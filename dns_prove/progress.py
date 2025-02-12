from tqdm import tqdm
import threading
import logging
from datetime import datetime

class ProgressTracker:
    def __init__(self):
        self.progress_bars = {}
        self.start_times = {}
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()

    def start_task(self, name, total, desc=None):
        """Start tracking progress for a named task.
        
        Args:
            name: Unique identifier for the task
            total: Total number of steps/items to process
            desc: Optional description of the task
        """
        with self._lock:
            self.start_times[name] = datetime.now()
            self.progress_bars[name] = tqdm(
                total=total,
                desc=desc or name,
                position=len(self.progress_bars),
                unit='items'
            )
            self.logger.info(f"Started task '{name}' with {total} items")

    def update(self, name, amount=1, status=None):
        """Update progress for a task.
        
        Args:
            name: Task identifier
            amount: Number of steps completed
            status: Optional status message
        """
        with self._lock:
            if name in self.progress_bars:
                self.progress_bars[name].update(amount)
                if status:
                    self.progress_bars[name].set_description(f"{name} - {status}")

    def complete(self, name):
        """Mark a task as complete and clean up.
        
        Args:
            name: Task identifier
        """
        with self._lock:
            if name in self.progress_bars:
                duration = datetime.now() - self.start_times[name]
                self.progress_bars[name].close()
                del self.progress_bars[name]
                del self.start_times[name]
                self.logger.info(f"Completed task '{name}' in {duration}")