"""
Pydantic schemas for extraction agent output.
"""

from pydantic import BaseModel, Field
from typing import Optional


class LabValues(BaseModel):
    """Extracted lab values from medical report."""
    
    hemoglobin: Optional[float] = Field(None, description="Hemoglobin level in g/dL")
    tsh: Optional[float] = Field(None, description="Thyroid Stimulating Hormone in mIU/L")
    cholesterol: Optional[float] = Field(None, description="Total cholesterol in mg/dL")
    wbc: Optional[float] = Field(None, description="White Blood Cell count in 10^3/μL")
    rbc: Optional[float] = Field(None, description="Red Blood Cell count in 10^6/μL")
    platelets: Optional[float] = Field(None, description="Platelet count in 10^3/μL")
    glucose: Optional[float] = Field(None, description="Blood glucose in mg/dL")
    creatinine: Optional[float] = Field(None, description="Creatinine in mg/dL")
    alt: Optional[float] = Field(None, description="Alanine aminotransferase in U/L")
    ast: Optional[float] = Field(None, description="Aspartate aminotransferase in U/L")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hemoglobin": 13.5,
                "tsh": 2.5,
                "cholesterol": 180.0,
                "wbc": 7.5
            }
        }


class ExtractionOutput(BaseModel):
    """Complete extraction agent output."""
    
    lab_values: LabValues = Field(..., description="Extracted laboratory values")
    raw_text_snippet: str = Field(..., description="Relevant snippet from the report")
    extraction_confidence: str = Field(..., description="Confidence level: High, Medium, Low")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lab_values": {
                    "hemoglobin": 13.5,
                    "tsh": 2.5,
                    "cholesterol": 180.0,
                    "wbc": 7.5
                },
                "raw_text_snippet": "Hemoglobin: 13.5 g/dL, TSH: 2.5 mIU/L",
                "extraction_confidence": "High"
            }
        }
