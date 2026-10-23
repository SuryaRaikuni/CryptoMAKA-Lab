"""Unit tests for the Interactive Security Playground engine."""

from __future__ import annotations

from cryptomaka.schemas.security import PlaygroundTamperRequest
from cryptomaka.security.playground import get_sample_packet, simulate_tamper


def test_playground_sample_packets():
    """Verify that sample packets can be fetched for all supported protocols."""
    for proto in ["ju_park", "ecc", "ml_kem"]:
        sample = get_sample_packet(proto)
        assert sample.protocol == proto
        assert len(sample.fields) > 0
        assert len(sample.field_descriptions) > 0
        assert len(sample.available_presets) > 0


def test_playground_jupark_bit_flip_detected():
    """Bit-flip tampering on V1 should be blocked by ControlServer with V1 failure."""
    req = PlaygroundTamperRequest(
        protocol="ju_park",
        attack_preset="bit_flip_mac",
    )
    resp = simulate_tamper(req)
    assert resp.is_blocked is True
    assert resp.verdict == "BLOCKED"
    assert resp.dropped_by == "ControlServer"
    assert "v1" in resp.reason.lower()
    assert len(resp.logs) > 0
    assert "V1" in resp.tampered_fields


def test_playground_jupark_stale_timestamp():
    """Clock drift exceeding freshness window should be blocked with stale timestamp."""
    req = PlaygroundTamperRequest(
        protocol="ju_park",
        attack_preset="stale_timestamp",
        timestamp_offset_seconds=-60,
    )
    resp = simulate_tamper(req)
    assert resp.is_blocked is True
    assert resp.verdict == "BLOCKED"
    assert "stale" in resp.reason.lower()


def test_playground_jupark_replay_attack():
    """Replaying a consumed pseudonym should be rejected as unknown PID."""
    req = PlaygroundTamperRequest(
        protocol="ju_park",
        attack_preset="replay_attack",
        simulate_replay=True,
    )
    resp = simulate_tamper(req)
    assert resp.is_blocked is True
    assert resp.verdict == "BLOCKED"
    assert "unknown pid" in resp.reason.lower() or "pid" in resp.reason.lower()


def test_playground_ecc_nonce_replay():
    """Replaying a consumed nonce in ECC should be blocked."""
    req = PlaygroundTamperRequest(
        protocol="ecc",
        attack_preset="nonce_replay",
        simulate_replay=True,
    )
    resp = simulate_tamper(req)
    assert resp.is_blocked is True
    assert resp.verdict == "BLOCKED"
    assert "nonce" in resp.reason.lower()


def test_playground_mlkem_forged_id():
    """Forged unregistered identity in ML-KEM should be blocked."""
    req = PlaygroundTamperRequest(
        protocol="ml_kem",
        attack_preset="forged_id",
    )
    resp = simulate_tamper(req)
    assert resp.is_blocked is True
    assert resp.verdict == "BLOCKED"
    assert "not registered" in resp.reason.lower()
