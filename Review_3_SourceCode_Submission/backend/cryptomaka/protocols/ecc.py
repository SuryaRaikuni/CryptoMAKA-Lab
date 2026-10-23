"""
Authenticated ECDH counterpart for the lightweight MAKA baseline.

Design goal:
Keep the same general 3-party shape as the generic MAKA prototype
while replacing the session-secret construction with ephemeral
P-256 ECDH + HKDF.

This is an experimental counterpart,
NOT a reproduction of the Ju-Park paper.
"""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# ============================================================
# ECC PARAMETERS
# ============================================================

CURVE = ec.SECP256R1()

HASH_BITS = 256
NONCE_BITS = 128
TIMESTAMP_BITS = 32

# P-256 uncompressed public key:
#
# 1 byte prefix
# + 32 bytes X
# + 32 bytes Y
#
# = 65 bytes = 520 bits

EC_PUBLIC_KEY_BITS = 65 * 8


# ============================================================
# HASH
# ============================================================

def H(*args: object) -> str:

    data = b"||".join(
        str(a).encode()
        for a in args
    )

    return hashlib.sha256(
        data
    ).hexdigest()


# ============================================================
# NONCE
# ============================================================

def nonce() -> str:

    return os.urandom(
        16
    ).hex()


# ============================================================
# PUBLIC KEY SERIALIZATION
# ============================================================

def public_key_hex(
    private_key: ec.EllipticCurvePrivateKey
) -> str:

    public = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )

    return public.hex()


# ============================================================
# LOAD PUBLIC KEY
# ============================================================

def load_public_key(
    pub_hex: str
) -> ec.EllipticCurvePublicKey:

    return ec.EllipticCurvePublicKey.from_encoded_point(
        CURVE,
        bytes.fromhex(pub_hex)
    )


# ============================================================
# SESSION KEY DERIVATION
# ============================================================

def derive_session_key(
    shared_secret: bytes,
    transcript: bytes
) -> bytes:

    """
    Derive the final session key from ECDH shared secret.

    HKDF-SHA256 provides key separation and binds the derived
    key to the protocol transcript.
    """

    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"MAKA-ECDH-v1|" + transcript,
    ).derive(
        shared_secret
    )


# ============================================================
# TIMESTAMP
# ============================================================

def _normalize_ts(
    timestamp: str
) -> int:

    return int(timestamp)


# ============================================================
# CONTROL SERVER
# ============================================================

class ControlServerECC:
    """
    Trusted registration and verification server.
    """

    def __init__(self) -> None:

        # Master secret.

        self.master_key = (
            os.urandom(32).hex()
        )

        # Used nonces prevent replay.

        self.used_nonces: set[str] = set()

    # --------------------------------------------------------
    # USER REGISTRATION
    # --------------------------------------------------------

    def register_user(
        self,
        user_id: str,
        rpw: str
    ) -> dict[str, str]:

        # Long-term user secret.

        a = H(
            user_id,
            self.master_key
        )

        # Mask A with password-derived value.

        b = format(
            int(a, 16)
            ^
            int(rpw, 16),
            "064x"
        )

        return {
            "Bi": b
        }

    # --------------------------------------------------------
    # LOGIN VERIFICATION
    # --------------------------------------------------------

    def verify_login(
        self,
        user_id: str,
        pu: str,
        ni: str,
        t1: str,
        vi: str,
        freshness_window: int = 30,
    ) -> tuple[
        bool,
        str | None,
        str
    ]:

        # Check timestamp.

        try:

            if (
                abs(
                    int(time.time())
                    -
                    _normalize_ts(t1)
                )
                >
                freshness_window
            ):

                return (
                    False,
                    None,
                    "stale timestamp"
                )

        except (
            TypeError,
            ValueError
        ):

            return (
                False,
                None,
                "invalid timestamp"
            )

        # Check nonce reuse.

        if ni in self.used_nonces:

            return (
                False,
                None,
                "nonce already used"
            )

        # Recreate long-term secret.

        a = H(
            user_id,
            self.master_key
        )

        # Expected authenticator.

        expected = H(
            user_id,
            a,
            pu,
            ni,
            t1
        )

        # Authentication check.

        if vi != expected:

            return (
                False,
                None,
                "user authenticator mismatch"
            )

        # Consume nonce.

        self.used_nonces.add(
            ni
        )

        return (
            True,
            a,
            "ok"
        )


# ============================================================
# USER
# ============================================================

@dataclass
class ECCUser:

    user_id: str
    password: str
    biometric: str

    def __post_init__(
        self
    ) -> None:

        self.smart_card: (
            dict[str, str] | None
        ) = None

    # --------------------------------------------------------
    # BIOMETRIC PLACEHOLDER
    # --------------------------------------------------------

    def _sigma(self) -> str:

        # Same simplified construction as the generic
        # prototype.

        return H(
            self.biometric
        )

    # --------------------------------------------------------
    # PASSWORD + BIOMETRIC
    # --------------------------------------------------------

    def rpw(self) -> str:

        return H(
            self.password,
            self._sigma()
        )

    # --------------------------------------------------------
    # REGISTRATION
    # --------------------------------------------------------

    def register(
        self,
        rc: ControlServerECC
    ) -> None:

        self.smart_card = (
            rc.register_user(
                self.user_id,
                self.rpw()
            )
        )

    # --------------------------------------------------------
    # RECOVER A
    # --------------------------------------------------------

    def recover_a(self) -> str:

        if self.smart_card is None:

            raise RuntimeError(
                "user is not registered"
            )

        return format(
            int(
                self.smart_card["Bi"],
                16
            )
            ^
            int(
                self.rpw(),
                16
            ),
            "064x"
        )

    # --------------------------------------------------------
    # START LOGIN
    # --------------------------------------------------------

    def start_login(
        self
    ) -> tuple[
        dict[str, str],
        str,
        ec.EllipticCurvePrivateKey
    ]:

        # Recover long-term authenticator.

        a = self.recover_a()

        # Generate ephemeral ECDH key pair.

        private_u = (
            ec.generate_private_key(
                CURVE
            )
        )

        # Serialize public key.

        pu = public_key_hex(
            private_u
        )

        # Fresh nonce.

        ni = nonce()

        # Timestamp.

        t1 = str(
            int(time.time())
        )

        # User authenticator.

        vi = H(
            self.user_id,
            a,
            pu,
            ni,
            t1
        )

        m1 = {

            "Vi": vi,

            "Pu": pu,

            "Ni": ni,

            "T1": t1,
        }

        return (
            m1,
            a,
            private_u
        )

    # --------------------------------------------------------
    # FINISH LOGIN
    # --------------------------------------------------------

    def finish_login(
        self,
        a: str,
        private_u: ec.EllipticCurvePrivateKey,
        m1: dict[str, str],
        m2: dict[str, str],
    ) -> tuple[
        bytes | None,
        str
    ]:

        # Verify server authenticator.

        expected = H(
            self.user_id,
            a,
            m1["Pu"],
            m1["Ni"],
            m1["T1"],
            m2["Pc"],
            m2["Nc"],
            m2["T2"],
        )

        if (
            m2["Vj"]
            != expected
        ):

            return (
                None,
                "server authenticator mismatch"
            )

        # Load cloud public key.

        peer = load_public_key(
            m2["Pc"]
        )

        # ECDH.

        shared = private_u.exchange(
            ec.ECDH(),
            peer
        )

        # Construct identical transcript.

        transcript = "||".join(
            [
                self.user_id,
                m1["Pu"],
                m1["Ni"],
                m1["T1"],
                m2["Pc"],
                m2["Nc"],
                m2["T2"],
            ]
        ).encode()

        # Derive final session key.

        return (
            derive_session_key(
                shared,
                transcript
            ),
            "ok"
        )


# ============================================================
# CLOUD SERVER
# ============================================================

class ECCCloudServer:

    def __init__(
        self,
        server_id: str
    ) -> None:

        self.id = server_id

    # --------------------------------------------------------
    # LOGIN RESPONSE
    # --------------------------------------------------------

    def respond_to_login(
        self,
        rc: ControlServerECC,
        user_id: str,
        m1: dict[str, str],
    ) -> tuple[
        dict[str, str] | None,
        bytes | None,
        ec.EllipticCurvePrivateKey | None,
        str
    ]:

        # RC verifies user.

        (
            ok,
            a,
            reason
        ) = rc.verify_login(
            user_id,
            m1["Pu"],
            m1["Ni"],
            m1["T1"],
            m1["Vi"]
        )

        if (
            not ok
            or a is None
        ):

            return (
                None,
                None,
                None,
                reason
            )

        # Validate client's ECC public key.

        try:

            load_public_key(
                m1["Pu"]
            )

        except ValueError:

            return (
                None,
                None,
                None,
                "invalid client public key"
            )

        # Generate ephemeral cloud key pair.

        private_c = (
            ec.generate_private_key(
                CURVE
            )
        )

        # Public key.

        pc = public_key_hex(
            private_c
        )

        # Fresh cloud nonce.

        nc = nonce()

        # Timestamp.

        t2 = str(
            int(time.time())
        )

        # Server authenticator.

        vj = H(
            user_id,
            a,
            m1["Pu"],
            m1["Ni"],
            m1["T1"],
            pc,
            nc,
            t2,
        )

        # Load user public key.

        peer = load_public_key(
            m1["Pu"]
        )

        # ECDH shared secret.

        shared = private_c.exchange(
            ec.ECDH(),
            peer
        )

        # Identical transcript.

        transcript = "||".join(
            [
                user_id,
                m1["Pu"],
                m1["Ni"],
                m1["T1"],
                pc,
                nc,
                t2,
            ]
        ).encode()

        # Derive session key.

        sk = derive_session_key(
            shared,
            transcript
        )

        m2 = {

            "Pc": pc,

            "Nc": nc,

            "T2": t2,

            "Vj": vj,
        }

        return (
            m2,
            sk,
            private_c,
            "ok"
        )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Setup
    # --------------------------------------------------------

    rc = ControlServerECC()

    cs = ECCCloudServer(
        "cloud-server-1"
    )

    alice = ECCUser(
        "alice",
        "correct-horse-battery",
        "fingerprint-template-xyz"
    )

    # --------------------------------------------------------
    # Registration
    # --------------------------------------------------------

    alice.register(
        rc
    )

    # --------------------------------------------------------
    # User login
    # --------------------------------------------------------

    (
        m1,
        a,
        user_private
    ) = alice.start_login()

    # --------------------------------------------------------
    # Cloud response
    # --------------------------------------------------------

    (
        m2,
        sk_server,
        _,
        reason
    ) = cs.respond_to_login(
        rc,
        alice.user_id,
        m1
    )

    if m2 is None:

        raise RuntimeError(
            reason
        )

    # --------------------------------------------------------
    # User verifies cloud and derives key
    # --------------------------------------------------------

    (
        sk_user,
        user_reason
    ) = alice.finish_login(
        a,
        user_private,
        m1,
        m2
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print(
        "ECDH exchange: OK"
    )

    print(
        "User key:  ",
        sk_user.hex()
        if sk_user
        else None
    )

    print(
        "Server key:",
        sk_server.hex()
        if sk_server
        else None
    )

    print(
        "Match:",
        sk_user == sk_server
    )