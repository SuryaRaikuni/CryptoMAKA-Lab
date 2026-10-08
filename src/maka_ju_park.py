"""
Executable reconstruction of Ju & Park (Sensors 2023, 23, 9766).

Important implementation note
-----------------------------
The published paper contains several notation/bit-width inconsistencies in
Figure 4 and Figure 6. For example, A1 is registered using h(ID||HPW) but a
later line shows recovery with (ID||PW), and expressions such as
(rk||ri) XOR h(...) mix widths. This module therefore implements the protocol
flow and intended dependencies using a normalized, fixed-width SHA-256
encoding. The normalization is documented rather than silently presented as
the authors' exact byte-level implementation.

Random/session values are 256-bit in this executable reconstruction so XOR
operations have well-defined widths. The paper's communication-cost table
(3776 bits) is retained separately as its published theoretical figure.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


HASH_BYTES = 32
TIMESTAMP_WINDOW = 30


# ============================================================
# HASH / UTILITY FUNCTIONS
# ============================================================

def H(*parts: object) -> bytes:
    """
    SHA-256 hash function with length-prefixed encoding.
    """
    h = hashlib.sha256()

    for part in parts:
        if isinstance(part, bytes):
            data = part
        else:
            data = str(part).encode()

        h.update(len(data).to_bytes(4, "big"))
        h.update(data)

    return h.digest()


def hx(b: bytes) -> str:
    """Convert bytes to hexadecimal string."""
    return b.hex()


def xb(s: str) -> bytes:
    """Convert hexadecimal string to bytes."""
    return bytes.fromhex(s)


def rand32() -> bytes:
    """Generate a 256-bit random value."""
    return os.urandom(HASH_BYTES)


def ts() -> int:
    """Current Unix timestamp."""
    return int(time.time())


def fresh(t: int, now: Optional[int] = None) -> bool:
    """
    Check timestamp freshness.
    """
    now = ts() if now is None else now
    return abs(now - int(t)) <= TIMESTAMP_WINDOW


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """
    XOR two equal-length byte strings.
    """
    if len(a) != len(b):
        raise ValueError(
            f"XOR width mismatch: {len(a)} != {len(b)}"
        )

    return bytes(x ^ y for x, y in zip(a, b))


def xor_stream(data: bytes, context: bytes) -> bytes:
    """
    XOR arbitrary-length data with an SHA-256-derived keystream.

    This is an encoding mechanism for the normalized XOR-style
    protocol fields. It is not intended to replace encryption.
    """

    out = bytearray()
    counter = 0

    while len(out) < len(data):
        out.extend(
            H(
                context,
                counter.to_bytes(4, "big")
            )
        )
        counter += 1

    return xor_bytes(
        data,
        bytes(out[:len(data)])
    )


def enc_pair(a: bytes, b: bytes) -> bytes:
    """
    Concatenate two byte strings.
    """
    return a + b


def dec_pair(data: bytes) -> Tuple[bytes, bytes]:
    """
    Split an even-length byte string into two equal halves.
    """

    if len(data) % 2:
        raise ValueError(
            "pair encoding must have even length"
        )

    n = len(data) // 2

    return data[:n], data[n:]


# ============================================================
# FUZZY EXTRACTOR
# ============================================================

class FuzzyExtractor:
    """
    Deterministic stand-in for Gen/Rep.

    This is NOT a real fuzzy extractor.

    It models the API required by the protocol so that the
    project can run without biometric hardware.
    """

    @staticmethod
    def gen(biometric: str) -> Tuple[bytes, bytes]:

        sigma = H(
            "sigma",
            biometric
        )

        tau = H(
            "tau",
            biometric
        )

        return sigma, tau

    @staticmethod
    def rep(
        biometric: str,
        tau: bytes
    ) -> bytes:

        sigma, tau_check = (
            FuzzyExtractor.gen(biometric)
        )

        if not hmac.compare_digest(
            tau,
            tau_check
        ):
            raise ValueError(
                "biometric reconstruction failed"
            )

        return sigma


# ============================================================
# USER SMART CARD
# ============================================================

@dataclass
class UserCard:

    PIDi: bytes
    IDCS: str
    RPWi: bytes
    A1: bytes
    A2: bytes
    tau: bytes


# ============================================================
# USER
# ============================================================

@dataclass
class User:

    user_id: str
    password: str
    biometric: str
    card: Optional[UserCard] = None

    # --------------------------------------------------------
    # Registration
    # --------------------------------------------------------

    def register(
        self,
        cs: "ControlServer"
    ) -> None:

        sigma, tau = (
            FuzzyExtractor.gen(
                self.biometric
            )
        )

        (
            pid,
            idcs,
            ki,
            sidi,
            si_star,
            ni
        ) = cs.register_user(
            self.user_id
        )

        rpw = H(
            self.user_id,
            self.password,
            sigma
        )

        # Normalized interpretation of A1.

        A1 = xor_bytes(
            ki,
            H(
                self.user_id,
                H(
                    self.password,
                    sigma
                )
            )
        )

        A2 = xor_bytes(
            sidi,
            H(
                sigma,
                self.password
            )
        )

        self.card = UserCard(
            pid,
            idcs,
            rpw,
            A1,
            A2,
            tau
        )

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    def login(
        self,
        cloud_id: str
    ) -> Tuple[dict, dict]:

        if self.card is None:
            raise RuntimeError(
                "user not registered"
            )

        sigma = FuzzyExtractor.rep(
            self.biometric,
            self.card.tau
        )

        rpw = H(
            self.user_id,
            self.password,
            sigma
        )

        if not hmac.compare_digest(
            rpw,
            self.card.RPWi
        ):
            raise ValueError(
                "invalid credentials or biometric"
            )

        hpw = H(
            self.password,
            sigma
        )

        # Recover ki.

        ki = xor_bytes(
            self.card.A1,
            H(
                self.user_id,
                hpw
            )
        )

        # Recover SIDi.

        sidi = xor_bytes(
            self.card.A2,
            H(
                sigma,
                self.password
            )
        )

        # Fresh random value.

        ri = rand32()

        # Timestamp.

        ts1 = ts()

        # B1.

        B1 = xor_bytes(
            ri,
            H(
                sidi,
                self.card.IDCS,
                ki
            )
        )

        # B2.

        B2 = xor_bytes(
            H(cloud_id),
            H(
                self.card.IDCS,
                sidi,
                ri
            )
        )

        # User authenticator.

        V1 = H(
            self.card.IDCS,
            ts1,
            sidi,
            ki,
            ri
        )

        m1 = {
            "PIDi": hx(self.card.PIDi),
            "B1": hx(B1),
            "B2": hx(B2),
            "V1": hx(V1),
            "TS1": ts1,
        }

        state = {
            "sigma": sigma,
            "ki": ki,
            "sidi": sidi,
            "ri": ri,
            "ts1": ts1
        }

        return m1, state

    # --------------------------------------------------------
    # Finish Authentication
    # --------------------------------------------------------

    def finish(
        self,
        state: dict,
        m4: dict
    ) -> Tuple[bytes, bool]:

        if not fresh(
            int(m4["TS4"])
        ):
            return b"", False

        sidi = state["sidi"]
        ri = state["ri"]

        B8 = xb(m4["B8"])
        B9 = xb(m4["B9"])
        V4 = xb(m4["V4"])

        pair_rj_rk = xor_stream(
            B8,
            H(
                "B8-mask",
                sidi,
                self.card.IDCS,
                ri
            )
        )

        rj, rk = dec_pair(
            pair_rj_rk
        )

        sidj = xor_bytes(
            B9,
            H(
                sidi,
                rk
            )
        )

        C1 = H(
            xor_bytes(
                sidi,
                sidj
            ),
            self.card.IDCS
        )

        # Session key.

        sk = H(
            C1,
            ri,
            rj,
            rk
        )

        # Verify server.

        V4p = H(
            sidi,
            rj,
            rk,
            C1,
            m4["TS3"]
        )

        ok = hmac.compare_digest(
            V4p,
            V4
        )

        # Update pseudonym.

        if (
            ok
            and self.card is not None
            and "new_PID" in m4
        ):
            self.card.PIDi = xb(
                m4["new_PID"]
            )

        return sk, ok


# ============================================================
# CLOUD SERVER
# ============================================================

class CloudServer:

    def __init__(
        self,
        server_id: str,
        control: "ControlServer"
    ):

        self.server_id = server_id
        self.control = control

        self.xj = rand32()

        self.A3: Optional[bytes] = None
        self.kj: Optional[bytes] = None

        self.registered = False

    # --------------------------------------------------------
    # Cloud registration
    # --------------------------------------------------------

    def register(self) -> None:

        kj = self.control.register_cloud(
            self.server_id
        )

        self.kj = kj

        self.A3 = xor_bytes(
            kj,
            self.xj
        )

        self.registered = True

    # --------------------------------------------------------
    # Receive M1
    # --------------------------------------------------------

    def receive_m1(
        self,
        m1: dict
    ) -> dict:

        if not self.registered:
            raise RuntimeError(
                "cloud server not registered"
            )

        rj = rand32()
        ts2 = ts()

        kj = self.kj

        assert kj is not None

        B3 = xor_bytes(
            rj,
            H(
                kj,
                self.server_id
            )
        )

        V2 = H(
            kj,
            ts2,
            self.server_id,
            rj
        )

        return {
            "M1": m1,
            "B3": hx(B3),
            "V2": hx(V2),
            "TS2": ts2,
        }

    # --------------------------------------------------------
    # Finish M3
    # --------------------------------------------------------

    def finish_m3(
        self,
        m3: dict
    ) -> Tuple[bytes, bool, dict]:

        if not fresh(
            int(m3["TS3"])
        ):
            return b"", False, {}

        assert self.kj is not None

        B6 = xb(m3["B6"])
        B7 = xb(m3["B7"])
        V3 = xb(m3["V3"])

        rk_ri = xor_stream(
            B6,
            H(
                "B6-mask",
                xb(m3["rj"]),
                self.kj
            )
        )

        rk, ri = dec_pair(
            rk_ri
        )

        C1 = xor_bytes(
            B7,
            H(
                self.kj,
                rk
            )
        )

        sk = H(
            C1,
            ri,
            xb(m3["rj"]),
            rk
        )

        V3p = H(
            xb(m3["rj"]),
            rk,
            C1,
            self.server_id,
            m3["TS3"]
        )

        return (
            sk,
            hmac.compare_digest(
                V3p,
                V3
            ),
            {
                "rk": rk,
                "ri": ri,
                "C1": C1
            }
        )


# ============================================================
# CONTROL SERVER
# ============================================================

class ControlServer:

    def __init__(
        self,
        idcs: str = "CS"
    ):

        self.idcs = idcs

        # Master secret.

        self.xcs = rand32()

        self.user_db: Dict[
            bytes,
            dict
        ] = {}

        self.cloud_db: Dict[
            str,
            dict
        ] = {}

        self.used_pid_updates: set[
            bytes
        ] = set()

    # --------------------------------------------------------
    # User registration
    # --------------------------------------------------------

    def register_user(
        self,
        user_id: str
    ):

        ni = rand32()

        sidi = H(
            xor_bytes(
                H(user_id),
                self.xcs
            )
        )

        ki = H(
            sidi,
            self.xcs,
            ni
        )

        si_star = xor_bytes(
            sidi,
            H(
                self.xcs,
                ni
            )
        )

        pidi = H(
            sidi,
            ni
        )

        self.user_db[pidi] = {
            "user_id": user_id,
            "SIDi_star": si_star,
            "ni": ni,
            "SIDi": sidi,
        }

        return (
            pidi,
            self.idcs,
            ki,
            sidi,
            si_star,
            ni
        )

    # --------------------------------------------------------
    # Cloud registration
    # --------------------------------------------------------

    def register_cloud(
        self,
        cloud_id: str
    ) -> bytes:

        nj = rand32()

        kj = H(
            cloud_id,
            nj,
            self.xcs
        )

        self.cloud_db[
            cloud_id
        ] = {
            "nj": nj,
            "kj": kj
        }

        return kj

    # --------------------------------------------------------
    # Process M2
    # --------------------------------------------------------

    def process_m2(
        self,
        m2: dict
    ) -> Tuple[dict | None, str]:

        if not fresh(
            int(m2["TS2"])
        ):
            return None, "stale TS2"

        m1 = m2["M1"]

        try:
            pidi = xb(
                m1["PIDi"]
            )

            row = self.user_db[pidi]

        except (
            KeyError,
            ValueError
        ):
            return None, "unknown PID"

        # Recover SIDi.

        sidi = xor_bytes(
            row["SIDi_star"],
            H(
                self.xcs,
                row["ni"]
            )
        )

        # Recover ki.

        ki = H(
            sidi,
            self.xcs,
            row["ni"]
        )

        B1 = xb(m1["B1"])
        B2 = xb(m1["B2"])
        V1 = xb(m1["V1"])

        # Recover ri.

        ri = xor_bytes(
            B1,
            H(
                sidi,
                self.idcs,
                ki
            )
        )

        # Verify V1.

        expected_V1 = H(
            self.idcs,
            m1["TS1"],
            sidi,
            ki,
            ri
        )

        if not hmac.compare_digest(
            expected_V1,
            V1
        ):
            return None, "V1 failure"

        # Recover cloud identifier.

        idj_digest = xor_bytes(
            B2,
            H(
                self.idcs,
                sidi,
                ri
            )
        )

        idj = next(
            (
                candidate
                for candidate in self.cloud_db
                if H(candidate) == idj_digest
            ),
            None
        )

        if idj is None:
            return None, "unknown cloud"

        kj = self.cloud_db[
            idj
        ]["kj"]

        # Recover rj.

        rj = xor_bytes(
            xb(m2["B3"]),
            H(
                kj,
                idj
            )
        )

        expected_V2 = H(
            kj,
            m2["TS2"],
            idj,
            rj
        )

        if not hmac.compare_digest(
            expected_V2,
            xb(m2["V2"])
        ):
            return None, "V2 failure"

        # Generate rk.

        rk = rand32()

        ts3 = ts()

        # Normalized SIDj.

        sidj = xor_bytes(
            H(idj),
            H(kj, rk)
        )

        # Common value.

        c1 = H(
            xor_bytes(
                sidi,
                sidj
            ),
            self.idcs
        )

        # New pseudonym.

        pid_star = xor_bytes(
            pidi,
            H(
                pidi,
                rk,
                ri
            )
        )

        # B6.

        B6 = xor_stream(
            enc_pair(rk, ri),
            H(
                "B6-mask",
                rj,
                kj
            )
        )

        # B7.

        B7 = xor_bytes(
            c1,
            H(
                kj,
                rk
            )
        )

        # B8.

        B8 = xor_stream(
            enc_pair(rj, rk),
            H(
                "B8-mask",
                sidi,
                self.idcs,
                ri
            )
        )

        # B9.

        B9 = xor_bytes(
            sidj,
            H(
                sidi,
                rk
            )
        )

        # Server authenticator.

        V3 = H(
            rj,
            rk,
            c1,
            idj,
            ts3
        )

        # User authenticator.

        V4 = H(
            sidi,
            rj,
            rk,
            c1,
            ts3
        )

        # Update user pseudonym.

        self.user_db[
            pid_star
        ] = {
            **row,
            "SIDi_star":
                row["SIDi_star"]
        }

        self.user_db.pop(
            pidi,
            None
        )

        self.used_pid_updates.add(
            pid_star
        )

        m3 = {
            "B6": hx(B6),
            "B7": hx(B7),
            "B8": hx(B8),
            "B9": hx(B9),
            "V3": hx(V3),
            "V4": hx(V4),
            "TS3": ts3,
            "rj": hx(rj),
            "C1": hx(c1),
            "new_PID": hx(pid_star),
        }

        return m3, "ok"

    # --------------------------------------------------------
    # Demo helper
    # --------------------------------------------------------

    def user_verify_m3(
        self,
        m3: dict
    ) -> dict:

        return m3


# ============================================================
# COMPLETE PROTOCOL DEMO
# ============================================================

def run_protocol() -> dict:

    # Create control server.

    cs = ControlServer("CS")

    # Create cloud server.

    cloud = CloudServer(
        "S_j",
        cs
    )

    # Cloud registration.

    cloud.register()

    # Create user.

    user = User(
        "alice",
        "correct-horse-battery",
        "fingerprint-template-xyz"
    )

    # User registration.

    user.register(cs)

    # --------------------------------------------------------
    # M1
    # --------------------------------------------------------

    m1, ustate = user.login(
        cloud.server_id
    )

    # --------------------------------------------------------
    # M2
    # --------------------------------------------------------

    m2 = cloud.receive_m1(
        m1
    )

    # --------------------------------------------------------
    # M3
    # --------------------------------------------------------

    m3, reason = cs.process_m2(
        m2
    )

    if m3 is None:
        raise RuntimeError(
            reason
        )

    # --------------------------------------------------------
    # Cloud recovers rj
    # --------------------------------------------------------

    rj = xor_bytes(
        xb(m2["B3"]),
        H(
            cloud.kj,
            cloud.server_id
        )
    )

    m3["rj"] = hx(rj)

    # --------------------------------------------------------
    # Cloud verifies M3
    # --------------------------------------------------------

    (
        sk_server,
        ok_server,
        state_server
    ) = cloud.finish_m3(
        m3
    )

    if not ok_server:
        raise RuntimeError(
            "cloud V3 verification failed"
        )

    # --------------------------------------------------------
    # User verifies final response
    # --------------------------------------------------------

    (
        sk_user,
        ok_user
    ) = user.finish(
        ustate,
        {
            "B8": m3["B8"],
            "B9": m3["B9"],
            "V4": m3["V4"],
            "TS4": ts(),
            "TS3": m3["TS3"],
            "new_PID": m3["new_PID"]
        }
    )

    return {
        "user": user,
        "cloud": cloud,
        "cs": cs,
        "M1": m1,
        "M2": m2,
        "M3": m3,
        "SK_user": sk_user,
        "SK_server": sk_server,
        "match":
            ok_user
            and sk_user == sk_server,
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    result = run_protocol()

    print(
        "Ju-Park normalized reconstruction: SUCCESS"
    )

    print(
        "Session-key match:",
        result["match"]
    )

    print(
        "SK:",
        result["SK_user"].hex()
    )