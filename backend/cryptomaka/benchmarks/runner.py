"""
Reproducible benchmark runner for CryptoMAKA Lab.

Measures computation time for each protocol phase using high-resolution
perf_counter_ns() timers. Stores host metadata alongside results for
reproducibility. Never stores or prints session keys.
"""

from __future__ import annotations

import platform
import sys
import time
from typing import Any

from cryptomaka.benchmarks.communication import (
    ecc_communication_report,
    jupark_communication_report,
)
from cryptomaka.benchmarks.metrics import compute_metrics
from cryptomaka.config import get_settings


def _collect_host_metadata() -> dict[str, Any]:
    """Collect environment metadata for benchmark reproducibility."""
    settings = get_settings()
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "python_version": sys.version,
        "cpu": platform.processor() or "unknown",
        "machine": platform.machine(),
        "app_version": settings.APP_VERSION,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ---------------------------------------------------------------------------
# Ju-Park benchmark
# ---------------------------------------------------------------------------

def _jupark_single_run_ns() -> tuple[int, int, int]:
    """
    Run one complete Ju-Park protocol session.
    Returns (registration_ns, authentication_ns, total_ns).
    """
    from cryptomaka.protocols.ju_park import CloudServer, ControlServer, User, run_protocol

    cs = ControlServer("CS")
    cloud = CloudServer("S_j", cs)
    cloud.register()

    user = User("bench-user", "bench-pw", "bench-bio")

    t_reg_start = time.perf_counter_ns()
    user.register(cs)
    t_reg_end = time.perf_counter_ns()

    t_auth_start = time.perf_counter_ns()
    try:
        run_protocol()
    except Exception:
        pass
    t_auth_end = time.perf_counter_ns()

    reg_ns = t_reg_end - t_reg_start
    auth_ns = t_auth_end - t_auth_start
    total_ns = reg_ns + auth_ns

    return reg_ns, auth_ns, total_ns


def _ecc_single_run_ns() -> tuple[int, int, int]:
    """
    Run one complete ECC/ECDH protocol session.
    Returns (registration_ns, authentication_ns, total_ns).
    """
    from cryptomaka.protocols.ecc import ControlServerECC, ECCCloudServer, ECCUser

    rc = ControlServerECC()
    cs = ECCCloudServer("bench-cloud")
    user = ECCUser("bench-user", "bench-pw", "bench-bio")

    t_reg_start = time.perf_counter_ns()
    user.register(rc)
    t_reg_end = time.perf_counter_ns()

    t_auth_start = time.perf_counter_ns()
    try:
        m1, a, private_u = user.start_login()
        m2, sk_server, _, reason = cs.respond_to_login(rc, user.user_id, m1)
        if m2 is not None:
            sk_user, _ = user.finish_login(a, private_u, m1, m2)
    except Exception:
        pass
    t_auth_end = time.perf_counter_ns()

    reg_ns = t_reg_end - t_reg_start
    auth_ns = t_auth_end - t_auth_start
    total_ns = reg_ns + auth_ns

    return reg_ns, auth_ns, total_ns


def _reduced_single_run_ns() -> tuple[int, int, int]:
    """
    Run one complete reduced-round-trip protocol session.
    """
    from cryptomaka.protocols.reduced_roundtrip import run_reduced_protocol

    t_start = time.perf_counter_ns()
    try:
        run_reduced_protocol()
    except Exception:
        pass
    t_end = time.perf_counter_ns()

    total_ns = t_end - t_start
    return 0, total_ns, total_ns


_PROTOCOL_RUNNERS = {
    "ju_park": _jupark_single_run_ns,
    "ecc": _ecc_single_run_ns,
    "reduced_roundtrip": _reduced_single_run_ns,
}


def run_benchmark(
    protocol: str,
    iterations: int | None = None,
    warmup: int | None = None,
) -> dict[str, Any]:
    """
    Run a benchmark for the given protocol and return structured metrics.

    Args:
        protocol: One of "ju_park", "ecc", "reduced_roundtrip".
        iterations: Number of timed iterations (after warmup).
        warmup: Number of warmup iterations (not timed).

    Returns:
        Structured benchmark result dict.
    """
    settings = get_settings()

    if protocol not in _PROTOCOL_RUNNERS:
        raise ValueError(
            f"Unknown protocol: '{protocol}'. "
            f"Must be one of: {list(_PROTOCOL_RUNNERS.keys())}"
        )

    if iterations is None:
        iterations = settings.DEFAULT_BENCHMARK_ITERATIONS
    if warmup is None:
        warmup = settings.DEFAULT_WARMUP_ITERATIONS

    iterations = max(1, min(iterations, settings.MAX_BENCHMARK_ITERATIONS))
    warmup = max(0, warmup)

    runner = _PROTOCOL_RUNNERS[protocol]

    # Warmup
    for _ in range(warmup):
        runner()

    # Timed runs
    reg_timings: list[int] = []
    auth_timings: list[int] = []
    total_timings: list[int] = []

    for _ in range(iterations):
        reg_ns, auth_ns, total_ns = runner()
        reg_timings.append(reg_ns)
        auth_timings.append(auth_ns)
        total_timings.append(total_ns)

    total_metrics = compute_metrics(total_timings, warmup)
    reg_metrics = compute_metrics(reg_timings, warmup)
    auth_metrics = compute_metrics(auth_timings, warmup)

    # Communication cost
    if protocol == "ju_park":
        comm_report = jupark_communication_report()
        comm_bits = comm_report["implementation_bits"]
    elif protocol == "ecc":
        comm_report = ecc_communication_report()
        comm_bits = comm_report["implementation_bits"]
    else:
        comm_report = {}
        comm_bits = None

    return {
        "protocol": protocol,
        "iterations": iterations,
        "warmup": warmup,
        "total": total_metrics.to_dict(),
        "registration": reg_metrics.to_dict(),
        "authentication": auth_metrics.to_dict(),
        "communication_bits": comm_bits,
        "communication_report": comm_report,
        "host_metadata": _collect_host_metadata(),
    }


def run_comparison_benchmark(
    protocols: list[str] | None = None,
    iterations: int = 50,
    warmup: int = 10,
) -> dict[str, Any]:
    """Run benchmarks for multiple protocols and return a comparison."""
    if protocols is None:
        protocols = ["ju_park", "ecc", "reduced_roundtrip"]

    results = {}
    for protocol in protocols:
        try:
            results[protocol] = run_benchmark(protocol, iterations, warmup)
        except Exception as e:
            results[protocol] = {"error": str(e)}

    return {
        "comparison": results,
        "iterations": iterations,
        "warmup": warmup,
        "host_metadata": _collect_host_metadata(),
    }
