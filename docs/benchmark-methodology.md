# Benchmark Methodology & Performance Metrics

This document outlines the experimental benchmarking methodology implemented in **CryptoMAKA Lab** to produce reproducible performance and communication overhead measurements.

---

## 1. Timing Measurement Infrastructure

All execution timings are collected using Python's high-resolution monotonic performance counter:
```python
t_start = time.perf_counter_ns()
# ... protocol execution ...
t_end = time.perf_counter_ns()
elapsed_ms = (t_end - t_start) / 1_000_000.0
```

### 1.1 Platform Characteristics & Resolution
- **Windows:** Backed by `QueryPerformanceCounter` with sub-microsecond resolution ($< 100\text{ ns}$).
- **Linux:** Backed by `clock_gettime(CLOCK_MONOTONIC_RAW)`.
- **Reproducibility Guarantee:** All benchmark runs capture CPU architecture, OS kernel release, and Python version in the JSON output metadata.

---

## 2. Statistical Analysis & Outlier Control

To prevent CPU frequency scaling, cold caches, and OS context switching from skewing benchmark measurements:
1. **Warmup Cycles:** A default of $10$ unmeasured iterations are executed before measurements begin to warm caches and JIT paths.
2. **Batch Size:** Standard benchmark runs execute $N = 100$ or $N = 1,000$ iterations.
3. **Statistical Metrics Computed:**
   - **Arithmetic Mean ($\mu$):** General execution expectation.
   - **Median:** Robust metric resistant to OS scheduling interrupts.
   - **Minimum & Maximum:** Lower bound represents hardware baseline capacity; maximum identifies outlier latency spikes.
   - **Sample Standard Deviation ($\sigma$):** Indicator of measurement jitter.
   - **Throughput:** Operations per second calculated as $\frac{N}{\sum T_i}$.

---

## 3. Communication Cost Methodology: Published vs. Measured

### 3.1 Academic Distinction
- **Published Reference Cost ($3,776$ bits):** The authoritative figure reported in Ju \& Park (Sensors 2023, Table 5).
- **Implementation Measured Cost ($4,224$ bits):** The actual bit size measured in this normalized reconstruction.

### 3.2 Rationale for Field Normalization
In the original publication, bit lengths for certain nonces and hashed identities are represented with compressed parameters in theoretical tables. To guarantee byte-aligned, safe cryptographic XOR operations without bit truncation or padding ambiguities, our faithful software implementation normalizes all pseudo-identities, masked nonces, and authenticators to 256 bits (SHA-256 block size).

| Message | Published Paper Reference | Normalized Implementation | Field Breakdown |
|---|---|---|---|
| **$M_1$** | $1,056$ bits | $1,056$ bits | $PID_i (256) + B_1 (256) + B_2 (256) + V_1 (256) + TS_1 (32)$ |
| **$M_2$** | $1,600$ bits | $1,600$ bits | $M_1 (1056) + B_3 (256) + V_2 (256) + TS_2 (32)$ |
| **$M_3$ / $M_4$** | $1,120$ bits | $1,568$ bits | $B_6(256) + B_7(256) + B_8(256) + B_9(256) + V_3(256) + V_4(256) + TS_3(32)$ |
| **Total** | **$3,776$ bits** | **$4,224$ bits** | Full authentication exchange |

---

## 4. Reproducibility Checklist & Artifact Generation

To guarantee that any academic researcher or evaluator can reproduce the benchmarks reported in faculty reviews and publications, follow this standardized checklist:

### 4.1 Reproducibility Steps
- [ ] **Clean Environment:** Use a dedicated virtual environment with locked dependencies (`pip install -e ".[dev]"`).
- [ ] **CPU Frequency Pinning (Linux/WSL):** If running on Linux or bare-metal servers, set governor to performance (`cpupower frequency-set -g performance`) to eliminate clock throttling variance.
- [ ] **Background Load Minimization:** Close unnecessary IDE extensions, browser tabs, or concurrent build processes.
- [ ] **Execute Baseline Configuration:**
  ```bash
  # Run automated headless benchmark suite
  python -m cryptomaka.benchmarks.runner --iterations 1000 --warmup 10 --output research/results/benchmark_run_latest.json
  ```
- [ ] **Verify Consistency:** Ensure standard deviation $\sigma < 0.15 \cdot \mu$ across repeated batches.

### 4.2 Benchmark Output Artifact Schema
Every benchmark execution generates an immutable JSON structure:
```json
{
  "timestamp": "2026-10-11T14:00:00Z",
  "environment": {
    "platform": "Windows-10-10.0.26100-SP0",
    "processor": "Intel64 Family 6 Model 151 Stepping 2",
    "python_version": "3.12.6"
  },
  "config": {
    "iterations": 1000,
    "warmup": 10
  },
  "results": [
    {
      "protocol": "ju_park",
      "mean_latency_ms": 1.84,
      "median_latency_ms": 1.78,
      "min_latency_ms": 1.52,
      "max_latency_ms": 3.41,
      "std_dev_ms": 0.18,
      "throughput_ops_sec": 543.47,
      "communication_bits": 4224
    }
  ]
}
```
