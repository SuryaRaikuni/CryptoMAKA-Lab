import os
import subprocess
import sys
import time

# ============================================================
# Secure MAKA / ECC Faculty Demonstration
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
SECURITY_DIR = os.path.join(BASE_DIR, "security")
BENCHMARK_DIR = os.path.join(BASE_DIR, "benchmarks")
QUANTUM_DIR = os.path.join(BASE_DIR, "quantum")


def separator():
    print("=" * 70)


def run_script(script_path, title=None):
    """
    Run a Python script using the same Python interpreter
    that is running this demonstration.
    """

    if not os.path.exists(script_path):
        print()
        print("[ERROR] File not found:")
        print(script_path)
        print()
        return False

    if title:
        separator()
        print(title)
        separator()

    print(f"\nRunning: {script_path}\n")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=BASE_DIR,
            check=False
        )

        print()

        if result.returncode == 0:
            print("[OK] Script completed successfully.")
            return True
        else:
            print(
                f"[ERROR] Script exited with return code "
                f"{result.returncode}."
            )
            return False

    except Exception as e:
        print(f"[ERROR] Could not run script: {e}")
        return False


def check_project_structure():
    """
    Check whether the important project files exist before
    starting the demonstration.
    """

    separator()
    print("PROJECT STRUCTURE CHECK")
    separator()

    required_files = {
        "Ju-Park protocol": os.path.join(
            SRC_DIR, "maka_ju_park.py"
        ),

        "ECC counterpart": os.path.join(
            SRC_DIR, "ecc_counterpart.py"
        ),

        "Security analysis": os.path.join(
            SECURITY_DIR, "security_analysis.py"
        ),

        "Security comparison": os.path.join(
            SECURITY_DIR, "security_comparison.py"
        ),

        "Benchmark": os.path.join(
            BENCHMARK_DIR, "benchmark_head_to_head.py"
        ),

        "Quantum demonstration": os.path.join(
            QUANTUM_DIR, "quantum_demo.py"
        ),
    }

    missing = []

    for name, path in required_files.items():

        if os.path.exists(path):
            print(f"[OK]      {name}")
            print(f"          {path}")

        else:
            print(f"[MISSING] {name}")
            print(f"          {path}")
            missing.append(path)

    print()

    if missing:
        print("[WARNING]")
        print("Some files are missing.")
        print()
        print("Expected project structure:")
        print()
        print("cns/")
        print("├── demo/")
        print("│   └── faculty_demo_final.py")
        print("├── src/")
        print("│   ├── maka_ju_park.py")
        print("│   ├── ecc_counterpart.py")
        print("│   └── round_trip_extension.py")
        print("├── security/")
        print("│   ├── security_analysis.py")
        print("│   └── security_comparison.py")
        print("├── benchmarks/")
        print("│   └── benchmark_head_to_head.py")
        print("└── quantum/")
        print("    └── quantum_demo.py")
        print()

        return False

    print("[OK] All required demonstration files were found.")
    return True


def print_intro():
    os.system("cls" if os.name == "nt" else "clear")

    separator()
    print("        CRYPTOGRAPHY & NETWORK SECURITY")
    print("        MAKA + ECC COMPARATIVE DEMONSTRATION")
    separator()

    print()
    print("Project:")
    print("Lightweight Mutual Authentication and Key Agreement")
    print("for Cloud-IoT Environments")
    print()

    print("Components:")
    print("1. Normalized Ju-Park MAKA protocol")
    print("2. ECC / ECDH counterpart")
    print("3. Security testing")
    print("4. Performance comparison")
    print("5. Quantum-threat demonstration")
    print()

    print("Paper:")
    print(
        "Ju & Park, Sensors 2023, "
        "23(24), 9766"
    )

    print()
    print("This is an academic prototype/demo, not a production")
    print("cryptographic implementation.")
    print()


def run_core_protocols():
    """
    Run the two main authentication/key-agreement protocols.
    """

    # --------------------------------------------------------
    # 1. Normalized Ju-Park
    # --------------------------------------------------------

    run_script(
        os.path.join(SRC_DIR, "maka_ju_park.py"),
        "1. Faithful normalized Ju-Park protocol"
    )

    time.sleep(1)

    # --------------------------------------------------------
    # 2. ECC / ECDH
    # --------------------------------------------------------

    run_script(
        os.path.join(SRC_DIR, "ecc_counterpart.py"),
        "2. ECC / ECDH counterpart"
    )

    time.sleep(1)


def run_security_tests():
    """
    Run security-analysis scripts.
    """

    # --------------------------------------------------------
    # 3. Security analysis
    # --------------------------------------------------------

    run_script(
        os.path.join(SECURITY_DIR, "security_analysis.py"),
        "3. Security analysis"
    )

    time.sleep(1)

    # --------------------------------------------------------
    # 4. Security comparison
    # --------------------------------------------------------

    run_script(
        os.path.join(SECURITY_DIR, "security_comparison.py"),
        "4. Security comparison: MAKA vs ECC"
    )

    time.sleep(1)


def run_benchmark():
    """
    Run head-to-head performance benchmark.
    """

    run_script(
        os.path.join(
            BENCHMARK_DIR,
            "benchmark_head_to_head.py"
        ),
        "5. Head-to-head performance benchmark"
    )

    time.sleep(1)


def run_quantum_demo():
    """
    Run the quantum-threat demonstration.
    """

    run_script(
        os.path.join(
            QUANTUM_DIR,
            "quantum_demo.py"
        ),
        "6. Quantum threat demonstration"
    )

    time.sleep(1)


def print_summary():
    """
    Print the final faculty-demo summary.
    """

    separator()
    print("                 DEMONSTRATION COMPLETE")
    separator()

    print()
    print("The demonstration covered:")
    print()
    print("[1] Normalized Ju-Park MAKA")
    print("    - Lightweight hash/XOR authentication")
    print("    - Nonce-based session establishment")
    print("    - Three-party Cloud/Control Server structure")
    print()
    print("[2] ECC counterpart")
    print("    - P-256 elliptic-curve cryptography")
    print("    - Ephemeral ECDH")
    print("    - Shared-secret derivation")
    print()
    print("[3] Security testing")
    print("    - Replay")
    print("    - Timestamp freshness")
    print("    - Message tampering")
    print("    - Impersonation")
    print()
    print("[4] Performance")
    print("    - Computation-time comparison")
    print("    - Communication-cost comparison")
    print()
    print("[5] Quantum threat model")
    print("    - Shor's algorithm and ECDH")
    print("    - Grover's algorithm and hash functions")
    print()
    print("Important:")
    print(
        "The benchmark values produced by this project are "
        "prototype measurements and should not be presented "
        "as universal hardware-independent values."
    )
    print()

    separator()
    print("                         END")
    separator()


def main():

    print_intro()

    # First make sure paths are correct.
    if not check_project_structure():
        print()
        print(
            "Fix the missing files above and run the demo again."
        )
        return

    print()
    input(
        "Press ENTER to start the faculty demonstration..."
    )

    # ========================================================
    # CORE PROTOCOLS
    # ========================================================

    run_core_protocols()

    # ========================================================
    # SECURITY
    # ========================================================

    run_security_tests()

    # ========================================================
    # BENCHMARK
    # ========================================================

    run_benchmark()

    # ========================================================
    # QUANTUM
    # ========================================================

    run_quantum_demo()

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print_summary()


if __name__ == "__main__":
    main()