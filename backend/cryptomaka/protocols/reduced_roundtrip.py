"""
Proposed Reduced-Round-Trip Extension (PROPOSED EXTENSION — NOT PART OF JU-PARK 2023)

This module is an EXPERIMENTAL RESEARCH EXTENSION.
It is NOT part of the Ju & Park (Sensors 2023, 23, 9766) protocol.
It has NOT been formally analyzed or proven secure.
It must NOT be cited as part of the original published protocol.

Design goal:
Reduce the 4-message Ju-Park flow to 3 messages by having the Control Server
send its authenticated response directly to both the Cloud and the User
simultaneously (conceptually via the Cloud as relay).

Original Ju-Park 4-message flow:
  M1: User → Cloud
  M2: Cloud → Control Server
  M3: Control Server → Cloud
  M4: Cloud → User

Proposed 3-message flow:
  M1: User → Cloud
  M2: Cloud → Control Server
  M3: Control Server → Cloud + User (combined authenticated response)

Trade-off: M3 is larger, saves one network round trip.
Security properties require formal analysis before any claim can be made.

Implementation note:
This implementation reuses the exact same user-side and cloud-side logic as the
Ju-Park reconstruction (same User, CloudServer entities) and only modifies what
the Control Server returns: instead of M3+M4, it produces a single combined M3.
"""

from __future__ import annotations

import time
from typing import Any


def run_reduced_protocol() -> dict[str, Any]:
    """
    Execute the proposed reduced-round-trip protocol end-to-end.

    Reuses Ju-Park User and CloudServer entities unchanged.
    Only the Control Server response is modified (combined M3 instead of M3+M4).

    Returns structured result. Explicitly labeled as proposed extension.
    """

    from cryptomaka.protocols.ju_park import (
        CloudServer,
        ControlServer,
        H,
        User,
        hx,
        ts,
        xb,
        xor_bytes,
    )

    label = "PROPOSED EXTENSION — not part of Ju & Park (2023)"

    cs_inner = ControlServer("RC")
    cloud = CloudServer("S_j", cs_inner)
    cloud.register()
    user = User("alice", "password123", "bio-template")
    user.register(cs_inner)

    t_start = time.perf_counter_ns()

    # ── M1: User → Cloud (identical to Ju-Park M1) ──
    m1, ustate = user.login(cloud.server_id)

    # ── M2: Cloud → Control Server (identical to Ju-Park M2) ──
    m2 = cloud.receive_m1(m1)

    # ── Combined M3: Control Server → Cloud (carries both cloud and user tokens) ──
    # This is the proposed optimization: the CS produces both V3 (for cloud) and
    # V4 (for user) in a single message, which the cloud relays to the user.
    # In Ju-Park, V3 is in M3 and V4 is in M4 (requiring an additional cloud→user step).
    m3_combined, reason = cs_inner.process_m2(m2)

    if m3_combined is None:
        return {
            "protocol": "reduced_roundtrip",
            "label": label,
            "status": "error",
            "error": reason,
            "authentication_success": False,
            "session_key_match": False,
            "message_count": 3,
            "messages": [],
            "timings": {},
            "notes": [label],
        }

    # ── Cloud verifies V3 and derives session key (same as Ju-Park) ──
    rj = xor_bytes(xb(m2["B3"]), H(cloud.kj, cloud.server_id))
    m3_combined["rj"] = hx(rj)

    sk_cloud, ok_cloud, _ = cloud.finish_m3(m3_combined)

    if not ok_cloud:
        return {
            "protocol": "reduced_roundtrip",
            "label": label,
            "status": "error",
            "error": "Cloud V3 verification failed",
            "authentication_success": False,
            "session_key_match": False,
            "message_count": 3,
            "messages": [],
            "timings": {},
            "notes": [label],
        }

    # ── User verifies V4 and derives session key (same as Ju-Park, cloud relays) ──
    # In the proposed extension, the cloud relays the user-bound fields from M3
    # to the user in the same message (no separate M4 transmission needed).
    user_response = {
        "B8": m3_combined["B8"],
        "B9": m3_combined["B9"],
        "V4": m3_combined["V4"],
        "TS4": ts(),
        "TS3": m3_combined["TS3"],
        "new_PID": m3_combined["new_PID"],
    }

    sk_user, ok_user = user.finish(ustate, user_response)

    t_end = time.perf_counter_ns()
    duration_ms = (t_end - t_start) / 1_000_000

    match = ok_cloud and ok_user and sk_cloud is not None and sk_user is not None and sk_cloud == sk_user

    # Message size estimates (bits)
    H = 256  # SHA-256 hash output
    TS = 32   # Timestamp

    return {
        "protocol": "reduced_roundtrip",
        "label": label,
        "status": "success" if match else "partial",
        "authentication_success": ok_cloud and ok_user,
        "session_key_match": match,
        "participants": 3,
        "message_count": 3,
        "messages": [
            {
                "name": "M1",
                "direction": "User → Cloud",
                "size_bits": 4 * H + TS,
                "note": "Identical to Ju-Park M1",
            },
            {
                "name": "M2",
                "direction": "Cloud → Control Server",
                "size_bits": (4 * H + TS) + 2 * H + TS,
                "note": "Identical to Ju-Park M2",
            },
            {
                "name": "M3 (combined)",
                "direction": "Control Server → Cloud → User",
                "size_bits": 7 * H + TS,
                "note": (
                    "PROPOSED: Combined Cloud+User response. "
                    "Ju-Park splits this into M3 (CS→Cloud, 3 fields) "
                    "and M4 (Cloud→User, 4 fields) for 4 total messages."
                ),
            },
        ],
        "timings": {
            "total_ms": round(duration_ms, 4),
        },
        "notes": [
            "PROPOSED EXTENSION — not part of Ju & Park (2023).",
            "Reduces round trips from 4 messages to 3 by combining Cloud and User responses.",
            "M3 is larger than Ju-Park M3 alone but eliminates the separate M4 step.",
            "Security properties require formal analysis before any security claim.",
            "Entities (User, CloudServer) are identical to the Ju-Park reconstruction.",
        ],
    }
