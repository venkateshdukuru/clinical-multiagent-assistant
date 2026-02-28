"""
Sample test script to verify the Medical AI system works correctly.
Run this after starting the server to test functionality.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200


def test_analyze_text():
    """Test the text analysis endpoint with sample medical data."""
    print("🔍 Testing text analysis...")
    
    sample_text = """
    LABORATORY REPORT
    Patient: John Doe
    Date: 2024-01-15
    
    HEMATOLOGY:
    Hemoglobin: 13.5 g/dL (Normal: 13.5-17.5)
    WBC: 7.2 x10^3/μL (Normal: 4.0-11.0)
    RBC: 4.8 x10^6/μL (Normal: 4.5-6.0)
    Platelets: 250 x10^3/μL (Normal: 150-400)
    
    CHEMISTRY:
    Glucose (Fasting): 95 mg/dL (Normal: 70-100)
    Cholesterol: 185 mg/dL (Desirable: <200)
    Creatinine: 1.0 mg/dL (Normal: 0.6-1.2)
    
    THYROID:
    TSH: 8.5 mIU/L (Normal: 0.4-4.0) - HIGH
    
    LIVER FUNCTION:
    ALT: 35 U/L (Normal: 7-56)
    AST: 28 U/L (Normal: 10-40)
    """
    
    response = requests.post(
        f"{BASE_URL}/analyze-text",
        params={"text": sample_text}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n📊 Analysis Results:")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}\n")
        
        if result.get('extraction'):
            print("🔬 Extracted Lab Values:")
            print(json.dumps(result['extraction']['lab_values'], indent=2))
            print(f"Confidence: {result['extraction']['extraction_confidence']}\n")
        
        if result.get('analysis'):
            print("🔍 Analysis:")
            abnormal = result['analysis'].get('abnormal_values', [])
            print(f"Abnormal Values: {len(abnormal)}")
            for val in abnormal:
                print(f"  - {val['parameter']}: {val['value']} ({val['deviation']})")
            print(f"Possible Conditions: {', '.join(result['analysis'].get('possible_conditions', []))}\n")
        
        if result.get('risk'):
            print("⚠️ Risk Assessment:")
            print(f"Severity: {result['risk']['severity_level']}")
            print(f"Urgency: {result['risk']['urgency']}\n")
        
        if result.get('explanation'):
            print("💬 Patient Explanation:")
            print(result['explanation']['patient_friendly_explanation'][:200] + "...\n")
        
        if result.get('doctor_summary'):
            print("👨‍⚕️ Doctor Summary:")
            print(f"Suggested Tests: {', '.join(result['doctor_summary'].get('suggested_tests', []))}")
            print(f"Follow-up: {result['doctor_summary']['follow_up_timeline']}\n")
        
        return True
    else:
        print(f"Error: {response.text}\n")
        return False


def test_upload_report():
    """Test the PDF upload endpoint (requires a PDF file)."""
    print("🔍 Testing PDF upload...")
    print("Note: This test requires a PDF file named 'test_report.pdf' in the current directory.")
    print("Skipping PDF upload test - use the text analysis test instead.\n")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Medical AI Multi-Agent System - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Health Check", test_health_check),
        ("Text Analysis", test_analyze_text),
        ("PDF Upload", test_upload_report),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ {name} failed with error: {e}\n")
            results[name] = False
    
    print("=" * 60)
    print("Test Results:")
    print("=" * 60)
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    print("=" * 60)


if __name__ == "__main__":
    main()
