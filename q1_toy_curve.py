"""Question 1: arithmetic on the toy curve y^2 = x^3 + 2x + 1 (mod 5) from Stamp, Sec. 4.5.1."""

p, a, b = 5, 2, 1
INF = None


def on_curve(P):
    if P is INF:
        return True
    x, y = P
    return (y * y - (x ** 3 + a * x + b)) % p == 0


def add(P1, P2, verbose=False):
    if P1 is INF:
        return P2
    if P2 is INF:
        return P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0:
        return INF
    if P1 == P2:
        num, den = 3 * x1 * x1 + a, 2 * y1
    else:
        num, den = y2 - y1, x2 - x1
    m = num * pow(den, -1, p) % p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    if verbose:
        kind = "doubling" if P1 == P2 else "addition"
        print(f"  {P1} + {P2} ({kind}): m = {num % p} * {den % p}^-1 = {m}, "
              f"x3 = {m}^2 - {x1} - {x2} = {x3}, y3 = {m}({x1} - {x3}) - {y1} = {y3}")
    return (x3, y3)


points = [(x, y) for x in range(p) for y in range(p) if on_curve((x, y))]
print("Affine points:", points, "+ infinity; #E =", len(points) + 1)

P = (0, 1)
print("\n(a)")
P2 = add(P, P, verbose=True)
print("  2P =", P2, "on curve:", on_curve(P2))
P3 = add(P2, P, verbose=True)
print("  3P =", P3, "on curve:", on_curve(P3))

print("\n(b) brute force for Q = (3, 2)")
Q, R, k, adds = (3, 2), P, 1, 0
while R != Q:
    R = add(R, P)
    k += 1
    adds += 1
    print(f"  {k}P = {R}")
print(f"  k = {k}, found after {adds} point additions/doublings")

print("\nAll multiples of P:")
R = P
for i in range(1, 9):
    print(f"  {i}P = {R if R is not INF else 'inf'}")
    R = add(R, P)
