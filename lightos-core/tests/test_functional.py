import pytest
import requests
import json
import time

# Base URLs for local services
CONTEXT_URL = "http://localhost:8010"
ROUTER_URL = "http://localhost:8011"
INFERENCE_URL = "http://localhost:8012"
TELEMETRY_URL = "http://localhost:8013"

# The master API key configured in auth.py
API_KEY = "sk-lightos-demo"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Test Data
TEST_PROMPT = "What is the capital of France?"

def wait_for_services():
    """Wait for Context Engine to become ready before running tests."""
    print("Waiting for Context Engine on port 8010...")
    for _ in range(30):
        try:
            res = requests.get(f"{CONTEXT_URL}/context/health")
            if res.status_code == 200:
                print("Context Engine is ready!")
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    raise RuntimeError("Context Engine did not start in time.")

# Run once before any tests start
wait_for_services()

def test_context_engine_health():
    """Verify Context Engine is up and returns 200."""
    response = requests.get(f"{CONTEXT_URL}/context/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "vector_store_size" in data


def test_context_engine_retrieve_unauthorized():
    """Verify Context Engine blocks requests without API key."""
    response = requests.post(f"{CONTEXT_URL}/context/retrieve", json={
        "prompt": TEST_PROMPT,
        "user_id": "test_user",
        "app_id": "test_app"
    })
    assert response.status_code == 403
    assert "detail" in response.json()


def test_context_engine_retrieve_authorized():
    """Verify Context Engine returns valid chunks with API key."""
    response = requests.post(
        f"{CONTEXT_URL}/context/retrieve",
        headers=HEADERS,
        json={
            "prompt": TEST_PROMPT,
            "user_id": "test_user",
            "app_id": "test_app"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "chunks" in data
    assert isinstance(data["chunks"], list)
    assert "cache_hit" in data


def test_router_api_health():
    """Verify Router API is up."""
    response = requests.get(f"{ROUTER_URL}/router/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_router_api_policy_unauthorized():
    """Verify Router API blocks unauthorized GET requests? No, GET policy is open in auth.py? Wait, check router/main.py. Actually, let's just test the /router/route."""
    response = requests.post(f"{ROUTER_URL}/router/route", json={
        "prompt_length": 100,
        "context_tokens": 0
    })
    assert response.status_code == 403


def test_router_api_route():
    """Verify Router returns a model tier and context budget."""
    response = requests.post(
        f"{ROUTER_URL}/router/route",
        headers=HEADERS,
        json={
            "prompt_length": 50,
            "context_tokens": 10,
            "user_tier": "standard",
            "latency_slo_ms": 500
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "model_tier" in data
    assert data["model_tier"] in ["lightmicro", "lightbase", "lightmax"]
    assert "context_budget" in data


def test_inference_proxy_unauthorized():
    """Verify Inference Proxy blocks unauthorized requests."""
    response = requests.post(f"{INFERENCE_URL}/inference/run", json={
        "model_tier": "lightmicro",
        "prompt": TEST_PROMPT
    })
    assert response.status_code == 403


def test_inference_proxy_run():
    """Verify Inference Proxy returns a generated answer."""
    response = requests.post(
        f"{INFERENCE_URL}/inference/run",
        headers=HEADERS,
        json={
            "model_tier": "lightmicro",
            "prompt": TEST_PROMPT,
            "max_tokens": 50
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "job_id" in data
    assert "tokens_used" in data
    assert data["model_tier"] == "lightmicro"


def test_telemetry_api_health():
    """Verify Telemetry API is up."""
    response = requests.get(f"{TELEMETRY_URL}/telemetry/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_telemetry_api_event_unauthorized():
    """Verify Telemetry API blocks unauthorized POST requests."""
    response = requests.post(f"{TELEMETRY_URL}/telemetry/event", json={
        "job_id": "test-job-123",
        "model_tier": "lightmicro",
        "tokens_used": 100,
        "latency_ms": 50.0,
        "cache_hit": False
    })
    assert response.status_code == 403


def test_telemetry_api_event_and_jobs():
    """Verify an event can be posted and then retrieved in /telemetry/jobs."""
    job_id = f"test-job-{int(time.time())}"
    
    # Post Event
    post_res = requests.post(
        f"{TELEMETRY_URL}/telemetry/event",
        headers=HEADERS,
        json={
            "job_id": job_id,
            "model_tier": "lightmicro",
            "tokens_used": 100,
            "latency_ms": 55.5,
            "cache_hit": True,
            "cache_type": "exact",
            "cost_usd": 0.001
        }
    )
    assert post_res.status_code == 200
    assert post_res.json()["status"] == "recorded"
    
    # Retrieve Jobs
    get_res = requests.get(f"{TELEMETRY_URL}/telemetry/jobs?limit=5", headers=HEADERS)
    assert get_res.status_code == 200
    jobs = get_res.json()["jobs"]
    
    # Ensure our job is in the recent jobs list
    job_ids = [j["job_id"] for j in jobs]
    assert job_id in job_ids

