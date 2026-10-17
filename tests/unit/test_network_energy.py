"""
Unit tests for IoT Wireless Latency and Microjoule Energy Consumption Modeling.
"""

import pytest

from cryptomaka.benchmarks.network_energy import (
    HARDWARE_PROFILES,
    NETWORK_PROFILES,
    get_protocol_message_bytes,
    simulate_all_protocols,
    simulate_protocol_channel_energy,
)


def test_network_profiles_exist():
    """Ensure standard LPWAN, cellular, and LAN profiles exist."""
    required = ["lorawan_dr0", "lorawan_dr3", "nbiot", "ltem", "fiveg_iot", "lan_unconstrained"]
    for p in required:
        assert p in NETWORK_PROFILES
        prof = NETWORK_PROFILES[p]
        assert prof.bandwidth_kbps > 0
        assert prof.base_rtt_ms >= 0
        assert prof.mtu_bytes > 0


def test_hardware_profiles_exist():
    """Ensure embedded microcontroller hardware profiles exist."""
    required = ["cortex_m4", "esp32", "rpi_zero"]
    for h in required:
        assert h in HARDWARE_PROFILES
        prof = HARDWARE_PROFILES[h]
        assert prof.voltage > 0
        assert prof.active_cpu_ma > 0
        assert prof.radio_tx_ma > 0


def test_message_bytes_calculation():
    """Ensure wire bytes are non-zero and match expected order of magnitude."""
    for proto in ["ju_park", "ecc", "ml_kem", "reduced_roundtrip"]:
        b = get_protocol_message_bytes(proto)
        assert len(b) >= 2
        total = sum(b)
        assert total > 100
        if proto == "ml_kem":
            # ML-KEM includes public keys and ciphertexts (> 2000 bytes)
            assert total > 2000


def test_lorawan_dr0_mtu_fragmentation():
    """Verify that ML-KEM severely fragments over LoRaWAN 51-byte MTU."""
    lora = NETWORK_PROFILES["lorawan_dr0"]
    m4 = HARDWARE_PROFILES["cortex_m4"]

    jupark_sim = simulate_protocol_channel_energy("ju_park", lora, m4)
    mlkem_sim = simulate_protocol_channel_energy("ml_kem", lora, m4)

    assert jupark_sim.total_fragments < mlkem_sim.total_fragments
    assert mlkem_sim.total_fragments >= 20
    assert mlkem_sim.duty_cycle_warning is not None
    assert mlkem_sim.total_latency_ms > jupark_sim.total_latency_ms


def test_nbiot_latency_and_energy():
    """Verify NB-IoT latency and microjoule energy metrics."""
    nbiot = NETWORK_PROFILES["nbiot"]
    m4 = HARDWARE_PROFILES["cortex_m4"]

    sim = simulate_protocol_channel_energy("ju_park", nbiot, m4)
    assert sim.compute_time_ms > 0
    assert sim.network_latency_ms > 0
    assert sim.total_latency_ms == pytest.approx(sim.compute_time_ms + sim.network_latency_ms, 0.05)
    assert sim.cpu_energy_uj > 0
    assert sim.radio_energy_uj > 0
    assert sim.total_energy_uj == pytest.approx(sim.cpu_energy_uj + sim.radio_energy_uj, 0.05)
    assert sim.total_energy_mj == pytest.approx(sim.total_energy_uj / 1000.0, 0.01)
    assert sim.estimated_battery_lifetime_years > 0


def test_simulate_all_protocols():
    """Ensure simulation covers all 4 protocols and returns correct comparative metrics."""
    rep = simulate_all_protocols(network_id="nbiot", hardware_id="cortex_m4", handshakes_per_day=24)
    assert rep.network_profile.id == "nbiot"
    assert rep.hardware_profile.id == "cortex_m4"
    assert set(rep.results.keys()) == {"ju_park", "ecc", "reduced_roundtrip", "ml_kem"}

    # Ju-Park and Reduced-RTT should consume less energy than ML-KEM over cellular IoT
    assert rep.results["ju_park"].total_energy_uj < rep.results["ml_kem"].total_energy_uj
    assert rep.results["reduced_roundtrip"].total_latency_ms <= rep.results["ju_park"].total_latency_ms
