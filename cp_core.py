"""
Number-theory helpers for the CP tools page (loaded into Pyodide).
Uses SymPy for primes, factorization, and pi(x).
"""
from __future__ import annotations

import ast
import math
import operator as opmod
import sympy as sp

# Browser-friendly limits — keep hints in HTML in sync
FACTORIAL_MAX_N = 1_000
BINOMIAL_MAX_N = 1_000

# Safe expression evaluator — keep in sync with UI copy
EXPR_MAX_CHARS = 2_000
EXPR_MAX_NODES = 800

_ALLOWED_UNARY = (ast.UAdd, ast.USub)
_ALLOWED_BINOP = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
)

_BINOP_IMPL: dict[type[ast.operator], type] = {
    ast.Add: opmod.add,
    ast.Sub: opmod.sub,
    ast.Mult: opmod.mul,
    ast.Div: opmod.truediv,
    ast.FloorDiv: opmod.floordiv,
    ast.Mod: opmod.mod,
    ast.Pow: opmod.pow,
}

_UNARY_IMPL: dict[type[ast.unaryop], type] = {
    ast.UAdd: opmod.pos,
    ast.USub: opmod.neg,
}


def _caret_to_pow(src: str) -> str:
    """Treat ``^`` as exponentiation (``**``) for parsing; Python's ``^`` is not used."""
    return src.replace("^", "**")


def _expr_count_nodes(node: ast.AST) -> int:
    return sum(1 for _ in ast.walk(node))


def _ensure_safe_expr(node: ast.AST) -> None:
    if isinstance(node, ast.Expression):
        _ensure_safe_expr(node.body)
        return
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            raise ValueError("Boolean literals are not allowed in expressions.")
        if isinstance(node.value, (int, float, complex)):
            return
        raise ValueError("Only numeric literals are allowed.")
    if isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, _ALLOWED_UNARY):
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        _ensure_safe_expr(node.operand)
        return
    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, _ALLOWED_BINOP):
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
        _ensure_safe_expr(node.left)
        _ensure_safe_expr(node.right)
        return
    raise ValueError(f"Unsupported syntax ({type(node).__name__}); use Python arithmetic only.")


def _eval_safe_expr(node: ast.AST):  # int | float | complex
    if isinstance(node, ast.Expression):
        return _eval_safe_expr(node.body)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp):
        fn = _UNARY_IMPL[type(node.op)]
        return fn(_eval_safe_expr(node.operand))
    if isinstance(node, ast.BinOp):
        fn = _BINOP_IMPL[type(node.op)]
        return fn(_eval_safe_expr(node.left), _eval_safe_expr(node.right))
    raise ValueError("Internal evaluator error.")


def _parsed_safe_eval_nonbool(s: str):
    """
    Parse and evaluate ``s`` (already stripped, non-empty) with the same rules as
    ``evaluate_expression``: length, AST whitelist, and operators only.
    ``^`` is rewritten to ``**`` (power). Bitwise operators are not allowed.
    Returns int, float, or complex (never bool).
    """
    if len(s) > EXPR_MAX_CHARS:
        raise ValueError(f"Expression is too long (max {EXPR_MAX_CHARS:,} characters).")
    s = _caret_to_pow(s)
    try:
        tree = ast.parse(s, mode="eval")
    except SyntaxError as e:
        msg = getattr(e, "msg", None) or "invalid syntax"
        raise ValueError(f"Syntax error: {msg}") from e
    if _expr_count_nodes(tree) > EXPR_MAX_NODES:
        raise ValueError("Expression is too complex.")
    _ensure_safe_expr(tree)
    try:
        value = _eval_safe_expr(tree)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError) as e:
        raise ValueError(str(e) or "Could not evaluate expression.") from e
    if isinstance(value, bool):
        raise ValueError("Boolean values are not allowed in expressions.")
    if not isinstance(value, (int, float, complex)):
        raise ValueError("Expression did not evaluate to a number.")
    return value


def _scientific_repr(value) -> str:
    """Format a numeric value in decimal scientific (exponential) notation."""
    if isinstance(value, bool):
        raise ValueError("Boolean not supported in scientific output.")
    if isinstance(value, complex):
        if not math.isfinite(value.real) or not math.isfinite(value.imag):
            return repr(value)
        return str(sp.N(sp.sympify(complex(value)), 20))
    if isinstance(value, float):
        if not math.isfinite(value):
            return repr(value)
        return str(sp.N(sp.sympify(value), 20))
    # int, SymPy Integer/Rational, and other SymPy numbers: avoid float() (overflow → inf).
    return str(sp.N(sp.sympify(value), 20))


def evaluate_expression(raw: str, approximate: bool = False) -> str:
    """
    Evaluate an arithmetic expression: numeric literals and ``+ - * / // % **``, parentheses.
    ``^`` is treated as exponentiation (same as ``**``). Bitwise operators are not supported.
    """
    src = (raw or "").strip()
    if not src:
        raise ValueError("Enter an expression.")
    value = _parsed_safe_eval_nonbool(src)
    if approximate:
        shown = _scientific_repr(value)
    else:
        shown = repr(value)
    return f"{src} =\n{shown}"


def eval_integer_expression(raw: str) -> int:
    """Same expression rules as ``evaluate_expression``; result must be a real integer."""
    s = (raw or "").strip()
    if not s:
        raise ValueError("Enter an integer or expression.")
    value = _parsed_safe_eval_nonbool(s)
    if isinstance(value, complex):
        raise ValueError("Expression must be a real integer for this tool.")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Expression must be a finite number.")
        if not value.is_integer():
            raise ValueError("Expression must be an integer for this tool.")
        return int(value)
    if isinstance(value, int):
        return value
    raise ValueError("Expression did not evaluate to an integer.")


def _coerce_nt_int(x_raw) -> int:
    """Integer parameter: decimal / big-int string, or Python arithmetic expression string."""
    if isinstance(x_raw, str):
        return eval_integer_expression(x_raw)
    if isinstance(x_raw, bool):
        raise ValueError("Invalid integer")
    if isinstance(x_raw, int):
        return x_raw
    return _as_int(x_raw)


BASE_MIN = 2
BASE_MAX = 36
BASE_NUMBER_MAX_LEN = 4096

_BASE_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _int_to_base(n: int, b: int) -> str:
    if b < BASE_MIN or b > BASE_MAX:
        raise ValueError(f"Target base must be from {BASE_MIN} to {BASE_MAX}.")
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    parts: list[str] = []
    while n:
        parts.append(_BASE_DIGITS[n % b])
        n //= b
    return sign + "".join(reversed(parts))


def convert_base(number_raw: str, from_base_raw, to_base_raw) -> str:
    """
    Interpret ``number_raw`` in ``from_base`` (2–36) and write the same integer in ``to_base``.
    """
    s = (number_raw or "").strip()
    if not s:
        raise ValueError("Enter a number.")
    if len(s) > BASE_NUMBER_MAX_LEN:
        raise ValueError(f"Number is too long (max {BASE_NUMBER_MAX_LEN:,} characters).")
    fb = _as_int(from_base_raw)
    tb = _as_int(to_base_raw)
    if fb < BASE_MIN or fb > BASE_MAX:
        raise ValueError(f"Current base must be from {BASE_MIN} to {BASE_MAX}.")
    if tb < BASE_MIN or tb > BASE_MAX:
        raise ValueError(f"Target base must be from {BASE_MIN} to {BASE_MAX}.")
    try:
        value = int(s, fb)
    except ValueError as e:
        raise ValueError(f"Invalid digit or syntax for base {fb}.") from e
    out = _int_to_base(value, tb)
    return f"{s} in base {fb} =\n{out} in base {tb}"


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
        raise ValueError("Must be a valid integer.") from e


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
    return " * ".join(parts)


def prime_neighbors(x_raw) -> str:
    """Primality and closest primes below / above ``N`` (no factorization)."""
    x = _coerce_nt_int(x_raw)
    if x < 0:
        raise ValueError("N must be non-negative")

    lines = [f"N = {x}", f"  Is prime: {bool(sp.isprime(x))}"]

    if x in (0, 1):
        lines.append("Prev prime: —")
        try:
            lines.append(f"Next prime: {sp.nextprime(x)}")
        except ValueError:
            lines.append("Next prime: —")
        return "\n".join(lines)

    if x <= 2:
        lines.append("Prev prime: —")
    else:
        try:
            lines.append(f"Prev prime: {sp.prevprime(x)}")
        except ValueError:
            lines.append("Prev prime: —")

    try:
        lines.append(f"Next prime: {sp.nextprime(x)}")
    except ValueError:
        lines.append("Next prime: —")

    return "\n".join(lines)


def integer_factorization(x_raw) -> str:
    """Prime factorization of ``N`` (SymPy ``factorint``)."""
    x = _coerce_nt_int(x_raw)
    if x < 0:
        raise ValueError("N must be non-negative")

    lines = [f"{x} = "]

    if x in (0, 1):
        lines.append("")
        return "\n".join(lines)

    fac = dict(sp.factorint(x))
    lines.append(f"{format_factorization(fac)}")
    return "\n".join(lines)


def _primes_product_exceeds(limit: int) -> list[int]:
    """First primes until their product exceeds ``limit`` (gist ``gen_primes`` idea)."""
    primes: list[int] = []
    prod = 1
    for p in sp.primerange(2, 10**12):
        pp = int(p)
        primes.append(pp)
        prod *= pp
        if prod > limit:
            break
    return primes


def _gist_max_divisors_upto(x: int) -> tuple[int, int, list[int], list[int]]:
    """
    Track best (N, d(N)) while running the gist ``gen_hcn`` layer loop.
    Returns (best_n, best_tau, exponents, primes) for factorization output.
    """
    primes = _primes_product_exceeds(x)
    best_n, best_tau = 1, 1
    best_exp: list[int] = []

    def consider(n: int, tau: int, exps: list[int]) -> None:
        nonlocal best_n, best_tau, best_exp
        if n > x:
            return
        if tau > best_tau or (tau == best_tau and n > best_n):
            best_n, best_tau, best_exp = n, tau, list(exps)

    consider(1, 1, [])
    hcn: list[tuple[int, int, list[int]]] = [(1, 1, [])]

    for i in range(len(primes)):
        new_hcn: list[tuple[int, int, list[int]]] = []
        for el in hcn:
            new_hcn.append(el)
            n0, t0, e0 = el
            consider(n0, t0, e0)
            if len(el[2]) < i:
                continue
            e_max = el[2][i - 1] if i >= 1 else max(1, x.bit_length() - 1)
            n = el[0]
            for e in range(1, e_max + 1):
                n *= primes[i]
                if n > x:
                    break
                div = el[1] * (e + 1)
                exponents = el[2] + [e]
                tup = (n, div, exponents)
                new_hcn.append(tup)
                consider(n, div, exponents)
        new_hcn.sort()
        hcn = [(1, 1, [])]
        for el in new_hcn:
            if el[1] > hcn[-1][1]:
                hcn.append(el)

    return best_n, best_tau, best_exp, primes


def max_divisors_upto(x_raw) -> str:
    x = _coerce_nt_int(x_raw)
    if x < 1:
        raise ValueError("N must be at least 1")

    best_n, best_tau, exps, primes = _gist_max_divisors_upto(x)
    fac = {primes[j]: exps[j] for j in range(len(exps))}
    return (
        f"N = {x}\n"
        f"M = {best_n}\n"
        f"d(M) = {best_tau}\n"
        f"M = {format_factorization(fac)}"
    )


def prime_pi(x_raw) -> str:
    x = _coerce_nt_int(x_raw)
    if x < 0:
        raise ValueError("N must be non-negative")
    cnt = sp.primepi(x)
    return f"π({x}) = {cnt}\n(primes ≤ {x})"


def factorial_value(n_raw, approximate: bool = False) -> str:
    n = _as_int(n_raw)
    if n < 0:
        raise ValueError("N must be non-negative.")
    if n > FACTORIAL_MAX_N:
        raise ValueError(f"For this tool N must be ≤ {FACTORIAL_MAX_N:,} (browser time/memory).")
    v = sp.factorial(n)
    if approximate:
        body = _scientific_repr(v)
    else:
        body = str(v)
    return f"{n}! =\n{body}"


def binomial_value(n_raw, k_raw, approximate: bool = False) -> str:
    n = _as_int(n_raw)
    k = _as_int(k_raw)
    if n < 0 or k < 0:
        raise ValueError("N and K must be non-negative.")
    if k > n:
        raise ValueError("K must not exceed N.")
    if n > BINOMIAL_MAX_N:
        raise ValueError(f"For this tool N must be ≤ {BINOMIAL_MAX_N:,}.")
    v = sp.binomial(n, k)
    if approximate:
        body = _scientific_repr(v)
    else:
        body = str(v)
    return f"C({n}, {k}) =\n{body}"
