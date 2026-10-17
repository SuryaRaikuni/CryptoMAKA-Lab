"""
Communication cost calculation for MAKA protocols.

The Ju-Park paper (Sensors 2023, 23, 9766) reports a total communication cost
of 3776 bits in Table 5. That value is the published reference figure and is
stored separately from any locally measured values.

This module calculates the communication cost of this implementation's
normalized reconstruction. Differences from the paper's figure arise from:
  1. This reconstruction uses 256-bit SHA-256 hashes for all hash-derived fields.
  2. Nonces are 256 bits in the reconstruction vs. the paper's implicit assumption.
  3. The paper counts some fields at smaller widths (e.g. 128-bit nonces).

Both values are reported side-by-side; they are never merged.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Published reference value from Ju & Park (Sensors 2023, 23, 9766) Table 5.
# This is the authors' reported total; it is not a measurement from this code.
JU_PARK_PUBLISHED_BITS = 3776


@dataclass
class MessageField:
    name: str
    bits: int
    description: str = ""


@dataclass
class MessageSpec:
    name: str
    direction: str
    fields: list[MessageField] = field(default_factory=list)

    @property
    def total_bits(self) -> int:
        return sum(f.bits for f in self.fields)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "direction": self.direction,
            "fields": [
                {"name": f.name, "bits": f.bits, "description": f.description}
                for f in self.fields
            ],
            "total_bits": self.total_bits,
        }


# ---------------------------------------------------------------------------
# Ju-Park message specifications (this implementation's normalized encoding)
# ---------------------------------------------------------------------------

HASH_BITS = 256      # SHA-256
TIMESTAMP_BITS = 32  # Unix timestamp (seconds)
NONCE_BITS = 256     # 32-byte random nonce in this reconstruction


def jupark_message_specs() -> list[MessageSpec]:
    """
    Return message specs for the Ju-Park normalized reconstruction.

    Note: The paper describes messages at a conceptual level.
    Bit widths here reflect this implementation's fixed-width SHA-256 encoding.
    """
    return [
        MessageSpec(
            name="M1",
            direction="User → Cloud",
            fields=[
                MessageField("PIDi", HASH_BITS, "User pseudonym (SHA-256 hash)"),
                MessageField("B1", HASH_BITS, "XOR-masked random nonce ri"),
                MessageField("B2", HASH_BITS, "XOR-masked cloud identifier"),
                MessageField("V1", HASH_BITS, "User authenticator MAC"),
                MessageField("TS1", TIMESTAMP_BITS, "Timestamp"),
            ],
        ),
        MessageSpec(
            name="M2",
            direction="Cloud → Control Server",
            fields=[
                MessageField("M1", HASH_BITS * 4 + TIMESTAMP_BITS, "Forwarded M1 payload"),
                MessageField("B3", HASH_BITS, "XOR-masked cloud nonce rj"),
                MessageField("V2", HASH_BITS, "Cloud authenticator MAC"),
                MessageField("TS2", TIMESTAMP_BITS, "Timestamp"),
            ],
        ),
        MessageSpec(
            name="M3",
            direction="Control Server → Cloud → User",
            fields=[
                MessageField("B6", HASH_BITS, "Masked (rk, ri)"),
                MessageField("B7", HASH_BITS, "Masked common value c1"),
                MessageField("B8", HASH_BITS, "Masked (rj, rk)"),
                MessageField("B9", HASH_BITS, "Masked SIDj"),
                MessageField("V3", HASH_BITS, "Server authenticator for cloud"),
                MessageField("V4", HASH_BITS, "User authenticator"),
                MessageField("TS3", TIMESTAMP_BITS, "Timestamp"),
            ],
        ),
    ]


def ecc_message_specs() -> list[MessageSpec]:
    """
    Return message specs for the ECC/ECDH counterpart.
    P-256 uncompressed public key: 65 bytes = 520 bits.
    """
    EC_PUBLIC_KEY_BITS = 520  # P-256 uncompressed
    NONCE_128_BITS = 128      # 16-byte nonce

    return [
        MessageSpec(
            name="M1",
            direction="User → Cloud",
            fields=[
                MessageField("Pu", EC_PUBLIC_KEY_BITS, "User ephemeral public key (P-256)"),
                MessageField("Ni", NONCE_128_BITS, "User nonce"),
                MessageField("T1", TIMESTAMP_BITS, "Timestamp"),
                MessageField("Vi", HASH_BITS, "User authenticator"),
            ],
        ),
        MessageSpec(
            name="M2",
            direction="Cloud → User",
            fields=[
                MessageField("Pc", EC_PUBLIC_KEY_BITS, "Cloud ephemeral public key (P-256)"),
                MessageField("Nc", NONCE_128_BITS, "Cloud nonce"),
                MessageField("T2", TIMESTAMP_BITS, "Timestamp"),
                MessageField("Vj", HASH_BITS, "Server authenticator"),
            ],
        ),
    ]


def calculate_total_bits(specs: list[MessageSpec]) -> int:
    return sum(s.total_bits for s in specs)


def jupark_communication_report() -> dict:
    specs = jupark_message_specs()
    implementation_bits = calculate_total_bits(specs)
    return {
        "protocol": "ju_park",
        "published_reference_bits": JU_PARK_PUBLISHED_BITS,
        "published_reference_source": "Ju & Park, Sensors 2023, 23(24), 9766, Table 5",
        "implementation_bits": implementation_bits,
        "note": (
            "Difference from published figure is expected: this reconstruction uses "
            "256-bit nonces throughout for XOR-width consistency, while the paper's "
            "table may assume smaller nonce sizes. Published figure is the authoritative "
            "reference; implementation figure reflects this normalized reconstruction."
        ),
        "messages": [s.to_dict() for s in specs],
    }


def ecc_communication_report() -> dict:
    specs = ecc_message_specs()
    total_bits = calculate_total_bits(specs)
    return {
        "protocol": "ecc_ecdh",
        "implementation_bits": total_bits,
        "note": "ECC counterpart — no published reference figure from Ju & Park paper.",
        "messages": [s.to_dict() for s in specs],
    }


# ---------------------------------------------------------------------------
# ML-KEM-768 message specifications (NIST FIPS 203 Table 2 sizes)
# ---------------------------------------------------------------------------

# ML-KEM-768 parameter sizes (bytes)
MLKEM_PUBLIC_KEY_BYTES = 1184
MLKEM_CIPHERTEXT_BYTES = 1088

# Identifier field (ASCII user_id): assume ≤8 chars = 64 bits
MLKEM_UID_BITS = 64
MLKEM_AUTH_BITS = 256   # SHA3-256 authenticator


def mlkem_message_specs() -> list[MessageSpec]:
    """
    Return message specs for the ML-KEM-768 MAKA post-quantum prototype.

    Wire sizes follow NIST FIPS 203 Table 2 (ML-KEM-768):
      - Public key (ek): 1184 bytes = 9472 bits
      - Ciphertext (c):  1088 bytes = 8704 bits
    """
    PK_BITS = MLKEM_PUBLIC_KEY_BYTES * 8    # 9472 bits
    CT_BITS = MLKEM_CIPHERTEXT_BYTES * 8    # 8704 bits

    return [
        MessageSpec(
            name="M1",
            direction="User → Cloud Server",
            fields=[
                MessageField("user_id", MLKEM_UID_BITS, "User identifier (ASCII)"),
                MessageField("PK_u", PK_BITS, "User ML-KEM-768 encapsulation key"),
                MessageField("nonce_u", NONCE_BITS, "User fresh random nonce (256-bit)"),
                MessageField("T1", TIMESTAMP_BITS, "Timestamp"),
                MessageField("Auth_u", MLKEM_AUTH_BITS, "SHA3-256 user authenticator"),
            ],
        ),
        MessageSpec(
            name="M2",
            direction="Cloud Server → Registration Centre",
            fields=[
                MessageField("M1_forwarded", MLKEM_UID_BITS + PK_BITS + NONCE_BITS + TIMESTAMP_BITS + MLKEM_AUTH_BITS, "Forwarded M1 payload"),
            ],
        ),
        MessageSpec(
            name="M3",
            direction="Registration Centre → Cloud Server",
            fields=[
                MessageField("ciphertext", CT_BITS, "ML-KEM-768 ciphertext encapsulating shared secret"),
                MessageField("nonce_cs", NONCE_BITS, "Cloud server fresh nonce"),
                MessageField("T2", TIMESTAMP_BITS, "Timestamp"),
                MessageField("Auth_cs", MLKEM_AUTH_BITS, "SHA3-256 cloud authenticator"),
            ],
        ),
        MessageSpec(
            name="M4",
            direction="Cloud Server → User",
            fields=[
                MessageField("ciphertext", CT_BITS, "Forwarded ciphertext for user decapsulation"),
                MessageField("nonce_cs", NONCE_BITS, "Cloud server nonce"),
                MessageField("T2", TIMESTAMP_BITS, "Timestamp"),
                MessageField("Auth_cs", MLKEM_AUTH_BITS, "SHA3-256 cloud authenticator"),
            ],
        ),
    ]


def mlkem_communication_report() -> dict:
    specs = mlkem_message_specs()
    total_bits = calculate_total_bits(specs)
    return {
        "protocol": "ml_kem_768",
        "implementation_bits": total_bits,
        "note": (
            "Post-quantum ML-KEM-768 prototype (NIST FIPS 203). "
            "PK=1184B, CT=1088B as specified in FIPS 203 Table 2. "
            "No published MAKA reference figure — experimental baseline."
        ),
        "messages": [s.to_dict() for s in specs],
    }

