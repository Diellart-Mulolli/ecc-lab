"""Question 3(c): recovering an ECDSA private key from two signatures that reuse k (P-256)."""
import hashlib
import secrets

# NIST P-256 domain parameters (FIPS 186-5 / SP 800-186)
p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
a = p - 3
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
     0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)


def add(P1, P2):
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    (x1, y1), (x2, y2) = P1, P2
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P1 == P2:
        m = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        m = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (m * m - x1 - x2) % p
    return x3, (m * (x1 - x3) - y1) % p


def mul(k, P):
    """Left-to-right double-and-add (not constant time; demo only)."""
    R = None
    for bit in bin(k)[2:]:
        R = add(R, R)
        if bit == "1":
            R = add(R, P)
    return R


def h(msg):
    return int.from_bytes(hashlib.sha256(msg).digest(), "big") % n


def sign(d, msg, k):
    r = mul(k, G)[0] % n
    s = pow(k, -1, n) * (h(msg) + r * d) % n
    return r, s


def verify(Q, msg, r, s):
    w = pow(s, -1, n)
    X = add(mul(h(msg) * w % n, G), mul(r * w % n, Q))
    return X is not None and X[0] % n == r


d = secrets.randbelow(n - 1) + 1
Q = mul(d, G)
k = secrets.randbelow(n - 1) + 1  # the "constant" Sony-style nonce

m1, m2 = b"firmware 3.55", b"homebrew loader"
r1, s1 = sign(d, m1, k)
r2, s2 = sign(d, m2, k)
print("both signatures valid:", verify(Q, m1, r1, s1), verify(Q, m2, r2, s2))
print("r1 == r2 (visible reuse):", r1 == r2)

h1, h2 = h(m1), h(m2)
k_rec = (h1 - h2) * pow(s1 - s2, -1, n) % n
d_rec = (s1 * k_rec - h1) * pow(r1, -1, n) % n
print("recovered k correct:", k_rec == k)
print("recovered d correct:", d_rec == d)

forged = sign(d_rec, b"anything the attacker wants", 12345)
print("forged signature verifies:", verify(Q, b"anything the attacker wants", *forged))
