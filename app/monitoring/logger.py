"""
Centralized logging module for agent monitoring.
Provides structured JSON logging for all agent executions.
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from pythonjsonlogger import jsonlogger


class AgentLogger:
    """Centralized logger for agent execution tracking."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the agent logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("medical_ai.agents")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()  # Clear existing handlers
        
        # Console handler with JSON formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(name)s %(levelname)s %(message)s %(agent_name)s %(trace_id)s %(duration_ms)s %(status)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler with JSON formatter
        file_handler = logging.FileHandler(self.log_dir / "agents.log")
        file_handler.setLevel(logging.INFO)
        file_formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(name)s %(levelname)s %(message)s %(agent_name)s %(trace_id)s %(duration_ms)s %(status)s %(error)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def log_agent_start(
        self, 
        agent_name: str, 
        trace_id: str,
        input_summary: Optional[str] = None
    ):
        """
        Log agent execution start.
        
        Args:
            agent_name: Name of the agent
            trace_id: Unique trace identifier
            input_summary: Brief summary of input data
        """
        self.logger.info(
            f"Agent {agent_name} started",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_name": agent_name,
                "trace_id": trace_id,
                "status": "STARTED",
                "input_summary": input_summary or "N/A"
            }
        )
    
    def log_agent_success(
        self,
        agent_name: str,
        trace_id: str,
        duration_ms: float,
        output_summary: Optional[str] = None
    ):
        """
        Log successful agent execution.
        
        Args:
            agent_name: Name of the agent
            trace_id: Unique trace identifier
            duration_ms: Execution duration in milliseconds
            output_summary: Brief summary of output data
        """
        self.logger.info(
            f"Agent {agent_name} completed successfully",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_name": agent_name,
                "trace_id": trace_id,
                "duration_ms": round(duration_ms, 2),
                "status": "SUCCESS",
                "output_summary": output_summary or "N/A"
            }
        )
    
    def log_agent_failure(
        self,
        agent_name: str,
        trace_id: str,
        duration_ms: float,
        error_message: str,
        error_type: Optional[str] = None
    ):
        """
        Log failed agent execution.
        
        Args:
            agent_name: Name of the agent
            trace_id: Unique trace identifier
            duration_ms: Execution duration in milliseconds
            error_message: Error description
            error_type: Type of error
        """
        self.logger.error(
            f"Agent {agent_name} failed",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_name": agent_name,
                "trace_id": trace_id,
                "duration_ms": round(duration_ms, 2),
                "status": "FAILED",
                "error": error_message,
                "error_type": error_type or "Unknown"
            }
        )
    
    def log_agent_skipped(
        self,
        agent_name: str,
        trace_id: str,
        reason: str
    ):
        """
        Log skipped agent execution.
        
        Args:
            agent_name: Name of the agent
            trace_id: Unique trace identifier
            reason: Reason for skipping
        """
        self.logger.warning(
            f"Agent {agent_name} skipped",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "agent_name": agent_name,
                "trace_id": trace_id,
                "status": "SKIPPED",
                "reason": reason
            }
        )
    
    def log_custom(
        self,
        level: str,
        message: str,
        **kwargs
    ):
        """
        Log custom message with additional context.
        
        Args:
            level: Log level (info, warning, error)
            message: Log message
            **kwargs: Additional context
        """
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(
            message,
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                **kwargs
            }
        )


# Global logger instance
_logger_instance: Optional[AgentLogger] = None


def get_logger() -> AgentLogger:
    """Get or create global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AgentLogger()
    return _logger_instance
