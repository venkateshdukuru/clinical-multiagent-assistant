"""
Metrics collection module for agent performance monitoring.
Tracks execution statistics and performance metrics.
"""

from typing import Dict, Any, Optional
from threading import Lock
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentMetrics:
    """Performance metrics for a single agent."""
    agent_name: str
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    skipped_runs: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: Optional[float] = None
    max_duration_ms: Optional[float] = None
    last_run: Optional[str] = None
    last_status: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_runs == 0:
            return 0.0
        return round((self.successful_runs / self.total_runs) * 100, 2)
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.total_runs == 0:
            return 0.0
        return round((self.failed_runs / self.total_runs) * 100, 2)
    
    @property
    def avg_duration_ms(self) -> float:
        """Calculate average execution time."""
        if self.successful_runs == 0:
            return 0.0
        return round(self.total_duration_ms / self.successful_runs, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "agent_name": self.agent_name,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "skipped_runs": self.skipped_runs,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "avg_duration_ms": self.avg_duration_ms,
            "min_duration_ms": self.min_duration_ms,
            "max_duration_ms": self.max_duration_ms,
            "last_run": self.last_run,
            "last_status": self.last_status
        }


class MetricsCollector:
    """
    Thread-safe metrics collector for agent performance.
    Stores metrics in memory.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics: Dict[str, AgentMetrics] = {}
        self.lock = Lock()
        self.system_start_time = datetime.utcnow()
    
    def record_execution(
        self,
        agent_name: str,
        status: str,
        duration_ms: Optional[float] = None
    ):
        """
        Record an agent execution.
        
        Args:
            agent_name: Name of the agent
            status: Execution status (SUCCESS, FAILED, SKIPPED)
            duration_ms: Execution duration in milliseconds
        """
        with self.lock:
            if agent_name not in self.metrics:
                self.metrics[agent_name] = AgentMetrics(agent_name=agent_name)
            
            metrics = self.metrics[agent_name]
            metrics.total_runs += 1
            metrics.last_run = datetime.utcnow().isoformat()
            metrics.last_status = status
            
            if status == "SUCCESS":
                metrics.successful_runs += 1
                if duration_ms is not None:
                    metrics.total_duration_ms += duration_ms
                    
                    if metrics.min_duration_ms is None or duration_ms < metrics.min_duration_ms:
                        metrics.min_duration_ms = duration_ms
                    
                    if metrics.max_duration_ms is None or duration_ms > metrics.max_duration_ms:
                        metrics.max_duration_ms = duration_ms
            
            elif status == "FAILED":
                metrics.failed_runs += 1
            
            elif status == "SKIPPED":
                metrics.skipped_runs += 1
    
    def get_agent_metrics(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent metrics dictionary
        """
        with self.lock:
            if agent_name not in self.metrics:
                return None
            return self.metrics[agent_name].to_dict()
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for all agents.
        
        Returns:
            Dictionary of all agent metrics
        """
        with self.lock:
            return {
                agent_name: metrics.to_dict()
                for agent_name, metrics in self.metrics.items()
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get overall system metrics.
        
        Returns:
            System-wide metrics
        """
        with self.lock:
            total_runs = sum(m.total_runs for m in self.metrics.values())
            total_success = sum(m.successful_runs for m in self.metrics.values())
            total_failures = sum(m.failed_runs for m in self.metrics.values())
            
            return {
                "system_uptime": str(datetime.utcnow() - self.system_start_time),
                "total_requests": total_runs,
                "total_successful": total_success,
                "total_failed": total_failures,
                "overall_success_rate": round((total_success / total_runs * 100), 2) if total_runs > 0 else 0.0,
                "agents_count": len(self.metrics),
                "agents": list(self.metrics.keys())
            }
    
    def reset_metrics(self, agent_name: Optional[str] = None):
        """
        Reset metrics.
        
        Args:
            agent_name: Specific agent to reset, or None to reset all
        """
        with self.lock:
            if agent_name:
                if agent_name in self.metrics:
                    self.metrics[agent_name] = AgentMetrics(agent_name=agent_name)
            else:
                self.metrics.clear()
                self.system_start_time = datetime.utcnow()


# Global metrics collector instance
_metrics_instance: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance
