"""Design sketch for a reduced-round authenticated response.

This is intentionally a protocol-design note rather than a claimed secure
construction. The goal is to define what would need to be proved and tested
before claiming a 3-message optimization.
"""

EXTENSION_NAME = "Authenticated response consolidation"

ORIGINAL_FLOW = [
    "M1: User -> Cloud",
    "M2: Cloud -> Control",
    "M3: Control -> Cloud",
    "M4: Cloud -> User",
]

PROPOSED_FLOW = [
    "M1: User -> Cloud",
    "M2: Cloud -> Control",
    "M3: Control -> User/Cloud (combined authenticated response)",
]

REQUIRED_PROPERTIES = [
    "mutual authentication",
    "freshness / replay resistance",
    "session-key confirmation",
    "user untraceability",
    "resistance to message modification",
]

if __name__ == "__main__":
    print(EXTENSION_NAME)
    print("Original:")
    for x in ORIGINAL_FLOW:
        print(" ", x)
    print("Proposed:")
    for x in PROPOSED_FLOW:
        print(" ", x)
    print("\nMust be formally analyzed before it can be called secure:")
    for x in REQUIRED_PROPERTIES:
        print(" ", x)
