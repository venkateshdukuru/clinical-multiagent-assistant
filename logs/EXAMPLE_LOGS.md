# Example Log Output

This file shows example log entries from the Medical AI monitoring system.

## Successful Request Log Flow

```json
{"timestamp": "2024-01-15T10:30:45.123456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent extraction_agent started", "agent_name": "extraction_agent", "trace_id": "abc123-def456-789", "status": "STARTED", "input_summary": "Text length: 1234 characters"}

{"timestamp": "2024-01-15T10:30:46.023456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent extraction_agent completed successfully", "agent_name": "extraction_agent", "trace_id": "abc123-def456-789", "duration_ms": 900.0, "status": "SUCCESS", "output_summary": "Confidence: High"}

{"timestamp": "2024-01-15T10:30:46.123456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent analysis_agent started", "agent_name": "analysis_agent", "trace_id": "abc123-def456-789", "status": "STARTED", "input_summary": "Analyzing 8 lab values"}

{"timestamp": "2024-01-15T10:30:46.723456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent analysis_agent completed successfully", "agent_name": "analysis_agent", "trace_id": "abc123-def456-789", "duration_ms": 600.0, "status": "SUCCESS", "output_summary": "Found 2 abnormal values"}

{"timestamp": "2024-01-15T10:30:46.823456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent risk_agent started", "agent_name": "risk_agent", "trace_id": "abc123-def456-789", "status": "STARTED", "input_summary": "Assessing 2 abnormal values"}

{"timestamp": "2024-01-15T10:30:47.223456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent risk_agent completed successfully", "agent_name": "risk_agent", "trace_id": "abc123-def456-789", "duration_ms": 400.0, "status": "SUCCESS", "output_summary": "Severity: Moderate, Urgency: Doctor Visit"}

{"timestamp": "2024-01-15T10:30:47.323456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent explanation_agent started", "agent_name": "explanation_agent", "trace_id": "abc123-def456-789", "status": "STARTED", "input_summary": "Creating explanation for Moderate severity case"}

{"timestamp": "2024-01-15T10:30:48.123456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent explanation_agent completed successfully", "agent_name": "explanation_agent", "trace_id": "abc123-def456-789", "duration_ms": 800.0, "status": "SUCCESS", "output_summary": "Generated 4 key takeaways"}

{"timestamp": "2024-01-15T10:30:48.223456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent doctor_summary_agent started", "agent_name": "doctor_summary_agent", "trace_id": "abc123-def456-789", "status": "STARTED", "input_summary": "Creating clinical summary for Moderate severity case"}

{"timestamp": "2024-01-15T10:30:49.023456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent doctor_summary_agent completed successfully", "agent_name": "doctor_summary_agent", "trace_id": "abc123-def456-789", "duration_ms": 800.0, "status": "SUCCESS", "output_summary": "Generated 3 test recommendations"}
```

## Failed Request Log Flow (With Cascading Skip)

```json
{"timestamp": "2024-01-15T11:15:30.123456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent extraction_agent started", "agent_name": "extraction_agent", "trace_id": "xyz789-uvw456-123", "status": "STARTED", "input_summary": "Text length: 856 characters"}

{"timestamp": "2024-01-15T11:15:31.023456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent extraction_agent completed successfully", "agent_name": "extraction_agent", "trace_id": "xyz789-uvw456-123", "duration_ms": 900.0, "status": "SUCCESS", "output_summary": "Confidence: High"}

{"timestamp": "2024-01-15T11:15:31.123456", "name": "medical_ai.agents", "levelname": "INFO", "message": "Agent analysis_agent started", "agent_name": "analysis_agent", "trace_id": "xyz789-uvw456-123", "status": "STARTED", "input_summary": "Analyzing 6 lab values"}

{"timestamp": "2024-01-15T11:15:31.248456", "name": "medical_ai.agents", "levelname": "ERROR", "message": "Agent analysis_agent failed", "agent_name": "analysis_agent", "trace_id": "xyz789-uvw456-123", "duration_ms": 125.0, "status": "FAILED", "error": "Invalid numeric format in lab values", "error_type": "ValueError"}

{"timestamp": "2024-01-15T11:15:31.249456", "name": "medical_ai.agents", "levelname": "WARNING", "message": "Agent risk_agent skipped", "agent_name": "risk_agent", "trace_id": "xyz789-uvw456-123", "status": "SKIPPED", "reason": "Dependent agent failed"}

{"timestamp": "2024-01-15T11:15:31.250456", "name": "medical_ai.agents", "levelname": "WARNING", "message": "Agent explanation_agent skipped", "agent_name": "explanation_agent", "trace_id": "xyz789-uvw456-123", "status": "SKIPPED", "reason": "Dependent agent failed"}

{"timestamp": "2024-01-15T11:15:31.251456", "name": "medical_ai.agents", "levelname": "WARNING", "message": "Agent doctor_summary_agent skipped", "agent_name": "doctor_summary_agent", "trace_id": "xyz789-uvw456-123", "status": "SKIPPED", "reason": "Dependent agent failed"}
```

## Reading Logs

### Using jq (JSON processor)

```bash
# Pretty print all logs
cat logs/agents.log | jq .

# Filter by trace_id
cat logs/agents.log | jq 'select(.trace_id == "abc123-def456-789")'

# Filter by agent
cat logs/agents.log | jq 'select(.agent_name == "analysis_agent")'

# Filter by status
cat logs/agents.log | jq 'select(.status == "FAILED")'

# Get all errors
cat logs/agents.log | jq 'select(.levelname == "ERROR")'

# Calculate average duration for an agent
cat logs/agents.log | jq -s '[.[] | select(.agent_name == "extraction_agent" and .duration_ms != null) | .duration_ms] | add/length'
```

### Using grep

```bash
# Find all failures
grep "FAILED" logs/agents.log

# Find specific trace
grep "abc123-def456-789" logs/agents.log

# Find all skipped agents
grep "SKIPPED" logs/agents.log

# Count errors
grep -c "ERROR" logs/agents.log
```

### Using Python

```python
import json

# Read and parse logs
with open('logs/agents.log', 'r') as f:
    logs = [json.loads(line) for line in f]

# Filter by trace_id
trace_logs = [log for log in logs if log.get('trace_id') == 'abc123-def456-789']

# Get all failures
failures = [log for log in logs if log.get('status') == 'FAILED']

# Calculate metrics
durations = [log.get('duration_ms') for log in logs if log.get('duration_ms')]
avg_duration = sum(durations) / len(durations)
```

## Log Analysis Tips

1. **Track request flow** - Use trace_id to see complete journey
2. **Identify bottlenecks** - Look at duration_ms values
3. **Find error patterns** - Group by error_type
4. **Monitor success rates** - Count SUCCESS vs FAILED per agent
5. **Detect anomalies** - Compare duration_ms to averages

---

**These structured JSON logs make debugging and monitoring easy! 📊**
