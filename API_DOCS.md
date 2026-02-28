# 📚 API Documentation

Complete API reference for the Medical AI Multi-Agent System.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

Currently, the API does not require authentication. For production, consider adding:
- API key authentication
- JWT tokens
- OAuth 2.0

## Endpoints

### 1. Health Check

Check if the API is running and operational.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "message": "System is operational",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - System is healthy

---

### 2. Root

Get basic API information.

**Endpoint:** `GET /`

**Response:**
```json
{
  "status": "success",
  "message": "Medical AI Multi-Agent System is running",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - API is running

---

### 3. Upload Medical Report

Upload and analyze a PDF medical report.

**Endpoint:** `POST /upload-report`

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/upload-report" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@medical_report.pdf"
```

**Example (Python):**
```python
import requests

with open("medical_report.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload-report",
        files={"file": f}
    )
    
print(response.json())
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/upload-report', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "message": "Medical report analyzed successfully",
  "extraction": {
    "lab_values": {
      "hemoglobin": 13.5,
      "tsh": 8.5,
      "cholesterol": 180.0,
      "wbc": 7.5,
      "rbc": 4.8,
      "platelets": 250,
      "glucose": 95,
      "creatinine": 1.0,
      "alt": 35,
      "ast": 28
    },
    "raw_text_snippet": "HEMATOLOGY:\nHemoglobin: 13.5 g/dL...",
    "extraction_confidence": "High"
  },
  "analysis": {
    "abnormal_values": [
      {
        "parameter": "TSH",
        "value": 8.5,
        "normal_range": "0.4-4.0 mIU/L",
        "deviation": "High"
      }
    ],
    "possible_conditions": [
      "Hypothyroidism",
      "Thyroid dysfunction"
    ],
    "analysis_notes": "Elevated TSH suggests underactive thyroid function..."
  },
  "risk": {
    "severity_level": "Moderate",
    "urgency": "Doctor Visit",
    "risk_factors": [
      "Thyroid dysfunction",
      "Potential metabolic issues"
    ]
  },
  "explanation": {
    "patient_friendly_explanation": "Your lab results show that most values are within normal range...",
    "key_takeaways": [
      "Your thyroid hormone (TSH) is elevated",
      "This could indicate an underactive thyroid",
      "You should schedule a visit with your doctor",
      "Most other values look good"
    ]
  },
  "doctor_summary": {
    "clinical_summary": "Patient presents with elevated TSH (8.5 mIU/L)...",
    "suggested_tests": [
      "Free T4",
      "Free T3",
      "Thyroid antibodies (Anti-TPO, Anti-Tg)"
    ],
    "lifestyle_recommendations": [
      "Monitor energy levels and weight changes",
      "Ensure adequate iodine intake",
      "Reduce stress",
      "Regular sleep schedule"
    ],
    "follow_up_timeline": "2-4 weeks"
  },
  "error": null
}
```

**Error Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Only PDF files are accepted"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "status": "error",
  "message": "An error occurred while processing the report: ..."
}
```

**Status Codes:**
- `200 OK` - Report analyzed successfully
- `400 Bad Request` - Invalid file type or format
- `500 Internal Server Error` - Processing error

---

### 4. Analyze Text

Analyze medical report text directly without uploading a PDF.

**Endpoint:** `POST /analyze-text`

**Request:**
- Content-Type: `application/x-www-form-urlencoded`
- Parameter: `text` (string)

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/analyze-text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=LABORATORY REPORT\nPatient: John Doe\nHemoglobin: 13.5 g/dL\nTSH: 8.5 mIU/L"
```

**Example (Python):**
```python
import requests

text = """
LABORATORY REPORT
Patient: John Doe
Hemoglobin: 13.5 g/dL
TSH: 8.5 mIU/L
Cholesterol: 180 mg/dL
"""

response = requests.post(
    "http://localhost:8000/analyze-text",
    params={"text": text}
)

print(response.json())
```

**Example (JavaScript):**
```javascript
const text = `LABORATORY REPORT
Patient: John Doe
Hemoglobin: 13.5 g/dL
TSH: 8.5 mIU/L
Cholesterol: 180 mg/dL`;

fetch(`http://localhost:8000/analyze-text?text=${encodeURIComponent(text)}`, {
  method: 'POST'
})
.then(response => response.json())
.then(data => console.log(data));
```

**Success Response (200 OK):**
Same structure as `/upload-report` endpoint.

**Error Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Text is too short or empty"
}
```

**Status Codes:**
- `200 OK` - Text analyzed successfully
- `400 Bad Request` - Invalid or insufficient text
- `500 Internal Server Error` - Processing error

---

## Response Schema

### MedicalReportResponse

```typescript
{
  status: "success" | "error",
  message: string,
  extraction?: ExtractionOutput,
  analysis?: AnalysisOutput,
  risk?: RiskOutput,
  explanation?: ExplanationOutput,
  doctor_summary?: DoctorSummaryOutput,
  error?: string
}
```

### ExtractionOutput

```typescript
{
  lab_values: {
    hemoglobin?: number,
    tsh?: number,
    cholesterol?: number,
    wbc?: number,
    rbc?: number,
    platelets?: number,
    glucose?: number,
    creatinine?: number,
    alt?: number,
    ast?: number
  },
  raw_text_snippet: string,
  extraction_confidence: "High" | "Medium" | "Low"
}
```

### AnalysisOutput

```typescript
{
  abnormal_values: Array<{
    parameter: string,
    value: number,
    normal_range: string,
    deviation: "High" | "Low"
  }>,
  possible_conditions: string[],
  analysis_notes: string
}
```

### RiskOutput

```typescript
{
  severity_level: "Low" | "Moderate" | "High" | "Critical",
  urgency: "Routine" | "Doctor Visit" | "Immediate Attention" | "Emergency",
  risk_factors: string[]
}
```

### ExplanationOutput

```typescript
{
  patient_friendly_explanation: string,
  key_takeaways: string[]
}
```

### DoctorSummaryOutput

```typescript
{
  clinical_summary: string,
  suggested_tests: string[],
  lifestyle_recommendations: string[],
  follow_up_timeline: string
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "status": "error",
  "message": "Error description"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 500 | Internal Server Error - Processing failed |

---

## Rate Limiting

Currently, no rate limits are enforced. For production:
- Consider implementing rate limiting (e.g., 100 requests/hour)
- Use API keys for tracking
- Implement request quotas

---

## CORS

The API allows cross-origin requests from all domains in development.

For production, configure specific allowed origins in [app/main.py](app/main.py):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Testing

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

### Postman Collection

Import `postman_collection.json` into Postman for ready-to-use test requests.

### Test Script

Run the included test script:

```bash
python test_api.py
```

---

## Best Practices

1. **File Size**: Keep PDF files under 10MB
2. **Format**: Ensure PDFs contain extractable text (not scanned images)
3. **Timeout**: Long reports may take 30-60 seconds to process
4. **Validation**: Always check the `status` field in responses
5. **Error Handling**: Implement proper error handling in your client

---

## Support

For API issues or questions:
- Check the logs: `sudo journalctl -u medicalai`
- Review this documentation
- Test with the interactive docs at `/docs`

---

**API Version:** 1.0.0  
**Last Updated:** 2024
