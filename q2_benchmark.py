"""Question 2(c): RSA-3072 vs ECDSA P-256 vs Ed25519 (pyca/cryptography, OpenSSL backend)."""
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa

MSG = b"sensor reading: 21.4 C, 48 % RH"
RAW = serialization.Encoding.Raw, serialization.PublicFormat.Raw
DER = serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo


def bench(fn, reps):
    t = time.perf_counter()
    for _ in range(reps):
        fn()
    return (time.perf_counter() - t) / reps * 1e3  # ms per op


schemes = {
    "RSA-3072 (PSS)": dict(
        gen=lambda: rsa.generate_private_key(65537, 3072),
        sign=lambda sk: sk.sign(MSG, padding.PSS(padding.MGF1(hashes.SHA256()), 32), hashes.SHA256()),
        verify=lambda pk, s: pk.verify(s, MSG, padding.PSS(padding.MGF1(hashes.SHA256()), 32), hashes.SHA256()),
        gen_reps=5,
    ),
    "ECDSA P-256": dict(
        gen=lambda: ec.generate_private_key(ec.SECP256R1()),
        sign=lambda sk: sk.sign(MSG, ec.ECDSA(hashes.SHA256())),
        verify=lambda pk, s: pk.verify(s, MSG, ec.ECDSA(hashes.SHA256())),
        gen_reps=500,
    ),
    "Ed25519": dict(
        gen=ed25519.Ed25519PrivateKey.generate,
        sign=lambda sk: sk.sign(MSG),
        verify=lambda pk, s: pk.verify(s, MSG),
        gen_reps=500,
    ),
}

print(f"{'scheme':16} {'keygen ms':>10} {'sign ms':>9} {'verify ms':>10} {'pk DER B':>9} {'sig B':>6}")
for name, sc in schemes.items():
    sk = sc["gen"]()
    pk = sk.public_key()
    sig = sc["sign"](sk)
    tg = bench(sc["gen"], sc["gen_reps"])
    ts = bench(lambda: sc["sign"](sk), 300)
    tv = bench(lambda: sc["verify"](pk, sig), 300)
    pk_len = len(pk.public_bytes(*DER))
    print(f"{name:16} {tg:10.3f} {ts:9.3f} {tv:10.3f} {pk_len:9d} {len(sig):6d}")

p256 = ec.generate_private_key(ec.SECP256R1()).public_key()
print("\nP-256 public key: uncompressed",
      len(p256.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)),
      "B, compressed",
      len(p256.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.CompressedPoint)), "B")
print("Ed25519 public key raw:", len(ed25519.Ed25519PrivateKey.generate().public_key().public_bytes(*RAW)), "B")
