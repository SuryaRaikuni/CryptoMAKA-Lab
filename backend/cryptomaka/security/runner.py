"""
Security test runner for CryptoMAKA Lab.

Implements empirical attack simulations against the Ju-Park protocol.

IMPORTANT DISCLAIMER:
These are empirical simulations that verify expected protocol behavior.
They are NOT a substitute for formal security proofs (BAN logic, Real-or-Random
model, Scyther/ProVerif symbolic verification). "PASS" means the protocol
correctly rejected the simulated attack; it does not mean the protocol is
formally proven secure under that threat model.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

DISCLAIMER = (
    "These tests are empirical simulations. "
    "PASS means the protocol rejected the simulated attack. "
    "This is not a substitute for formal cryptographic proof."
)


@dataclass
class SecurityTestResult:
    test: str
    status: str  # "PASS" or "FAIL"
    description: str
    evidence: str
    severity: str  # "high", "medium", "low"
    duration_ms: float = 0.0


def _run_fresh_jupark():
    """Set up a fresh Ju-Park protocol instance and complete authentication."""
    # Import here to avoid circular imports
    from cryptomaka.protocols.ju_park import run_protocol
    return run_protocol()


# ---------------------------------------------------------------------------
# Test 1: Replay attack (immediate nonce reuse)
# ---------------------------------------------------------------------------

def test_replay_attack() -> SecurityTestResult:
    """
    Eve captures M1 before a legitimate session, lets the session complete,
    then replays the captured M1.

    The Ju-Park protocol uses pseudonym updates: after a successful authentication
    the original PIDi is consumed and replaced. A replayed M1 carrying the old
    PIDi is therefore rejected by the Control Server with "unknown PID",
    demonstrating the pseudonym-update mechanism also provides replay protection.
    """
    from cryptomaka.protocols.ju_park import CloudServer, ControlServer, User
    start = time.perf_counter()

    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()
    user = User("alice", "password123", "bio-template")
    user.register(cs)

    # Eve intercepts M1 (captured before the legitimate session runs)
    m1_captured, ustate = user.login(cloud.server_id)

    # ── Legitimate full protocol run (CS updates the PID) ──
    m2_legit = cloud.receive_m1(m1_captured)
    m3_legit, reason_legit = cs.process_m2(m2_legit)
    assert m3_legit is not None, f"Baseline failed: {reason_legit}"

    # ── Eve replays the captured M1 ──
    m2_replay = cloud.receive_m1(m1_captured)
    m3_replay, reason_replay = cs.process_m2(m2_replay)
    blocked = m3_replay is None

    elapsed = (time.perf_counter() - start) * 1000

    return SecurityTestResult(
        test="replay_attack",
        status="PASS" if blocked else "FAIL",
        description=(
            "Eve captures M1 before a session, waits for the session to complete, "
            "then replays M1. The pseudonym-update mechanism consumes the original "
            "PIDi, so the replayed M1 is rejected as 'unknown PID'."
        ),
        evidence=(
            f"CS rejected replay with: '{reason_replay}' — pseudonym update prevented reuse."
            if blocked
            else "Protocol accepted a replayed M1 — PID reuse not prevented."
        ),
        severity="high",
        duration_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# Test 2: Delayed replay / stale timestamp
# ---------------------------------------------------------------------------

def test_stale_timestamp() -> SecurityTestResult:
    """
    Eve replays a message after the timestamp freshness window has passed.
    """
    from cryptomaka.protocols.ju_park import (
        TIMESTAMP_WINDOW,
        CloudServer,
        ControlServer,
        User,
    )
    start = time.perf_counter()

    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()
    user = User("alice", "password123", "bio-template")
    user.register(cs)

    m1, ustate = user.login(cloud.server_id)

    # Forge a stale timestamp: 2× the window in the past
    m2 = cloud.receive_m1(m1)
    stale_ts = int(m2["TS2"]) - (TIMESTAMP_WINDOW * 2 + 10)
    m2_stale = {**m2, "TS2": stale_ts}

    m3, reason = cs.process_m2(m2_stale)
    blocked = m3 is None and "stale" in reason.lower()

    elapsed = (time.perf_counter() - start) * 1000

    return SecurityTestResult(
        test="stale_timestamp_replay",
        status="PASS" if blocked else "FAIL",
        description=(
            f"Eve replays a message with a timestamp more than {TIMESTAMP_WINDOW}s old. "
            "The protocol's freshness check should reject stale messages."
        ),
        evidence=(
            f"Control server returned: '{reason}'"
            if blocked
            else f"Protocol unexpectedly accepted stale timestamp. Reason: {reason}"
        ),
        severity="high",
        duration_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# Test 3: Message tampering
# ---------------------------------------------------------------------------

def test_message_tampering() -> SecurityTestResult:
    """
    Eve intercepts M1 and flips a bit in the authenticator V1.
    The protocol should detect the tampered authenticator.
    """
    from cryptomaka.protocols.ju_park import CloudServer, ControlServer, User
    start = time.perf_counter()

    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()
    user = User("alice", "password123", "bio-template")
    user.register(cs)

    m1, ustate = user.login(cloud.server_id)

    # Tamper V1: flip last hex character
    original_v1 = m1["V1"]
    last_char = original_v1[-1]
    flipped = "0" if last_char != "0" else "1"
    tampered_m1 = {**m1, "V1": original_v1[:-1] + flipped}

    m2 = cloud.receive_m1(tampered_m1)  # Cloud forwards to CS
    m3, reason = cs.process_m2(m2)
    blocked = m3 is None

    elapsed = (time.perf_counter() - start) * 1000

    return SecurityTestResult(
        test="message_tampering",
        status="PASS" if blocked else "FAIL",
        description=(
            "Eve intercepts M1 and modifies the authenticator V1 in transit. "
            "The MAC/hash verification should detect the tampering."
        ),
        evidence=(
            f"Control server rejected tampered message: '{reason}'"
            if blocked
            else "Protocol accepted a tampered message — integrity check failed."
        ),
        severity="high",
        duration_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# Test 4: User impersonation
# ---------------------------------------------------------------------------

def test_user_impersonation() -> SecurityTestResult:
    """
    Eve tries to log in as Alice without knowing Alice's credentials.
    Eve generates a random V1 hoping it passes.
    """
    from cryptomaka.protocols.ju_park import CloudServer, ControlServer, User, hx, rand32, ts
    start = time.perf_counter()

    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()
    user = User("alice", "password123", "bio-template")
    user.register(cs)

    # Eve picks a random PIDi and forged values
    forged_pid = hx(rand32())
    forged_b1 = hx(rand32())
    forged_b2 = hx(rand32())
    forged_v1 = hx(rand32())

    forged_m1 = {
        "PIDi": forged_pid,
        "B1": forged_b1,
        "B2": forged_b2,
        "V1": forged_v1,
        "TS1": ts(),
    }

    m2 = cloud.receive_m1(forged_m1)
    m3, reason = cs.process_m2(m2)
    blocked = m3 is None

    elapsed = (time.perf_counter() - start) * 1000

    return SecurityTestResult(
        test="user_impersonation",
        status="PASS" if blocked else "FAIL",
        description=(
            "Eve attempts to impersonate Alice by forging all M1 fields "
            "without knowledge of Alice's secret credentials."
        ),
        evidence=(
            f"Control server rejected forged identity: '{reason}'"
            if blocked
            else "Protocol accepted forged credentials — impersonation succeeded."
        ),
        severity="high",
        duration_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# Test 5: MITM / cloud server impersonation
# ---------------------------------------------------------------------------

def test_mitm_cloud_impersonation() -> SecurityTestResult:
    """
    Eve intercepts M3 from the Control Server and modifies V3 (cloud authenticator).
    The cloud server should reject the tampered response.
    """
    from cryptomaka.protocols.ju_park import (
        CloudServer,
        ControlServer,
        H,
        User,
        hx,
        xb,
        xor_bytes,
    )
    start = time.perf_counter()

    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()
    user = User("alice", "password123", "bio-template")
    user.register(cs)

    m1, ustate = user.login(cloud.server_id)
    m2 = cloud.receive_m1(m1)
    m3, reason = cs.process_m2(m2)

    if m3 is None:
        return SecurityTestResult(
            test="mitm_cloud_impersonation",
            status="FAIL",
            description="Could not set up baseline for MITM test.",
            evidence=f"Protocol setup failed: {reason}",
            severity="medium",
            duration_ms=(time.perf_counter() - start) * 1000,
        )

    # Tamper V3 (cloud authenticator in M3)
    original_v3 = m3["V3"]
    flipped = "0" if original_v3[-1] != "0" else "1"
    tampered_m3 = {**m3, "V3": original_v3[:-1] + flipped}

    # Recover rj so cloud can finish (using original m2)
    rj = xor_bytes(xb(m2["B3"]), H(cloud.kj, cloud.server_id))
    tampered_m3["rj"] = hx(rj)

    sk_server, ok_server, _ = cloud.finish_m3(tampered_m3)
    blocked = not ok_server

    elapsed = (time.perf_counter() - start) * 1000

    return SecurityTestResult(
        test="mitm_cloud_impersonation",
        status="PASS" if blocked else "FAIL",
        description=(
            "Eve intercepts M3 and modifies V3 (the server authenticator). "
            "The cloud server should reject the tampered response."
        ),
        evidence=(
            "Cloud server correctly rejected tampered V3."
            if blocked
            else "Cloud server accepted a tampered V3 — MITM succeeded."
        ),
        severity="medium",
        duration_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# Test 6: Nonce reuse detection
# ---------------------------------------------------------------------------

def test_nonce_reuse() -> SecurityTestResult:
    """
    Two protocol runs using the same nonce should be distinguishable.
    This verifies that the protocol uses fresh randomness per session.
    """
    from cryptomaka.protocols.ju_park import CloudServer, ControlServer, User
    start = time.perf_counter()

    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()

    u1 = User("alice", "password123", "bio-template")
    u1.register(cs)

    u2 = User("bob", "password456", "bio-template2")
    u2.register(cs)

    m1_alice, _ = u1.login(cloud.server_id)
    m1_bob, _ = u2.login(cloud.server_id)

    # Check that both M1 messages have distinct PIDs and V1s
    pids_distinct = m1_alice["PIDi"] != m1_bob["PIDi"]
    v1s_distinct = m1_alice["V1"] != m1_bob["V1"]

    # Also check that two logins by same user produce different nonces
    m1_alice2, _ = u1.login(cloud.server_id)
    # Note: alice's PID changes after each login due to pseudonym update in registration
    # The nonces ri should differ
    nonces_distinct = m1_alice["B1"] != m1_alice2["B1"]

    all_distinct = pids_distinct and v1s_distinct and nonces_distinct

    elapsed = (time.perf_counter() - start) * 1000

    return SecurityTestResult(
        test="nonce_reuse_detection",
        status="PASS" if all_distinct else "FAIL",
        description=(
            "Verify that each authentication session produces distinct nonces, "
            "PIDs, and authenticators — preventing linkability and replay."
        ),
        evidence=(
            f"PIDs distinct: {pids_distinct}, V1s distinct: {v1s_distinct}, "
            f"Session nonces distinct: {nonces_distinct}"
        ),
        severity="medium",
        duration_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# Test 7: Session key mismatch detection
# ---------------------------------------------------------------------------

def test_session_key_agreement() -> SecurityTestResult:
    """
    After a legitimate run, verify that user and cloud derive the same session key.
    This is a positive control: if it fails, the protocol implementation is broken.
    """
    start = time.perf_counter()

    try:
        result = _run_fresh_jupark()
        match = result.get("match", False)
        elapsed = (time.perf_counter() - start) * 1000

        return SecurityTestResult(
            test="session_key_agreement",
            status="PASS" if match else "FAIL",
            description=(
                "Verify that after a legitimate authentication, both the user "
                "and cloud server independently derive identical session keys."
            ),
            evidence=(
                "User and cloud session keys match — mutual key agreement confirmed."
                if match
                else "Session key mismatch — one or both parties derived different keys."
            ),
            severity="high",
            duration_ms=elapsed,
        )
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return SecurityTestResult(
            test="session_key_agreement",
            status="FAIL",
            description="Session key agreement positive control test.",
            evidence=f"Protocol execution failed: {e}",
            severity="high",
            duration_ms=elapsed,
        )


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_all_security_tests(protocol: str = "ju_park") -> dict[str, Any]:
    """
    Run all security tests and return structured results.

    Currently all tests target the Ju-Park protocol.
    The `protocol` parameter is reserved for future multi-protocol support.
    """
    tests = [
        test_replay_attack,
        test_stale_timestamp,
        test_message_tampering,
        test_user_impersonation,
        test_mitm_cloud_impersonation,
        test_nonce_reuse,
        test_session_key_agreement,
    ]

    results = []
    passed = 0
    failed = 0

    for test_fn in tests:
        try:
            r = test_fn()
        except Exception as exc:
            r = SecurityTestResult(
                test=test_fn.__name__,
                status="FAIL",
                description="Test raised an unexpected exception.",
                evidence=str(exc),
                severity="high",
            )

        results.append({
            "test": r.test,
            "status": r.status,
            "description": r.description,
            "evidence": r.evidence,
            "severity": r.severity,
            "duration_ms": round(r.duration_ms, 3),
        })

        if r.status == "PASS":
            passed += 1
        else:
            failed += 1

    return {
        "protocol": protocol,
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "disclaimer": DISCLAIMER,
        "results": results,
    }
