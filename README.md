# CP number theory tools (Pyodide)

Static page that runs **Python + SymPy** in the browser via [Pyodide](https://pyodide.org/), suitable for [GitHub Pages](https://pages.github.com/).

## Features

- **Primes around N**: primality, largest prime `< N`, smallest prime `> N`.
- **Factorization**: prime factorization of `N` (SymPy).
- **Max divisors ≤ N**: argmax `M ≤ N` by divisor count.
- **π(N)**: count of primes `≤ N` via SymPy.
- **Factorial** `N!` and **binomial** `C(N, K)` (exact SymPy; bounded `N` in the page copy).
- **Arithmetic expression**: numeric operators (`**` or `^` for powers) and `sqrt`, `cbrt`, `log` (base 10), `log2`, `ln`; no bitwise ops, variables, or other calls.
- **Base conversion**: convert number from one base to another.
- **Constants**: π, e, and φ up to 40 digits after the decimal, with a copy icon.

## Local preview

`fetch()` loads `cp_core.py`, so open the site over HTTP (not `file://`):

```bash
python -m http.server 8080
```

Then visit `http://localhost:8080/`.

