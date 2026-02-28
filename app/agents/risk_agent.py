"""
Risk Agent: Assesses risk and urgency based on analysis results.
"""

import logging
import json
import time
from openai import AsyncOpenAI
from ..schemas.analysis_schema import AnalysisOutput, RiskOutput
from ..config import get_settings
from ..monitoring import (
    get_logger,
    get_tracer,
    get_metrics_collector,
    AgentExecutionError
)

logger = logging.getLogger(__name__)
settings = get_settings()


class RiskAgent:
    """Agent responsible for risk assessment and urgency determination."""
    
    def __init__(self):
        """Initialize the risk agent."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name
        self.agent_name = "risk_agent"
        self.monitor_logger = get_logger()
        self.tracer = get_tracer()
        self.metrics = get_metrics_collector()
        
    async def run(self, analysis_data: AnalysisOutput, trace_id: str) -> RiskOutput:
        """
        Assess risk and urgency.
        
        Args:
            analysis_data: Output from analysis agent
            trace_id: Unique trace identifier for request tracking
            
        Returns:
            RiskOutput with severity and urgency levels
        """
        start_time = time.time()
        
        # Log and trace start
        abnormal_count = len(analysis_data.abnormal_values)
        input_summary = f"Assessing {abnormal_count} abnormal values"
        self.monitor_logger.log_agent_start(self.agent_name, trace_id, input_summary)
        self.tracer.start_agent(trace_id, self.agent_name, input_summary)
        
        logger.info("Starting risk agent")
        
        try:
            system_prompt = """You are a medical risk assessment specialist.

Your task is to evaluate the severity and urgency of medical findings.

Severity Levels:
- Low: Minor deviations, likely not concerning
- Moderate: Notable abnormalities requiring attention
- High: Significant abnormalities requiring prompt medical care
- Critical: Life-threatening values requiring immediate intervention

Urgency Levels:
- Routine: Can be addressed at next regular checkup
- Doctor Visit: Should see doctor within 1-2 weeks
- Immediate Attention: Requires medical attention within 24-48 hours
- Emergency: Requires immediate emergency care

Consider:
1. Number and type of abnormal values
2. Degree of deviation from normal
3. Potential severity of associated conditions
4. Presence of multiple risk factors
5. Clinical significance of findings"""

            analysis_dict = analysis_data.model_dump()
            
            user_prompt = f"""Assess the risk level for these findings:

Abnormal Values: {json.dumps(analysis_dict.get('abnormal_values', []), indent=2)}

Possible Conditions: {json.dumps(analysis_dict.get('possible_conditions', []), indent=2)}

Analysis Notes: {analysis_dict.get('analysis_notes', '')}

Provide risk assessment in this JSON format:
{{
    "severity_level": "Low|Moderate|High|Critical",
    "urgency": "Routine|Doctor Visit|Immediate Attention|Emergency",
    "risk_factors": ["factor1", "factor2"]
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
            logger.info(f"Risk assessment: {result.get('severity_level')} severity, {result.get('urgency')} urgency")
            
            risk_output = RiskOutput(**result)
            
            # Log success
            duration_ms = (time.time() - start_time) * 1000
            output_summary = f"Severity: {result.get('severity_level')}, Urgency: {result.get('urgency')}"
            self.monitor_logger.log_agent_success(self.agent_name, trace_id, duration_ms, output_summary)
            self.tracer.end_agent(trace_id, self.agent_name, success=True, output_summary=output_summary)
            self.metrics.record_execution(self.agent_name, "SUCCESS", duration_ms)
            
            return risk_output
            
        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f"Risk agent error: {e}")
            self.monitor_logger.log_agent_failure(self.agent_name, trace_id, duration_ms, error_msg, error_type)
            self.tracer.end_agent(trace_id, self.agent_name, success=False, error=error_msg, error_type=error_type)
            self.metrics.record_execution(self.agent_name, "FAILED")
            
            raise AgentExecutionError(
                agent_name=self.agent_name,
                error_message=error_msg,
                error_type=error_type,
                trace_id=trace_id
            )
