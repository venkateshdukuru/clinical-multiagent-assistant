"""
Request tracing module for tracking agent execution flow.
Assigns unique trace IDs and tracks execution timeline.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from threading import Lock
from dataclasses import dataclass, asdict, field


@dataclass
class AgentExecution:
    """Details of a single agent execution."""
    agent_name: str
    status: str  # STARTED, SUCCESS, FAILED, SKIPPED
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None


@dataclass
class ExecutionTrace:
    """Complete execution trace for a request."""
    trace_id: str
    start_time: float
    end_time: Optional[float] = None
    total_duration_ms: Optional[float] = None
    status: str = "IN_PROGRESS"  # IN_PROGRESS, COMPLETED, PARTIAL_FAILURE, FAILED
    agents: List[AgentExecution] = field(default_factory=list)
    failed_agent: Optional[str] = None
    skipped_agents: List[str] = field(default_factory=list)


class AgentTracer:
    """
    Tracer for tracking agent execution flow across requests.
    Thread-safe implementation for concurrent requests.
    """
    
    def __init__(self, max_traces: int = 1000):
        """
        Initialize the tracer.
        
        Args:
            max_traces: Maximum number of traces to keep in memory
        """
        self.traces: Dict[str, ExecutionTrace] = {}
        self.max_traces = max_traces
        self.lock = Lock()
    
    def create_trace(self) -> str:
        """
        Create a new trace for a request.
        
        Returns:
            Unique trace ID
        """
        trace_id = str(uuid.uuid4())
        
        with self.lock:
            # Clean old traces if needed
            if len(self.traces) >= self.max_traces:
                # Remove oldest trace
                oldest_id = min(self.traces.keys(), key=lambda k: self.traces[k].start_time)
                del self.traces[oldest_id]
            
            # Create new trace
            self.traces[trace_id] = ExecutionTrace(
                trace_id=trace_id,
                start_time=time.time()
            )
        
        return trace_id
    
    def start_agent(
        self,
        trace_id: str,
        agent_name: str,
        input_summary: Optional[str] = None
    ):
        """
        Mark agent execution start.
        
        Args:
            trace_id: Trace identifier
            agent_name: Name of the agent
            input_summary: Brief summary of input
        """
        with self.lock:
            if trace_id not in self.traces:
                return
            
            execution = AgentExecution(
                agent_name=agent_name,
                status="STARTED",
                start_time=time.time(),
                input_summary=input_summary
            )
            
            self.traces[trace_id].agents.append(execution)
    
    def end_agent(
        self,
        trace_id: str,
        agent_name: str,
        success: bool,
        output_summary: Optional[str] = None,
        error: Optional[str] = None,
        error_type: Optional[str] = None
    ):
        """
        Mark agent execution end.
        
        Args:
            trace_id: Trace identifier
            agent_name: Name of the agent
            success: Whether execution was successful
            output_summary: Brief summary of output
            error: Error message if failed
            error_type: Type of error
        """
        with self.lock:
            if trace_id not in self.traces:
                return
            
            trace = self.traces[trace_id]
            
            # Find the agent execution
            for execution in reversed(trace.agents):
                if execution.agent_name == agent_name and execution.status == "STARTED":
                    execution.end_time = time.time()
                    execution.duration_ms = (execution.end_time - execution.start_time) * 1000
                    execution.status = "SUCCESS" if success else "FAILED"
                    execution.output_summary = output_summary
                    execution.error = error
                    execution.error_type = error_type
                    
                    if not success:
                        trace.failed_agent = agent_name
                    
                    break
    
    def skip_agent(
        self,
        trace_id: str,
        agent_name: str,
        reason: str
    ):
        """
        Mark agent as skipped.
        
        Args:
            trace_id: Trace identifier
            agent_name: Name of the agent
            reason: Reason for skipping
        """
        with self.lock:
            if trace_id not in self.traces:
                return
            
            trace = self.traces[trace_id]
            
            execution = AgentExecution(
                agent_name=agent_name,
                status="SKIPPED",
                error=reason
            )
            
            trace.agents.append(execution)
            trace.skipped_agents.append(agent_name)
    
    def complete_trace(
        self,
        trace_id: str,
        status: str = "COMPLETED"
    ):
        """
        Mark trace as completed.
        
        Args:
            trace_id: Trace identifier
            status: Final status (COMPLETED, PARTIAL_FAILURE, FAILED)
        """
        with self.lock:
            if trace_id not in self.traces:
                return
            
            trace = self.traces[trace_id]
            trace.end_time = time.time()
            trace.total_duration_ms = (trace.end_time - trace.start_time) * 1000
            trace.status = status
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace details.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            Trace details as dictionary
        """
        with self.lock:
            if trace_id not in self.traces:
                return None
            
            trace = self.traces[trace_id]
            return {
                "trace_id": trace.trace_id,
                "start_time": datetime.fromtimestamp(trace.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(trace.end_time).isoformat() if trace.end_time else None,
                "total_duration_ms": round(trace.total_duration_ms, 2) if trace.total_duration_ms else None,
                "status": trace.status,
                "failed_agent": trace.failed_agent,
                "skipped_agents": trace.skipped_agents,
                "agents": [
                    {
                        "name": agent.agent_name,
                        "status": agent.status,
                        "start_time": datetime.fromtimestamp(agent.start_time).isoformat() if agent.start_time else None,
                        "end_time": datetime.fromtimestamp(agent.end_time).isoformat() if agent.end_time else None,
                        "duration_ms": round(agent.duration_ms, 2) if agent.duration_ms else None,
                        "error": agent.error,
                        "error_type": agent.error_type,
                        "input_summary": agent.input_summary,
                        "output_summary": agent.output_summary
                    }
                    for agent in trace.agents
                ]
            }
    
    def get_all_traces(self) -> List[Dict[str, Any]]:
        """
        Get all traces (summary view).
        
        Returns:
            List of trace summaries
        """
        with self.lock:
            return [
                {
                    "trace_id": trace.trace_id,
                    "start_time": datetime.fromtimestamp(trace.start_time).isoformat(),
                    "status": trace.status,
                    "total_duration_ms": round(trace.total_duration_ms, 2) if trace.total_duration_ms else None,
                    "agent_count": len(trace.agents),
                    "failed_agent": trace.failed_agent
                }
                for trace in self.traces.values()
            ]


# Global tracer instance
_tracer_instance: Optional[AgentTracer] = None


def get_tracer() -> AgentTracer:
    """Get or create global tracer instance."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = AgentTracer()
    return _tracer_instance
