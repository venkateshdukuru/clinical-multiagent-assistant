"""
Pydantic schemas for analysis agent output.
"""

from pydantic import BaseModel, Field
from typing import List


class AbnormalValue(BaseModel):
    """Details about an abnormal lab value."""
    
    parameter: str = Field(..., description="Name of the lab parameter")
    value: float = Field(..., description="Measured value")
    normal_range: str = Field(..., description="Normal reference range")
    deviation: str = Field(..., description="How it deviates: High or Low")


class AnalysisOutput(BaseModel):
    """Analysis agent output."""
    
    abnormal_values: List[AbnormalValue] = Field(
        default_factory=list, 
        description="List of abnormal lab values"
    )
    possible_conditions: List[str] = Field(
        default_factory=list,
        description="Possible medical conditions based on abnormal values"
    )
    analysis_notes: str = Field(..., description="Additional analysis notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "abnormal_values": [
                    {
                        "parameter": "TSH",
                        "value": 8.5,
                        "normal_range": "0.4-4.0 mIU/L",
                        "deviation": "High"
                    }
                ],
                "possible_conditions": ["Hypothyroidism", "Thyroid dysfunction"],
                "analysis_notes": "Elevated TSH suggests underactive thyroid"
            }
        }


class RiskOutput(BaseModel):
    """Risk assessment agent output."""
    
    severity_level: str = Field(
        ..., 
        description="Risk severity: Low, Moderate, High, Critical"
    )
    urgency: str = Field(
        ..., 
        description="Action urgency: Routine, Doctor Visit, Immediate Attention"
    )
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Identified risk factors"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "severity_level": "Moderate",
                "urgency": "Doctor Visit",
                "risk_factors": ["Thyroid dysfunction", "Potential metabolic issues"]
            }
        }


class ExplanationOutput(BaseModel):
    """Patient-friendly explanation agent output."""
    
    patient_friendly_explanation: str = Field(
        ..., 
        description="Simple explanation for patients"
    )
    key_takeaways: List[str] = Field(
        default_factory=list,
        description="Key points the patient should understand"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_friendly_explanation": "Your TSH level is higher than normal...",
                "key_takeaways": [
                    "Your thyroid may be underactive",
                    "This can cause fatigue and weight gain",
                    "See your doctor for follow-up"
                ]
            }
        }


class DoctorSummaryOutput(BaseModel):
    """Doctor summary agent output."""
    
    clinical_summary: str = Field(..., description="Professional clinical summary")
    suggested_tests: List[str] = Field(
        default_factory=list,
        description="Recommended follow-up tests"
    )
    lifestyle_recommendations: List[str] = Field(
        default_factory=list,
        description="Lifestyle and dietary recommendations"
    )
    follow_up_timeline: str = Field(..., description="Suggested follow-up timeline")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clinical_summary": "Patient presents with elevated TSH...",
                "suggested_tests": ["Free T4", "Thyroid antibodies"],
                "lifestyle_recommendations": [
                    "Increase iodine-rich foods",
                    "Monitor energy levels"
                ],
                "follow_up_timeline": "2-4 weeks"
            }
        }
