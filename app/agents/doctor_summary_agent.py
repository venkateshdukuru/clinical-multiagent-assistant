"""
Doctor Summary Agent: Generates clinical summary for healthcare providers.
"""

import logging
import json
import time
from openai import AsyncOpenAI
from ..schemas.extraction_schema import ExtractionOutput
from ..schemas.analysis_schema import (
    AnalysisOutput, 
    RiskOutput, 
    ExplanationOutput,
    DoctorSummaryOutput
)
from ..config import get_settings
from ..monitoring import (
    get_logger,
    get_tracer,
    get_metrics_collector,
    AgentExecutionError
)

logger = logging.getLogger(__name__)
settings = get_settings()


class DoctorSummaryAgent:
    """Agent responsible for generating clinical summaries for physicians."""
    
    def __init__(self):
        """Initialize the doctor summary agent."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name
        self.agent_name = "doctor_summary_agent"
        self.monitor_logger = get_logger()
        self.tracer = get_tracer()
        self.metrics = get_metrics_collector()
        
    async def run(
        self, 
        extraction_data: ExtractionOutput,
        analysis_data: AnalysisOutput, 
        risk_data: RiskOutput,
        trace_id: str
    ) -> DoctorSummaryOutput:
        """
        Generate clinical summary for physicians.
        
        Args:
            extraction_data: Output from extraction agent
            analysis_data: Output from analysis agent
            risk_data: Output from risk agent
            trace_id: Unique trace identifier for request tracking
            
        Returns:
            DoctorSummaryOutput with clinical summary
        """
        start_time = time.time()
        
        # Log and trace start
        input_summary = f"Creating clinical summary for {risk_data.severity_level} severity case"
        self.monitor_logger.log_agent_start(self.agent_name, trace_id, input_summary)
        self.tracer.start_agent(trace_id, self.agent_name, input_summary)
        
        logger.info("Starting doctor summary agent")
        
        try:
            system_prompt = """You are a senior attending physician preparing clinical summaries.

Your task is to create a concise, professional clinical summary for healthcare providers.

Include:
1. Clinical Summary: Professional assessment of findings
2. Suggested Tests: Appropriate follow-up diagnostic tests
3. Lifestyle Recommendations: Evidence-based lifestyle modifications
4. Follow-up Timeline: Recommended timeframe for reassessment

Use medical terminology appropriately.
Base recommendations on current clinical guidelines.
Be specific and actionable.
Consider differential diagnoses.
Prioritize patient safety."""

            extraction_dict = extraction_data.lab_values.model_dump(exclude_none=True)
            analysis_dict = analysis_data.model_dump()
            risk_dict = risk_data.model_dump()
            
            user_prompt = f"""Generate a clinical summary based on these findings:

Lab Values:
{json.dumps(extraction_dict, indent=2)}

Abnormal Values:
{json.dumps(analysis_dict.get('abnormal_values', []), indent=2)}

Possible Conditions:
{json.dumps(analysis_dict.get('possible_conditions', []), indent=2)}

Risk Assessment:
Severity: {risk_dict.get('severity_level')}
Urgency: {risk_dict.get('urgency')}

Provide the summary in this JSON format:
{{
    "clinical_summary": "Professional clinical assessment (2-3 paragraphs)",
    "suggested_tests": [
        "Specific test 1",
        "Specific test 2"
    ],
    "lifestyle_recommendations": [
        "Evidence-based recommendation 1",
        "Evidence-based recommendation 2"
    ],
    "follow_up_timeline": "Specific timeframe"
}}

If all values are normal, recommend routine preventive care."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Clinical summary generated successfully")
            
            doctor_summary_output = DoctorSummaryOutput(**result)
            
            # Log success
            duration_ms = (time.time() - start_time) * 1000
            output_summary = f"Generated {len(result.get('suggested_tests', []))} test recommendations"
            self.monitor_logger.log_agent_success(self.agent_name, trace_id, duration_ms, output_summary)
            self.tracer.end_agent(trace_id, self.agent_name, success=True, output_summary=output_summary)
            self.metrics.record_execution(self.agent_name, "SUCCESS", duration_ms)
            
            return doctor_summary_output
            
        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f"Doctor summary agent error: {e}")
            self.monitor_logger.log_agent_failure(self.agent_name, trace_id, duration_ms, error_msg, error_type)
            self.tracer.end_agent(trace_id, self.agent_name, success=False, error=error_msg, error_type=error_type)
            self.metrics.record_execution(self.agent_name, "FAILED")
            
            raise AgentExecutionError(
                agent_name=self.agent_name,
                error_message=error_msg,
                error_type=error_type,
                trace_id=trace_id
            )
