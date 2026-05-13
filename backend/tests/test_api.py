from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_scenarios():
    response = client.get("/api/scenarios")

    assert response.status_code == 200
    assert response.json()[0]["id"] == "SCN-001"


def test_run_sample_exercise_end_to_end():
    response = client.post(
        "/api/exercises",
        json={
            "scenario_id": "SCN-001",
            "requested_by": "pytest",
            "role": "Exercise Director",
        },
    )

    assert response.status_code == 201
    exercise = response.json()
    assert exercise["status"] == "completed"

    exercise_id = exercise["id"]
    detections = client.get(f"/api/exercises/{exercise_id}/detections").json()
    evidence = client.get(f"/api/exercises/{exercise_id}/evidence?role=Auditor").json()
    report = client.get(f"/api/exercises/{exercise_id}/report?role=Auditor").json()
    siem = client.get(f"/api/exercises/{exercise_id}/siem-export?role=Exercise Director").json()

    assert detections[0]["rule_id"] == "DET-001"
    assert evidence[0]["sha256"]
    assert report["status"] == "passed"
    assert siem["splunk_hec"][0]["sourcetype"] == "breach:simulation"


def test_viewer_cannot_access_audit_endpoint():
    response = client.get("/api/audit?role=Viewer")

    assert response.status_code == 403

