"""Unit tests for the ECC/ECDH counterpart protocol."""

from __future__ import annotations

import pytest


def test_ecc_registration():
    """User registration with the ECC control server should succeed."""
    from cryptomaka.protocols.ecc import ControlServerECC, ECCUser
    rc = ControlServerECC()
    user = ECCUser("alice", "password123", "bio-template")
    user.register(rc)
    assert user.smart_card is not None


def test_ecc_full_authentication():
    """Full ECC/ECDH authentication should succeed with matching session keys."""
    from cryptomaka.protocols.ecc import ControlServerECC, ECCCloudServer, ECCUser
    rc = ControlServerECC()
    cs = ECCCloudServer("cloud-1")
    user = ECCUser("alice", "password123", "bio-template")
    user.register(rc)

    m1, a, private_u = user.start_login()
    m2, sk_server, _, reason = cs.respond_to_login(rc, user.user_id, m1)

    assert m2 is not None, f"Login rejected: {reason}"
    assert sk_server is not None

    sk_user, user_reason = user.finish_login(a, private_u, m1, m2)

    assert sk_user is not None, f"User key derivation failed: {user_reason}"
    assert sk_user == sk_server, "Session keys do not match!"


def test_ecc_tampered_authenticator():
    """A tampered Vi should be rejected by the control server."""
    from cryptomaka.protocols.ecc import ControlServerECC, ECCCloudServer, ECCUser
    rc = ControlServerECC()
    cs = ECCCloudServer("cloud-1")
    user = ECCUser("alice", "password123", "bio-template")
    user.register(rc)

    m1, a, private_u = user.start_login()
    # Tamper Vi
    original_vi = m1["Vi"]
    tampered_m1 = {**m1, "Vi": original_vi[:-1] + ("0" if original_vi[-1] != "0" else "1")}

    m2, sk_server, _, reason = cs.respond_to_login(rc, user.user_id, tampered_m1)
    assert m2 is None, "Tampered authenticator should be rejected"


def test_ecc_public_key_serialization():
    """Public key round-trip serialization should be consistent."""
    from cryptomaka.protocols.ecc import public_key_hex, load_public_key
    from cryptography.hazmat.primitives.asymmetric import ec
    private = ec.generate_private_key(ec.SECP256R1())
    pub_hex = public_key_hex(private)
    recovered = load_public_key(pub_hex)
    assert recovered is not None


def test_ecc_session_key_length():
    """Derived session keys should be 32 bytes (256 bits)."""
    from cryptomaka.protocols.ecc import ControlServerECC, ECCCloudServer, ECCUser
    rc = ControlServerECC()
    cs = ECCCloudServer("cloud-1")
    user = ECCUser("alice", "pw", "bio")
    user.register(rc)

    m1, a, private_u = user.start_login()
    m2, sk_server, _, _ = cs.respond_to_login(rc, user.user_id, m1)
    sk_user, _ = user.finish_login(a, private_u, m1, m2)

    assert sk_user is not None
    assert len(sk_user) == 32
