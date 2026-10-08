"""
Statistical metrics helpers for benchmark results.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass


@dataclass
class BenchmarkMetrics:
    iterations: int
    warmup_iterations: int
    mean_ms: float
    median_ms: float
    min_ms: float
    max_ms: float
    stddev_ms: float
    throughput_ops_per_sec: float

    def to_dict(self) -> dict:
        return {
            "iterations": self.iterations,
            "warmup_iterations": self.warmup_iterations,
            "mean_ms": round(self.mean_ms, 4),
            "median_ms": round(self.median_ms, 4),
            "min_ms": round(self.min_ms, 4),
            "max_ms": round(self.max_ms, 4),
            "stddev_ms": round(self.stddev_ms, 4),
            "throughput_ops_per_sec": round(self.throughput_ops_per_sec, 2),
        }


def compute_metrics(
    timings_ns: list[int],
    warmup_count: int,
) -> BenchmarkMetrics:
    """
    Compute statistical metrics from a list of nanosecond timings.
    Warmup iterations should already be excluded from timings_ns.
    """
    if not timings_ns:
        raise ValueError("Empty timings list")

    timings_ms = [t / 1_000_000 for t in timings_ns]
    n = len(timings_ms)
    mean = statistics.mean(timings_ms)
    median = statistics.median(timings_ms)
    stddev = statistics.pstdev(timings_ms) if n > 1 else 0.0
    minimum = min(timings_ms)
    maximum = max(timings_ms)
    throughput = 1000.0 / mean if mean > 0 else 0.0

    return BenchmarkMetrics(
        iterations=n,
        warmup_iterations=warmup_count,
        mean_ms=mean,
        median_ms=median,
        min_ms=minimum,
        max_ms=maximum,
        stddev_ms=stddev,
        throughput_ops_per_sec=throughput,
    )
