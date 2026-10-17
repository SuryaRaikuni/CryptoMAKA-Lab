"""Pydantic schemas for benchmark endpoints."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class BenchmarkRunRequest(BaseModel):
    protocol: str = Field(..., description="Protocol: ju_park, ecc, or reduced_roundtrip")
    iterations: int = Field(default=100, ge=1, le=10000)
    warmup: int = Field(default=10, ge=0, le=100)


class BenchmarkMetricsSchema(BaseModel):
    iterations: int
    warmup_iterations: int
    mean_ms: float
    median_ms: float
    min_ms: float
    max_ms: float
    stddev_ms: float
    throughput_ops_per_sec: float


class BenchmarkRunResponse(BaseModel):
    run_id: str
    protocol: str
    iterations: int
    warmup: int
    total: BenchmarkMetricsSchema
    registration: BenchmarkMetricsSchema
    authentication: BenchmarkMetricsSchema
    communication_bits: Optional[int] = None
    communication_report: Optional[dict[str, Any]] = None
    host_metadata: dict[str, Any]


class ComparisonRunRequest(BaseModel):
    protocols: list[str] = Field(
        default=["ju_park", "ecc", "reduced_roundtrip", "ml_kem"]
    )
    iterations: int = Field(default=50, ge=1, le=5000)
    warmup: int = Field(default=10, ge=0, le=100)


class NetworkProfileSchema(BaseModel):
    id: str
    name: str
    technology: str
    bandwidth_kbps: float
    downlink_kbps: float
    base_rtt_ms: float
    mtu_bytes: int
    packet_loss_rate: float
    description: str


class HardwareProfileSchema(BaseModel):
    id: str
    name: str
    architecture: str
    clock_mhz: float
    voltage: float
    active_cpu_ma: float
    radio_tx_ma: float
    radio_rx_ma: float
    sleep_ua: float
    description: str


class ProtocolNetworkEnergySimulationSchema(BaseModel):
    protocol_id: str
    protocol_name: str
    total_wire_bytes: int
    message_count: int
    total_fragments: int
    mtu_exceeded: bool
    compute_time_ms: float
    network_latency_ms: float
    total_latency_ms: float
    cpu_energy_uj: float
    radio_energy_uj: float
    total_energy_uj: float
    total_energy_mj: float
    estimated_battery_lifetime_years: float
    duty_cycle_warning: Optional[str] = None


class NetworkEnergySimulateRequest(BaseModel):
    network_profile: str = Field(default="nbiot", description="Wireless network profile ID")
    hardware_profile: str = Field(default="cortex_m4", description="Embedded MCU profile ID")
    handshakes_per_day: int = Field(default=24, ge=1, le=100000, description="Duty cycle handshakes/day")
    battery_capacity_mah: float = Field(default=220.0, ge=1.0, le=50000.0, description="Battery capacity in mAh")


class NetworkEnergySimulateResponse(BaseModel):
    network_profile: NetworkProfileSchema
    hardware_profile: HardwareProfileSchema
    battery_capacity_mah: float
    handshakes_per_day: int
    results: dict[str, ProtocolNetworkEnergySimulationSchema]


class NetworkEnergyProfilesResponse(BaseModel):
    network_profiles: list[NetworkProfileSchema]
    hardware_profiles: list[HardwareProfileSchema]

