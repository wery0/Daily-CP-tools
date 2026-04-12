# CP number theory tools (Pyodide)

Static page that runs **Python + SymPy** in the browser via [Pyodide](https://pyodide.org/), suitable for [GitHub Pages](https://pages.github.com/).

## Features

- **Primes around X**: primality, factorization, largest prime `< X`, smallest prime `> X`.
- **Max divisors ≤ X**: argmax `N ≤ X` by divisor count (ties → larger `N`), with `O(X log X)` sieve; capped at `2·10⁶`.
- **π(X)**: count of primes `≤ X` via SymPy.

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
