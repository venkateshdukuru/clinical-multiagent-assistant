# 🚀 Quick Setup Guide

## Step-by-Step Installation

### 1. Prerequisites
- Python 3.10 or higher installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### 2. Setup Instructions

#### For Windows:

```powershell
# Navigate to project directory
cd medical_ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env file and add your OpenAI API key
notepad .env

# Run the application
python -m app.main
```

Or simply run:
```powershell
.\run.bat
```

#### For Linux/Mac:

```bash
# Navigate to project directory
cd medical_ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env file and add your OpenAI API key
nano .env

# Run the application
python -m app.main
```

Or simply run:
```bash
chmod +x run.sh
./run.sh
```

### 3. Configure .env File

Open `.env` and update:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
MODEL_NAME=gpt-4o
```

### 4. Verify Installation

Once running, open your browser:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 5. Test the API

#### Using the Interactive Docs:
1. Go to http://localhost:8000/docs
2. Click on `POST /upload-report`
3. Click "Try it out"
4. Upload a medical report PDF
5. Click "Execute"

#### Using cURL:

```bash
curl -X POST "http://localhost:8000/upload-report" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_medical_report.pdf"
```

#### Using Python:

```python
import requests

with open("medical_report.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload-report",
        files={"file": f}
    )

print(response.json())
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "OpenAI API key not found"

**Solution:** Check your `.env` file has the correct API key:
```env
OPENAI_API_KEY=sk-your-key-here
```

### Issue: Port 8000 already in use

**Solution:** Change the port in `.env`:
```env
APP_PORT=8001
```

### Issue: PDF processing fails

**Solution:** Ensure the PDF contains text (not just images). Scanned PDFs may need OCR preprocessing.

## Next Steps

1. ✅ Test with sample medical reports
2. ✅ Review the API documentation at `/docs`
3. ✅ Integrate with your frontend application
4. ✅ Customize agent prompts as needed
5. ✅ Deploy to production server

## Production Deployment

For production:

```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
# In .env:
APP_RELOAD=false
LOG_LEVEL=WARNING

# Run with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Support

- Check README.md for detailed documentation
- Review API docs at http://localhost:8000/docs
- Check logs for error messages

---

Happy coding! 🎉
