"""Unit tests for the security test engine."""

from __future__ import annotations

import pytest


def test_security_runner_imports():
    from cryptomaka.security.runner import run_all_security_tests
    assert callable(run_all_security_tests)


def test_security_all_tests_run():
    """All 7 security tests should execute and return structured results."""
    from cryptomaka.security.runner import run_all_security_tests
    report = run_all_security_tests("ju_park")

    assert report["protocol"] == "ju_park"
    assert report["total"] == 7
    assert "passed" in report
    assert "failed" in report
    assert "results" in report
    assert len(report["results"]) == 7


def test_security_result_schema():
    """Each result should have required fields."""
    from cryptomaka.security.runner import run_all_security_tests
    report = run_all_security_tests("ju_park")

    required = {"test", "status", "description", "evidence", "severity", "duration_ms"}
    for result in report["results"]:
        missing = required - set(result.keys())
        assert not missing, f"Result missing fields: {missing}"


def test_security_status_values():
    """Status must be PASS or FAIL only."""
    from cryptomaka.security.runner import run_all_security_tests
    report = run_all_security_tests("ju_park")

    for result in report["results"]:
        assert result["status"] in {"PASS", "FAIL"}, (
            f"Invalid status '{result['status']}' for test '{result['test']}'"
        )


def test_security_replay_attack():
    """Replay attack test should return PASS (protocol blocks it)."""
    from cryptomaka.security.runner import test_replay_attack
    result = test_replay_attack()
    assert result.status == "PASS", f"Replay attack not blocked: {result.evidence}"


def test_security_stale_timestamp():
    """Stale timestamp test should return PASS."""
    from cryptomaka.security.runner import test_stale_timestamp
    result = test_stale_timestamp()
    assert result.status == "PASS", f"Stale timestamp not blocked: {result.evidence}"


def test_security_message_tampering():
    """Message tampering test should return PASS."""
    from cryptomaka.security.runner import test_message_tampering
    result = test_message_tampering()
    assert result.status == "PASS", f"Tampering not blocked: {result.evidence}"


def test_security_user_impersonation():
    """User impersonation test should return PASS."""
    from cryptomaka.security.runner import test_user_impersonation
    result = test_user_impersonation()
    assert result.status == "PASS", f"Impersonation not blocked: {result.evidence}"


def test_security_session_key_agreement():
    """Session key agreement positive control should PASS."""
    from cryptomaka.security.runner import test_session_key_agreement
    result = test_session_key_agreement()
    assert result.status == "PASS", f"Key agreement failed: {result.evidence}"


def test_security_disclaimer_present():
    """Security report must include the academic disclaimer."""
    from cryptomaka.security.runner import run_all_security_tests
    report = run_all_security_tests("ju_park")
    assert "disclaimer" in report
    assert len(report["disclaimer"]) > 20
