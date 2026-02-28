"""
FastAPI Main Application
Medical AI Multi-Agent System for Report Analysis
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .agents.orchestrator import MedicalReportOrchestrator
from .utils.pdf_reader import PDFProcessor
from .schemas.response_schema import MedicalReportResponse, HealthCheckResponse
from .monitoring import get_tracer, get_metrics_collector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Global orchestrator instance
orchestrator: Optional[MedicalReportOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global orchestrator
    logger.info("Starting Medical AI Application")
    logger.info(f"Using model: {settings.model_name}")
    
    # Initialize orchestrator
    orchestrator = MedicalReportOrchestrator()
    logger.info("Orchestrator initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Medical AI Application")


# Create FastAPI application
app = FastAPI(
    title="Medical AI Multi-Agent System",
    description="AI-powered medical report analysis using multi-agent architecture with LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint - health check."""
    return HealthCheckResponse(
        status="success",
        message="Medical AI Multi-Agent System is running",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    return HealthCheckResponse(
        status="healthy",
        message="System is operational",
        version="1.0.0"
    )


@app.get("/metrics")
async def get_metrics():
    """
    Get agent performance metrics.
    
    Returns metrics for all agents including:
    - Total runs
    - Success rate
    - Failure rate
    - Average execution time
    """
    logger.info("Metrics requested")
    metrics_collector = get_metrics_collector()
    
    return {
        "status": "success",
        "system_metrics": metrics_collector.get_system_metrics(),
        "agent_metrics": metrics_collector.get_all_metrics()
    }


@app.get("/trace/{trace_id}")
async def get_trace(trace_id: str):
    """
    Get detailed execution trace for a specific request.
    
    Args:
        trace_id: Unique trace identifier
        
    Returns:
        Complete execution flow with timing and status for each agent
    """
    logger.info(f"Trace requested: {trace_id}")
    tracer = get_tracer()
    
    trace_data = tracer.get_trace(trace_id)
    
    if not trace_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {trace_id} not found"
        )
    
    return {
        "status": "success",
        "trace": trace_data
    }


@app.get("/traces")
async def get_all_traces():
    """
    Get summary of all execution traces.
    
    Returns:
        List of trace summaries with basic information
    """
    logger.info("All traces requested")
    tracer = get_tracer()
    
    return {
        "status": "success",
        "traces": tracer.get_all_traces(),
        "count": len(tracer.get_all_traces())
    }


@app.post("/upload-report", response_model=MedicalReportResponse)
async def upload_report(file: UploadFile = File(...)):
    """
    Upload and analyze a medical report PDF.
    
    Args:
        file: PDF file containing medical lab report
        
    Returns:
        MedicalReportResponse with complete analysis
    """
    logger.info(f"Received file upload: {file.filename}")
    
    # Validate file type
    if not file.content_type == "application/pdf":
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted"
        )
    
    try:
        # Read PDF content
        pdf_content = await file.read()
        logger.info(f"Read {len(pdf_content)} bytes from PDF")
        
        # Extract text from PDF
        pdf_text = await PDFProcessor.process_pdf(pdf_content)
        logger.info(f"Extracted {len(pdf_text)} characters from PDF")
        
        if not pdf_text or len(pdf_text) < 50:
            raise ValueError("PDF appears to be empty or unreadable")
        
        # Process through multi-agent workflow
        if orchestrator is None:
            raise RuntimeError("Orchestrator not initialized")
        
        final_state = await orchestrator.process_report(pdf_text)
        
        # Determine response status
        if final_state.get("failed_agent"):
            if final_state.get("skipped_agents"):
                # Partial failure - some agents succeeded
                status_msg = "partial_failure"
                message = f"Processing partially failed at {final_state['failed_agent']}"
            else:
                # Complete failure
                status_msg = "failed"
                message = f"Processing failed at {final_state['failed_agent']}"
            
            logger.warning(f"{message}. Trace ID: {final_state.get('trace_id')}")
            
            return {
                "status": status_msg,
                "message": message,
                "trace_id": final_state.get("trace_id"),
                "failed_agent": final_state.get("failed_agent"),
                "skipped_agents": final_state.get("skipped_agents", []),
                "error": final_state.get("error"),
                "extraction": final_state.get("extraction"),
                "analysis": final_state.get("analysis"),
                "risk": final_state.get("risk"),
                "explanation": final_state.get("explanation"),
                "doctor_summary": final_state.get("doctor_summary")
            }
        
        # Success - all agents completed
        response = MedicalReportResponse(
            status="success",
            message="Medical report analyzed successfully",
            extraction=final_state.get("extraction"),
            analysis=final_state.get("analysis"),
            risk=final_state.get("risk"),
            explanation=final_state.get("explanation"),
            doctor_summary=final_state.get("doctor_summary")
        )
        
        # Add trace_id to response
        response_dict = response.model_dump()
        response_dict["trace_id"] = final_state.get("trace_id")
        
        logger.info(f"Report processing completed successfully. Trace ID: {final_state.get('trace_id')}")
        return response_dict
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the report: {str(e)}"
        )


@app.post("/analyze-text")
async def analyze_text(text: str):
    """
    Analyze medical report text directly (without PDF upload).
    
    Useful for testing or when text is already extracted.
    
    Args:
        text: Medical report text
        
    Returns:
        MedicalReportResponse with complete analysis
    """
    logger.info(f"Received text analysis request ({len(text)} characters)")
    
    if not text or len(text) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text is too short or empty"
        )
    
    try:
        # Process through multi-agent workflow
        if orchestrator is None:
            raise RuntimeError("Orchestrator not initialized")
        
        final_state = await orchestrator.process_report(text)
        
        # Determine response status
        if final_state.get("failed_agent"):
            if final_state.get("skipped_agents"):
                # Partial failure - some agents succeeded
                status_msg = "partial_failure"
                message = f"Processing partially failed at {final_state['failed_agent']}"
            else:
                # Complete failure
                status_msg = "failed"
                message = f"Processing failed at {final_state['failed_agent']}"
            
            logger.warning(f"{message}. Trace ID: {final_state.get('trace_id')}")
            
            return {
                "status": status_msg,
                "message": message,
                "trace_id": final_state.get("trace_id"),
                "failed_agent": final_state.get("failed_agent"),
                "skipped_agents": final_state.get("skipped_agents", []),
                "error": final_state.get("error"),
                "extraction": final_state.get("extraction"),
                "analysis": final_state.get("analysis"),
                "risk": final_state.get("risk"),
                "explanation": final_state.get("explanation"),
                "doctor_summary": final_state.get("doctor_summary")
            }
        
        # Success - all agents completed
        response = MedicalReportResponse(
            status="success",
            message="Medical report text analyzed successfully",
            extraction=final_state.get("extraction"),
            analysis=final_state.get("analysis"),
            risk=final_state.get("risk"),
            explanation=final_state.get("explanation"),
            doctor_summary=final_state.get("doctor_summary")
        )
        
        # Add trace_id to response
        response_dict = response.model_dump()
        response_dict["trace_id"] = final_state.get("trace_id")
        
        logger.info(f"Text analysis completed successfully. Trace ID: {final_state.get('trace_id')}")
        return response_dict
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the text: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
        log_level=settings.log_level.lower()
    )
