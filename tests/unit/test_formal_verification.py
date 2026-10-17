"""
Unit tests for the Multi-Engine Formal Verification Suite (ProVerif, Tamarin Prover, Scyther).
"""

import pytest

from research.formal_verification.runner import (
    ENGINE_MODELS,
    MODELS,
    FormalVerificationRunner,
)


@pytest.fixture
def runner():
    return FormalVerificationRunner()


def test_supported_engines(runner):
    """Ensure all 3 formal engines are declared and supported."""
    engines = runner.get_supported_engines()
    assert len(engines) == 3
    engine_ids = {e["id"] for e in engines}
    assert engine_ids == {"proverif", "tamarin", "scyther"}
    for e in engines:
        assert e["model_count"] == 3
        assert "name" in e
        assert "version" in e


# ---------------------------------------------------------------------------
# ProVerif Tests
# ---------------------------------------------------------------------------

def test_proverif_model_files_exist(runner):
    """Ensure all declared .pv files exist on disk."""
    for proto_id in MODELS:
        path = runner.get_model_path(proto_id, engine="proverif")
        assert path.is_file(), f"Model file missing for {proto_id}: {path}"
        content = runner.get_model_source(proto_id, engine="proverif")
        assert len(content) > 200, f"Model content too short for {proto_id}"


def test_proverif_transcript_files_exist(runner):
    """Ensure all certified ProVerif transcripts exist."""
    for proto_id in MODELS:
        transcript = runner.get_transcript(proto_id, engine="proverif")
        assert "RESULT" in transcript
        assert "is true" in transcript


@pytest.mark.parametrize("proto_id", ["ju_park", "ecc", "ml_kem"])
def test_proverif_model_syntax_validation(runner, proto_id):
    """Validate applied pi-calculus AST syntax for each protocol model."""
    source = runner.get_model_source(proto_id, engine="proverif")
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


# ---------------------------------------------------------------------------
# Tamarin Prover Tests
# ---------------------------------------------------------------------------

def test_tamarin_model_files_exist(runner):
    """Ensure all declared .spthy files exist on disk."""
    for proto_id in ENGINE_MODELS["tamarin"]:
        path = runner.get_model_path(proto_id, engine="tamarin")
        assert path.is_file(), f"Tamarin model file missing for {proto_id}: {path}"
        content = runner.get_model_source(proto_id, engine="tamarin")
        assert len(content) > 200, f"Tamarin model content too short for {proto_id}"


def test_tamarin_transcripts_exist(runner):
    """Ensure all certified Tamarin transcripts exist."""
    for proto_id in ENGINE_MODELS["tamarin"]:
        transcript = runner.get_transcript(proto_id, engine="tamarin")
        assert "verified" in transcript
        assert "Tamarin Prover" in transcript


@pytest.mark.parametrize("proto_id", ["ju_park", "ecc", "ml_kem"])
def test_tamarin_syntax_validation(runner, proto_id):
    """Validate Tamarin theory, rules, and lemmas."""
    source = runner.get_model_source(proto_id, engine="tamarin")
    val = runner.validate_tamarin_syntax(source)
    assert val.valid is True, f"Tamarin syntax validation failed for {proto_id}: {val.errors}"
    assert len(val.processes_found) >= 4  # rules
    assert len(val.queries_found) >= 4    # lemmas


def test_verify_protocol_tamarin(runner):
    """Verify Tamarin proof evaluation across all protocols."""
    results = runner.verify_all(engine="tamarin")
    assert set(results.keys()) == {"ju_park", "ecc", "ml_kem"}
    for proto_id, summary in results.items():
        assert summary.all_proved is True
        assert summary.theorems_count >= 5
        assert summary.theorems_proved == summary.theorems_count
        assert summary.engine == "tamarin"
        assert summary.engine_name == "Tamarin Prover"


# ---------------------------------------------------------------------------
# Scyther Tests
# ---------------------------------------------------------------------------

def test_scyther_model_files_exist(runner):
    """Ensure all declared .spdl files exist on disk."""
    for proto_id in ENGINE_MODELS["scyther"]:
        path = runner.get_model_path(proto_id, engine="scyther")
        assert path.is_file(), f"Scyther model file missing for {proto_id}: {path}"
        content = runner.get_model_source(proto_id, engine="scyther")
        assert len(content) > 200, f"Scyther model content too short for {proto_id}"


def test_scyther_transcripts_exist(runner):
    """Ensure all certified Scyther transcripts exist."""
    for proto_id in ENGINE_MODELS["scyther"]:
        transcript = runner.get_transcript(proto_id, engine="scyther")
        assert "Ok" in transcript
        assert "Scyther version" in transcript


@pytest.mark.parametrize("proto_id", ["ju_park", "ecc", "ml_kem"])
def test_scyther_syntax_validation(runner, proto_id):
    """Validate Scyther roles, usertypes, and claims."""
    source = runner.get_model_source(proto_id, engine="scyther")
    val = runner.validate_scyther_syntax(source)
    assert val.valid is True, f"Scyther syntax validation failed for {proto_id}: {val.errors}"
    assert len(val.processes_found) >= 2  # roles
    assert len(val.queries_found) >= 6    # claims


def test_verify_protocol_scyther(runner):
    """Verify Scyther proof evaluation across all protocols."""
    results = runner.verify_all(engine="scyther")
    assert set(results.keys()) == {"ju_park", "ecc", "ml_kem"}
    for proto_id, summary in results.items():
        assert summary.all_proved is True
        assert summary.theorems_count == 11
        assert summary.theorems_proved == 11
        assert summary.engine == "scyther"
        assert summary.engine_name == "Scyther"


# ---------------------------------------------------------------------------
# Error Handling & Edge Cases
# ---------------------------------------------------------------------------

def test_invalid_protocol_and_engine(runner):
    """Test error handling for unrecognized protocol and engine IDs."""
    with pytest.raises(KeyError):
        runner.get_model_path("non_existent_protocol", engine="proverif")

    with pytest.raises(KeyError):
        runner.get_model_path("ju_park", engine="invalid_engine")

    with pytest.raises(KeyError):
        runner.verify_protocol("ju_park", engine="invalid_engine")
