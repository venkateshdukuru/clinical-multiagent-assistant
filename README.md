# Medical AI Multi-Agent System

A production-ready FastAPI backend for analyzing medical lab reports using a multi-agent AI architecture powered by LangGraph and OpenAI GPT-4o.

## 🎯 Overview

This system processes medical report PDFs through a sophisticated multi-agent workflow:

1. **Extraction Agent** - Extracts lab values from PDF text
2. **Analysis Agent** - Identifies abnormal values and possible conditions
3. **Risk Agent** - Assesses severity and urgency
4. **Explanation Agent** - Generates patient-friendly explanations
5. **Doctor Summary Agent** - Creates clinical summaries for physicians

## 🏗️ Architecture

```
medical_ai/
│
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and environment settings
│   │
│   ├── agents/                 # Multi-agent system
│   │   ├── orchestrator.py     # LangGraph workflow orchestrator
│   │   ├── extraction_agent.py # Lab value extraction
│   │   ├── analysis_agent.py   # Abnormality analysis
│   │   ├── risk_agent.py       # Risk assessment
│   │   ├── explanation_agent.py # Patient explanations
│   │   └── doctor_summary_agent.py # Clinical summaries
│   │
│   ├── monitoring/             # Monitoring and tracing
│   │   ├── logger.py           # Structured JSON logging
│   │   ├── tracer.py           # Request tracing
│   │   ├── metrics.py          # Performance metrics
│   │   └── failure_handler.py  # Error handling
│   │
│   ├── schemas/                # Pydantic models
│   │   ├── extraction_schema.py
│   │   ├── analysis_schema.py
│   │   └── response_schema.py
│   │
│   └── utils/                  # Utilities
│       └── pdf_reader.py       # PDF text extraction
│
├── logs/                       # Application logs
│   └── agents.log              # Agent execution logs (JSON)
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── MONITORING.md               # Monitoring system guide
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key with GPT-4o access

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd medical_ai
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-key-here
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Or use Python directly:
   ```bash
   python -m app.main
   ```

The API will be available at: `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

## 📡 API Endpoints

### `GET /`
Health check endpoint

**Response:**
```json
{
  "status": "success",
  "message": "Medical AI Multi-Agent System is running",
  "version": "1.0.0"
}
```

### `POST /upload-report`
Upload and analyze a medical report PDF

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
```json
{
  "status": "success",
  "message": "Medical report analyzed successfully",
  "extraction": {
    "lab_values": {
      "hemoglobin": 13.5,
      "tsh": 2.5,
      "cholesterol": 180.0,
      "wbc": 7.5
    },
    "raw_text_snippet": "...",
    "extraction_confidence": "High"
  },
  "analysis": {
    "abnormal_values": [],
    "possible_conditions": [],
    "analysis_notes": "..."
  },
  "risk": {
    "severity_level": "Low",
    "urgency": "Routine",
    "risk_factors": []
  },
  "explanation": {
    "patient_friendly_explanation": "...",
    "key_takeaways": []
  },
  "doctor_summary": {
    "clinical_summary": "...",
    "suggested_tests": [],
    "lifestyle_recommendations": [],
    "follow_up_timeline": "..."
  }
}
```

### `POST /analyze-text`
Analyze medical report text directly (no PDF)

**Request:**
- Content-Type: `application/json`
- Body: `{"text": "medical report text..."}`

**Response:** Same as `/upload-report`

## 🛠️ Configuration

Configure the application via environment variables in `.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here
MODEL_NAME=gpt-4o

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_RELOAD=true

# Logging
LOG_LEVEL=INFO
```

## 🔧 Technology Stack

- **FastAPI** - Modern, high-performance web framework
- **LangGraph** - Multi-agent workflow orchestration
- **OpenAI GPT-4o** - Advanced language model
- **Pydantic** - Data validation and settings management
- **PyPDF2** - PDF text extraction
- **Uvicorn** - ASGI server

## 📊 Agent Specifications

### Extraction Agent
- **Input:** Raw PDF text
- **Output:** Structured lab values (hemoglobin, TSH, cholesterol, WBC, etc.)
- **Model:** GPT-4o with JSON mode

### Analysis Agent
- **Input:** Extracted lab values
- **Output:** Abnormal values, possible conditions, analysis notes
- **Features:** Uses medical reference ranges

### Risk Agent
- **Input:** Analysis results
- **Output:** Severity level, urgency, risk factors
- **Levels:** Low/Moderate/High/Critical

### Explanation Agent
- **Input:** Analysis + Risk data
- **Output:** Patient-friendly explanation, key takeaways
- **Style:** Compassionate, clear, non-technical

### Doctor Summary Agent
- **Input:** All previous outputs
- **Output:** Clinical summary, suggested tests, lifestyle recommendations
- **Audience:** Healthcare professionals

## 🔒 Best Practices

- All agents use async/await for optimal performance
- Structured JSON responses for reliability
- Comprehensive monitoring with request tracing
- Automatic cascading failure prevention
- Structured JSON logging (console + file)
- Performance metrics tracking
- Clean separation of concerns
- Production-ready code structure
- Type hints and Pydantic validation

## 🧪 Testing

### Test Scripts

**Basic API Testing:**
```bash
python test_api.py
```

**Monitoring System Testing:**
```bash
python test_monitoring.py
```

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Upload report
curl -X POST "http://localhost:8000/upload-report" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/report.pdf"

# Get metrics
curl http://localhost:8000/metrics

# Get traces
curl http://localhost:8000/traces
```

### Using Python

```python
import requests

# Upload report
with open("medical_report.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload-report",
        files={"file": f}
    )

print(response.json())
```

## � Monitoring & Tracing

The system includes comprehensive monitoring and tracing capabilities:

### Features
- **Request Tracing** - Unique trace ID for every request
- **Agent Execution Tracking** - Start/end times, duration, status
- **Failure Detection** - Automatic cascading failure prevention
- **Performance Metrics** - Success rates, average execution times
- **Structured Logging** - JSON format logs (console + file)

### Monitoring Endpoints

**GET /metrics** - System and per-agent performance metrics
```bash
curl http://localhost:8000/metrics
```

**GET /trace/{trace_id}** - Detailed execution trace for specific request
```bash
curl http://localhost:8000/trace/abc123-def456-789
```

**GET /traces** - List of all traces
```bash
curl http://localhost:8000/traces
```

### Example Response with Trace ID
```json
{
  "status": "success",
  "trace_id": "abc123-def456-789",
  "message": "Medical report analyzed successfully",
  "extraction": {...},
  "analysis": {...}
}
```

### Logs

Logs are written in JSON format to:
- Console (real-time output)
- `logs/agents.log` (persistent storage)

Example log entry:
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "agent_name": "extraction_agent",
  "trace_id": "abc123-def456-789",
  "status": "SUCCESS",
  "duration_ms": 420.5
}
```

**📖 For complete monitoring guide, see [MONITORING.md](MONITORING.md)**

## 🚀 Deployment

For production deployment:

1. **Set environment to production:**
   ```env
   APP_RELOAD=false
   LOG_LEVEL=WARNING
   ```

2. **Use production ASGI server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **Configure CORS properly** for your frontend domain

4. **Set up reverse proxy** (Nginx/Apache) for SSL/TLS

5. **Monitor logs** and set up alerting

## 📄 License

This is a demonstration project for medical report analysis.

## ⚠️ Disclaimer

This system is for educational and demonstration purposes. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions.

## 🤝 Support

For issues or questions, please refer to the documentation or contact the development team.

---

**Built with ❤️ using FastAPI and LangGraph**
