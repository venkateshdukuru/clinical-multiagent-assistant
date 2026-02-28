"""
Extraction Agent: Extracts lab values from medical report text.
"""

import logging
import json
import time
from typing import Dict, Any
from openai import AsyncOpenAI
from ..schemas.extraction_schema import ExtractionOutput, LabValues
from ..config import get_settings
from ..monitoring import (
    get_logger,
    get_tracer,
    get_metrics_collector,
    AgentExecutionError
)

logger = logging.getLogger(__name__)
settings = get_settings()


class ExtractionAgent:
    """Agent responsible for extracting lab values from medical reports."""
    
    def __init__(self):
        """Initialize the extraction agent."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name
        self.agent_name = "extraction_agent"
        self.monitor_logger = get_logger()
        self.tracer = get_tracer()
        self.metrics = get_metrics_collector()
        
    async def run(self, pdf_text: str, trace_id: str) -> ExtractionOutput:
        """
        Extract lab values from PDF text.
        
        Args:
            pdf_text: Raw text extracted from medical report PDF
            trace_id: Unique trace identifier for request tracking
            
        Returns:
            ExtractionOutput with structured lab values
        """
        start_time = time.time()
        
        # Log and trace start
        input_summary = f"Text length: {len(pdf_text)} characters"
        self.monitor_logger.log_agent_start(self.agent_name, trace_id, input_summary)
        self.tracer.start_agent(trace_id, self.agent_name, input_summary)
        
        logger.info("Starting extraction agent")
        
        try:
            system_prompt = """You are a medical data extraction specialist.
Your task is to extract laboratory test values from medical reports.

Extract the following lab values if present:
- Hemoglobin (g/dL)
- TSH - Thyroid Stimulating Hormone (mIU/L)
- Cholesterol (mg/dL)
- WBC - White Blood Cell count (10^3/μL)
- RBC - Red Blood Cell count (10^6/μL)
- Platelets (10^3/μL)
- Glucose (mg/dL)
- Creatinine (mg/dL)
- ALT - Alanine aminotransferase (U/L)
- AST - Aspartate aminotransferase (U/L)

Return only values that are explicitly mentioned in the report.
Use null for values not found.

Also provide:
1. A snippet of the relevant text containing the values
2. Your confidence level (High, Medium, Low) based on how clearly the values are stated
"""

            user_prompt = f"""Extract lab values from this medical report:

{pdf_text}

Provide the response in this JSON format:
{{
    "lab_values": {{
        "hemoglobin": <float or null>,
        "tsh": <float or null>,
        "cholesterol": <float or null>,
        "wbc": <float or null>,
        "rbc": <float or null>,
        "platelets": <float or null>,
        "glucose": <float or null>,
        "creatinine": <float or null>,
        "alt": <float or null>,
        "ast": <float or null>
    }},
    "raw_text_snippet": "<relevant portion of text>",
    "extraction_confidence": "High|Medium|Low"
}}"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Extraction completed with confidence: {result.get('extraction_confidence')}")
            
            # Parse into Pydantic model
            extraction_output = ExtractionOutput(**result)
            
            # Log success
            duration_ms = (time.time() - start_time) * 1000
            output_summary = f"Confidence: {result.get('extraction_confidence')}"
            self.monitor_logger.log_agent_success(self.agent_name, trace_id, duration_ms, output_summary)
            self.tracer.end_agent(trace_id, self.agent_name, success=True, output_summary=output_summary)
            self.metrics.record_execution(self.agent_name, "SUCCESS", duration_ms)
            
            return extraction_output
            
        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f"Extraction agent error: {e}")
            self.monitor_logger.log_agent_failure(self.agent_name, trace_id, duration_ms, error_msg, error_type)
            self.tracer.end_agent(trace_id, self.agent_name, success=False, error=error_msg, error_type=error_type)
            self.metrics.record_execution(self.agent_name, "FAILED")
            
            # Raise custom exception
            raise AgentExecutionError(
                agent_name=self.agent_name,
                error_message=error_msg,
                error_type=error_type,
                trace_id=trace_id
            )
