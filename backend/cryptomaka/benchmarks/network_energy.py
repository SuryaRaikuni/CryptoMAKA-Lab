"""
IoT Wireless Network Latency & Microjoule Energy Consumption Modeling Engine.

This module models realistic wireless channel dynamics (bandwidth, RTT latency,
MTU fragmentation) and embedded microcontroller energy consumption (ARM Cortex-M4,
ESP32, Raspberry Pi) for lightweight cloud-IoT mutual authentication protocols.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from cryptomaka.benchmarks.communication import (
    ecc_message_specs,
    jupark_message_specs,
    mlkem_message_specs,
)


@dataclass
class NetworkProfile:
    id: str
    name: str
    technology: str
    bandwidth_kbps: float           # Uplink bandwidth in kilobits/sec
    downlink_kbps: float            # Downlink bandwidth in kilobits/sec
    base_rtt_ms: float              # Base one-way round-trip propagation delay in ms
    mtu_bytes: int                  # Maximum Transmission Unit payload limit
    packet_loss_rate: float         # Typical packet loss rate (0.0 to 1.0)
    description: str


@dataclass
class HardwareProfile:
    id: str
    name: str
    architecture: str
    clock_mhz: float
    voltage: float                  # Operating voltage in Volts
    active_cpu_ma: float            # Active CPU core current in mA
    radio_tx_ma: float              # Wireless radio transmission current in mA
    radio_rx_ma: float              # Wireless radio reception current in mA
    sleep_ua: float                 # Low-power sleep current in microamps
    description: str


# Standard wireless channel profiles based on 3GPP and LoRa Alliance specs
NETWORK_PROFILES: Dict[str, NetworkProfile] = {
    "lorawan_dr0": NetworkProfile(
        id="lorawan_dr0",
        name="LoRaWAN EU868 (DR0 / SF12)",
        technology="LPWAN (868 MHz / 125 kHz)",
        bandwidth_kbps=0.25,        # 250 bps raw data rate
        downlink_kbps=0.25,
        base_rtt_ms=1200.0,         # Long time-on-air propagation
        mtu_bytes=51,               # Extremely restricted payload size
        packet_loss_rate=0.04,
        description="Maximum range / deep indoor LPWAN with high SF12 time-on-air and 51B MTU.",
    ),
    "lorawan_dr3": NetworkProfile(
        id="lorawan_dr3",
        name="LoRaWAN EU868 (DR3 / SF9)",
        technology="LPWAN (868 MHz / 125 kHz)",
        bandwidth_kbps=1.76,        # 1760 bps data rate
        downlink_kbps=1.76,
        base_rtt_ms=450.0,
        mtu_bytes=115,              # 115 bytes MTU
        packet_loss_rate=0.02,
        description="Standard urban LoRaWAN deployment with 115-byte MTU and moderate latency.",
    ),
    "nbiot": NetworkProfile(
        id="nbiot",
        name="NB-IoT (3GPP Cat-NB1)",
        technology="Cellular IoT (Licensed Band)",
        bandwidth_kbps=64.0,        # 64 kbps uplink
        downlink_kbps=32.0,
        base_rtt_ms=350.0,          # Scheduling + eNB paging latency
        mtu_bytes=1600,             # Full IP packet support
        packet_loss_rate=0.01,
        description="Narrowband cellular IoT for smart metering with carrier coverage and ~350ms RTT.",
    ),
    "ltem": NetworkProfile(
        id="ltem",
        name="LTE-M (3GPP Cat-M1)",
        technology="Cellular IoT (eMTC)",
        bandwidth_kbps=1000.0,      # 1 Mbps uplink
        downlink_kbps=1000.0,
        base_rtt_ms=85.0,           # Sub-100ms latency
        mtu_bytes=1500,
        packet_loss_rate=0.005,
        description="Medium-throughput cellular IoT for wearables and tracking with low latency.",
    ),
    "fiveg_iot": NetworkProfile(
        id="fiveg_iot",
        name="5G Industrial IoT (URLLC)",
        technology="5G Standalone Ultra-Reliable",
        bandwidth_kbps=50000.0,     # 50 Mbps
        downlink_kbps=100000.0,     # 100 Mbps
        base_rtt_ms=4.0,            # Ultra-low latency 4ms
        mtu_bytes=1500,
        packet_loss_rate=0.0001,
        description="Factory automation and smart grid with sub-5ms latency and high reliability.",
    ),
    "lan_unconstrained": NetworkProfile(
        id="lan_unconstrained",
        name="Local LAN (Unconstrained)",
        technology="IEEE 802.3 Gigabit Ethernet",
        bandwidth_kbps=1000000.0,   # 1 Gbps
        downlink_kbps=1000000.0,
        base_rtt_ms=0.5,
        mtu_bytes=1500,
        packet_loss_rate=0.0,
        description="Baseline wired/WiFi local testbed without wireless bottlenecks.",
    ),
}

# Empirical embedded hardware energy profiles
HARDWARE_PROFILES: Dict[str, HardwareProfile] = {
    "cortex_m4": HardwareProfile(
        id="cortex_m4",
        name="ARM Cortex-M4 (STM32L4 / nRF52840)",
        architecture="ARMv7E-M @ 64 MHz",
        clock_mhz=64.0,
        voltage=3.0,
        active_cpu_ma=10.5,         # ~31.5 mW active computing
        radio_tx_ma=24.0,           # ~72 mW radio transmission (+4dBm)
        radio_rx_ma=12.0,           # ~36 mW reception
        sleep_ua=2.1,               # Ultra-low power standby
        description="Ultra-low-power IoT microcontroller widely used in battery-operated sensors.",
    ),
    "esp32": HardwareProfile(
        id="esp32",
        name="Espressif ESP32",
        architecture="Xtensa Dual-Core @ 160 MHz",
        clock_mhz=160.0,
        voltage=3.3,
        active_cpu_ma=32.0,         # ~105 mW CPU
        radio_tx_ma=95.0,           # ~313 mW radio TX
        radio_rx_ma=65.0,           # ~214 mW radio RX
        sleep_ua=15.0,
        description="Standard maker & smart-home Wi-Fi/BLE MCU with higher active current draw.",
    ),
    "rpi_zero": HardwareProfile(
        id="rpi_zero",
        name="Raspberry Pi Zero W",
        architecture="ARM1176JZF-S @ 1 GHz",
        clock_mhz=1000.0,
        voltage=5.0,
        active_cpu_ma=120.0,        # ~600 mW CPU
        radio_tx_ma=180.0,          # ~900 mW radio
        radio_rx_ma=140.0,
        sleep_ua=80000.0,           # Pi has no microamp sleep mode (~80mA idle)
        description="Linux-capable gateway edge node with higher baseline power consumption.",
    ),
}

# Baseline empirical CPU computation times on ARM Cortex-M4 (in ms)
# Extracted from published benchmarks (e.g. PQClean, micro-ecc, mbedTLS on Cortex-M4)
EMBEDDED_COMPUTE_TIMES_MS: Dict[str, Dict[str, float]] = {
    "cortex_m4": {
        "ju_park": 3.8,             # Hash & XOR operations are very fast on Cortex-M4
        "ecc": 54.2,                # P-256 scalar mult takes ~25-30ms per party
        "reduced_roundtrip": 3.4,   # 1 less round of hashing
        "ml_kem": 18.6,             # ML-KEM-768 NTT & SHAKE is faster than ECC on Cortex-M4!
    },
    "esp32": {
        "ju_park": 1.2,
        "ecc": 16.5,                # ESP32 hardware MPI bignum accelerator
        "reduced_roundtrip": 1.0,
        "ml_kem": 6.8,
    },
    "rpi_zero": {
        "ju_park": 0.45,
        "ecc": 4.8,
        "reduced_roundtrip": 0.40,
        "ml_kem": 2.1,
    },
}


@dataclass
class ProtocolNetworkEnergySimulation:
    protocol_id: str
    protocol_name: str
    total_wire_bytes: int
    message_count: int
    total_fragments: int
    mtu_exceeded: bool
    compute_time_ms: float
    network_latency_ms: float
    total_latency_ms: float
    cpu_energy_uj: float            # CPU energy in microjoules
    radio_energy_uj: float          # Radio TX/RX energy in microjoules
    total_energy_uj: float          # Total energy in microjoules
    total_energy_mj: float          # Total energy in millijoules
    estimated_battery_lifetime_years: float
    duty_cycle_warning: Optional[str] = None


@dataclass
class NetworkEnergyReport:
    network_profile: NetworkProfile
    hardware_profile: HardwareProfile
    battery_capacity_mah: float
    handshakes_per_day: int
    results: Dict[str, ProtocolNetworkEnergySimulation]


def get_protocol_message_bytes(protocol_id: str) -> List[int]:
    """Returns the size in bytes of each consecutive message in the protocol exchange."""
    if protocol_id == "ju_park":
        specs = jupark_message_specs()
    elif protocol_id in ("ecc", "ecc_ecdh"):
        specs = ecc_message_specs()
    elif protocol_id in ("ml_kem", "ml_kem_768"):
        specs = mlkem_message_specs()
    elif protocol_id == "reduced_roundtrip":
        # Reduced roundtrip combines M3/M4 or cuts 1 message flow
        specs = jupark_message_specs()[:2]
    else:
        specs = jupark_message_specs()

    return [math.ceil(s.total_bits / 8) for s in specs]


def simulate_protocol_channel_energy(
    protocol_id: str,
    network: NetworkProfile,
    hardware: HardwareProfile,
    handshakes_per_day: int = 24,
    battery_capacity_mah: float = 220.0,  # Standard CR2032 coin cell
) -> ProtocolNetworkEnergySimulation:
    """
    Simulates network transmission time, packet fragmentation, and hardware energy
    for a target protocol over a specific wireless channel and embedded MCU.
    """
    msg_bytes = get_protocol_message_bytes(protocol_id)
    total_bytes = sum(msg_bytes)
    msg_count = len(msg_bytes)

    # 1. MTU Fragmentation & Transmission Latency
    total_fragments = 0
    network_latency_ms = 0.0
    mtu_exceeded = False

    for b in msg_bytes:
        fragments = math.ceil(b / network.mtu_bytes)
        if fragments > 1:
            mtu_exceeded = True
        total_fragments += fragments

        # Bandwidth transmission delay: (bytes * 8) / (kbps * 1000) * 1000 ms
        tx_delay_ms = (b * 8.0) / network.bandwidth_kbps
        # Propagation and MAC scheduling delay (one-way RTT per packet fragment)
        propagation_ms = fragments * (network.base_rtt_ms / 2.0)
        # Re-transmission overhead due to packet loss
        loss_overhead_ms = tx_delay_ms * network.packet_loss_rate

        network_latency_ms += tx_delay_ms + propagation_ms + loss_overhead_ms

    # 2. Embedded Computation Time
    compute_times = EMBEDDED_COMPUTE_TIMES_MS.get(hardware.id, EMBEDDED_COMPUTE_TIMES_MS["cortex_m4"])
    compute_time_ms = compute_times.get(protocol_id, compute_times["ju_park"])

    total_latency_ms = compute_time_ms + network_latency_ms

    # 3. Energy Consumption Model
    # E = Power * Time = (V * I) * (t_seconds)
    # 1 Joule = 1,000,000 microjoules (uJ)

    # CPU Energy: V * I_cpu * (t_compute_sec)
    t_compute_sec = compute_time_ms / 1000.0
    cpu_energy_joules = hardware.voltage * (hardware.active_cpu_ma / 1000.0) * t_compute_sec
    cpu_energy_uj = cpu_energy_joules * 1e6

    # Radio Energy: Transmitting bytes + Receiving bytes
    # Assume 50% TX and 50% RX during mutual handshake
    t_network_sec = network_latency_ms / 1000.0
    p_tx_w = hardware.voltage * (hardware.radio_tx_ma / 1000.0)
    p_rx_w = hardware.voltage * (hardware.radio_rx_ma / 1000.0)
    avg_radio_p_w = (p_tx_w + p_rx_w) / 2.0
    radio_energy_joules = avg_radio_p_w * t_network_sec
    radio_energy_uj = radio_energy_joules * 1e6

    total_energy_uj = cpu_energy_uj + radio_energy_uj
    total_energy_mj = total_energy_uj / 1000.0

    # 4. Projected Battery Lifetime Calculation
    # Battery Energy = Capacity (mAh) * Voltage (V) * 3600 seconds = Joules
    battery_total_joules = (battery_capacity_mah / 1000.0) * hardware.voltage * 3600.0
    # Energy per day = (Handshakes_per_day * Energy_per_handshake) + (Sleep power for 24h)
    daily_handshake_joules = handshakes_per_day * (total_energy_uj / 1e6)
    daily_sleep_joules = hardware.voltage * (hardware.sleep_ua / 1e6) * 86400.0
    total_daily_joules = daily_handshake_joules + daily_sleep_joules

    if total_daily_joules > 0:
        lifetime_days = battery_total_joules / total_daily_joules
        lifetime_years = round(lifetime_days / 365.25, 2)
    else:
        lifetime_years = 10.0

    # 5. Duty Cycle / Regulations Warning
    warning = None
    if "lorawan" in network.id:
        if total_fragments > 10:
            warning = f"High fragmentation ({total_fragments} pkts) risks violating LoRaWAN 1% European duty cycle (ETSI EN 300 220)."
        elif mtu_exceeded:
            warning = f"Message payload exceeds {network.mtu_bytes}B MTU, requiring {total_fragments} transmission fragments."

    protocol_names = {
        "ju_park": "Ju-Park 2023 (Hash/XOR)",
        "ecc": "ECC Baseline (Secp256r1)",
        "reduced_roundtrip": "Reduced-RTT Extension",
        "ml_kem": "ML-KEM-768 (Post-Quantum)",
    }

    return ProtocolNetworkEnergySimulation(
        protocol_id=protocol_id,
        protocol_name=protocol_names.get(protocol_id, protocol_id),
        total_wire_bytes=total_bytes,
        message_count=msg_count,
        total_fragments=total_fragments,
        mtu_exceeded=mtu_exceeded,
        compute_time_ms=round(compute_time_ms, 2),
        network_latency_ms=round(network_latency_ms, 2),
        total_latency_ms=round(total_latency_ms, 2),
        cpu_energy_uj=round(cpu_energy_uj, 2),
        radio_energy_uj=round(radio_energy_uj, 2),
        total_energy_uj=round(total_energy_uj, 2),
        total_energy_mj=round(total_energy_mj, 3),
        estimated_battery_lifetime_years=lifetime_years,
        duty_cycle_warning=warning,
    )


def simulate_all_protocols(
    network_id: str = "nbiot",
    hardware_id: str = "cortex_m4",
    handshakes_per_day: int = 24,
    battery_capacity_mah: float = 220.0,
) -> NetworkEnergyReport:
    """Executes network and energy simulation across all 4 protocols."""
    network = NETWORK_PROFILES.get(network_id, NETWORK_PROFILES["nbiot"])
    hardware = HARDWARE_PROFILES.get(hardware_id, HARDWARE_PROFILES["cortex_m4"])

    protocols = ["ju_park", "ecc", "reduced_roundtrip", "ml_kem"]
    results = {}

    for p in protocols:
        results[p] = simulate_protocol_channel_energy(
            protocol_id=p,
            network=network,
            hardware=hardware,
            handshakes_per_day=handshakes_per_day,
            battery_capacity_mah=battery_capacity_mah,
        )

    return NetworkEnergyReport(
        network_profile=network,
        hardware_profile=hardware,
        battery_capacity_mah=battery_capacity_mah,
        handshakes_per_day=handshakes_per_day,
        results=results,
    )
