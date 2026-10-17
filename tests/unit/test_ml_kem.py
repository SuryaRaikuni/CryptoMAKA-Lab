"""Unit tests for the ML-KEM-768 Post-Quantum MAKA Protocol Prototype."""

from __future__ import annotations


# ---------------------------------------------------------------------------
# KEM primitive tests
# ---------------------------------------------------------------------------

def test_mlkem_keypair_creation():
    """MLKEMKeypair should generate a 1184-byte (9472-bit) public key."""
    from cryptomaka.protocols.ml_kem import MLKEMKeypair, MLKEM_PUBLIC_KEY_BYTES
    kp = MLKEMKeypair()
    assert len(kp.public_key) == MLKEM_PUBLIC_KEY_BYTES, (
        f"Expected public key of {MLKEM_PUBLIC_KEY_BYTES} bytes, got {len(kp.public_key)}"
    )


def test_mlkem_kem_roundtrip_same_keypair():
    """Encapsulate then decapsulate on the same keypair should yield identical shared secrets."""
    from cryptomaka.protocols.ml_kem import MLKEMKeypair
    kp = MLKEMKeypair()
    ciphertext, sk_encap = kp.encapsulate(kp.public_key)
    sk_decap = kp.decapsulate(ciphertext)
    assert sk_encap == sk_decap, "Shared secret mismatch on same-keypair KEM roundtrip"


def test_mlkem_kem_cross_keypair():
    """
    Encapsulate to user's public key with a separate engine; user's keypair
    must decapsulate and recover the same shared secret.
    """
    from cryptomaka.protocols.ml_kem import MLKEMKeypair
    user_kp = MLKEMKeypair()
    encap_engine = MLKEMKeypair()
    ciphertext, sk_encap = encap_engine.encapsulate(user_kp.public_key)
    sk_decap = user_kp.decapsulate(ciphertext)
    assert sk_encap == sk_decap, "Shared secret mismatch on cross-keypair KEM roundtrip"


def test_mlkem_ciphertext_size():
    """Ciphertext should be exactly 1088 bytes (ML-KEM-768 wire size per FIPS 203)."""
    from cryptomaka.protocols.ml_kem import MLKEMKeypair, MLKEM_CIPHERTEXT_BYTES
    kp = MLKEMKeypair()
    ciphertext, _ = kp.encapsulate(kp.public_key)
    assert len(ciphertext) == MLKEM_CIPHERTEXT_BYTES, (
        f"Expected ciphertext of {MLKEM_CIPHERTEXT_BYTES} bytes, got {len(ciphertext)}"
    )


def test_mlkem_shared_secret_size():
    """Shared secret should be 32 bytes (256-bit)."""
    from cryptomaka.protocols.ml_kem import MLKEMKeypair
    kp = MLKEMKeypair()
    _, sk = kp.encapsulate(kp.public_key)
    assert len(sk) == 32, f"Expected 32-byte shared secret, got {len(sk)}"


# ---------------------------------------------------------------------------
# Full protocol flow tests
# ---------------------------------------------------------------------------

def test_mlkem_registration():
    """User registration with ML-KEM RC should return credential token."""
    from cryptomaka.protocols.ml_kem import MLKEMRegistrationCentre, MLKEMUser
    rc = MLKEMRegistrationCentre()
    user = MLKEMUser("alice", "password123", "bio-template")
    user.register(rc)
    assert user._smart_card is not None
    assert "R" in user._smart_card
    assert "h_id" in user._smart_card


def test_mlkem_full_protocol_session_key_match():
    """Full ML-KEM MAKA handshake: user and cloud derive identical session keys."""
    from cryptomaka.protocols.ml_kem import (
        MLKEMRegistrationCentre, MLKEMCloudServer, MLKEMUser
    )
    rc = MLKEMRegistrationCentre()
    cs = MLKEMCloudServer("cloud-mlkem-test")
    user = MLKEMUser("alice", "correct-horse-battery", "fingerprint-xyz")
    user.register(rc)

    m1, _ = user.start_authentication()
    m2, sk_server, reason = cs.process_authentication(rc, m1)

    assert m2 is not None, f"Cloud rejected authentication: {reason}"
    assert sk_server is not None

    sk_user, user_reason = user.verify_and_derive_key(m1, m2)
    assert sk_user is not None, f"User key derivation failed: {user_reason}"
    assert sk_user == sk_server, "Session keys do not match!"


def test_mlkem_tampered_user_authenticator_rejected():
    """Tampering with Auth_u in M1 should cause RC to reject the authentication."""
    from cryptomaka.protocols.ml_kem import (
        MLKEMRegistrationCentre, MLKEMCloudServer, MLKEMUser
    )
    rc = MLKEMRegistrationCentre()
    cs = MLKEMCloudServer("cloud-mlkem-tamper-test")
    user = MLKEMUser("alice", "correct-horse-battery", "fingerprint-xyz")
    user.register(rc)

    m1, _ = user.start_authentication()
    m1_tampered = dict(m1)
    m1_tampered["Auth_u"] = "0" * 64  # corrupted authenticator

    m2, sk_server, reason = cs.process_authentication(rc, m1_tampered)
    assert m2 is None, "Tampered Auth_u should be rejected by RC"
    assert "mismatch" in reason or "rejected" in reason.lower() or reason != "ok"


def test_mlkem_replay_nonce_rejected():
    """Reusing the same nonce in a second authentication should be rejected."""
    from cryptomaka.protocols.ml_kem import (
        MLKEMRegistrationCentre, MLKEMCloudServer, MLKEMUser
    )
    rc = MLKEMRegistrationCentre()
    cs = MLKEMCloudServer("cloud-mlkem-replay-test")
    user = MLKEMUser("alice", "correct-horse-battery", "fingerprint-xyz")
    user.register(rc)

    # First authentication succeeds
    m1, _ = user.start_authentication()
    m2, _, reason = cs.process_authentication(rc, m1)
    assert m2 is not None, f"First auth should succeed: {reason}"

    # Replay the same M1 — should fail due to used nonce
    m2_replay, _, reason_replay = cs.process_authentication(rc, m1)
    assert m2_replay is None, "Replayed M1 with used nonce should be rejected"
    assert "nonce" in reason_replay.lower()


# ---------------------------------------------------------------------------
# run_protocol() integration test
# ---------------------------------------------------------------------------

def test_mlkem_run_protocol_success():
    """run_protocol() should return status=success with all required fields."""
    from cryptomaka.protocols.ml_kem import run_protocol
    result = run_protocol()

    assert result["status"] == "success"
    assert result["authentication_success"] is True
    assert result["session_key_match"] is True
    assert result["message_count"] == 4
    assert len(result["messages"]) == 4
    assert result["communication_bits"] > 0
    assert "timings" in result
    assert result["timings"]["total_ms"] >= 0


def test_mlkem_run_protocol_notes_disclaimer():
    """run_protocol() notes should contain the post-quantum prototype disclaimer."""
    from cryptomaka.protocols.ml_kem import run_protocol
    result = run_protocol()
    notes_text = " ".join(result.get("notes", []))
    assert "PROTOTYPE" in notes_text or "prototype" in notes_text.lower(), (
        "Expected post-quantum disclaimer in notes"
    )
    assert "FIPS 203" in notes_text or "fips" in notes_text.lower()


def test_mlkem_communication_bits_fips203_sizes():
    """Communication cost should reflect ML-KEM-768 wire sizes (PK=1184B, CT=1088B)."""
    from cryptomaka.protocols.ml_kem import (
        MLKEM_PUBLIC_KEY_BYTES, MLKEM_CIPHERTEXT_BYTES, run_protocol
    )
    result = run_protocol()
    # Minimum lower bound: 2 messages containing ciphertext (1088*8 bits each)
    # plus public key in M1 (1184*8 bits)
    min_expected = MLKEM_CIPHERTEXT_BYTES * 8 * 2
    assert result["communication_bits"] >= min_expected, (
        f"communication_bits {result['communication_bits']} is below "
        f"minimum expected {min_expected} for ML-KEM-768"
    )
