"""
Test script for monitoring and tracing endpoints.

This script tests:
1. Basic request creates trace_id
2. Metrics endpoint returns data
3. Trace endpoint returns execution details
4. Traces list endpoint works
5. Failed request handling
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"

def print_json(data: Dict[str, Any], title: str = ""):
    """Pretty print JSON data"""
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    print(json.dumps(data, indent=2))

def test_analyze_text() -> str:
    """Test text analysis and get trace_id"""
    print("\n🧪 TEST 1: Analyze Text (Get Trace ID)")
    print("=" * 50)
    
    url = f"{BASE_URL}/analyze-text"
    data = {
        "text": """LABORATORY REPORT
Patient: John Doe
Date: 2024-01-15

TEST RESULTS:
Hemoglobin: 13.5 g/dL (Normal Range: 13.5-17.5)
TSH: 8.5 mIU/L (Normal Range: 0.4-4.0)
Glucose: 95 mg/dL (Normal Range: 70-100)
Cholesterol: 210 mg/dL (Normal Range: <200)
"""
    }
    
    print(f"📤 Sending request to {url}")
    response = requests.post(url, json=data)
    
    print(f"📥 Status Code: {response.status_code}")
    result = response.json()
    
    # Print key information
    print(f"\n✅ Status: {result.get('status')}")
    print(f"🆔 Trace ID: {result.get('trace_id')}")
    print(f"📊 Message: {result.get('message')}")
    
    # Check if we have results
    if result.get('extraction'):
        lab_count = len(result['extraction'].get('lab_values', []))
        print(f"🔬 Lab Values Extracted: {lab_count}")
    
    if result.get('analysis'):
        abnormal_count = len(result['analysis'].get('abnormal_values', []))
        print(f"⚠️ Abnormal Values Found: {abnormal_count}")
    
    if result.get('risk'):
        print(f"🚨 Severity: {result['risk'].get('severity')}")
        print(f"⏰ Urgency: {result['risk'].get('urgency')}")
    
    return result.get('trace_id')

def test_get_metrics():
    """Test metrics endpoint"""
    print("\n🧪 TEST 2: Get System Metrics")
    print("=" * 50)
    
    url = f"{BASE_URL}/metrics"
    print(f"📤 Sending request to {url}")
    
    response = requests.get(url)
    print(f"📥 Status Code: {response.status_code}")
    
    result = response.json()
    
    # Print system metrics
    if result.get('system_metrics'):
        sys_metrics = result['system_metrics']
        print(f"\n📊 System Metrics:")
        print(f"  Total Requests: {sys_metrics.get('total_requests')}")
        print(f"  Successful: {sys_metrics.get('total_successful')}")
        print(f"  Failed: {sys_metrics.get('total_failed')}")
        print(f"  Success Rate: {sys_metrics.get('overall_success_rate', 0):.2f}%")
    
    # Print agent metrics summary
    if result.get('agent_metrics'):
        print(f"\n🤖 Per-Agent Metrics:")
        for agent_name, metrics in result['agent_metrics'].items():
            print(f"\n  {agent_name}:")
            print(f"    Total Runs: {metrics.get('total_runs')}")
            print(f"    Success Rate: {metrics.get('success_rate', 0):.2f}%")
            print(f"    Avg Duration: {metrics.get('avg_duration_ms', 0):.2f}ms")
            print(f"    Last Status: {metrics.get('last_status', 'N/A')}")

def test_get_trace(trace_id: str):
    """Test trace endpoint"""
    print("\n🧪 TEST 3: Get Trace Details")
    print("=" * 50)
    
    url = f"{BASE_URL}/trace/{trace_id}"
    print(f"📤 Sending request to {url}")
    print(f"🆔 Trace ID: {trace_id}")
    
    response = requests.get(url)
    print(f"📥 Status Code: {response.status_code}")
    
    result = response.json()
    
    if result.get('trace'):
        trace = result['trace']
        print(f"\n📋 Trace Information:")
        print(f"  Status: {trace.get('status')}")
        print(f"  Total Duration: {trace.get('total_duration_ms', 0):.2f}ms")
        print(f"  Failed Agent: {trace.get('failed_agent', 'None')}")
        print(f"  Skipped Agents: {trace.get('skipped_agents', [])}")
        
        if trace.get('agents'):
            print(f"\n🔍 Agent Execution Details:")
            for agent in trace['agents']:
                status_icon = "✅" if agent['status'] == "SUCCESS" else "❌"
                print(f"\n  {status_icon} {agent['name']}:")
                print(f"      Status: {agent['status']}")
                print(f"      Duration: {agent.get('duration_ms', 0):.2f}ms")
                if agent.get('error'):
                    print(f"      Error: {agent['error']}")

def test_get_traces():
    """Test traces list endpoint"""
    print("\n🧪 TEST 4: Get All Traces")
    print("=" * 50)
    
    url = f"{BASE_URL}/traces"
    print(f"📤 Sending request to {url}")
    
    response = requests.get(url)
    print(f"📥 Status Code: {response.status_code}")
    
    result = response.json()
    
    if result.get('traces'):
        print(f"\n📜 Found {result.get('count')} traces:")
        for trace in result['traces'][:5]:  # Show first 5
            print(f"\n  🆔 {trace.get('trace_id')}")
            print(f"      Status: {trace.get('status')}")
            print(f"      Duration: {trace.get('total_duration_ms', 0):.2f}ms")
            print(f"      Agents: {trace.get('agent_count')}")
            if trace.get('failed_agent'):
                print(f"      Failed At: {trace['failed_agent']}")

def test_invalid_text():
    """Test with invalid text to trigger potential failures"""
    print("\n🧪 TEST 5: Test Error Handling (Invalid Input)")
    print("=" * 50)
    
    url = f"{BASE_URL}/analyze-text"
    data = {
        "text": "Not a medical report - just random text"
    }
    
    print(f"📤 Sending request with non-medical text")
    response = requests.post(url, json=data)
    
    print(f"📥 Status Code: {response.status_code}")
    result = response.json()
    
    print(f"\n✅ Status: {result.get('status')}")
    print(f"🆔 Trace ID: {result.get('trace_id')}")
    print(f"📊 Message: {result.get('message')}")
    
    if result.get('status') == 'partial_failure':
        print(f"⚠️ Failed Agent: {result.get('failed_agent')}")
        print(f"⏭️ Skipped Agents: {result.get('skipped_agents')}")
        print(f"❌ Error: {result.get('error')}")
    
    return result.get('trace_id')

def main():
    """Run all monitoring tests"""
    print("🚀 MEDICAL AI MONITORING SYSTEM TEST SUITE")
    print("=" * 50)
    print("\nTesting monitoring and tracing endpoints...")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Test 1: Analyze text and get trace_id
        trace_id = test_analyze_text()
        time.sleep(1)
        
        # Test 2: Get system metrics
        test_get_metrics()
        time.sleep(1)
        
        # Test 3: Get specific trace details
        if trace_id:
            test_get_trace(trace_id)
            time.sleep(1)
        
        # Test 4: Get all traces
        test_get_traces()
        time.sleep(1)
        
        # Test 5: Test error handling
        error_trace_id = test_invalid_text()
        time.sleep(1)
        
        # Check error trace
        if error_trace_id:
            test_get_trace(error_trace_id)
        
        print("\n✅ ALL TESTS COMPLETED!")
        print("=" * 50)
        print("\n📝 Check logs/agents.log for detailed execution logs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server")
        print(f"Make sure the server is running at {BASE_URL}")
        print("Run: python -m app.main")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
