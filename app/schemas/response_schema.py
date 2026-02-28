"""
Pydantic schemas for API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from .extraction_schema import ExtractionOutput
from .analysis_schema import (
    AnalysisOutput,
    RiskOutput,
    ExplanationOutput,
    DoctorSummaryOutput
)


class AgentState(BaseModel):
    """State object that flows through the LangGraph agents."""
    
    # Input
    pdf_text: Optional[str] = None
    
    # Agent outputs
    extraction: Optional[ExtractionOutput] = None
    analysis: Optional[AnalysisOutput] = None
    risk: Optional[RiskOutput] = None
    explanation: Optional[ExplanationOutput] = None
    doctor_summary: Optional[DoctorSummaryOutput] = None
    
    # Metadata
    status: str = "pending"
    error: Optional[str] = None


class MedicalReportResponse(BaseModel):
    """Final API response structure."""
    
    status: str = Field(..., description="Processing status: success or error")
    message: str = Field(..., description="Status message")
    
    # Agent outputs
    extraction: Optional[ExtractionOutput] = None
    analysis: Optional[AnalysisOutput] = None
    risk: Optional[RiskOutput] = None
    explanation: Optional[ExplanationOutput] = None
    doctor_summary: Optional[DoctorSummaryOutput] = None
    
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Medical report analyzed successfully",
                "extraction": {
                    "lab_values": {"hemoglobin": 13.5, "tsh": 2.5},
                    "raw_text_snippet": "...",
                    "extraction_confidence": "High"
                },
                "analysis": {
                    "abnormal_values": [],
                    "possible_conditions": [],
                    "analysis_notes": "All values within normal range"
                },
                "risk": {
                    "severity_level": "Low",
                    "urgency": "Routine",
                    "risk_factors": []
                },
                "explanation": {
                    "patient_friendly_explanation": "Your results look good!",
                    "key_takeaways": ["All values normal"]
                },
                "doctor_summary": {
                    "clinical_summary": "Normal lab results",
                    "suggested_tests": [],
                    "lifestyle_recommendations": ["Maintain healthy lifestyle"],
                    "follow_up_timeline": "Annual checkup"
                }
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str
    message: str
    version: str = "1.0.0"
