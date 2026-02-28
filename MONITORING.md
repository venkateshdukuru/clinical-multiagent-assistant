# 🔍 Monitoring & Tracing System Guide

Complete guide for the Medical AI monitoring and failure tracing system.

## 📋 Overview

The monitoring system provides comprehensive tracking of:
- **Request Tracing** - Unique trace ID for each request
- **Agent Execution Tracking** - Start/end times, duration, status
- **Failure Detection** - Cascading failure prevention
- **Performance Metrics** - Success rates, average times
- **Structured Logging** - JSON format logs

## 🏗️ Architecture

### Components

```
app/
├── monitoring/
│   ├── logger.py           # Centralized JSON logging
│   ├── tracer.py           # Request tracing & workflow tracking
│   ├── metrics.py          # Performance metrics collection
│   └── failure_handler.py  # Error handling & cascading prevention
```

### Data Flow

```
Request → Generate Trace ID → Execute Agents → Log/Trace/Metrics → Response
                                     ↓
                              Agent Fails?
                                     ↓
                         Skip Dependent Agents
                                     ↓
                         Return Partial Response
```

## 📡 Monitoring Endpoints

### 1. GET /metrics

Get performance metrics for all agents.

**Response:**
```json
{
  "status": "success",
  "system_metrics": {
    "system_uptime": "1:23:45.678900",
    "total_requests": 42,
    "total_successful": 38,
    "total_failed": 4,
    "overall_success_rate": 90.48,
    "agents_count": 5,
    "agents": [
      "extraction_agent",
      "analysis_agent",
      "risk_agent",
      "explanation_agent",
      "doctor_summary_agent"
    ]
  },
  "agent_metrics": {
    "extraction_agent": {
      "agent_name": "extraction_agent",
      "total_runs": 42,
      "successful_runs": 40,
      "failed_runs": 2,
      "skipped_runs": 0,
      "success_rate": 95.24,
      "failure_rate": 4.76,
      "avg_duration_ms": 420.5,
      "min_duration_ms": 280.2,
      "max_duration_ms": 890.7,
      "last_run": "2024-01-15T10:30:45.123456",
      "last_status": "SUCCESS"
    },
    "analysis_agent": {
      "agent_name": "analysis_agent",
      "total_runs": 40,
      "successful_runs": 39,
      "failed_runs": 1,
      "skipped_runs": 2,
      "success_rate": 97.5,
      "failure_rate": 2.5,
      "avg_duration_ms": 380.2
    }
  }
}
```

### 2. GET /trace/{trace_id}

Get detailed execution trace for a specific request.

**Example:** `GET /trace/abc123-def456-789`

**Response:**
```json
{
  "status": "success",
  "trace": {
    "trace_id": "abc123-def456-789",
    "start_time": "2024-01-15T10:30:45.123456",
    "end_time": "2024-01-15T10:31:12.456789",
    "total_duration_ms": 27333.33,
    "status": "COMPLETED",
    "failed_agent": null,
    "skipped_agents": [],
    "agents": [
      {
        "name": "extraction_agent",
        "status": "SUCCESS",
        "start_time": "2024-01-15T10:30:45.223456",
        "end_time": "2024-01-15T10:30:46.123456",
        "duration_ms": 900.0,
        "error": null,
        "error_type": null,
        "input_summary": "Text length: 1234 characters",
        "output_summary": "Confidence: High"
      },
      {
        "name": "analysis_agent",
        "status": "SUCCESS",
        "start_time": "2024-01-15T10:30:46.223456",
        "end_time": "2024-01-15T10:30:46.823456",
        "duration_ms": 600.0,
        "error": null,
        "input_summary": "Analyzing 8 lab values",
        "output_summary": "Found 2 abnormal values"
      }
    ]
  }
}
```

### 3. GET /traces

Get summary of all traces.

**Response:**
```json
{
  "status": "success",
  "count": 42,
  "traces": [
    {
      "trace_id": "abc123-def456-789",
      "start_time": "2024-01-15T10:30:45.123456",
      "status": "COMPLETED",
      "total_duration_ms": 27333.33,
      "agent_count": 5,
      "failed_agent": null
    },
    {
      "trace_id": "xyz789-uvw456-123",
      "start_time": "2024-01-15T10:25:30.123456",
      "status": "PARTIAL_FAILURE",
      "total_duration_ms": 12500.45,
      "agent_count": 3,
      "failed_agent": "analysis_agent"
    }
  ]
}
```

## 📊 Response Formats

### Successful Response

```json
{
  "status": "success",
  "message": "Medical report analyzed successfully",
  "trace_id": "abc123-def456-789",
  "extraction": { ... },
  "analysis": { ... },
  "risk": { ... },
  "explanation": { ... },
  "doctor_summary": { ... }
}
```

### Partial Failure Response

```json
{
  "status": "partial_failure",
  "message": "Processing partially failed at analysis_agent",
  "trace_id": "abc123-def456-789",
  "failed_agent": "analysis_agent",
  "skipped_agents": ["risk_agent", "explanation_agent", "doctor_summary_agent"],
  "error": "Invalid numeric format in lab values",
  "extraction": { ... },
  "analysis": null,
  "risk": null,
  "explanation": null,
  "doctor_summary": null
}
```

### Complete Failure Response

```json
{
  "status": "failed",
  "message": "Processing failed at extraction_agent",
  "trace_id": "abc123-def456-789",
  "failed_agent": "extraction_agent",
  "skipped_agents": [
    "analysis_agent",
    "risk_agent",
    "explanation_agent",
    "doctor_summary_agent"
  ],
  "error": "Failed to extract text from PDF",
  "extraction": null,
  "analysis": null,
  "risk": null,
  "explanation": null,
  "doctor_summary": null
}
```

## 📝 Log Format

### Console & File Logs

Logs are written in JSON format to both console and `logs/agents.log`.

**Example log entry:**
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "name": "medical_ai.agents",
  "levelname": "INFO",
  "message": "Agent extraction_agent completed successfully",
  "agent_name": "extraction_agent",
  "trace_id": "abc123-def456-789",
  "duration_ms": 420.5,
  "status": "SUCCESS",
  "output_summary": "Confidence: High"
}
```

**Failure log entry:**
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "name": "medical_ai.agents",
  "levelname": "ERROR",
  "message": "Agent analysis_agent failed",
  "agent_name": "analysis_agent",
  "trace_id": "abc123-def456-789",
  "duration_ms": 125.3,
  "status": "FAILED",
  "error": "Invalid numeric format",
  "error_type": "ValueError"
}
```

## 🔍 Agent Dependency Chain

The system automatically detects dependencies:

```
extraction_agent (no dependencies)
    ↓
analysis_agent (depends on: extraction_agent)
    ↓
risk_agent (depends on: analysis_agent)
    ↓
explanation_agent (depends on: analysis_agent, risk_agent)
    ↓
doctor_summary_agent (depends on: extraction_agent, analysis_agent, risk_agent)
```

If an agent fails, all dependent agents are automatically skipped.

## 🛠️ Monitoring in Action

### 1. Make a Request

```bash
curl -X POST "http://localhost:8000/analyze-text" \
  -d "text=LABORATORY REPORT\nHemoglobin: 13.5 g/dL\nTSH: 8.5 mIU/L"
```

**Response includes trace_id:**
```json
{
  "status": "success",
  "trace_id": "abc123-def456-789",
  ...
}
```

### 2. Check Trace Details

```bash
curl "http://localhost:8000/trace/abc123-def456-789"
```

### 3. View Metrics

```bash
curl "http://localhost:8000/metrics"
```

### 4. Check Logs

```bash
# View live logs
tail -f logs/agents.log

# View formatted logs (if jq is installed)
cat logs/agents.log | jq .
```

## 📈 Metrics Tracking

Metrics are automatically collected for each agent:

- **Total Runs** - Number of times agent executed
- **Successful Runs** - Number of successful executions
- **Failed Runs** - Number of failed executions
- **Skipped Runs** - Number of times skipped due to upstream failure
- **Success Rate** - Percentage of successful runs
- **Failure Rate** - Percentage of failed runs
- **Average Duration** - Mean execution time in milliseconds
- **Min/Max Duration** - Fastest and slowest execution times
- **Last Run** - Timestamp of most recent execution
- **Last Status** - Status of most recent execution

## 🚨 Failure Handling

### Cascading Failure Prevention

When an agent fails:
1. Error is logged with full context
2. Trace is updated with failure information
3. Metrics are recorded
4. Dependent agents are identified
5. Dependent agents are skipped (not executed)
6. Partial response is returned with successful data

### Custom Exception

All agent failures raise `AgentExecutionError`:

```python
class AgentExecutionError(Exception):
    agent_name: str
    error_message: str
    error_type: str
    trace_id: str
```

## 📊 Debugging with Traces

### Scenario: Analysis Agent Fails

1. **Check response** - See which agent failed
2. **Get trace details** - `GET /trace/{trace_id}`
3. **Review logs** - Check `logs/agents.log`
4. **Identify issue** - Error message and type
5. **View metrics** - Check if this is recurring

### Example Debug Session

```bash
# 1. Request fails
POST /analyze-text → {"status": "partial_failure", "trace_id": "xyz123"}

# 2. Get trace details
GET /trace/xyz123
→ Shows analysis_agent failed at timestamp X
→ Error: "Invalid numeric format"
→ Risk, Explanation, and Doctor Summary were skipped

# 3. Check if this is common
GET /metrics
→ analysis_agent failure_rate: 5.2%
→ avg_duration_ms: 380.2

# 4. Review logs
cat logs/agents.log | grep xyz123
→ Full execution flow with timing
```

## 🎯 Best Practices

1. **Always log trace_id** when reporting issues
2. **Monitor metrics regularly** to detect degradation
3. **Set up alerts** for high failure rates
4. **Rotate logs** to prevent disk space issues
5. **Use traces** to understand request flow
6. **Track performance trends** over time

## 🔧 Configuration

### Log Retention

Logs are stored in `logs/agents.log`. Configure log rotation:

**Linux logrotate config:**
```
/path/to/medical_ai/logs/agents.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### Trace Retention

Default: 1000 most recent traces in memory

To change:
```python
# In orchestrator initialization
tracer = AgentTracer(max_traces=5000)
```

## 📚 Additional Resources

- See [API_DOCS.md](API_DOCS.md) for complete API reference
- See [README.md](README.md) for general usage
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

---

**Monitoring system ensures full visibility into the multi-agent workflow! 🚀**
