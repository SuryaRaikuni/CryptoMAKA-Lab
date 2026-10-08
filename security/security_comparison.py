"""Side-by-side security tests for hash/XOR and authenticated-ECDH prototypes."""

from __future__ import annotations

import time

from maka_skeleton import ControlServer, CloudServer, User, H, nonce
from ecc_counterpart import ControlServerECC, ECCCloudServer, ECCUser, H as EH, nonce as enonce


def hashxor_tests():
    results = {}
    rc = ControlServer(); cs = CloudServer("cs", rc.register_cloud_server("cs")); u = User("alice", "pw", "bio"); u.register(rc)
    m1, a = u.start_login(); cs.respond_to_login(rc, u.id, m1["Ni"], m1["T1"], m1["Vi"])
    _, sk, _ = cs.respond_to_login(rc, u.id, m1["Ni"], m1["T1"], m1["Vi"])
    results["replay"] = sk is None

    rc = ControlServer(); cs = CloudServer("cs", rc.register_cloud_server("cs")); u = User("alice", "pw", "bio"); u.register(rc)
    m1, _ = u.start_login(); bad = m1["Vi"][:-1] + ("0" if m1["Vi"][-1] != "0" else "1")
    _, sk, _ = cs.respond_to_login(rc, u.id, m1["Ni"], m1["T1"], bad)
    results["tampering"] = sk is None

    rc = ControlServer(); cs = CloudServer("cs", rc.register_cloud_server("cs")); u = User("alice", "pw", "bio"); u.register(rc)
    n = nonce(); t = str(int(time.time())); guessed = H("wrong-secret"); vi = H(u.id, guessed, n, t)
    _, sk, _ = cs.respond_to_login(rc, u.id, n, t, vi)
    results["impersonation"] = sk is None
    return results


def ecc_tests():
    results = {}
    rc = ControlServerECC(); cs = ECCCloudServer("cs"); u = ECCUser("alice", "pw", "bio"); u.register(rc)
    m1, a, priv = u.start_login(); m2, sk, _, reason = cs.respond_to_login(rc, u.user_id, m1)
    assert reason == "ok" and m2 is not None
    _, replay_sk, _, _ = cs.respond_to_login(rc, u.user_id, m1)
    results["replay"] = replay_sk is None

    rc = ControlServerECC(); cs = ECCCloudServer("cs"); u = ECCUser("alice", "pw", "bio"); u.register(rc)
    m1, a, priv = u.start_login(); m1["Vi"] = m1["Vi"][:-1] + ("0" if m1["Vi"][-1] != "0" else "1")
    _, sk, _, _ = cs.respond_to_login(rc, u.user_id, m1)
    results["tampering"] = sk is None

    rc = ControlServerECC(); cs = ECCCloudServer("cs"); u = ECCUser("alice", "pw", "bio"); u.register(rc)
    n = enonce(); pu_fake = ec_fake_public(); t = str(int(time.time())); guessed = EH("wrong-secret")
    vi = EH(u.user_id, guessed, pu_fake, n, t)
    fake = {"Vi": vi, "Pu": pu_fake, "Ni": n, "T1": t}
    _, sk, _, _ = cs.respond_to_login(rc, u.user_id, fake)
    results["impersonation"] = sk is None

    rc = ControlServerECC(); cs = ECCCloudServer("cs"); u = ECCUser("alice", "pw", "bio"); u.register(rc)
    m1, a, priv = u.start_login(); m2, sk_server, _, _ = cs.respond_to_login(rc, u.user_id, m1)
    sk_user, reason = u.finish_login(a, priv, m1, m2)
    results["key_match"] = (reason == "ok" and sk_user == sk_server)
    return results


def ec_fake_public():
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    key = ec.generate_private_key(ec.SECP256R1())
    return key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex()


def main():
    hx = hashxor_tests(); ec = ecc_tests()
    print("Security comparison")
    print("Scenario        Hash/XOR    P-256 ECDH")
    print("---------------------------------------")
    for k in ["replay", "tampering", "impersonation"]:
        print(f"{k:15s} {'PASS' if hx[k] else 'FAIL':9s} {'PASS' if ec[k] else 'FAIL'}")
    print(f"{'key_match':15s} {'n/a':9s} {'PASS' if ec['key_match'] else 'FAIL'}")


if __name__ == "__main__":
    main()
