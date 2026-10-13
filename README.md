# ECC Lab – Python scripts and report

**Course:** Information Security, *Elliptic Curve Cryptography in Practice* lab
**Author:** Diellart Mulolli (230756200035)

This folder contains the lab report (`report.tex` / `report.pdf`) and three small Python
scripts. The scripts check the calculations and claims made in the report:

| Script | Report section | What it shows |
|---|---|---|
| `q1_toy_curve.py` | Question 1 (a), (b) | Point doubling/addition on the toy curve and brute-forcing the ECDLP |
| `q2_benchmark.py` | Question 2 (c), (d) | Real speed and size comparison of RSA-3072, ECDSA P-256 and Ed25519 |
| `q3_nonce_reuse.py` | Question 3 (c) | Recovering an ECDSA private key when the nonce `k` is reused (Sony PS3 bug) |

## Project structure

```
ecc_lab/
├── README.md            this file: running guide and explanation of every script
├── requirements.txt     Python dependency for q2 (cryptography)
├── report.tex           LaTeX source of the report (IEEE references, pdfLaTeX/Overleaf compatible)
├── report.pdf           compiled report, 10 pages
├── q1_toy_curve.py      Q1: point arithmetic on y^2 = x^3 + 2x + 1 (mod 5), brute-force ECDLP
├── q2_benchmark.py      Q2: RSA-3072 vs ECDSA P-256 vs Ed25519 timing and sizes
└── q3_nonce_reuse.py    Q3: ECDSA private-key recovery from a reused nonce on NIST P-256
```

---

## Running guide

### 1. Prerequisites

| Requirement | Needed for | Check with |
|---|---|---|
| Python 3.8 or newer | all scripts (`pow(x, -1, p)` computes modular inverses) | `python3 --version` |
| `cryptography` ≥ 41 | `q2_benchmark.py` only | `python3 -c "import cryptography; print(cryptography.__version__)"` |

`q1_toy_curve.py` and `q3_nonce_reuse.py` use only the Python standard library, so they
run on any Python 3.8+ installation without installing anything.

### 2. Set up (once)

Open a terminal in the `ecc_lab` folder. Using a virtual environment keeps the dependency
separate from the system Python:

```bash
python3 -m venv .venv
```
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```

On Windows, use `py -m venv .venv`, then `.venv\Scripts\activate`, then the same `pip`
command. If you skip the virtual environment, `pip install cryptography` is enough.
Run `deactivate` when you are done.

### 3. Run the scripts

Run each script from inside `ecc_lab` (on Windows, write `py` instead of `python3`).

| Step | Command | Runtime* | What to look for in the output |
|---|---|---|---|
| 1 | `python3 q1_toy_curve.py` | < 0.1 s | `2P = (1, 3)`, `3P = (3, 3)`, both `on curve: True`; `k = 4, found after 3 point additions/doublings`; `7P = inf` |
| 2 | `python3 q3_nonce_reuse.py` | ≈ 0.2 s | five lines, all ending in `True`, the last being `forged signature verifies: True` |
| 3 | `python3 q2_benchmark.py` | ≈ 4 s | a table where RSA has the slowest key generation and the fastest verification; signature sizes 384 / 70–72 / 64 bytes |

\*Measured on the author's laptop. `q2` takes longest because it generates five RSA-3072
key pairs.

### 4. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'cryptography'` | Activate the virtual environment, or run `pip install -r requirements.txt`. |
| `ValueError: pow() 2nd argument cannot be negative when 3rd argument specified` | Your Python is older than 3.8; upgrade it. |
| `python3: command not found` (Windows) | Use `py` or `python` instead. |
| `q2` numbers differ from the report | This is expected: timings depend on the machine and change on every run (see the `q2_benchmark.py` section below). |

### 5. Suggested live demo for the presentation

`python3 q3_nonce_reuse.py` makes the best live demo. It finishes in well under a second,
and every run uses a fresh random private key, which the script recovers from just two
signatures.

---

## 1. `q1_toy_curve.py` – the ECDLP on a toy curve

### What it does

It uses the curve from Stamp, Section 4.5.1:

E: y² ≡ x³ + 2x + 1 (mod 5), with base point P = (0, 1)

1. It lists every point that satisfies the equation, by checking all 5 × 5 pairs (x, y).
2. It computes 2P (a *doubling*) and 3P = 2P + P (an *addition*) with the formulas from
   Stamp, Table 4.1, and prints each slope `m`, `x3` and `y3`.
3. It brute-forces the private key `k` for the public key Q = (3, 2). It adds P again and
   again until the result equals Q.
4. It prints every multiple of P, so you can see the whole cycle.

The `add()` function covers all the cases in the lab handout: the point at infinity
(`None`), P + (−P) = ∞, doubling, and ordinary addition.

### Output

```
Affine points: [(0, 1), (0, 4), (1, 2), (1, 3), (3, 2), (3, 3)] + infinity; #E = 7

(a)
  (0, 1) + (0, 1) (doubling): m = 2 * 2^-1 = 1, x3 = 1^2 - 0 - 0 = 1, y3 = 1(0 - 1) - 1 = 3
  2P = (1, 3) on curve: True
  (1, 3) + (0, 1) (addition): m = 3 * 4^-1 = 2, x3 = 2^2 - 1 - 0 = 3, y3 = 2(1 - 3) - 3 = 3
  3P = (3, 3) on curve: True

(b) brute force for Q = (3, 2)
  2P = (1, 3)
  3P = (3, 3)
  4P = (3, 2)
  k = 4, found after 3 point additions/doublings

All multiples of P:
  1P = (0, 1)
  2P = (1, 3)
  3P = (3, 3)
  4P = (3, 2)
  5P = (1, 2)
  6P = (0, 4)
  7P = inf
  8P = (0, 1)
```

### What the output means

- **`#E = 7`** – The curve has 6 normal points plus the point at infinity, which matches
  the set given in the lab. Since 7 is prime, every point except ∞ generates the whole
  group, so P has order n = 7.
- **Doubling line** – The slope is (3x₁² + a)(2y₁)⁻¹ = 2 · 2⁻¹. The inverse of 2 mod 5 is 3,
  so m = 2 · 3 = 6 ≡ 1. The script prints the numerator and denominator already reduced
  mod 5. The final y-value is −2 ≡ 3 (mod 5), so **2P = (1, 3)**.
- **Addition line** – The slope is (y₂ − y₁)(x₂ − x₁)⁻¹ = (1 − 3)(0 − 1)⁻¹ = (−2)(−1)⁻¹.
  Reduced mod 5 this is 3 · 4⁻¹ = 3 · 4 = 12 ≡ 2. This gives **3P = (3, 3)**.
- **`on curve: True`** – Each result satisfies y² ≡ x³ + 2x + 1 (mod 5), which is the
  check that Question 1(a) asks for.
- **`k = 4, found after 3 point additions/doublings`** – This answers Question 1(b). The
  script found k by **exhaustive search** with 3 group operations (one doubling to get 2P,
  then two additions). On average a brute-force search needs about n/2 steps. That is
  nothing for n = 7, but about 2²⁵⁵ steps for P-256, which is why this method is useless
  against real curves.
- **Cycle of multiples** – After 7P = ∞ the sequence starts again (8P = P), which
  confirms that P has order 7. The cycle also shows that 4P = (3, 2) = −(3, 3) = −3P
  (same x-value, negated y-value), as expected since 4 ≡ −3 (mod 7).

---

## 2. `q2_benchmark.py` – RSA-3072 vs ECDSA P-256 vs Ed25519

### What it does

All three schemes give about 128-bit security (NIST SP 800-57). For each one the script:

1. Times **key generation** (only 5 runs for RSA, because it is slow; 500 for ECC).
2. Times **signing** and **verification** of a short sensor message (300 runs each).
   RSA uses PSS padding with SHA-256, ECDSA uses SHA-256, and Ed25519 uses SHA-512
   internally.
3. Prints the **public-key size** in the standard X.509 `SubjectPublicKeyInfo` DER
   encoding, and the **signature size** in bytes.
4. Prints the raw P-256 key sizes (uncompressed and compressed) and the raw Ed25519 key
   size.

The cryptography itself runs inside OpenSSL. Python only adds a small, roughly constant
overhead per call, so the *ratios* between schemes are what matter.

### Output (sample run)

```
scheme            keygen ms   sign ms  verify ms  pk DER B  sig B
RSA-3072 (PSS)     1085.746     0.597      0.043       422    384
ECDSA P-256           0.026     0.021      0.054        91     71
Ed25519               0.034     0.033      0.086        44     64

P-256 public key: uncompressed 65 B, compressed 33 B
Ed25519 public key raw: 32 B
```

The timings **change on every run**: they depend on CPU load, frequency scaling and, for
RSA key generation, luck in finding primes. The table in the report (Question 2(c)) comes
from an earlier run (RSA keygen 813 ms, sign 1.39 ms, verify 0.09 ms, and so on). The
absolute numbers differ, but the conclusions are the same.

### What the output means

| Observation | Explanation |
|---|---|
| **RSA key generation is ~10⁴–10⁵× slower** (about 0.8–1.1 s versus about 0.03 ms) | RSA has to find two random 1536-bit primes, which takes many primality tests. An ECC private key is just a random number, and the public key is one scalar multiplication `dG`. This varies the most between runs. |
| **RSA signing is ~20–30× slower** | Signing computes `m^d mod N` with a 3072-bit private exponent (sped up with CRT). ECC signing does one 256-bit scalar multiplication. |
| **RSA verification is the fastest operation in the table** | The public exponent is e = 65537 = 2¹⁶ + 1, so verification takes only 17 modular multiplications. ECDSA and Ed25519 verification each need a *double* scalar multiplication with full 256-bit scalars. This is the "one operation where RSA is faster" asked for in Question 2(c). |
| **Public keys: 422 B vs 91 B vs 44 B** (DER) | Most of the RSA key is the 384-byte modulus. A P-256 key is a 65-byte uncompressed point (`04‖x‖y`, or 33 bytes compressed). An Ed25519 key is a 32-byte encoded point. The rest of each DER size is the algorithm identifier wrapper. |
| **Signatures: 384 B vs 70–72 B vs 64 B** | An RSA signature is always as long as the modulus. An ECDSA signature is two 32-byte integers `(r, s)` = 64 bytes raw, but in DER each integer gets a tag and length, plus a leading zero byte if its top bit is set. That is why it is **71 bytes in this run and 72 in the earlier one**. Ed25519 signatures are always exactly 64 bytes `(R, S)`. |

These results support the recommendation in Question 2(d). For a battery-powered sensor
that *signs*, Ed25519/ECDSA is much cheaper and its signatures are 6× smaller to transmit.
When a few powerful servers *sign* and millions of small devices *verify*, RSA's very
cheap verification becomes an advantage.

---

## 3. `q3_nonce_reuse.py` – ECDSA nonce reuse (Sony PS3, 2010)

### What it does

The script implements ECDSA from scratch on the real **NIST P-256** curve, using the
domain parameters from FIPS 186-5 / SP 800-186:

- `add()` uses the same point-addition formulas as in `q1`, but with the 256-bit prime p.
- `mul()` is left-to-right **double-and-add** scalar multiplication (Question 1(c)(i)).
  It is *not* constant-time, so it is for demonstration only.
- `sign()` follows the textbook formulas: r = x(kG) mod n, s = k⁻¹(h + r·d) mod n.
- `verify()` checks that the x-coordinate of (h·s⁻¹)G + (r·s⁻¹)Q, taken mod n, equals r.

It then repeats Sony's mistake:

1. It generates a random private key `d` and public key `Q = dG`.
2. It picks **one** random nonce `k` and uses it to sign two different messages.
3. As the attacker, it uses only the public data (r, s₁, s₂, h₁, h₂) to compute

   k = (h₁ − h₂)(s₁ − s₂)⁻¹ mod n
   d = (s₁·k − h₁)·r⁻¹ mod n

4. It uses the recovered `d` to sign a new message of the attacker's choice, and checks
   that this signature verifies under the victim's public key.

### Output

```
both signatures valid: True True
r1 == r2 (visible reuse): True
recovered k correct: True
recovered d correct: True
forged signature verifies: True
```

`d` and `k` are random on every run, but the output is always the same five `True` lines.

### What the output means

| Line | Meaning |
|---|---|
| `both signatures valid: True True` | Both signatures are correct ECDSA signatures and pass normal verification. Nonce reuse does **not** make signatures look invalid, so the victim notices nothing. |
| `r1 == r2 (visible reuse): True` | Because r depends only on k (r = x(kG) mod n), reusing k gives the same r. Anyone can spot this by comparing public signatures. With a random 256-bit k, a repeated r would happen with probability about 2⁻²⁵⁶. |
| `recovered k correct: True` | Subtracting the two equations for s cancels the unknown private key: s₁ − s₂ = k⁻¹(h₁ − h₂). This gives k from public values only. |
| `recovered d correct: True` | Once k is known, d = (s₁k − h₁)/r. **The private key is fully recovered.** Pollard's rho would need about 2¹²⁸ operations; this attack needs two modular inversions. |
| `forged signature verifies: True` | The attacker can now sign *anything* as the victim. The victim's public key accepts a signature on `"anything the attacker wants"`. For Sony, this meant anyone could sign homebrew software as if it were official PS3 firmware. |

This supports the main lesson of Questions 3(d) and 5: the attack does **not** break the
ECDLP. It only uses the fact that the implementation leaked information through bad nonce
handling. RFC 6979 (deterministic ECDSA) and EdDSA (RFC 8032) derive the nonce from the
private key and the message, which prevents this class of failure.

---

## Building the PDF

`report.pdf` is already compiled. To rebuild it after editing `report.tex`, use any one of
these options:

- **Overleaf (no installation):** upload `report.tex` to a new project and click
  *Recompile*. The default pdfLaTeX compiler works.
- **Tectonic** (single binary that downloads only the packages it needs; see the
  [installation page](https://tectonic-typesetting.github.io)):
  ```bash
  tectonic report.tex
  ```
- **TeX Live** (for example `sudo apt install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended`).
  Run pdfLaTeX twice so that the citation numbers are resolved:
  ```bash
  pdflatex report.tex && pdflatex report.tex
  ```
