const PYODIDE_VERSION = "0.26.4";
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

const MAX_TAU_X = 2_000_000;

/** @type {any} */
let pyodide = null;

function setBanner(kind, text) {
  const el = document.getElementById("runtime-banner");
  if (!el) return;
  el.className = `banner banner--${kind}`;
  el.querySelector(".banner__text").textContent = text;
}

function setReadyUi(enabled) {
  for (const id of ["btn-prime", "btn-tau", "btn-pi"]) {
    const b = document.getElementById(id);
    if (b) b.disabled = !enabled;
  }
  for (const btn of document.querySelectorAll("button.copy")) {
    btn.disabled = !enabled;
  }
}

/**
 * Parse a string into BigInt; reject floats and garbage.
 * @param {string} s
 * @returns {bigint}
 */
function parseIntegerString(s) {
  const t = s.trim().replace(/^\+/, "");
  if (t === "" || t === "-" || t === "+") {
    throw new Error("Enter an integer.");
  }
  if (t.includes(".") || t.includes("e") || t.includes("E")) {
    throw new Error("Use an integer (no decimals or scientific notation).");
  }
  if (!/^-?\d+$/.test(t)) {
    throw new Error("Invalid characters; enter an integer.");
  }
  try {
    return BigInt(t);
  } catch {
    throw new Error("Value is not a valid integer.");
  }
}

/**
 * @param {bigint} v
 * @returns {boolean}
 */
function fitsSafeInteger(v) {
  const max = BigInt(Number.MAX_SAFE_INTEGER);
  const min = BigInt(Number.MIN_SAFE_INTEGER);
  return v >= min && v <= max;
}

/**
 * @param {any} py
 * @param {bigint} v
 */
function toPyArg(py, v) {
  if (fitsSafeInteger(v)) {
    return Number(v);
  }
  return py.toPy(v);
}

async function loadCpCore(py) {
  const res = await fetch("cp_core.py", { cache: "no-cache" });
  if (!res.ok) {
    throw new Error(`Failed to load cp_core.py (${res.status})`);
  }
  const code = await res.text();
  await py.runPythonAsync(code);
}

async function initPyodide() {
  setBanner("info", "Loading Pyodide runtime…");
  // @ts-ignore — loaded from CDN at runtime
  const { loadPyodide } = await import(`${INDEX_URL}pyodide.mjs`);
  const py = await loadPyodide({ indexURL: INDEX_URL });
  setBanner("info", "Installing SymPy (micropip)…");
  const micropip = py.pyimport("micropip");
  await micropip.install("sympy==1.13.3");
  await loadCpCore(py);
  pyodide = py;
  setBanner("ok", "Ready — SymPy loaded.");
  setReadyUi(true);
}

function showError(preId, err) {
  const pre = document.getElementById(preId);
  if (pre) {
    pre.textContent = err instanceof Error ? err.message : String(err);
  }
}

async function runPrimeToolkit() {
  const input = document.getElementById("input-prime");
  const pre = document.getElementById("out-prime");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const v = parseIntegerString(/** @type {HTMLInputElement} */ (input).value);
    if (v < 0n) {
      throw new Error("X must be non-negative.");
    }
    const arg = toPyArg(pyodide, v);
    const fn = pyodide.globals.get("prime_toolkit");
    const out = await fn.callAsync(arg);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-prime", e);
  }
}

async function runMaxTau() {
  const input = document.getElementById("input-tau");
  const pre = document.getElementById("out-tau");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const v = parseIntegerString(/** @type {HTMLInputElement} */ (input).value);
    if (v < 1n) {
      throw new Error("X must be at least 1.");
    }
    if (v > BigInt(MAX_TAU_X)) {
      throw new Error(`X must be ≤ ${MAX_TAU_X.toLocaleString()} for this tool.`);
    }
    const fn = pyodide.globals.get("max_divisors_upto");
    const out = await fn.callAsync(Number(v));
    pre.textContent = String(out);
  } catch (e) {
    showError("out-tau", e);
  }
}

async function runPrimePi() {
  const input = document.getElementById("input-pi");
  const pre = document.getElementById("out-pi");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const v = parseIntegerString(/** @type {HTMLInputElement} */ (input).value);
    if (v < 0n) {
      throw new Error("X must be non-negative.");
    }
    const arg = toPyArg(pyodide, v);
    const fn = pyodide.globals.get("prime_pi");
    const out = await fn.callAsync(arg);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-pi", e);
  }
}

async function copyPre(id) {
  const pre = document.getElementById(id);
  if (!pre || !pre.textContent) return;
  try {
    await navigator.clipboard.writeText(pre.textContent);
  } catch {
    pre.select?.();
  }
}

document.getElementById("btn-prime")?.addEventListener("click", () => {
  void runPrimeToolkit();
});
document.getElementById("btn-tau")?.addEventListener("click", () => {
  void runMaxTau();
});
document.getElementById("btn-pi")?.addEventListener("click", () => {
  void runPrimePi();
});

for (const btn of document.querySelectorAll("button.copy")) {
  btn.addEventListener("click", () => {
    const id = btn.getAttribute("data-copy");
    if (id) void copyPre(id);
  });
}

initPyodide().catch((e) => {
  console.error(e);
  setBanner("err", `Failed to start Pyodide: ${e instanceof Error ? e.message : String(e)}`);
});
