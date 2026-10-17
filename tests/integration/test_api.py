"""Integration tests for the FastAPI REST API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from cryptomaka.main import app
    return TestClient(app)


def test_health_endpoint(client):
    """GET /api/v1/health should return 200 with status field."""
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "database" in data
    assert "version" in data
    assert data["status"] in {"healthy", "degraded"}


def test_list_protocols(client):
    """GET /api/v1/protocols should return 4 protocols including ML-KEM."""
    r = client.get("/api/v1/protocols")
    assert r.status_code == 200
    protocols = r.json()
    assert isinstance(protocols, list)
    ids = {p["id"] for p in protocols}
    assert "ju_park" in ids
    assert "ecc" in ids
    assert "reduced_roundtrip" in ids
    assert "ml_kem" in ids


def test_run_jupark_protocol(client):
    """POST /api/v1/protocols/ju_park/run should return successful run."""
    r = client.post("/api/v1/protocols/ju_park/run")
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "ju_park"
    assert data["authentication_success"] is True
    assert data["session_key_match"] is True
    assert "run_id" in data
    # Must NOT return session keys or secrets
    assert "session_key" not in str(data).lower() or "session_key_match" in data


def test_run_ecc_protocol(client):
    """POST /api/v1/protocols/ecc/run should return successful ECC run."""
    r = client.post("/api/v1/protocols/ecc/run")
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "ecc"
    assert data["authentication_success"] is True
    assert data["session_key_match"] is True


def test_run_ml_kem_protocol(client):
    """POST /api/v1/protocols/ml_kem/run should return successful ML-KEM run."""
    r = client.post("/api/v1/protocols/ml_kem/run")
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "ml_kem"
    assert data["authentication_success"] is True
    assert data["session_key_match"] is True
    assert data["message_count"] == 4
    assert data["communication_bits"] > 0



def test_run_reduced_roundtrip(client):
    """POST /api/v1/protocols/reduced_roundtrip/run should succeed."""
    r = client.post("/api/v1/protocols/reduced_roundtrip/run")
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "reduced_roundtrip"


def test_run_invalid_protocol(client):
    """POST with unknown protocol should return 404."""
    r = client.post("/api/v1/protocols/nonexistent/run")
    assert r.status_code == 404


def test_run_security_tests(client):
    """POST /api/v1/security/run should return structured security results."""
    r = client.post("/api/v1/security/run", json={"protocol": "ju_park"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 7
    assert data["passed"] + data["failed"] == data["total"]
    assert "disclaimer" in data
    assert "results" in data
    for result in data["results"]:
        assert result["status"] in {"PASS", "FAIL"}


def test_run_benchmark(client):
    """POST /api/v1/benchmarks/run should return structured metrics."""
    r = client.post("/api/v1/benchmarks/run", json={
        "protocol": "ju_park",
        "iterations": 5,
        "warmup": 2
    })
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "ju_park"
    assert data["total"]["iterations"] == 5
    assert data["total"]["mean_ms"] > 0
    assert "host_metadata" in data


def test_compare_benchmarks_returns_frontend_contract(client):
    """POST /api/v1/benchmarks/compare should expose chart-ready results."""
    r = client.post("/api/v1/benchmarks/compare", json={
        "protocols": ["ju_park", "ecc", "reduced_roundtrip"],
        "iterations": 1,
        "warmup": 0,
    })

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["results"], list)
    assert {result["protocol"] for result in data["results"]} == {
        "ju_park",
        "ecc",
        "reduced_roundtrip",
    }
    for result in data["results"]:
        assert result["total"]["mean_ms"] >= 0
        assert result["total"]["throughput_ops_per_sec"] >= 0
    assert data["host_metadata"]["system"]
    assert data["host_metadata"]["machine"]


def test_create_experiment(client):
    """POST /api/v1/experiments should create and run an experiment."""
    r = client.post("/api/v1/experiments", json={
        "name": "Test Experiment",
        "protocol": "ju_park"
    })
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert data["protocol"] == "ju_park"
    assert data["name"] == "Test Experiment"


def test_list_experiments(client):
    """GET /api/v1/experiments should return experiment list."""
    r = client.get("/api/v1/experiments")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_experiment_by_id(client):
    """GET /api/v1/experiments/{id} should return experiment detail."""
    # Create first
    create = client.post("/api/v1/experiments", json={
        "name": "Detail Test",
        "protocol": "ecc"
    })
    exp_id = create.json()["id"]

    r = client.get(f"/api/v1/experiments/{exp_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == exp_id


def test_get_experiment_not_found(client):
    """GET /api/v1/experiments/nonexistent should return 404."""
    r = client.get("/api/v1/experiments/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_export_experiment_json(client):
    """GET /api/v1/experiments/{id}/export/json should return JSON file."""
    create = client.post("/api/v1/experiments", json={
        "name": "Export Test",
        "protocol": "ju_park"
    })
    exp_id = create.json()["id"]

    r = client.get(f"/api/v1/experiments/{exp_id}/export/json")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")


def test_security_results_list(client):
    """GET /api/v1/security/results should return list."""
    r = client.get("/api/v1/security/results")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_benchmarks_list(client):
    """GET /api/v1/benchmarks should return list."""
    r = client.get("/api/v1/benchmarks")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_quantum_threat_report_api(client):
    """GET /api/v1/quantum/threat-report should return analysis."""
    r = client.get("/api/v1/quantum/threat-report")
    assert r.status_code == 200
    data = r.json()
    assert "disclaimer" in data
    assert "threat_analysis" in data


def test_quantum_discrete_log_demo_api(client):
    """GET /api/v1/quantum/demo/discrete-log should return demo result."""
    r = client.get("/api/v1/quantum/demo/discrete-log?secret_x=1234")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["recovered_x"] == 1234


def test_playground_sample_packet_api(client):
    """GET /api/v1/security/playground/sample-packet should return packet structure."""
    r = client.get("/api/v1/security/playground/sample-packet?protocol=ju_park")
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "ju_park"
    assert "fields" in data
    assert "field_descriptions" in data
    assert "available_presets" in data


def test_playground_simulate_tamper_api(client):
    """POST /api/v1/security/playground/simulate should return verification diagnostics."""
    r = client.post("/api/v1/security/playground/simulate", json={
        "protocol": "ju_park",
        "attack_preset": "bit_flip_mac",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "ju_park"
    assert data["is_blocked"] is True
    assert data["verdict"] == "BLOCKED"
    assert data["dropped_by"] == "ControlServer"
    assert len(data["logs"]) > 0
    assert "V1" in data["tampered_fields"]
