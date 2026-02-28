"""
LangGraph Orchestrator: Coordinates multi-agent workflow with monitoring and failure handling.
"""

import logging
from typing import TypedDict, Annotated, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

from .extraction_agent import ExtractionAgent
from .analysis_agent import AnalysisAgent
from .risk_agent import RiskAgent
from .explanation_agent import ExplanationAgent
from .doctor_summary_agent import DoctorSummaryAgent

from ..schemas.extraction_schema import ExtractionOutput
from ..schemas.analysis_schema import (
    AnalysisOutput,
    RiskOutput,
    ExplanationOutput,
    DoctorSummaryOutput
)
from ..monitoring import (
    get_logger,
    get_tracer,
    get_metrics_collector,
    AgentExecutionError,
    FailureHandler
)

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State object that flows through the agent graph."""
    pdf_text: str
    trace_id: str
    extraction: ExtractionOutput | None
    analysis: AnalysisOutput | None
    risk: RiskOutput | None
    explanation: ExplanationOutput | None
    doctor_summary: DoctorSummaryOutput | None
    error: str | None
    failed_agent: str | None
    skipped_agents: list | None


class MedicalReportOrchestrator:
    """
    Orchestrates the multi-agent workflow using LangGraph with monitoring and failure handling.
    
    The workflow follows this sequence:
    1. Extraction Agent: Extract lab values from PDF
    2. Analysis Agent: Analyze values for abnormalities
    3. Risk Agent: Assess severity and urgency
    4. Explanation Agent: Generate patient-friendly explanation
    5. Doctor Summary Agent: Generate clinical summary
    
    Features:
    - Request tracing
    - Failure detection and cascading prevention
    - Metrics collection
    - Structured logging
    """
    
    def __init__(self):
        """Initialize the orchestrator and all agents."""
        logger.info("Initializing Medical Report Orchestrator with Monitoring")
        
        # Initialize all agents
        self.extraction_agent = ExtractionAgent()
        self.analysis_agent = AnalysisAgent()
        self.risk_agent = RiskAgent()
        self.explanation_agent = ExplanationAgent()
        self.doctor_summary_agent = DoctorSummaryAgent()
        
        # Initialize monitoring
        self.monitor_logger = get_logger()
        self.tracer = get_tracer()
        self.metrics = get_metrics_collector()
        self.failure_handler = FailureHandler()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Define agent nodes
        workflow.add_node("extract", self._extraction_node)
        workflow.add_node("analyze", self._analysis_node)
        workflow.add_node("assess_risk", self._risk_node)
        workflow.add_node("explain", self._explanation_node)
        workflow.add_node("doctor_summary", self._doctor_summary_node)
        
        # Define the workflow edges (sequence)
        workflow.set_entry_point("extract")
        workflow.add_edge("extract", "analyze")
        workflow.add_edge("analyze", "assess_risk")
        workflow.add_edge("assess_risk", "explain")
        workflow.add_edge("explain", "doctor_summary")
        workflow.add_edge("doctor_summary", END)
        
        # Compile the workflow
        return workflow.compile()
    
    async def _extraction_node(self, state: AgentState) -> AgentState:
        """Execute extraction agent with error handling."""
        logger.info("Executing extraction node")
        
        # Check if previous agent failed
        if state.get("failed_agent"):
            return state
        
        try:
            extraction_output = await self.extraction_agent.run(
                state["pdf_text"],
                state["trace_id"]
            )
            state["extraction"] = extraction_output
        except AgentExecutionError as e:
            logger.error(f"Extraction node error: {e}")
            state["error"] = e.error_message
            state["failed_agent"] = e.agent_name
        except Exception as e:
            logger.error(f"Unexpected extraction node error: {e}")
            state["error"] = str(e)
            state["failed_agent"] = "extraction_agent"
        
        return state
    
    async def _analysis_node(self, state: AgentState) -> AgentState:
        """Execute analysis agent with error handling."""
        logger.info("Executing analysis node")
        
        # Check if should skip due to previous failure
        if state.get("failed_agent"):
            if not self.failure_handler.should_continue(state["failed_agent"], "analysis_agent"):
                self.tracer.skip_agent(state["trace_id"], "analysis_agent", "Dependent agent failed")
                self.monitor_logger.log_agent_skipped("analysis_agent", state["trace_id"], "Dependent agent failed")
                if state.get("skipped_agents") is None:
                    state["skipped_agents"] = []
                state["skipped_agents"].append("analysis_agent")
                return state
        
        try:
            if state["extraction"]:
                analysis_output = await self.analysis_agent.run(
                    state["extraction"],
                    state["trace_id"]
                )
                state["analysis"] = analysis_output
            else:
                raise ValueError("No extraction data available")
        except AgentExecutionError as e:
            logger.error(f"Analysis node error: {e}")
            state["error"] = e.error_message
            state["failed_agent"] = e.agent_name
        except Exception as e:
            logger.error(f"Unexpected analysis node error: {e}")
            state["error"] = str(e)
            state["failed_agent"] = "analysis_agent"
        
        return state
    
    async def _risk_node(self, state: AgentState) -> AgentState:
        """Execute risk assessment agent with error handling."""
        logger.info("Executing risk assessment node")
        
        # Check if should skip due to previous failure
        if state.get("failed_agent"):
            if not self.failure_handler.should_continue(state["failed_agent"], "risk_agent"):
                self.tracer.skip_agent(state["trace_id"], "risk_agent", "Dependent agent failed")
                self.monitor_logger.log_agent_skipped("risk_agent", state["trace_id"], "Dependent agent failed")
                if state.get("skipped_agents") is None:
                    state["skipped_agents"] = []
                state["skipped_agents"].append("risk_agent")
                return state
        
        try:
            if state["analysis"]:
                risk_output = await self.risk_agent.run(
                    state["analysis"],
                    state["trace_id"]
                )
                state["risk"] = risk_output
            else:
                raise ValueError("No analysis data available")
        except AgentExecutionError as e:
            logger.error(f"Risk node error: {e}")
            state["error"] = e.error_message
            state["failed_agent"] = e.agent_name
        except Exception as e:
            logger.error(f"Unexpected risk node error: {e}")
            state["error"] = str(e)
            state["failed_agent"] = "risk_agent"
        
        return state
    
    async def _explanation_node(self, state: AgentState) -> AgentState:
        """Execute explanation agent with error handling."""
        logger.info("Executing explanation node")
        
        # Check if should skip due to previous failure
        if state.get("failed_agent"):
            if not self.failure_handler.should_continue(state["failed_agent"], "explanation_agent"):
                self.tracer.skip_agent(state["trace_id"], "explanation_agent", "Dependent agent failed")
                self.monitor_logger.log_agent_skipped("explanation_agent", state["trace_id"], "Dependent agent failed")
                if state.get("skipped_agents") is None:
                    state["skipped_agents"] = []
                state["skipped_agents"].append("explanation_agent")
                return state
        
        try:
            if state["analysis"] and state["risk"]:
                explanation_output = await self.explanation_agent.run(
                    state["analysis"], 
                    state["risk"],
                    state["trace_id"]
                )
                state["explanation"] = explanation_output
            else:
                raise ValueError("Missing analysis or risk data")
        except AgentExecutionError as e:
            logger.error(f"Explanation node error: {e}")
            state["error"] = e.error_message
            state["failed_agent"] = e.agent_name
        except Exception as e:
            logger.error(f"Unexpected explanation node error: {e}")
            state["error"] = str(e)
            state["failed_agent"] = "explanation_agent"
        
        return state
    
    async def _doctor_summary_node(self, state: AgentState) -> AgentState:
        """Execute doctor summary agent with error handling."""
        logger.info("Executing doctor summary node")
        
        # Check if should skip due to previous failure
        if state.get("failed_agent"):
            if not self.failure_handler.should_continue(state["failed_agent"], "doctor_summary_agent"):
                self.tracer.skip_agent(state["trace_id"], "doctor_summary_agent", "Dependent agent failed")
                self.monitor_logger.log_agent_skipped("doctor_summary_agent", state["trace_id"], "Dependent agent failed")
                if state.get("skipped_agents") is None:
                    state["skipped_agents"] = []
                state["skipped_agents"].append("doctor_summary_agent")
                return state
        
        try:
            if state["extraction"] and state["analysis"] and state["risk"]:
                doctor_summary_output = await self.doctor_summary_agent.run(
                    state["extraction"],
                    state["analysis"],
                    state["risk"],
                    state["trace_id"]
                )
                state["doctor_summary"] = doctor_summary_output
            else:
                raise ValueError("Missing required data for doctor summary")
        except AgentExecutionError as e:
            logger.error(f"Doctor summary node error: {e}")
            state["error"] = e.error_message
            state["failed_agent"] = e.agent_name
        except Exception as e:
            logger.error(f"Unexpected doctor summary node error: {e}")
            state["error"] = str(e)
            state["failed_agent"] = "doctor_summary_agent"
        
        return state
    
    async def process_report(self, pdf_text: str) -> AgentState:
        """
        Process a medical report through the multi-agent workflow with monitoring.
        
        Args:
            pdf_text: Extracted text from medical report PDF
            
        Returns:
            Final state with all agent outputs and trace information
        """
        # Generate trace ID
        trace_id = self.tracer.create_trace()
        logger.info(f"Starting medical report processing workflow - Trace ID: {trace_id}")
        
        # Initialize state
        initial_state: AgentState = {
            "pdf_text": pdf_text,
            "trace_id": trace_id,
            "extraction": None,
            "analysis": None,
            "risk": None,
            "explanation": None,
            "doctor_summary": None,
            "error": None,
            "failed_agent": None,
            "skipped_agents": None
        }
        
        try:
            # Execute the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Determine final status
            if final_state.get("failed_agent"):
                if final_state.get("skipped_agents"):
                    status = "PARTIAL_FAILURE"
                else:
                    status = "FAILED"
            else:
                status = "COMPLETED"
            
            # Complete the trace
            self.tracer.complete_trace(trace_id, status)
            
            logger.info(f"Workflow completed with status: {status}")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            self.tracer.complete_trace(trace_id, "FAILED")
            initial_state["error"] = f"Workflow failed: {str(e)}"
            initial_state["failed_agent"] = "orchestrator"
            return initial_state
