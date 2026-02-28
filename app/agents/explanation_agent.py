"""
Explanation Agent: Generates patient-friendly explanations.
"""

import logging
import json
import time
from openai import AsyncOpenAI
from ..schemas.analysis_schema import AnalysisOutput, RiskOutput, ExplanationOutput
from ..config import get_settings
from ..monitoring import (
    get_logger,
    get_tracer,
    get_metrics_collector,
    AgentExecutionError
)

logger = logging.getLogger(__name__)
settings = get_settings()


class ExplanationAgent:
    """Agent responsible for creating patient-friendly explanations."""
    
    def __init__(self):
        """Initialize the explanation agent."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name
        self.agent_name = "explanation_agent"
        self.monitor_logger = get_logger()
        self.tracer = get_tracer()
        self.metrics = get_metrics_collector()
        
    async def run(self, analysis_data: AnalysisOutput, risk_data: RiskOutput, trace_id: str) -> ExplanationOutput:
        """
        Generate patient-friendly explanation.
        
        Args:
            analysis_data: Output from analysis agent
            risk_data: Output from risk agent
            trace_id: Unique trace identifier for request tracking
            
        Returns:
            ExplanationOutput with patient-friendly text
        """
        start_time = time.time()
        
        # Log and trace start
        input_summary = f"Creating explanation for {risk_data.severity_level} severity case"
        self.monitor_logger.log_agent_start(self.agent_name, trace_id, input_summary)
        self.tracer.start_agent(trace_id, self.agent_name, input_summary)
        
        logger.info("Starting explanation agent")
        
        try:
            system_prompt = """You are a compassionate medical communicator specializing in patient education.

Your task is to explain medical findings in simple, clear language that patients can understand.

Guidelines:
1. Use plain language, avoid medical jargon
2. Be reassuring but honest
3. Explain what abnormal values mean in practical terms
4. Provide context about why these values matter
5. Be empathetic and supportive
6. Focus on actionable information
7. Don't diagnose - explain what tests show
8. Keep explanations concise but complete

Tone: Professional yet friendly, informative yet accessible"""

            analysis_dict = analysis_data.model_dump()
            risk_dict = risk_data.model_dump()
            
            user_prompt = f"""Create a patient-friendly explanation for these findings:

Abnormal Values: {json.dumps(analysis_dict.get('abnormal_values', []), indent=2)}

Possible Conditions: {json.dumps(analysis_dict.get('possible_conditions', []), indent=2)}

Severity: {risk_dict.get('severity_level')}
Urgency: {risk_dict.get('urgency')}

Provide the explanation in this JSON format:
{{
    "patient_friendly_explanation": "Clear, compassionate explanation in 3-5 paragraphs",
    "key_takeaways": [
        "Important point 1",
        "Important point 2",
        "Important point 3"
    ]
}}

If all values are normal, provide a positive, reassuring message."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Patient explanation generated successfully")
            
            explanation_output = ExplanationOutput(**result)
            
            # Log success
            duration_ms = (time.time() - start_time) * 1000
            output_summary = f"Generated {len(result.get('key_takeaways', []))} key takeaways"
            self.monitor_logger.log_agent_success(self.agent_name, trace_id, duration_ms, output_summary)
            self.tracer.end_agent(trace_id, self.agent_name, success=True, output_summary=output_summary)
            self.metrics.record_execution(self.agent_name, "SUCCESS", duration_ms)
            
            return explanation_output
            
        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f"Explanation agent error: {e}")
            self.monitor_logger.log_agent_failure(self.agent_name, trace_id, duration_ms, error_msg, error_type)
            self.tracer.end_agent(trace_id, self.agent_name, success=False, error=error_msg, error_type=error_type)
            self.metrics.record_execution(self.agent_name, "FAILED")
            
            raise AgentExecutionError(
                agent_name=self.agent_name,
                error_message=error_msg,
                error_type=error_type,
                trace_id=trace_id
            )
