"""Head-to-head benchmark for the current Hash/XOR prototype and P-256 ECDH.

The benchmark uses the same fresh-user workload for each implementation.
Timing is local to this machine and is not a reproduction of the paper's
Raspberry Pi/MIRACL timing environment. Communication sizes use the actual
fields in the prototypes; the Ju-Park 3776-bit figure is a literature reference
for the complete four-message scheme and is therefore not treated as an
apples-to-apples total with the two-message prototypes here.
"""

from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path

from maka_skeleton import CloudServer, ControlServer, User
from ecc_counterpart import ECCCloudServer, ControlServerECC, ECCUser

OUT = Path("/mnt/data/benchmark_results.csv")
N = 300


def avg_us(fn, n=N):
    vals = []
    for _ in range(n):
        t0 = time.perf_counter_ns()
        fn()
        vals.append((time.perf_counter_ns() - t0) / 1000)
    return statistics.mean(vals)


def hashxor_registration():
    rc = ControlServer(); u = User("bench", "pw", "bio")
    u.register(rc)


def hashxor_login():
    rc = ControlServer(); u = User("bench", "pw", "bio"); u.register(rc)
    u.start_login()


def hashxor_server_response():
    rc = ControlServer(); cs = CloudServer("cs", rc.register_cloud_server("cs")); u = User("bench", "pw", "bio"); u.register(rc)
    m1, _ = u.start_login(); cs.respond_to_login(rc, u.id, m1["Ni"], m1["T1"], m1["Vi"])


def hashxor_round():
    rc = ControlServer(); cs = CloudServer("cs", rc.register_cloud_server("cs")); u = User("bench", "pw", "bio"); u.register(rc)
    m1, a = u.start_login(); m2, sk, reason = cs.respond_to_login(rc, u.id, m1["Ni"], m1["T1"], m1["Vi"])
    if m2 is None or sk is None or reason != "ok": raise RuntimeError(reason)
    assert u.derive_session_key(a, m1["Ni"], m2["Nc"]) == sk


def ecdh_registration():
    rc = ControlServerECC(); u = ECCUser("bench", "pw", "bio")
    u.register(rc)


def ecdh_login():
    rc = ControlServerECC(); u = ECCUser("bench", "pw", "bio"); u.register(rc)
    u.start_login()


def ecdh_server_response():
    rc = ControlServerECC(); cs = ECCCloudServer("cs"); u = ECCUser("bench", "pw", "bio"); u.register(rc)
    m1, _, _ = u.start_login(); cs.respond_to_login(rc, u.user_id, m1)


def ecdh_round():
    rc = ControlServerECC(); cs = ECCCloudServer("cs"); u = ECCUser("bench", "pw", "bio"); u.register(rc)
    m1, a, priv = u.start_login(); m2, sk, _, reason = cs.respond_to_login(rc, u.user_id, m1)
    if m2 is None or sk is None or reason != "ok": raise RuntimeError(reason)
    sk_u, reason_u = u.finish_login(a, priv, m1, m2)
    assert reason_u == "ok" and sk_u == sk


def measure_message_sizes():
    # Hash/XOR: M1 = Vi + Ni + T1; M2 = Nc + T2.
    hx_m1 = 256 + 128 + 32
    hx_m2 = 128 + 32

    # P-256 uncompressed public key = 65 bytes = 520 bits.
    # ECC M1 = Vi + Pu + Ni + T1; ECC M2 = Pc + Nc + T2 + Vj.
    ecdh_m1 = 256 + 520 + 128 + 32
    ecdh_m2 = 520 + 128 + 32 + 256

    return {
        "Hash-XOR M1 bits": hx_m1,
        "Hash-XOR M2 bits": hx_m2,
        "Hash-XOR total bits": hx_m1 + hx_m2,
        "ECDH M1 bits": ecdh_m1,
        "ECDH M2 bits": ecdh_m2,
        "ECDH total bits": ecdh_m1 + ecdh_m2,
        "Paper total bits": 3776,
    }


def main():
    funcs = [
        ("hash_xor", "registration_us", hashxor_registration),
        ("hash_xor", "login_us", hashxor_login),
        ("hash_xor", "server_response_us", hashxor_server_response),
        ("hash_xor", "end_to_end_round_us", hashxor_round),
        ("p256_ecdh", "registration_us", ecdh_registration),
        ("p256_ecdh", "login_us", ecdh_login),
        ("p256_ecdh", "server_response_us", ecdh_server_response),
        ("p256_ecdh", "end_to_end_round_us", ecdh_round),
    ]

    timing_rows = []
    for scheme, metric, fn in funcs:
        value = avg_us(fn)
        timing_rows.append([scheme, metric, f"{value:.4f}"])

    sizes = measure_message_sizes()
    size_rows = [
        ["hash_xor", "M1_communication_bits", sizes["Hash-XOR M1 bits"]],
        ["hash_xor", "M2_communication_bits", sizes["Hash-XOR M2 bits"]],
        ["hash_xor", "total_user_cloud_bits", sizes["Hash-XOR total bits"]],
        ["p256_ecdh", "M1_communication_bits", sizes["ECDH M1 bits"]],
        ["p256_ecdh", "M2_communication_bits", sizes["ECDH M2 bits"]],
        ["p256_ecdh", "total_user_cloud_bits", sizes["ECDH total bits"]],
        ["paper_ju_park", "reported_complete_protocol_bits", sizes["Paper total bits"]],
    ]

    with OUT.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["scheme", "metric", "value"]); w.writerows(timing_rows + size_rows)

    print("Head-to-head benchmark")
    for row in timing_rows:
        print(f"{row[0]:12s} {row[1]:22s}: {row[2]} us/op")
    hx = float(next(r[2] for r in timing_rows if r[0] == "hash_xor" and r[1] == "end_to_end_round_us"))
    ec = float(next(r[2] for r in timing_rows if r[0] == "p256_ecdh" and r[1] == "end_to_end_round_us"))
    print(f"\nECDH / Hash-XOR end-to-end ratio: {ec/hx:.2f}x")
    print(f"Hash/XOR user-cloud exchange: {sizes['Hash-XOR total bits']} bits")
    print(f"P-256 ECDH user-cloud exchange: {sizes['ECDH total bits']} bits")
    print(f"Ju-Park complete-protocol literature figure: {sizes['Paper total bits']} bits")
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
