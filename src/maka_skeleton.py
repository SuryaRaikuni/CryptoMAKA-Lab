"""
Skeleton for a lightweight XOR+hash mutual authentication and key
agreement (MAKA) scheme, following the standard 3-party structure used
by this class of paper: Ju, S.; Park, Y. "Provably Secure Lightweight
Mutual Authentication and Key Agreement Scheme for Cloud-Based IoT
Environments." Sensors 2023, 23, 9766.

This models the GENERIC structure common to XOR+hash MAKA schemes
(registration -> login -> mutual auth + key agreement via masked
identities and nonces). It is NOT copied from the paper's exact
formulas -- swap in the paper's precise definitions for Ai/Bi/Vi and
the session-key derivation once you have the PDF open. The phases and
message flow will stay the same; only the hash inputs change.
"""

import hashlib
import os
import time


def H(*args) -> str:
    """One-way hash function h(.) -> hex digest."""
    data = "||".join(str(a) for a in args).encode()
    return hashlib.sha256(data).hexdigest()


def xor_hex(a: str, b: str) -> str:
    """XOR two hex strings, hex in/out (pads to the longer length)."""
    length = max(len(a), len(b))
    return format(int(a, 16) ^ int(b, 16), f"0{length}x")


def nonce() -> str:
    return os.urandom(16).hex()


# ---------------------------------------------------------------------
# Control / Registration Server (RC) - trusted third party
# ---------------------------------------------------------------------
class ControlServer:
    def __init__(self):
        self.master_key = os.urandom(32).hex()   # x
        self.registered_servers = {}              # CSid -> Kcs
        self.used_nonces = set()                   # replay defense

    def register_user(self, user_id: str, rpw: str):
        """RC-side of user registration. Returns smart-card contents."""
        Ai = H(user_id, self.master_key)
        Bi = xor_hex(Ai, rpw)
        return {"Bi": Bi}

    def register_cloud_server(self, cs_id: str):
        Kcs = H(cs_id, self.master_key)
        self.registered_servers[cs_id] = Kcs
        return Kcs

    def verify_login(self, user_id, Ni, T1, Vi, freshness_window=30):
        """RC-assisted check: recompute Ai from the master key and verify
        the authenticator, timestamp freshness, and nonce reuse. Returns
        (ok, Ai_or_None, reason)."""
        now = int(time.time())
        if abs(now - int(T1)) > freshness_window:
            return False, None, "stale timestamp (possible replay)"
        if Ni in self.used_nonces:
            return False, None, "nonce already used (replay)"
        Ai = H(user_id, self.master_key)
        expected_Vi = H(user_id, Ai, Ni, T1)
        if Vi != expected_Vi:
            return False, None, "authenticator mismatch (tampering/impersonation)"
        self.used_nonces.add(Ni)
        return True, Ai, "ok"


# ---------------------------------------------------------------------
# User
# ---------------------------------------------------------------------
class User:
    def __init__(self, user_id: str, password: str, biometric: str):
        self.id = user_id
        self.pw = password
        self.bio = biometric   # placeholder input to a fuzzy extractor
        self.smart_card = None

    def _sigma(self) -> str:
        # TODO: replace with a real fuzzy extractor Gen(BIOi) -> (sigma_i, tau_i)
        return H(self.bio)

    def rpw(self) -> str:
        return H(self.pw, self._sigma())

    def register(self, rc: ControlServer):
        self.smart_card = rc.register_user(self.id, self.rpw())

    def start_login(self):
        """Phase 2: build login request M1."""
        Ai = xor_hex(self.smart_card["Bi"], self.rpw())
        Ni = nonce()
        T1 = str(int(time.time()))
        # TODO: replace Vi with the paper's exact authenticator / DIDi formula
        Vi = H(self.id, Ai, Ni, T1)
        return {"Vi": Vi, "Ni": Ni, "T1": T1}, Ai

    def derive_session_key(self, Ai, Ni, Nc):
        return H(self.id, Ni, Nc, Ai)


# ---------------------------------------------------------------------
# Cloud Server
# ---------------------------------------------------------------------
class CloudServer:
    def __init__(self, cs_id: str, shared_key: str):
        self.id = cs_id
        self.Kcs = shared_key

    def respond_to_login(self, rc: ControlServer, user_id, Ni, T1, Vi):
        """Phase 3: forward to RC for verification (RC-assisted, since only
        RC can recompute Ai), then pick a nonce and derive the session key."""
        ok, Ai, reason = rc.verify_login(user_id, Ni, T1, Vi)
        if not ok:
            return None, None, reason
        Nc = nonce()
        T2 = str(int(time.time()))
        SK = H(user_id, Ni, Nc, Ai)
        # TODO: replace with the paper's exact response authenticator
        return {"Nc": Nc, "T2": T2}, SK, "ok"


# ---------------------------------------------------------------------
# Demo run
# ---------------------------------------------------------------------
if __name__ == "__main__":
    rc = ControlServer()
    cs_shared_key = rc.register_cloud_server("cloud-server-1")
    cs = CloudServer("cloud-server-1", cs_shared_key)

    alice = User("alice", "correct-horse-battery", "fingerprint-template-xyz")
    alice.register(rc)

    m1, Ai = alice.start_login()
    m2, sk_server, reason = cs.respond_to_login(rc, alice.id, m1["Ni"], m1["T1"], m1["Vi"])
    sk_user = alice.derive_session_key(Ai, m1["Ni"], m2["Nc"])

    print("User session key:  ", sk_user)
    print("Server session key:", sk_server)
    print("Match:", sk_user == sk_server)
