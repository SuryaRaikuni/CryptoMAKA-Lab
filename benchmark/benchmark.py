"""
Performance benchmark for the MAKA skeleton: computation time per phase
and communication cost per message, checked against the paper's reported
total communication cost (3776 bits, Ju & Park, Sensors 2023, 23:9766).

Two caveats worth stating explicitly in the report:
1. This skeleton calls rc.verify_login() directly (an in-process function
   call) instead of sending an explicit CS<->RC message over the wire, so
   the communication-cost total below UNDER-counts a real 3-hop
   deployment -- there's no session-key confirmation message either.
2. "Bits per field" use the standard convention this literature uses for
   cost tables: hash output = 256 bits (SHA-256), timestamp = 32 bits.
   Nonce/identity sizes below are measured from the actual skeleton
   output. Swap the assumed constants for the paper's own table once you
   have it open.
"""

import time
from maka_skeleton import ControlServer, CloudServer, User

N_TIMING = 2000       # iterations for the registration-only timing
N_ROUND_TRIP = 500    # iterations for the full end-to-end timing

HASH_BITS = 256
TIMESTAMP_BITS = 32
PAPER_TOTAL_BITS = 3776   # Ju & Park's reported total communication cost


def avg_time_us(fn, n):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    elapsed = time.perf_counter() - start
    return (elapsed / n) * 1e6  # microseconds/op


def bench_computation():
    rc = ControlServer()
    alice = User("alice", "correct-horse-battery", "fingerprint-template-xyz")

    t_register = avg_time_us(lambda: alice.register(rc), N_TIMING)

    cs = CloudServer("cloud-server-1", rc.register_cloud_server("cloud-server-1"))

    def full_round():
        u = User("bench-user", "pw", "bio")
        u.register(rc)
        m1, _ = u.start_login()
        cs.respond_to_login(rc, u.id, m1["Ni"], m1["T1"], m1["Vi"])

    t_full_round = avg_time_us(full_round, N_ROUND_TRIP)

    print("Computation time (average over repeated runs, this machine):")
    print(f"  registration only                              : {t_register:8.2f} us/op")
    print(f"  register + login + verify + key-agreement (e2e): {t_full_round:8.2f} us/op")
    return t_register, t_full_round


def bit_len_hex(hexstr: str) -> int:
    return len(hexstr) * 4


def bench_communication():
    rc = ControlServer()
    cs = CloudServer("cloud-server-1", rc.register_cloud_server("cloud-server-1"))
    alice = User("alice", "correct-horse-battery", "fingerprint-template-xyz")
    alice.register(rc)
    m1, Ai = alice.start_login()
    m2, sk, reason = cs.respond_to_login(rc, alice.id, m1["Ni"], m1["T1"], m1["Vi"])

    Vi_bits, Ni_bits, T1_bits = HASH_BITS, bit_len_hex(m1["Ni"]), TIMESTAMP_BITS
    Nc_bits, T2_bits = bit_len_hex(m2["Nc"]), TIMESTAMP_BITS

    m1_total = Vi_bits + Ni_bits + T1_bits
    m2_total = Nc_bits + T2_bits
    round_trip_total = m1_total + m2_total

    print("\nCommunication cost (User <-> CS, this skeleton):")
    print(f"  M1 (User->CS): Vi={Vi_bits} + Ni={Ni_bits} + T1={T1_bits} bits = {m1_total} bits")
    print(f"  M2 (CS->User): Nc={Nc_bits} + T2={T2_bits} bits = {m2_total} bits")
    print(f"  round-trip total                 : {round_trip_total} bits")
    print(f"  paper's reported total (23:9766) : {PAPER_TOTAL_BITS} bits")
    print(f"  this skeleton is {round_trip_total / PAPER_TOTAL_BITS:.1%} of the paper's figure")
    print("  (lower mainly because there's no explicit CS<->RC wire leg or")
    print("   session-key confirmation message here -- see file docstring)")
    return round_trip_total


if __name__ == "__main__":
    bench_computation()
    bench_communication()
