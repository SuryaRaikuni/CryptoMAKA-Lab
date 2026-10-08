"""Toy discrete-log demonstration for the faculty presentation.

This is deliberately small and educational. It demonstrates the mathematical
shape of the discrete-log problem; it is not an implementation of Shor's
algorithm and says nothing quantitative about breaking P-256.
"""

from __future__ import annotations

import time


def find_discrete_log(g: int, y: int, p: int) -> int | None:
    value = 1
    for x in range(p):
        if value == y:
            return x
        value = (value * g) % p
    return None


def main():
    # Small prime/group parameters chosen so brute force is immediate.
    p = 2147483647
    g = 5
    secret_x = 123456789
    y = pow(g, secret_x, p)

    start = time.perf_counter()
    recovered = find_discrete_log(g, y, p)
    elapsed_ms = (time.perf_counter() - start) * 1000

    print("Toy discrete-log demonstration")
    print(f"p                 = {p}")
    print(f"generator g       = {g}")
    print(f"public value y    = {y}")
    print(f"hidden exponent x = {secret_x}")
    print(f"recovered x       = {recovered}")
    print(f"brute-force time   = {elapsed_ms:.2f} ms")
    print()
    print("Interpretation:")
    print("  Small groups can be brute-forced classically.")
    print("  Real P-256 uses a vastly larger group and is not brute-forceable this way.")
    print("  A sufficiently large fault-tolerant quantum computer could use Shor's algorithm")
    print("  against the elliptic-curve discrete-log assumption underlying ECDH.")
    print("  This script is only a visual teaching aid; it is not a quantum attack.")


if __name__ == "__main__":
    main()
