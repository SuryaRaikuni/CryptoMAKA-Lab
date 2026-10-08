"""
Informal security analysis for the MAKA skeleton (maka_skeleton.py).

Runs three attacker scenarios against the login/key-agreement phase and
checks that each is rejected. This is the code-side companion to the
BAN-logic / Real-or-Random proof in Ju & Park (Sensors 2023, 23:9766) --
those are pen-and-paper arguments and this script can't replace them, but
it gives you concrete pass/fail evidence to cite (or screenshot) in the
project's security-analysis section, and a harness to extend if you add
more attack scenarios.
"""

import time
import os
import sys

# Add the project's src directory to Python's import path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from maka_skeleton import ControlServer, CloudServer, User, H, nonce


def fresh_setup():
    rc = ControlServer()
    cs = CloudServer("cloud-server-1", rc.register_cloud_server("cloud-server-1"))
    alice = User("alice", "correct-horse-battery", "fingerprint-template-xyz")
    alice.register(rc)
    return rc, cs, alice


def legit_baseline():
    rc, cs, alice = fresh_setup()
    m1, Ai = alice.start_login()
    m2, sk_server, reason = cs.respond_to_login(rc, alice.id, m1["Ni"], m1["T1"], m1["Vi"])
    ok = sk_server is not None
    print(f"[baseline]        legit login accepted: {ok}  ({reason})")
    assert ok, "baseline login should succeed"


def test_replay_immediate():
    """Eve captures a valid M1 and replays it right away."""
    rc, cs, alice = fresh_setup()
    m1, Ai = alice.start_login()
    cs.respond_to_login(rc, alice.id, m1["Ni"], m1["T1"], m1["Vi"])          # legit run consumes the nonce
    _, sk_replay, reason = cs.respond_to_login(rc, alice.id, m1["Ni"], m1["T1"], m1["Vi"])
    blocked = sk_replay is None
    print(f"[replay-immediate] attack blocked: {blocked}  ({reason})")
    assert blocked, "immediate replay should be rejected (nonce reuse)"


def test_replay_delayed():
    """Eve captures a valid M1 and replays it after the freshness window."""
    rc, cs, alice = fresh_setup()
    m1, Ai = alice.start_login()
    stale_T1 = str(int(m1["T1"]) - 60)   # 60s old, window is 30s
    _, sk_replay, reason = cs.respond_to_login(rc, alice.id, m1["Ni"], stale_T1, m1["Vi"])
    blocked = sk_replay is None
    print(f"[replay-delayed]  attack blocked: {blocked}  ({reason})")
    assert blocked, "delayed replay should be rejected (stale timestamp)"


def test_tampering():
    """Eve intercepts M1 and flips part of the authenticator in transit."""
    rc, cs, alice = fresh_setup()
    m1, Ai = alice.start_login()
    tampered_Vi = m1["Vi"][:-1] + ("0" if m1["Vi"][-1] != "0" else "1")
    _, sk_tampered, reason = cs.respond_to_login(rc, alice.id, m1["Ni"], m1["T1"], tampered_Vi)
    blocked = sk_tampered is None
    print(f"[tampering/MITM]  attack blocked: {blocked}  ({reason})")
    assert blocked, "a tampered authenticator should be rejected"


def test_impersonation():
    """Eve has no smart card / no valid Ai and tries to forge a login
    from scratch for a user she doesn't control."""
    rc, cs, alice = fresh_setup()
    forged_Ni = nonce()
    forged_T1 = str(int(time.time()))
    guessed_Ai = H("eve-guessed-this")           # Eve does not know the real Ai
    forged_Vi = H(alice.id, guessed_Ai, forged_Ni, forged_T1)
    _, sk_forged, reason = cs.respond_to_login(rc, alice.id, forged_Ni, forged_T1, forged_Vi)
    blocked = sk_forged is None
    print(f"[impersonation]   attack blocked: {blocked}  ({reason})")
    assert blocked, "a forged login without the real Ai should be rejected"


if __name__ == "__main__":
    legit_baseline()
    test_replay_immediate()
    test_replay_delayed()
    test_tampering()
    test_impersonation()
    print("\nAll checks passed: baseline works, all three attacks blocked.")
