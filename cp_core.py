"""
Number-theory helpers for the CP tools page (loaded into Pyodide).
Uses SymPy for primes, factorization, and pi(x).
"""
from __future__ import annotations

import sympy as sp

# O(X log X) divisor sieve — keep in sync with UI copy / JS validation
MAX_TAU_X = 2_000_000


def _as_int(x) -> int:
    if x is None:
        raise ValueError("Missing value")
    if isinstance(x, bool):
        raise ValueError("Invalid integer")
    if isinstance(x, int):
        return x
    try:
        return int(x)
    except (TypeError, ValueError) as e:
        raise ValueError("X must be an integer") from e


def format_factorization(factors: dict) -> str:
    if not factors:
        return "1"
    parts = []
    for p in sorted(factors):
        e = factors[p]
        if e == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}^{e}")
    return " × ".join(parts)


def prime_toolkit(x_raw) -> str:
    x = _as_int(x_raw)
    if x < 0:
        raise ValueError("X must be non-negative")

    lines = [f"X = {x}", ""]

    if x in (0, 1):
        lines.append(f"Prime? {bool(sp.isprime(x))}")
        lines.append("Factorization: (empty / unit)")
        lines.append("Largest prime < X: —")
        try:
            lines.append(f"Smallest prime > X: {sp.nextprime(x)}")
        except ValueError:
            lines.append("Smallest prime > X: —")
        return "\n".join(lines)

    is_p = sp.isprime(x)
    fac = dict(sp.factorint(x))
    lines.append(f"Prime? {is_p}")
    lines.append(f"Factorization: {format_factorization(fac)}")

    if x <= 2:
        lines.append("Largest prime < X: —")
    else:
        try:
            lines.append(f"Largest prime < X: {sp.prevprime(x)}")
        except ValueError:
            lines.append("Largest prime < X: —")

    try:
        lines.append(f"Smallest prime > X: {sp.nextprime(x)}")
    except ValueError:
        lines.append("Smallest prime > X: —")

    return "\n".join(lines)


def max_divisors_upto(x_raw) -> str:
    x = _as_int(x_raw)
    if x < 1:
        raise ValueError("X must be at least 1")
    if x > MAX_TAU_X:
        raise ValueError(f"For this tool X must be ≤ {MAX_TAU_X:,} (browser time/memory).")

    tau = [0] * (x + 1)
    for i in range(1, x + 1):
        for j in range(i, x + 1, i):
            tau[j] += 1

    best_n = 1
    best_tau = 1
    for n in range(1, x + 1):
        t = tau[n]
        if t > best_tau or (t == best_tau and n > best_n):
            best_tau = t
            best_n = n

    fac = dict(sp.factorint(best_n))
    return (
        f"X = {x}\n"
        f"N with maximum d(N) among 1..X: {best_n}\n"
        f"d(N) = {best_tau}\n"
        f"Factorization of N: {format_factorization(fac)}"
    )


def prime_pi(x_raw) -> str:
    x = _as_int(x_raw)
    if x < 0:
        raise ValueError("X must be non-negative")
    cnt = sp.primepi(x)
    return f"π({x}) = {cnt}\n(primes ≤ X)"
