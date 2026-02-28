"""Schema modules for the Medical AI application."""

from .extraction_schema import ExtractionOutput, LabValues
from .analysis_schema import (
    AnalysisOutput,
    RiskOutput,
    ExplanationOutput,
    DoctorSummaryOutput,
    AbnormalValue
)
from .response_schema import (
    MedicalReportResponse,
    AgentState,
    HealthCheckResponse
)

__all__ = [
    "ExtractionOutput",
    "LabValues",
    "AnalysisOutput",
    "RiskOutput",
    "ExplanationOutput",
    "DoctorSummaryOutput",
    "AbnormalValue",
    "MedicalReportResponse",
    "AgentState",
    "HealthCheckResponse"
]
