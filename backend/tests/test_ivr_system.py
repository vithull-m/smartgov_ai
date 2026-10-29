import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ivr_start_call():
    response = client.post("/api/ivr/call/start", json={"phone_number": "+919876543210"})
    assert response.status_code == 200
    data = response.json()
    assert "call_sid" in data
    assert data["current_step"] == "language_selection"
    assert "<Response>" in data["twiml"]
    assert len(data["options"]) == 3


def test_ivr_language_selection_tamil():
    # Start call
    res_start = client.post("/api/ivr/call/start", json={"phone_number": "+919876543210"})
    call_sid = res_start.json()["call_sid"]

    # Select digit 2 for Tamil
    res_action = client.post("/api/ivr/call/action", json={
        "call_sid": call_sid,
        "digit": "2",
        "current_step": "language_selection"
    })
    assert res_action.status_code == 200
    data = res_action.json()
    assert data["language"] == "ta"
    assert data["current_step"] == "main_menu"
    assert "விவசாயம்" in data["prompt"]


def test_ivr_scheme_selection_pm_kisan():
    res_start = client.post("/api/ivr/call/start", json={"phone_number": "+919876543210"})
    call_sid = res_start.json()["call_sid"]

    # Select Tamil
    client.post("/api/ivr/call/action", json={
        "call_sid": call_sid,
        "digit": "2",
        "current_step": "language_selection"
    })

    # Select Option 1 (Agriculture / PM-KISAN)
    res_scheme = client.post("/api/ivr/call/action", json={
        "call_sid": call_sid,
        "digit": "1",
        "current_step": "main_menu"
    })
    assert res_scheme.status_code == 200
    data = res_scheme.json()
    assert data["current_step"] == "scheme_detail"
    assert len(data["prompt"]) > 0


def test_ivr_speech_question_processing():
    res_start = client.post("/api/ivr/call/start", json={"phone_number": "+919876543210"})
    call_sid = res_start.json()["call_sid"]

    # Select English (1)
    client.post("/api/ivr/call/action", json={
        "call_sid": call_sid,
        "digit": "1",
        "current_step": "language_selection"
    })

    # Speak question
    res_speech = client.post("/api/ivr/call/action", json={
        "call_sid": call_sid,
        "speech_text": "What are the benefits of PM Scholarship for college students?",
        "current_step": "speech_input"
    })
    assert res_speech.status_code == 200
    data = res_speech.json()
    assert data["current_step"] == "speech_response"
    assert len(data["prompt"]) > 0


def test_ivr_call_logs_endpoint():
    res_logs = client.get("/api/ivr/logs")
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert isinstance(logs, list)
    assert len(logs) > 0
