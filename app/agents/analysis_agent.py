"""
Analysis Agent: Analyzes lab values and identifies abnormalities.
"""

import logging
import json
import time
from openai import AsyncOpenAI
from ..schemas.extraction_schema import ExtractionOutput
from ..schemas.analysis_schema import AnalysisOutput
from ..config import get_settings
from ..monitoring import (
    get_logger,
    get_tracer,
    get_metrics_collector,
    AgentExecutionError
)

logger = logging.getLogger(__name__)
settings = get_settings()


class AnalysisAgent:
    """Agent responsible for analyzing lab values and identifying abnormalities."""
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name
        self.agent_name = "analysis_agent"
        self.monitor_logger = get_logger()
        self.tracer = get_tracer()
        self.metrics = get_metrics_collector()
        
    async def run(self, extraction_data: ExtractionOutput, trace_id: str) -> AnalysisOutput:
        """
        Analyze extracted lab values.
        
        Args:
            extraction_data: Output from extraction agent
            trace_id: Unique trace identifier for request tracking
            
        Returns:
            AnalysisOutput with abnormal values and possible conditions
        """
        start_time = time.time()
        
        # Log and trace start
        lab_count = len(extraction_data.lab_values.model_dump(exclude_none=True))
        input_summary = f"Analyzing {lab_count} lab values"
        self.monitor_logger.log_agent_start(self.agent_name, trace_id, input_summary)
        self.tracer.start_agent(trace_id, self.agent_name, input_summary)
        
        logger.info("Starting analysis agent")
        
        try:
            system_prompt = """You are an expert medical analyst specializing in laboratory test interpretation.

Your task is to:
1. Identify abnormal lab values based on standard medical reference ranges
2. Determine if values are High or Low
3. Suggest possible medical conditions associated with these abnormalities
4. Provide professional analysis notes

Standard reference ranges:
- Hemoglobin: 12.0-16.0 g/dL (women), 13.5-17.5 g/dL (men)
- TSH: 0.4-4.0 mIU/L
- Cholesterol: <200 mg/dL (desirable), 200-239 (borderline high), ≥240 (high)
- WBC: 4.0-11.0 × 10^3/μL
- RBC: 4.0-5.5 × 10^6/μL (women), 4.5-6.0 (men)
- Platelets: 150-400 × 10^3/μL
- Glucose (fasting): 70-100 mg/dL
- Creatinine: 0.6-1.2 mg/dL
- ALT: 7-56 U/L
- AST: 10-40 U/L

Be thorough but conservative in your analysis."""

            lab_values_dict = extraction_data.lab_values.model_dump(exclude_none=True)
            
            user_prompt = f"""Analyze these lab values:

{json.dumps(lab_values_dict, indent=2)}

Identify abnormal values and provide analysis in this JSON format:
{{
    "abnormal_values": [
        {{
            "parameter": "name",
            "value": 123.4,
            "normal_range": "range",
            "deviation": "High|Low"
        }}
    ],
    "possible_conditions": ["condition1", "condition2"],
    "analysis_notes": "detailed analysis"
}}

If all values are normal, return empty arrays for abnormal_values and possible_conditions."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Analysis completed. Found {len(result.get('abnormal_values', []))} abnormal values")
            
            analysis_output = AnalysisOutput(**result)
            
            # Log success
            duration_ms = (time.time() - start_time) * 1000
            output_summary = f"Found {len(result.get('abnormal_values', []))} abnormal values"
            self.monitor_logger.log_agent_success(self.agent_name, trace_id, duration_ms, output_summary)
            self.tracer.end_agent(trace_id, self.agent_name, success=True, output_summary=output_summary)
            self.metrics.record_execution(self.agent_name, "SUCCESS", duration_ms)
            
            return analysis_output
            
        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f"Analysis agent error: {e}")
            self.monitor_logger.log_agent_failure(self.agent_name, trace_id, duration_ms, error_msg, error_type)
            self.tracer.end_agent(trace_id, self.agent_name, success=False, error=error_msg, error_type=error_type)
            self.metrics.record_execution(self.agent_name, "FAILED")
            
            raise AgentExecutionError(
                agent_name=self.agent_name,
                error_message=error_msg,
                error_type=error_type,
                trace_id=trace_id
            )
