"""Monitoring system for tracking crew performance."""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import os
from pathlib import Path

@dataclass
class CrewMetrics:
    """Metrics for a crew run."""
    crew_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    num_tasks: int = 0
    num_completed: int = 0
    num_failed: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.errors is None:
            self.errors = []
            
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "crew_type": self.crew_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            "num_tasks": self.num_tasks,
            "num_completed": self.num_completed,
            "num_failed": self.num_failed,
            "completion_rate": self.num_completed / self.num_tasks if self.num_tasks > 0 else 0,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "errors": self.errors
        }

class PerformanceMonitor:
    """Monitors and tracks crew performance."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize the monitor.
        
        Args:
            storage_dir: Directory to store metrics (default: ./metrics)
        """
        self.storage_dir = Path(storage_dir or "./metrics")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_runs: Dict[str, CrewMetrics] = {}
        self.logger = logging.getLogger(__name__)
        
    def start_monitoring(self, run_id: str, crew_type: str, num_tasks: int) -> None:
        """Start monitoring a crew run.
        
        Args:
            run_id: Unique identifier for the run
            crew_type: Type of crew being monitored
            num_tasks: Number of tasks in the run
        """
        self.current_runs[run_id] = CrewMetrics(
            crew_type=crew_type,
            start_time=datetime.now(),
            num_tasks=num_tasks
        )
        self.logger.info(f"Started monitoring run {run_id} ({crew_type})")
        
    def log_task_completion(
        self,
        run_id: str,
        task_id: str,
        success: bool,
        tokens: int,
        cost: float
    ) -> None:
        """Log the completion of a task.
        
        Args:
            run_id: Run identifier
            task_id: Task identifier
            success: Whether the task succeeded
            tokens: Number of tokens used
            cost: Cost of the task
        """
        metrics = self.current_runs.get(run_id)
        if not metrics:
            raise ValueError(f"No active monitoring for run {run_id}")
            
        if success:
            metrics.num_completed += 1
        else:
            metrics.num_failed += 1
            
        metrics.total_tokens += tokens
        metrics.total_cost += cost
        
        self.logger.info(
            f"Task {task_id} completed - Success: {success}, "
            f"Tokens: {tokens}, Cost: ${cost:.4f}"
        )
        
    def log_error(self, run_id: str, error: str) -> None:
        """Log an error for a run.
        
        Args:
            run_id: Run identifier
            error: Error message
        """
        metrics = self.current_runs.get(run_id)
        if not metrics:
            raise ValueError(f"No active monitoring for run {run_id}")
            
        metrics.errors.append(error)
        self.logger.error(f"Run {run_id} error: {error}")
        
    def end_monitoring(self, run_id: str) -> Dict:
        """End monitoring for a run and save metrics.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Dictionary with run metrics
        """
        metrics = self.current_runs.get(run_id)
        if not metrics:
            raise ValueError(f"No active monitoring for run {run_id}")
            
        metrics.end_time = datetime.now()
        metrics_dict = metrics.to_dict()
        
        # Save metrics to file
        metrics_file = self.storage_dir / f"{run_id}_{metrics.crew_type}.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics_dict, f, indent=2)
            
        del self.current_runs[run_id]
        self.logger.info(f"Ended monitoring for run {run_id}")
        
        return metrics_dict
        
    def get_metrics(self, run_id: str) -> Optional[Dict]:
        """Get metrics for a specific run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Dictionary with run metrics or None if not found
        """
        # Check active runs
        if run_id in self.current_runs:
            return self.current_runs[run_id].to_dict()
            
        # Check saved metrics
        for file in self.storage_dir.glob(f"{run_id}_*.json"):
            with open(file) as f:
                return json.load(f)
                
        return None
        
    def get_crew_stats(self, crew_type: str, days: int = 30) -> Dict:
        """Get statistics for a crew type over time.
        
        Args:
            crew_type: Type of crew to analyze
            days: Number of days to look back
            
        Returns:
            Dictionary with crew statistics
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        metrics_list = []
        
        # Load all metrics files for this crew type
        for file in self.storage_dir.glob(f"*_{crew_type}.json"):
            with open(file) as f:
                metrics = json.load(f)
                start_time = datetime.fromisoformat(metrics["start_time"]).timestamp()
                if start_time >= cutoff_time:
                    metrics_list.append(metrics)
                    
        if not metrics_list:
            return {
                "crew_type": crew_type,
                "num_runs": 0,
                "avg_duration": 0,
                "avg_completion_rate": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "error_rate": 0
            }
            
        # Calculate statistics
        num_runs = len(metrics_list)
        avg_duration = sum(
            m["duration"] for m in metrics_list if m["duration"]
        ) / num_runs
        avg_completion_rate = sum(
            m["completion_rate"] for m in metrics_list
        ) / num_runs
        total_tokens = sum(m["total_tokens"] for m in metrics_list)
        total_cost = sum(m["total_cost"] for m in metrics_list)
        error_rate = sum(
            1 for m in metrics_list if m["errors"]
        ) / num_runs
        
        return {
            "crew_type": crew_type,
            "num_runs": num_runs,
            "avg_duration": avg_duration,
            "avg_completion_rate": avg_completion_rate,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "error_rate": error_rate
        }