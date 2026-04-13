# CP number theory tools (Pyodide)

Static page that runs **Python + SymPy** in the browser via [Pyodide](https://pyodide.org/), suitable for [GitHub Pages](https://pages.github.com/).

## Features

- **Primes around N**: primality, largest prime `< N`, smallest prime `> N`.
- **Factorization**: prime factorization of `N` (SymPy).
- **Max divisors ≤ N**: argmax `M ≤ N` by divisor count (ties → larger `M`), using the [HCN gist](https://gist.github.com/dario2994/fb4713f252ca86c1254d) layer loop.
- **π(N)**: count of primes `≤ N` via SymPy.
- **Factorial** `N!` and **binomial** `C(N, K)` (exact SymPy; bounded `N` in the page copy).
- **Arithmetic expression**: numeric operators only (`**` or `^` for powers); no bitwise ops, variables, or calls.
- **Constants**: π, e, and φ (golden ratio) to 50 digits after the decimal, with a copy icon (no Pyodide).

## Deploy to GitHub Pages

1. Create a new repository and push this folder’s contents to the default branch.
2. Repository **Settings → Pages**: build from the branch root (`/`).
3. After the workflow finishes, open `https://<username>.github.io/<repo>/`.

Use a project site URL as above, or name the repo `<username>.github.io` for `https://<username>.github.io/`.

## Local preview

`fetch()` loads `cp_core.py`, so open the site over HTTP (not `file://`):

```bash
python -m http.server 8080
```

Then visit `http://localhost:8080/`.

## Extending

Add functions in `cp_core.py`, load them with `pyodide.runPythonAsync`, and call from `main.js` using the same pattern as the existing buttons.
