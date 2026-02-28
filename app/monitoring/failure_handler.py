"""
Failure handling module for agent errors and cascading failures.
Provides custom exceptions and failure management.
"""

from typing import Optional, List, Any, Dict


class AgentExecutionError(Exception):
    """
    Custom exception for agent execution failures.
    Provides detailed error context.
    """
    
    def __init__(
        self,
        agent_name: str,
        error_message: str,
        error_type: Optional[str] = None,
        input_data: Optional[Any] = None,
        trace_id: Optional[str] = None
    ):
        """
        Initialize agent execution error.
        
        Args:
            agent_name: Name of the failed agent
            error_message: Error description
            error_type: Type/category of error
            input_data: Input that caused the failure
            trace_id: Associated trace ID
        """
        self.agent_name = agent_name
        self.error_message = error_message
        self.error_type = error_type or "UnknownError"
        self.input_data = input_data
        self.trace_id = trace_id
        
        super().__init__(f"Agent '{agent_name}' failed: {error_message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "agent_name": self.agent_name,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "trace_id": self.trace_id
        }


class PartialFailureResponse:
    """
    Structured response for partial pipeline failures.
    Contains successful outputs and failure details.
    """
    
    def __init__(
        self,
        status: str,
        failed_agent: str,
        error_message: str,
        skipped_agents: List[str],
        successful_outputs: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ):
        """
        Initialize partial failure response.
        
        Args:
            status: Response status
            failed_agent: Name of the agent that failed
            error_message: Error description
            skipped_agents: List of agents that were skipped
            successful_outputs: Outputs from successful agents
            trace_id: Associated trace ID
        """
        self.status = status
        self.failed_agent = failed_agent
        self.error_message = error_message
        self.skipped_agents = skipped_agents
        self.successful_outputs = successful_outputs or {}
        self.trace_id = trace_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "status": self.status,
            "failed_agent": self.failed_agent,
            "error_message": self.error_message,
            "skipped_agents": self.skipped_agents,
            "successful_outputs": self.successful_outputs,
            "trace_id": self.trace_id
        }


class FailureHandler:
    """Handles agent failures and determines cascading behavior."""
    
    # Define agent dependencies (which agents depend on which)
    # IMPORTANT: Include ALL transitive dependencies to prevent agents
    # from running when upstream data is unavailable
    AGENT_DEPENDENCIES = {
        "extraction_agent": [],
        "analysis_agent": ["extraction_agent"],
        "risk_agent": ["extraction_agent", "analysis_agent"],  # Added extraction_agent (transitive)
        "explanation_agent": ["extraction_agent", "analysis_agent", "risk_agent"],  # Added extraction_agent
        "doctor_summary_agent": ["extraction_agent", "analysis_agent", "risk_agent"]
    }
    
    @staticmethod
    def get_dependent_agents(failed_agent: str) -> List[str]:
        """
        Get list of agents that depend on the failed agent.
        
        Args:
            failed_agent: Name of the failed agent
            
        Returns:
            List of agents that should be skipped
        """
        dependent_agents = []
        
        for agent, dependencies in FailureHandler.AGENT_DEPENDENCIES.items():
            if failed_agent in dependencies:
                dependent_agents.append(agent)
        
        return dependent_agents
    
    @staticmethod
    def should_continue(
        failed_agent: str,
        current_agent: str
    ) -> bool:
        """
        Determine if current agent should run given a failure.
        
        Args:
            failed_agent: Name of the failed agent
            current_agent: Name of the agent about to run
            
        Returns:
            True if agent can run, False if should be skipped
        """
        dependencies = FailureHandler.AGENT_DEPENDENCIES.get(current_agent, [])
        return failed_agent not in dependencies
    
    @staticmethod
    def create_partial_response(
        failed_agent: str,
        error: AgentExecutionError,
        successful_outputs: Dict[str, Any],
        trace_id: str
    ) -> PartialFailureResponse:
        """
        Create a partial failure response.
        
        Args:
            failed_agent: Name of the failed agent
            error: The exception that was raised
            successful_outputs: Outputs from agents that succeeded
            trace_id: Associated trace ID
            
        Returns:
            PartialFailureResponse object
        """
        skipped_agents = FailureHandler.get_dependent_agents(failed_agent)
        
        return PartialFailureResponse(
            status="partial_failure",
            failed_agent=failed_agent,
            error_message=error.error_message,
            skipped_agents=skipped_agents,
            successful_outputs=successful_outputs,
            trace_id=trace_id
        )
    
    @staticmethod
    def handle_critical_failure(
        agent_name: str,
        error: Exception,
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle a critical failure that prevents all further execution.
        
        Args:
            agent_name: Name of the failed agent
            error: The exception that was raised
            trace_id: Associated trace ID
            
        Returns:
            Error response dictionary
        """
        return {
            "status": "failed",
            "failed_agent": agent_name,
            "error_message": str(error),
            "error_type": type(error).__name__,
            "trace_id": trace_id,
            "note": "Critical failure prevented workflow completion"
        }


def wrap_agent_execution(agent_name: str):
    """
    Decorator to wrap agent execution with error handling.
    
    Args:
        agent_name: Name of the agent
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                trace_id = kwargs.get('trace_id', 'unknown')
                raise AgentExecutionError(
                    agent_name=agent_name,
                    error_message=str(e),
                    error_type=type(e).__name__,
                    trace_id=trace_id
                )
        return wrapper
    return decorator
