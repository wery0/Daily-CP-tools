const PYODIDE_VERSION = "0.26.4";
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

/** @type {any} */
let pyodide = null;

function setBanner(kind, text) {
  const el = document.getElementById("runtime-banner");
  if (!el) return;
  el.className = `banner banner--${kind}`;
  el.querySelector(".banner__text").textContent = text;
}

function setReadyUi(enabled) {
  for (const b of document.querySelectorAll(
    'main button.btn[type="button"][id^="btn-"]',
  )) {
    b.disabled = !enabled;
  }
  for (const btn of document.querySelectorAll("button.copy-when-ready")) {
    btn.disabled = !enabled;
  }
}

/**
 * Parse a string into BigInt; reject floats and garbage.
 * @param {string} s
 * @returns {bigint}
 */
function parseIntegerString(s) {
  const t = s.replace(/\s+/g, "").replace(/^\+/, "");
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
  setBanner("info", "Loading micropip…");
  await py.loadPackage("micropip");
  setBanner("info", "Installing SymPy (micropip)…");
  const micropip = py.pyimport("micropip");
  await micropip.install("sympy");
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

/**
 * @param {string} btnId
 * @param {() => Promise<void>} fn
 */
async function withButtonBusy(btnId, fn) {
  const btn = document.getElementById(btnId);
  if (btn) btn.disabled = true;
  try {
    await fn();
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function runPrimeToolkit() {
  const input = document.getElementById("input-prime");
  const pre = document.getElementById("out-prime");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const raw = /** @type {HTMLTextAreaElement} */ (input).value;
    const fn = pyodide.globals.get("prime_neighbors");
    const out = fn.call(null, raw);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-prime", e);
  }
}

async function runPrimeToolkitWrapped() {
  await withButtonBusy("btn-prime", runPrimeToolkit);
}

async function runFactorization() {
  const input = document.getElementById("input-fac");
  const pre = document.getElementById("out-fac");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const raw = /** @type {HTMLTextAreaElement} */ (input).value;
    const fn = pyodide.globals.get("integer_factorization");
    const out = fn.call(null, raw);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-fac", e);
  }
}

async function runFactorizationWrapped() {
  await withButtonBusy("btn-fac", runFactorization);
}

async function runMaxTau() {
  const input = document.getElementById("input-tau");
  const pre = document.getElementById("out-tau");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const raw = /** @type {HTMLTextAreaElement} */ (input).value;
    const fn = pyodide.globals.get("max_divisors_upto");
    const out = fn.call(null, raw);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-tau", e);
  }
}

async function runMaxTauWrapped() {
  await withButtonBusy("btn-tau", runMaxTau);
}

async function runPrimePi() {
  const input = document.getElementById("input-pi");
  const pre = document.getElementById("out-pi");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const raw = /** @type {HTMLTextAreaElement} */ (input).value;
    const fn = pyodide.globals.get("prime_pi");
    const out = fn.call(null, raw);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-pi", e);
  }
}

async function runPrimePiWrapped() {
  await withButtonBusy("btn-pi", runPrimePi);
}

async function runFactorial() {
  const input = document.getElementById("input-fact");
  const pre = document.getElementById("out-fact");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const v = parseIntegerString(/** @type {HTMLTextAreaElement} */ (input).value);
    if (v < 0n) {
      throw new Error("N must be non-negative.");
    }
    const approx = /** @type {HTMLInputElement} */ (document.getElementById("chk-factorial-approx"))
      ?.checked;
    const fn = pyodide.globals.get("factorial_value");
    const out = fn.call(null, toPyArg(pyodide, v), !!approx);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-fact", e);
  }
}

async function runFactorialWrapped() {
  await withButtonBusy("btn-factorial", runFactorial);
}

async function runBinomial() {
  const inputN = document.getElementById("input-binom-n");
  const inputK = document.getElementById("input-binom-k");
  const pre = document.getElementById("out-binom");
  if (!inputN || !inputK || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const n = parseIntegerString(/** @type {HTMLTextAreaElement} */ (inputN).value);
    const k = parseIntegerString(/** @type {HTMLTextAreaElement} */ (inputK).value);
    if (n < 0n || k < 0n) {
      throw new Error("N and K must be non-negative.");
    }
    const approx = /** @type {HTMLInputElement} */ (document.getElementById("chk-binom-approx"))
      ?.checked;
    const fn = pyodide.globals.get("binomial_value");
    const out = fn.call(null, toPyArg(pyodide, n), toPyArg(pyodide, k), !!approx);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-binom", e);
  }
}

async function runBinomialWrapped() {
  await withButtonBusy("btn-binom", runBinomial);
}

async function runExpression() {
  const input = document.getElementById("input-expr");
  const pre = document.getElementById("out-expr");
  if (!input || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const src = /** @type {HTMLTextAreaElement} */ (input).value;
    const approx = /** @type {HTMLInputElement} */ (document.getElementById("chk-expr-approx"))
      ?.checked;
    const fn = pyodide.globals.get("evaluate_expression");
    const out = fn.call(null, src, !!approx);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-expr", e);
  }
}

async function runExpressionWrapped() {
  await withButtonBusy("btn-expr", runExpression);
}

/**
 * @param {string} s
 * @param {number} defaultValue
 * @param {string} label
 * @returns {number}
 */
function parseBaseInt(s, defaultValue, label) {
  const t = s.trim().replace(/^\+/, "");
  if (t === "") return defaultValue;
  if (!/^\d+$/.test(t)) {
    throw new Error(`${label} must be an integer from 2 to 36.`);
  }
  const v = Number.parseInt(t, 10);
  if (v < 2 || v > 36) {
    throw new Error(`${label} must be from 2 to 36.`);
  }
  return v;
}

async function runBaseConvert() {
  const inputNum = document.getElementById("input-base-num");
  const inputFrom = document.getElementById("input-base-from");
  const inputTo = document.getElementById("input-base-to");
  const pre = document.getElementById("out-base");
  if (!inputNum || !inputFrom || !inputTo || !pre || !pyodide) return;
  pre.textContent = "";
  try {
    const numStr = /** @type {HTMLTextAreaElement} */ (inputNum).value;
    const fromB = parseBaseInt(
      /** @type {HTMLTextAreaElement} */ (inputFrom).value,
      10,
      "Current base",
    );
    const toB = parseBaseInt(
      /** @type {HTMLTextAreaElement} */ (inputTo).value,
      2,
      "Target base",
    );
    const fn = pyodide.globals.get("convert_base");
    const out = fn.call(null, numStr, fromB, toB);
    pre.textContent = String(out);
  } catch (e) {
    showError("out-base", e);
  }
}

async function runBaseConvertWrapped() {
  await withButtonBusy("btn-base", runBaseConvert);
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
  void runPrimeToolkitWrapped();
});
document.getElementById("btn-fac")?.addEventListener("click", () => {
  void runFactorizationWrapped();
});
document.getElementById("btn-tau")?.addEventListener("click", () => {
  void runMaxTauWrapped();
});
document.getElementById("btn-pi")?.addEventListener("click", () => {
  void runPrimePiWrapped();
});
document.getElementById("btn-factorial")?.addEventListener("click", () => {
  void runFactorialWrapped();
});
document.getElementById("btn-binom")?.addEventListener("click", () => {
  void runBinomialWrapped();
});
document.getElementById("btn-expr")?.addEventListener("click", () => {
  void runExpressionWrapped();
});
document.getElementById("btn-base")?.addEventListener("click", () => {
  void runBaseConvertWrapped();
});

for (const btn of document.querySelectorAll("button[data-copy]")) {
  btn.addEventListener("click", () => {
    const id = btn.getAttribute("data-copy");
    if (id) void copyPre(id);
  });
}

for (const [chkId, preId] of [
  ["chk-factorial-approx", "out-fact"],
  ["chk-binom-approx", "out-binom"],
  ["chk-expr-approx", "out-expr"],
]) {
  document.getElementById(chkId)?.addEventListener("change", () => {
    const pre = document.getElementById(preId);
    if (pre) pre.textContent = "";
  });
}

initPyodide().catch((e) => {
  console.error(e);
  setBanner("err", `Failed to start Pyodide: ${e instanceof Error ? e.message : String(e)}`);
});
