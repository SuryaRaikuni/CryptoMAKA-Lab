"""Unit tests for benchmarks and quantum modules."""

from __future__ import annotations


def test_benchmark_metrics_computation():
    """compute_metrics should return correct stats."""
    from cryptomaka.benchmarks.metrics import compute_metrics
    timings_ns = [1_000_000, 2_000_000, 3_000_000]  # 1ms, 2ms, 3ms
    metrics = compute_metrics(timings_ns, warmup_count=0)

    assert metrics.iterations == 3
    assert abs(metrics.mean_ms - 2.0) < 0.001
    assert abs(metrics.min_ms - 1.0) < 0.001
    assert abs(metrics.max_ms - 3.0) < 0.001
    assert metrics.throughput_ops_per_sec > 0


def test_benchmark_communication_jupark():
    """Ju-Park communication report should have expected fields."""
    from cryptomaka.benchmarks.communication import (
        JU_PARK_PUBLISHED_BITS,
        jupark_communication_report,
    )
    report = jupark_communication_report()

    assert report["protocol"] == "ju_park"
    assert report["published_reference_bits"] == JU_PARK_PUBLISHED_BITS
    assert report["implementation_bits"] > 0
    assert "messages" in report
    assert len(report["messages"]) == 3  # M1, M2, M3


def test_benchmark_communication_ecc():
    """ECC communication report should have expected fields."""
    from cryptomaka.benchmarks.communication import ecc_communication_report
    report = ecc_communication_report()

    assert report["protocol"] == "ecc_ecdh"
    assert report["implementation_bits"] > 0
    assert "messages" in report
    assert len(report["messages"]) == 2  # M1, M2


def test_benchmark_published_vs_implementation():
    """Published bits and implementation bits should BOTH be present and labeled."""
    from cryptomaka.benchmarks.communication import jupark_communication_report
    report = jupark_communication_report()
    # Both values must be present — never merged
    assert "published_reference_bits" in report
    assert "implementation_bits" in report
    assert report["published_reference_source"] is not None


def test_quantum_threat_report():
    """Quantum threat report should have all required sections."""
    from cryptomaka.quantum.threat_model import get_full_threat_report
    report = get_full_threat_report()

    assert "disclaimer" in report
    assert "threat_analysis" in report
    assert "ecc_ecdh" in report["threat_analysis"]
    assert "sha256" in report["threat_analysis"]
    assert "comparison_table" in report
    assert "pqc_recommendations" in report


def test_quantum_threat_claims():
    """Quantum module must not claim Shor is implemented."""
    from cryptomaka.quantum.threat_model import get_full_threat_report
    report = get_full_threat_report()
    disclaimer = report["disclaimer"].lower()
    # Should warn about limitations
    assert "conceptual" in disclaimer or "no practical" in disclaimer


def test_quantum_discrete_log_demo():
    """Toy discrete-log demo should find the correct exponent."""
    from cryptomaka.quantum.threat_model import toy_discrete_log_demo
    result = toy_discrete_log_demo(secret_x=9999)
    assert result["success"] is True
    assert result["recovered_x"] == 9999
    assert "NOT a quantum simulation" in result["label"]


def test_reduced_roundtrip_protocol():
    """Proposed reduced-round-trip extension should complete successfully."""
    from cryptomaka.protocols.reduced_roundtrip import run_reduced_protocol
    result = run_reduced_protocol()
    assert result["protocol"] == "reduced_roundtrip"
    assert result["message_count"] == 3
    assert "PROPOSED EXTENSION" in result["label"]


def test_reduced_roundtrip_not_jupark():
    """The extension must be clearly labeled as NOT the Ju-Park protocol."""
    from cryptomaka.protocols.reduced_roundtrip import run_reduced_protocol
    result = run_reduced_protocol()
    # Must not claim to be the original protocol
    label = result.get("label", "")
    assert "PROPOSED" in label or "NOT" in label
