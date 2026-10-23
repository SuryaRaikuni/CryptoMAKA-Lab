"""
Interactive Security Playground Engine.

Allows researchers and evaluators to manually or programmatically inject custom
tampering actions into MAKA protocol messages (Ju-Park, ECC, ML-KEM) and inspect
real-time packet rejection diagnostics, Dolev-Yao adversary intercept traces,
and defense validation logs.
"""

from __future__ import annotations

import os
import time
from typing import Any

from cryptomaka.schemas.security import (
    PlaygroundLogEntry,
    PlaygroundSamplePacketResponse,
    PlaygroundTamperRequest,
    PlaygroundTamperResponse,
)


def _flip_last_char(val: str) -> str:
    """Flip the last hex character or alphanumeric char."""
    if not val:
        return "1"
    last = val[-1]
    flipped = "0" if last != "0" else "1"
    return val[:-1] + flipped


def _apply_tamper_to_value(
    orig_val: Any,
    action: str,
    custom_val: str | None = None,
) -> Any:
    """Apply the chosen tampering mutation to a field value."""
    str_val = str(orig_val)

    if action == "flip_bit":
        return _flip_last_char(str_val)
    elif action == "random_noise":
        length = max(8, len(str_val))
        return os.urandom(length // 2).hex()
    elif action == "zero_out":
        if isinstance(orig_val, int):
            return 0
        return "0" * len(str_val)
    elif action == "custom_value":
        if custom_val is not None:
            if isinstance(orig_val, int):
                try:
                    return int(custom_val)
                except ValueError:
                    return custom_val
            return custom_val
        return _flip_last_char(str_val)
    return orig_val


def get_sample_packet(protocol: str = "ju_park") -> PlaygroundSamplePacketResponse:
    """Return a baseline legitimate sample packet and UI metadata for a protocol."""
    if protocol == "ecc":
        from cryptomaka.protocols.ecc import ControlServerECC, ECCUser
        rc = ControlServerECC()
        user = ECCUser("alice", "password123", "bio-template")
        user.register(rc)
        m1, _, _ = user.start_login()

        raw_fields = dict(m1)
        raw_fields["T1"] = int(m1["T1"])

        descriptions = {
            "Pu": "Ephemeral NIST P-256 public key (65 bytes uncompressed)",
            "Ni": "User fresh challenge nonce (128-bit)",
            "T1": "Freshness timestamp (Unix seconds)",
            "Vi": "User authenticator tag HMAC/SHA-256",
        }
        presets = [
            {"id": "stale_timestamp", "name": "Stale Timestamp Attack (+60s clock drift)"},
            {"id": "bit_flip_mac", "name": "Authenticator Corruption (Flip bit in Vi)"},
            {"id": "nonce_replay", "name": "Nonce Replay (Reuse previously consumed Ni)"},
            {"id": "tamper_public_key", "name": "Public Key Point Tampering (Corrupt Pu)"},
        ]
        direction = "User (Ui) → Cloud Server (Sj)"
        msg_name = "M1 (Login Request)"

    elif protocol == "ml_kem":
        from cryptomaka.protocols.ml_kem import MLKEMRegistrationCentre, MLKEMUser
        rc = MLKEMRegistrationCentre()
        user = MLKEMUser("alice", "password123", "bio-template")
        user.register(rc)
        m1, _ = user.start_authentication()

        raw_fields = dict(m1)
        raw_fields["T1"] = int(m1["T1"])

        descriptions = {
            "user_id": "User public identifier (ASCII string)",
            "PK_u": "ML-KEM-768 encapsulation key (1,184 bytes per FIPS 203)",
            "nonce_u": "Fresh random nonce (256-bit CSPRNG)",
            "T1": "Freshness timestamp (Unix seconds)",
            "Auth_u": "SHA3-256 user authentication tag",
        }
        presets = [
            {"id": "stale_timestamp", "name": "Stale Timestamp Attack (+60s clock drift)"},
            {"id": "bit_flip_mac", "name": "Authenticator Corruption (Flip bit in Auth_u)"},
            {"id": "nonce_replay", "name": "Nonce Replay (Reuse previously consumed nonce)"},
            {"id": "forged_id", "name": "User Identity Forgery (Unregistered User ID)"},
        ]
        direction = "User (Ui) → Cloud Server (Sj)"
        msg_name = "M1 (KEM Authentication Request)"

    else:
        # Default: ju_park
        from cryptomaka.protocols.ju_park import CloudServer, ControlServer, User
        cs = ControlServer("CS")
        cloud = CloudServer("S_j", cs)
        cloud.register()
        user = User("alice", "password123", "bio-template")
        user.register(cs)
        m1, _ = user.login(cloud.server_id)

        raw_fields = dict(m1)

        descriptions = {
            "PIDi": "User dynamic pseudonym (SHA-256 hash derived during registration)",
            "B1": "XOR-masked random nonce ri: ri ⊕ H(SIDi ∥ IDCS ∥ ki)",
            "B2": "XOR-masked cloud identifier IDj: H(IDj) ⊕ H(IDCS ∥ SIDi ∥ ri)",
            "V1": "User authenticator tag: H(IDCS ∥ TS1 ∥ SIDi ∥ ki ∥ ri)",
            "TS1": "Freshness timestamp (Unix seconds)",
        }
        presets = [
            {"id": "stale_timestamp", "name": "Stale Timestamp Attack (+60s clock drift)"},
            {"id": "bit_flip_mac", "name": "Authenticator Bit-Flip (Corrupt V1)"},
            {"id": "replay_attack", "name": "Replay Attack (Replay consumed pseudonym PIDi)"},
            {"id": "fake_identity", "name": "Identity Forgery (Random counterfeit PIDi)"},
            {"id": "mask_tamper", "name": "Masked Payload Tampering (Corrupt B1 nonce mask)"},
        ]
        direction = "User (Ui) → Cloud Server (Sj)"
        msg_name = "M1 (Authentication Request)"

    return PlaygroundSamplePacketResponse(
        protocol=protocol,
        message_name=msg_name,
        direction=direction,
        fields=raw_fields,
        field_descriptions=descriptions,
        available_presets=presets,
    )


def simulate_tamper(req: PlaygroundTamperRequest) -> PlaygroundTamperResponse:
    """
    Simulate an adversarial attack/tampering vector against the selected protocol.

    Executes a step-by-step trace showing where the packet is intercepted,
    what modifications were applied, and which exact validation check dropped it.
    """
    start_time = time.perf_counter()
    logs: list[PlaygroundLogEntry] = []

    def log(level: str, node: str, message: str):
        elapsed = round((time.perf_counter() - start_time) * 1000, 3)
        logs.append(PlaygroundLogEntry(timestamp_ms=elapsed, level=level, node=node, message=message))

    proto = req.protocol.lower()

    if proto == "ecc":
        return _simulate_ecc_tamper(req, log, logs, start_time)
    elif proto == "ml_kem":
        return _simulate_mlkem_tamper(req, log, logs, start_time)
    else:
        return _simulate_jupark_tamper(req, log, logs, start_time)


# ---------------------------------------------------------------------------
# Ju-Park Playground Simulation
# ---------------------------------------------------------------------------

def _simulate_jupark_tamper(
    req: PlaygroundTamperRequest,
    log: Any,
    logs: list[PlaygroundLogEntry],
    start_time: float,
) -> PlaygroundTamperResponse:
    from cryptomaka.protocols.ju_park import (
        TIMESTAMP_WINDOW,
        CloudServer,
        ControlServer,
        User,
        hx,
        rand32,
    )

    log("INFO", "ControlServer", "Initializing trusted registration authority (CS)...")
    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()
    log("INFO", "CloudServer", f"Cloud Server '{cloud.server_id}' registered with Control Server.")

    user = User("alice", "password123", "bio-template")
    user.register(cs)
    log("INFO", "User", f"User '{user.user_id}' registered with card (PIDi={hx(user.card.PIDi)[:12]}...).")

    # Handle Replay Preset
    if req.simulate_replay or req.attack_preset == "replay_attack":
        log("ADVERSARY", "Adversary", "Eavesdropping on public wireless channel...")
        m1_captured, ustate = user.login(cloud.server_id)
        log("INFO", "User", f"User generates legitimate M1 (TS1={m1_captured['TS1']}). Adversary caches copy.")

        # Legitimate run completes first
        m2_legit = cloud.receive_m1(m1_captured)
        m3_legit, _ = cs.process_m2(m2_legit)
        cloud.finish_m3(m3_legit)
        log("INFO", "ControlServer", "Legitimate session authenticated. PIDi rotated in Control Server DB.")

        log("ADVERSARY", "Adversary", "Replaying cached M1 after session completion...")
        tampered_m1 = dict(m1_captured)
        orig_packet = dict(m1_captured)
        tampered_fields = ["PIDi (Replayed consumed token)"]

        # Forward replayed M1 through cloud to CS
        m2_replay = cloud.receive_m1(tampered_m1)
        m3_replay, reason = cs.process_m2(m2_replay)

        blocked = m3_replay is None
        elapsed = round((time.perf_counter() - start_time) * 1000, 3)

        if blocked:
            log("DROP", "ControlServer", f"Pseudonym lookup failed: {reason}. Dropped replayed request.")
            explanation = (
                "The Ju-Park protocol uses one-time dynamic pseudonyms. After a successful authentication, "
                "the Control Server consumed PIDi and rotated it to a fresh value. The replayed message "
                "referred to an expired pseudonym, preventing replay attacks without requiring synchronized state."
            )
        else:
            log("VERIFY", "ControlServer", "WARNING: Replayed packet was unexpectedly accepted.")
            explanation = "Replay was accepted."

        return PlaygroundTamperResponse(
            protocol="ju_park",
            verdict="BLOCKED" if blocked else "ACCEPTED",
            is_blocked=blocked,
            stopped_at_stage="M2 Verification at Control Server",
            dropped_by="ControlServer",
            reason=reason or "unknown PID",
            defense_explanation=explanation,
            original_packet=orig_packet,
            tampered_packet=tampered_m1,
            tampered_fields=tampered_fields,
            logs=logs,
            duration_ms=elapsed,
        )

    # Standard / Custom Tampering Flow
    m1_orig, ustate = user.login(cloud.server_id)
    orig_packet = dict(m1_orig)
    tampered_m1 = dict(m1_orig)
    tampered_fields = []

    log("INFO", "User", f"User constructs legitimate M1: PIDi={m1_orig['PIDi'][:10]}..., V1={m1_orig['V1'][:10]}..., TS1={m1_orig['TS1']}")

    # Apply Attack Preset Shortcuts
    if req.attack_preset == "stale_timestamp":
        offset = 60
        tampered_m1["TS1"] = str(int(tampered_m1["TS1"]) - offset)
        tampered_fields.append("TS1")
        log("ADVERSARY", "Adversary", f"Injected clock drift: subtracted {offset}s from TS1 ({tampered_m1['TS1']}).")
    elif req.attack_preset == "bit_flip_mac":
        tampered_m1["V1"] = _flip_last_char(tampered_m1["V1"])
        tampered_fields.append("V1")
        log("ADVERSARY", "Adversary", f"Flipped bit in authenticator V1 -> {tampered_m1['V1'][:12]}...")
    elif req.attack_preset == "fake_identity":
        tampered_m1["PIDi"] = hx(rand32())
        tampered_fields.append("PIDi")
        log("ADVERSARY", "Adversary", f"Replaced PIDi with forged random pseudonym -> {tampered_m1['PIDi'][:12]}...")
    elif req.attack_preset == "mask_tamper":
        tampered_m1["B1"] = _flip_last_char(tampered_m1["B1"])
        tampered_fields.append("B1")
        log("ADVERSARY", "Adversary", f"Corrupted masked nonce B1 -> {tampered_m1['B1'][:12]}...")
    else:
        # Custom Tampering Settings
        if req.timestamp_offset_seconds != 0:
            new_ts = str(int(tampered_m1["TS1"]) + req.timestamp_offset_seconds)
            tampered_m1["TS1"] = new_ts
            tampered_fields.append("TS1")
            log("ADVERSARY", "Adversary", f"Modified timestamp TS1 by {req.timestamp_offset_seconds:+d}s -> {new_ts}")

        if req.field_to_tamper and req.field_to_tamper in tampered_m1:
            orig_val = tampered_m1[req.field_to_tamper]
            mutated = _apply_tamper_to_value(orig_val, req.tamper_action or "flip_bit", req.custom_tamper_value)
            tampered_m1[req.field_to_tamper] = mutated
            tampered_fields.append(req.field_to_tamper)
            log("ADVERSARY", "Adversary", f"Mutated field '{req.field_to_tamper}': '{orig_val}' -> '{mutated}' (Action: {req.tamper_action})")

    # Cloud receives M1
    log("INFO", "CloudServer", "Cloud Server intercepts/receives M1 packet from user.")
    m2 = cloud.receive_m1(tampered_m1)

    # If TS1 was modified, adjust forwarded TS2 in M2 to reflect stale arrival if requested
    if "TS1" in tampered_fields and req.timestamp_offset_seconds < -TIMESTAMP_WINDOW:
        m2["TS2"] = int(m2["TS2"]) + req.timestamp_offset_seconds
        log("ADVERSARY", "Adversary", f"Simulated transit delay reflected in cloud timestamp TS2={m2['TS2']}")

    log("INFO", "CloudServer", "Cloud Server packs forwarded M1 into M2 challenge and routes to Control Server.")
    log("VERIFY", "ControlServer", "Control Server parsing M2: verifying timestamp freshness and user authenticator...")

    # Control Server processes M2
    m3, reason = cs.process_m2(m2)
    elapsed = round((time.perf_counter() - start_time) * 1000, 3)

    if m3 is None:
        # Dropped at Control Server
        log("DROP", "ControlServer", f"[REJECTION] Dropped packet. Rejection reason: '{reason}'")
        if "stale" in (reason or "").lower():
            explanation = (
                f"Freshness check failed: Received timestamp differs from current time by more than "
                f"ΔT = {TIMESTAMP_WINDOW}s. The Control Server discards stale requests to prevent delayed replay attacks."
            )
        elif "v1" in (reason or "").lower():
            explanation = (
                "Authenticator verification failed: The HMAC/SHA-256 tag V1 does not match the expected "
                "hash derived from the user's master key ki and nonce ri. Bit alteration detected."
            )
        elif "pid" in (reason or "").lower():
            explanation = (
                "Identity lookup failed: The pseudonym PIDi does not exist in the Control Server database. "
                "Adversary cannot forge a valid pseudonym without knowing master secret xcs."
            )
        else:
            explanation = f"Control Server verification rejected packet with reason: '{reason}'."

        return PlaygroundTamperResponse(
            protocol="ju_park",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M2 Verification at Control Server",
            dropped_by="ControlServer",
            reason=reason or "Verification Failed",
            defense_explanation=explanation,
            original_packet=orig_packet,
            tampered_packet=tampered_m1,
            tampered_fields=tampered_fields,
            logs=logs,
            duration_ms=elapsed,
        )

    # Cloud server processes M3
    log("VERIFY", "CloudServer", "Control Server returned M3. Cloud Server validating authenticator V3...")
    sk_server, ok_server, m4 = cloud.finish_m3(m3)

    if not ok_server:
        log("DROP", "CloudServer", "[REJECTION] Cloud Server rejected M3 (server authenticator failure).")
        return PlaygroundTamperResponse(
            protocol="ju_park",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M3 Verification at Cloud Server",
            dropped_by="CloudServer",
            reason="V3 verification failed",
            defense_explanation="Cloud Server verified V3 using its private key kj and rejected the corrupted response.",
            original_packet=orig_packet,
            tampered_packet=tampered_m1,
            tampered_fields=tampered_fields,
            logs=logs,
            duration_ms=elapsed,
        )

    # User finishes M4
    log("VERIFY", "User", "User validating M4 response from cloud...")
    sk_user, ok_user = user.finish(ustate, m4)

    if not ok_user:
        log("DROP", "User", "[REJECTION] User rejected M4 (mutual authenticator V4 mismatch).")
        return PlaygroundTamperResponse(
            protocol="ju_park",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M4 Verification at User",
            dropped_by="User",
            reason="V4 verification failed",
            defense_explanation="User recomputed V4 using its local state and detected a parameter mismatch.",
            original_packet=orig_packet,
            tampered_packet=tampered_m1,
            tampered_fields=tampered_fields,
            logs=logs,
            duration_ms=elapsed,
        )

    # If execution reached here:
    if tampered_fields:
        log("ADVERSARY", "Adversary", "ALERT: Tampered packet was accepted by all entities! Security breach simulated.")
        verdict = "ACCEPTED"
        blocked = False
        explanation = "The tampering was not detected by the protocol checks."
    else:
        log("SUCCESS", "User", "Clean run verified: User and Cloud derived matching 256-bit session key.")
        verdict = "ACCEPTED"
        blocked = False
        explanation = "Clean baseline handshake completed successfully with mutual authentication."

    return PlaygroundTamperResponse(
        protocol="ju_park",
        verdict=verdict,
        is_blocked=blocked,
        stopped_at_stage="Session Established (End of Handshake)",
        dropped_by="None",
        reason="Mutual Authentication Succeeded",
        defense_explanation=explanation,
        original_packet=orig_packet,
        tampered_packet=tampered_m1,
        tampered_fields=tampered_fields,
        logs=logs,
        duration_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# ECC Playground Simulation
# ---------------------------------------------------------------------------

def _simulate_ecc_tamper(
    req: PlaygroundTamperRequest,
    log: Any,
    logs: list[PlaygroundLogEntry],
    start_time: float,
) -> PlaygroundTamperResponse:
    from cryptomaka.protocols.ecc import ControlServerECC, ECCCloudServer, ECCUser

    log("INFO", "ControlServer", "Initializing ECC Registration Authority (RC)...")
    rc = ControlServerECC()
    cs = ECCCloudServer("cloud-1")
    user = ECCUser("alice", "password123", "bio-template")
    user.register(rc)
    log("INFO", "User", "User registered with ECC Registration Centre.")

    # Replay simulation
    if req.simulate_replay or req.attack_preset == "nonce_replay":
        log("ADVERSARY", "Adversary", "Capturing valid M1 and waiting for session to complete...")
        m1_captured, a, private_u = user.start_login()
        cs.respond_to_login(rc, user.user_id, m1_captured)
        log("INFO", "ControlServer", f"Session 1 completed. Nonce '{m1_captured['Ni'][:8]}...' added to consumed nonce set.")

        log("ADVERSARY", "Adversary", "Replaying identical M1 with consumed nonce Ni...")
        m2, _, _, reason = cs.respond_to_login(rc, user.user_id, m1_captured)
        elapsed = round((time.perf_counter() - start_time) * 1000, 3)

        log("DROP", "ControlServer", f"[REJECTION] Control Server rejected replayed M1: '{reason}'.")
        return PlaygroundTamperResponse(
            protocol="ecc",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M1 Verification at Control Server",
            dropped_by="ControlServer",
            reason=reason,
            defense_explanation="ControlServerECC tracks all observed nonces in self.used_nonces. Replayed nonces are rejected immediately.",
            original_packet=dict(m1_captured),
            tampered_packet=dict(m1_captured),
            tampered_fields=["Ni (Replayed Nonce)"],
            logs=logs,
            duration_ms=elapsed,
        )

    m1_orig, a, private_u = user.start_login()
    orig_packet = dict(m1_orig)
    tampered_m1 = dict(m1_orig)
    tampered_fields = []

    log("INFO", "User", f"Generated ephemeral ECDH keypair Pu={m1_orig['Pu'][:16]}..., Vi={m1_orig['Vi'][:8]}...")

    if req.attack_preset == "stale_timestamp":
        offset = 60
        tampered_m1["T1"] = str(int(tampered_m1["T1"]) - offset)
        tampered_fields.append("T1")
        log("ADVERSARY", "Adversary", f"Injected stale timestamp T1={tampered_m1['T1']} (-{offset}s).")
    elif req.attack_preset == "bit_flip_mac":
        tampered_m1["Vi"] = _flip_last_char(tampered_m1["Vi"])
        tampered_fields.append("Vi")
        log("ADVERSARY", "Adversary", f"Corrupted authenticator Vi -> {tampered_m1['Vi'][:12]}...")
    elif req.attack_preset == "tamper_public_key":
        tampered_m1["Pu"] = _flip_last_char(tampered_m1["Pu"])
        tampered_fields.append("Pu")
        log("ADVERSARY", "Adversary", f"Corrupted ECC public key point Pu -> {tampered_m1['Pu'][:12]}...")
    else:
        if req.timestamp_offset_seconds != 0:
            new_ts = str(int(tampered_m1["T1"]) + req.timestamp_offset_seconds)
            tampered_m1["T1"] = new_ts
            tampered_fields.append("T1")
            log("ADVERSARY", "Adversary", f"Modified timestamp T1 by {req.timestamp_offset_seconds:+d}s -> {new_ts}")

        if req.field_to_tamper and req.field_to_tamper in tampered_m1:
            orig_val = tampered_m1[req.field_to_tamper]
            mutated = _apply_tamper_to_value(orig_val, req.tamper_action or "flip_bit", req.custom_tamper_value)
            tampered_m1[req.field_to_tamper] = mutated
            tampered_fields.append(req.field_to_tamper)
            log("ADVERSARY", "Adversary", f"Mutated field '{req.field_to_tamper}': '{orig_val}' -> '{mutated}'")

    log("VERIFY", "ControlServer", "Cloud Server querying Control Server to verify user login...")
    m2, sk_server, _, reason = cs.respond_to_login(rc, user.user_id, tampered_m1)
    elapsed = round((time.perf_counter() - start_time) * 1000, 3)

    if m2 is None:
        log("DROP", "ControlServer", f"[REJECTION] Control Server dropped login request: '{reason}'.")
        return PlaygroundTamperResponse(
            protocol="ecc",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M1 Verification at Control Server",
            dropped_by="ControlServer",
            reason=reason,
            defense_explanation="ControlServerECC verified timestamp window, nonce uniqueness, and HMAC-SHA256 authenticator Vi.",
            original_packet=orig_packet,
            tampered_packet=tampered_m1,
            tampered_fields=tampered_fields,
            logs=logs,
            duration_ms=elapsed,
        )

    log("VERIFY", "User", "User verifying cloud response M2 and performing ECDH exchange...")
    sk_user, user_reason = user.finish_login(a, private_u, tampered_m1, m2)

    if sk_user is None:
        log("DROP", "User", f"[REJECTION] User rejected M2: '{user_reason}'.")
        return PlaygroundTamperResponse(
            protocol="ecc",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M2 Verification at User",
            dropped_by="User",
            reason=user_reason,
            defense_explanation="User verified cloud authenticator Vj over transcript and detected mismatch.",
            original_packet=orig_packet,
            tampered_packet=tampered_m1,
            tampered_fields=tampered_fields,
            logs=logs,
            duration_ms=elapsed,
        )

    log("SUCCESS", "User", "ECC/ECDH session key established with forward secrecy.")
    return PlaygroundTamperResponse(
        protocol="ecc",
        verdict="ACCEPTED",
        is_blocked=False,
        stopped_at_stage="Session Established",
        dropped_by="None",
        reason="Mutual Key Agreement Established",
        defense_explanation="Clean handshake verified.",
        original_packet=orig_packet,
        tampered_packet=tampered_m1,
        tampered_fields=tampered_fields,
        logs=logs,
        duration_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# ML-KEM Playground Simulation
# ---------------------------------------------------------------------------

def _simulate_mlkem_tamper(
    req: PlaygroundTamperRequest,
    log: Any,
    logs: list[PlaygroundLogEntry],
    start_time: float,
) -> PlaygroundTamperResponse:
    from cryptomaka.protocols.ml_kem import (
        MLKEMCloudServer,
        MLKEMRegistrationCentre,
        MLKEMUser,
    )

    log("INFO", "RegistrationCentre", "Initializing Post-Quantum Registration Authority (RC)...")
    rc = MLKEMRegistrationCentre()
    cs = MLKEMCloudServer("cloud-mlkem-1")
    user = MLKEMUser("alice", "password123", "bio-template")
    user.register(rc)
    log("INFO", "User", "Registered ML-KEM-768 public key with RC.")

    if req.simulate_replay or req.attack_preset == "nonce_replay":
        m1_captured, _ = user.start_authentication()
        cs.process_authentication(rc, m1_captured)
        log("INFO", "RegistrationCentre", f"Nonce '{m1_captured['nonce_u'][:8]}...' added to used nonces.")

        log("ADVERSARY", "Adversary", "Replaying M1 carrying consumed nonce...")
        m2, _, reason = cs.process_authentication(rc, m1_captured)
        elapsed = round((time.perf_counter() - start_time) * 1000, 3)

        log("DROP", "RegistrationCentre", f"[REJECTION] RC rejected replayed M1: '{reason}'.")
        return PlaygroundTamperResponse(
            protocol="ml_kem",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M1 Verification at Registration Centre",
            dropped_by="RegistrationCentre",
            reason=reason,
            defense_explanation="RC checks nonce freshness in self.used_nonces and rejects duplicates under Dolev-Yao model.",
            original_packet=dict(m1_captured),
            tampered_packet=dict(m1_captured),
            tampered_fields=["nonce_u (Replayed Nonce)"],
            logs=logs,
            duration_ms=elapsed,
        )

    m1_orig, _ = user.start_authentication()
    orig_packet = dict(m1_orig)
    tampered_m1 = dict(m1_orig)
    tampered_fields = []

    log("INFO", "User", f"Generated ML-KEM-768 keypair (1184B) and SHA3 authenticator Auth_u={m1_orig['Auth_u'][:8]}...")

    if req.attack_preset == "stale_timestamp":
        offset = 60
        tampered_m1["T1"] = str(int(tampered_m1["T1"]) - offset)
        tampered_fields.append("T1")
        log("ADVERSARY", "Adversary", f"Injected stale timestamp T1={tampered_m1['T1']} (-{offset}s).")
    elif req.attack_preset == "bit_flip_mac":
        tampered_m1["Auth_u"] = _flip_last_char(tampered_m1["Auth_u"])
        tampered_fields.append("Auth_u")
        log("ADVERSARY", "Adversary", f"Corrupted SHA3-256 authenticator Auth_u -> {tampered_m1['Auth_u'][:12]}...")
    elif req.attack_preset == "forged_id":
        tampered_m1["user_id"] = "mallory_attacker"
        tampered_fields.append("user_id")
        log("ADVERSARY", "Adversary", "Substituted user_id with unregistered entity 'mallory_attacker'.")
    else:
        if req.timestamp_offset_seconds != 0:
            new_ts = str(int(tampered_m1["T1"]) + req.timestamp_offset_seconds)
            tampered_m1["T1"] = new_ts
            tampered_fields.append("T1")
            log("ADVERSARY", "Adversary", f"Modified timestamp T1 by {req.timestamp_offset_seconds:+d}s -> {new_ts}")

        if req.field_to_tamper and req.field_to_tamper in tampered_m1:
            orig_val = tampered_m1[req.field_to_tamper]
            mutated = _apply_tamper_to_value(orig_val, req.tamper_action or "flip_bit", req.custom_tamper_value)
            tampered_m1[req.field_to_tamper] = mutated
            tampered_fields.append(req.field_to_tamper)
            log("ADVERSARY", "Adversary", f"Mutated field '{req.field_to_tamper}': '{orig_val}' -> '{mutated}'")

    log("VERIFY", "RegistrationCentre", "Cloud Server requesting RC verification and KEM encapsulation...")
    m2, sk_server, reason = cs.process_authentication(rc, tampered_m1)
    elapsed = round((time.perf_counter() - start_time) * 1000, 3)

    if m2 is None:
        log("DROP", "RegistrationCentre", f"[REJECTION] RC rejected request: '{reason}'.")
        return PlaygroundTamperResponse(
            protocol="ml_kem",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M1 Verification at Registration Centre",
            dropped_by="RegistrationCentre",
            reason=reason,
            defense_explanation="RC verified timestamp freshness, user identity, and SHA3-256 authenticator.",
            original_packet=orig_packet,
            tampered_packet=tampered_m1,
            tampered_fields=tampered_fields,
            logs=logs,
            duration_ms=elapsed,
        )

    log("VERIFY", "User", "User validating M2 and decapsulating ML-KEM ciphertext (1088 bytes)...")
    sk_user, user_reason = user.verify_and_derive_key(tampered_m1, m2)

    if sk_user is None:
        log("DROP", "User", f"[REJECTION] User rejected M2: '{user_reason}'.")
        return PlaygroundTamperResponse(
            protocol="ml_kem",
            verdict="BLOCKED",
            is_blocked=True,
            stopped_at_stage="M2 Verification at User",
            dropped_by="User",
            reason=user_reason,
            defense_explanation="User verified Auth_cs tag and decapsulated ciphertext to establish shared secret.",
            original_packet=orig_packet,
            tampered_packet=tampered_m1,
            tampered_fields=tampered_fields,
            logs=logs,
            duration_ms=elapsed,
        )

    log("SUCCESS", "User", "ML-KEM post-quantum session key established successfully.")
    return PlaygroundTamperResponse(
        protocol="ml_kem",
        verdict="ACCEPTED",
        is_blocked=False,
        stopped_at_stage="Session Established",
        dropped_by="None",
        reason="Mutual Key Agreement Established",
        defense_explanation="Clean handshake verified.",
        original_packet=orig_packet,
        tampered_packet=tampered_m1,
        tampered_fields=tampered_fields,
        logs=logs,
        duration_ms=elapsed,
    )
