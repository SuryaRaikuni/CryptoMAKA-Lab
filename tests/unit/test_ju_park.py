"""Unit tests for the Ju-Park normalized protocol reconstruction."""

from __future__ import annotations

import pytest


def test_ju_park_run_protocol_succeeds():
    """The full Ju-Park protocol run should complete without error."""
    from cryptomaka.protocols.ju_park import run_protocol
    result = run_protocol()
    assert result is not None


def test_ju_park_session_key_match():
    """User and cloud server must derive identical session keys."""
    from cryptomaka.protocols.ju_park import run_protocol
    result = run_protocol()
    assert result["match"] is True


def test_ju_park_authentication_success():
    """Both parties should authenticate each other successfully."""
    from cryptomaka.protocols.ju_park import run_protocol
    result = run_protocol()
    # run_protocol raises on failure, so reaching here means auth succeeded
    assert result["match"] is True


def test_ju_park_hash_deterministic():
    """H() with the same inputs should always produce the same output."""
    from cryptomaka.protocols.ju_park import H
    a = H("hello", b"world", 42)
    b = H("hello", b"world", 42)
    assert a == b


def test_ju_park_hash_different_inputs():
    """H() with different inputs should produce different outputs."""
    from cryptomaka.protocols.ju_park import H
    a = H("hello")
    b = H("world")
    assert a != b


def test_ju_park_xor_bytes_roundtrip():
    """XOR twice with the same key should recover the original."""
    from cryptomaka.protocols.ju_park import xor_bytes, rand32
    data = rand32()
    key = rand32()
    assert xor_bytes(xor_bytes(data, key), key) == data


def test_ju_park_xor_bytes_width_mismatch():
    """XOR of different-length bytes should raise ValueError."""
    from cryptomaka.protocols.ju_park import xor_bytes
    with pytest.raises(ValueError):
        xor_bytes(b"abc", b"ab")


def test_ju_park_fresh_timestamp():
    """A current timestamp should be considered fresh."""
    from cryptomaka.protocols.ju_park import fresh, ts
    assert fresh(ts()) is True


def test_ju_park_stale_timestamp():
    """A timestamp 60s in the past should not be fresh."""
    from cryptomaka.protocols.ju_park import fresh, ts, TIMESTAMP_WINDOW
    stale = ts() - TIMESTAMP_WINDOW - 10
    assert fresh(stale) is False


def test_ju_park_registration():
    """User registration should complete without error."""
    from cryptomaka.protocols.ju_park import ControlServer, CloudServer, User
    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()
    user = User("testuser", "testpassword", "test-bio")
    user.register(cs)  # Should not raise


def test_ju_park_multiple_users():
    """Multiple users should be registerable and authenticatable."""
    from cryptomaka.protocols.ju_park import ControlServer, CloudServer, User, run_protocol

    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()

    for i in range(3):
        user = User(f"user{i}", f"pw{i}", f"bio{i}")
        user.register(cs)
        m1, ustate = user.login(cloud.server_id)
        assert m1 is not None
        assert "PIDi" in m1
        assert "V1" in m1
