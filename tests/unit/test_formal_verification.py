"""
Unit tests for the Formal Verification Suite (ProVerif models & runner).
"""

from pathlib import Path
import pytest

from research.formal_verification.runner import (
    FormalVerificationRunner,
    MODELS,
    PROTOCOL_METADATA,
    FormalQuery,
    ProtocolProofSummary,
)


@pytest.fixture
def runner():
    return FormalVerificationRunner()


def test_model_files_exist(runner):
    """Ensure all declared .pv files exist on disk."""
    for proto_id in MODELS:
        path = runner.get_model_path(proto_id)
        assert path.is_file(), f"Model file missing for {proto_id}: {path}"
        content = runner.get_model_source(proto_id)
        assert len(content) > 200, f"Model content too short for {proto_id}"


def test_transcript_files_exist(runner):
    """Ensure all certified verification transcripts exist."""
    for proto_id in MODELS:
        transcript = runner.get_transcript(proto_id)
        assert "RESULT" in transcript
        assert "is true" in transcript


@pytest.mark.parametrize("proto_id", ["ju_park", "ecc", "ml_kem"])
def test_model_syntax_validation(runner, proto_id):
    """Validate applied pi-calculus AST syntax for each protocol model."""
    source = runner.get_model_source(proto_id)
    val = runner.validate_pv_syntax(source)
    assert val.valid is True, f"Syntax validation failed for {proto_id}: {val.errors}"
    assert len(val.channels_found) >= 1
    assert len(val.types_found) >= 3
    assert len(val.events_found) >= 3
    assert len(val.queries_found) >= 3
    assert len(val.processes_found) >= 2


def test_parse_proverif_output_custom(runner):
    """Test custom output parsing with positive and negative queries."""
    sample_output = """
    RESULT not attacker(SK_User_Secret[]) is true.
    RESULT inj-event(endUser(u, cs, sj, k)) ==> inj-event(endCloud(u, cs, sj, k)) is true.
    RESULT not attacker(broken_key[]) is false.
    """
    queries = runner.parse_proverif_output(sample_output)
    assert len(queries) == 3

    assert queries[0].query_type == "secrecy"
    assert queries[0].proved is True
    assert queries[0].status == "PROVED_TRUE"

    assert queries[1].query_type == "injective_correspondence"
    assert queries[1].proved is True

    assert queries[2].query_type == "secrecy"
    assert queries[2].proved is False
    assert queries[2].status == "FAILED"


def test_verify_protocol_ju_park(runner):
    """Verify Ju-Park proof summary."""
    summary = runner.verify_protocol("ju_park")
    assert isinstance(summary, ProtocolProofSummary)
    assert summary.protocol_id == "ju_park"
    assert summary.all_proved is True
    assert summary.theorems_count == 5
    assert summary.theorems_proved == 5
    assert summary.syntax_validation.valid is True

    targets = [q.target for q in summary.queries]
    assert any("SK_User" in t for t in targets)
    assert any("SK_Cloud" in t for t in targets)
    assert any("Mutual Authentication" in t for t in targets)


def test_verify_protocol_ecc(runner):
    """Verify ECC baseline proof summary."""
    summary = runner.verify_protocol("ecc")
    assert summary.protocol_id == "ecc"
    assert summary.all_proved is True
    assert summary.theorems_count == 4
    assert summary.theorems_proved == 4


def test_verify_protocol_ml_kem(runner):
    """Verify Post-Quantum ML-KEM proof summary."""
    summary = runner.verify_protocol("ml_kem")
    assert summary.protocol_id == "ml_kem"
    assert summary.all_proved is True
    assert summary.theorems_count == 4
    assert summary.theorems_proved == 4


def test_verify_all(runner):
    """Verify runner.verify_all() returns all 3 models."""
    res = runner.verify_all()
    assert set(res.keys()) == {"ju_park", "ecc", "ml_kem"}
    for proto_id, summary in res.items():
        assert summary.all_proved is True
        assert len(summary.features) > 0


def test_invalid_protocol(runner):
    """Test error handling for unrecognized protocol IDs."""
    with pytest.raises(KeyError):
        runner.get_model_path("non_existent_protocol")

    with pytest.raises(KeyError):
        runner.get_model_source("non_existent_protocol")
