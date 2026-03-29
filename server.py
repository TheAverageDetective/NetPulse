"""
server.py — Flask web server for Network Traffic Analyzer
Run: python server.py
Then open: http://localhost:5000
"""

import json
import os
import threading
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, send_file

from src import analysis, charts, dl_thread

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
DATA_PATH   = str(BASE_DIR / "data" / "data.csv")
REPORT_PATH = str(BASE_DIR / "data" / "report.json")
CHART_PATH  = str(BASE_DIR / "data" / "chart.jpg")

app = Flask(__name__)

# ── State ─────────────────────────────────────────────────────────────────────
_monitor_running = False
_monitor_lock    = threading.Lock()


# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/api/status")
def api_status():
    return jsonify({"running": _monitor_running})


@app.route("/api/start", methods=["POST"])
def api_start():
    global _monitor_running
    body     = request.get_json(silent=True) or {}
    url      = body.get("url", "")
    interval = int(body.get("interval", 1))

    if not url:
        return jsonify({"error": "url is required"}), 400

    with _monitor_lock:
        if _monitor_running:
            return jsonify({"error": "Monitor already running"}), 409
        dl_thread.start(url, interval, DATA_PATH)
        _monitor_running = True

    return jsonify({"ok": True, "message": f"Monitor started — downloading every {interval} min"})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    global _monitor_running
    with _monitor_lock:
        if not _monitor_running:
            return jsonify({"error": "Monitor is not running"}), 409
        dl_thread.stop()
        _monitor_running = False

    try:
        analysis.analyze(DATA_PATH, REPORT_PATH)
        charts.generate(DATA_PATH, CHART_PATH)
    except Exception as e:
        return jsonify({"ok": True, "warning": str(e)})

    return jsonify({"ok": True, "message": "Monitor stopped. Report and chart updated."})


@app.route("/api/report")
def api_report():
    if not os.path.exists(REPORT_PATH):
        return jsonify({"error": "No report found. Run a session first."}), 404
    with open(REPORT_PATH) as f:
        return jsonify(json.load(f))


@app.route("/api/chart")
def api_chart():
    if not os.path.exists(CHART_PATH):
        return jsonify({"error": "No chart found. Run a session first."}), 404
    response = send_file(CHART_PATH, mimetype="image/jpeg")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    if not os.path.exists(DATA_PATH):
        return jsonify({"error": "No data file found."}), 404
    try:
        analysis.analyze(DATA_PATH, REPORT_PATH)
        charts.generate(DATA_PATH, CHART_PATH)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": True})


# ── Frontend ──────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>NetPulse — Network Traffic Analyzer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:      #080c10;
    --surface: #0d1117;
    --border:  #1a2332;
    --accent:  #00ff88;
    --accent2: #00c4ff;
    --danger:  #ff3c5a;
    --text:    #c9d1d9;
    --muted:   #4a5568;
    --mono:    'Share Tech Mono', monospace;
    --sans:    'Syne', sans-serif;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    overflow-x: hidden;
  }

  body::before {
    content: "";
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg, transparent, transparent 2px,
      rgba(0,255,136,0.015) 2px, rgba(0,255,136,0.015) 4px
    );
    pointer-events: none;
    z-index: 100;
  }

  body::after {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .shell {
    position: relative;
    z-index: 1;
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
  }

  header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.25rem;
    margin-bottom: 2.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .logo { font-size: 2rem; font-weight: 800; letter-spacing: -1px; color: #fff; }
  .logo span { color: var(--accent); }

  .badge {
    font-family: var(--mono);
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 2px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }
  .badge-idle    { border: 1px solid var(--muted); color: var(--muted); }
  .badge-running { border: 1px solid var(--accent); color: var(--accent);
                   box-shadow: 0 0 8px rgba(0,255,136,0.3); animation: pulse 2s infinite; }

  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }

  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .panel-title {
    font-family: var(--mono);
    font-size: 0.7rem;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 1rem;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr auto auto auto;
    gap: 0.75rem;
    align-items: end;
  }

  .field { display: flex; flex-direction: column; gap: 0.4rem; }

  label {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
  }

  input[type="text"], input[type="number"] {
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: var(--mono);
    font-size: 0.85rem;
    padding: 0.6rem 0.85rem;
    border-radius: 3px;
    outline: none;
    transition: border-color 0.2s;
    width: 100%;
  }
  input:focus { border-color: var(--accent2); }

  .btn {
    font-family: var(--mono);
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0.65rem 1.4rem;
    border-radius: 3px;
    border: 1px solid;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
    background: transparent;
  }
  .btn-start { border-color: var(--accent); color: var(--accent); }
  .btn-start:hover:not(:disabled) { background: var(--accent); color: var(--bg); box-shadow: 0 0 18px rgba(0,255,136,0.4); }
  .btn-stop  { border-color: var(--danger); color: var(--danger); }
  .btn-stop:hover:not(:disabled)  { background: var(--danger); color: #fff; box-shadow: 0 0 18px rgba(255,60,90,0.4); }
  .btn-refresh { border-color: var(--accent2); color: var(--accent2); }
  .btn-refresh:hover:not(:disabled) { background: var(--accent2); color: var(--bg); }
  .btn:disabled { opacity: 0.3; cursor: not-allowed; }

  #toast {
    position: fixed;
    bottom: 2rem; right: 2rem;
    font-family: var(--mono);
    font-size: 0.75rem;
    padding: 0.75rem 1.25rem;
    border-radius: 3px;
    border-left: 3px solid var(--accent);
    background: var(--surface);
    color: var(--text);
    opacity: 0;
    transform: translateY(12px);
    transition: all 0.25s;
    z-index: 200;
    max-width: 320px;
  }
  #toast.show  { opacity: 1; transform: translateY(0); }
  #toast.error { border-color: var(--danger); color: var(--danger); }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.25rem 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .stat-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
    opacity: 0;
    transition: opacity 0.3s;
  }
  .stat-card:hover { border-color: var(--accent); }
  .stat-card:hover::before { opacity: 1; }

  .stat-label {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
  }
  .stat-value { font-family: var(--mono); font-size: 1.6rem; color: #fff; line-height: 1; }
  .stat-unit  { font-size: 0.65rem; color: var(--muted); margin-top: 0.3rem; font-family: var(--mono); }
  .stat-card.accent  .stat-value { color: var(--accent); }
  .stat-card.accent2 .stat-value { color: var(--accent2); }
  .stat-card.danger  .stat-value { color: var(--danger); }

  .chart-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  .chart-wrap img { width: 100%; border-radius: 2px; display: block; }

  .empty-state {
    font-family: var(--mono);
    font-size: 0.8rem;
    color: var(--muted);
    text-align: center;
    padding: 3rem 0;
    letter-spacing: 1px;
  }

  .action-bar { display: flex; gap: 0.75rem; flex-wrap: wrap; }

  @media (max-width: 640px) {
    .form-row { grid-template-columns: 1fr; }
    .stat-value { font-size: 1.25rem; }
  }
</style>
</head>
<body>
<div class="shell">

  <header>
    <div class="logo">Net<span>Pulse</span></div>
    <span id="status-badge" class="badge badge-idle">● IDLE</span>
  </header>

  <div class="panel">
    <div class="panel-title">// Monitor Config</div>
    <div class="form-row">
      <div class="field">
        <label>Download URL</label>
        <input type="text" id="url-input" placeholder="https://..." />
      </div>
      <div class="field">
        <label>Interval (min)</label>
        <input type="number" id="interval-input" value="1" min="1" max="60" style="width:100px"/>
      </div>
      <button class="btn btn-start" id="btn-start">▶ Start</button>
      <button class="btn btn-stop"  id="btn-stop" disabled>■ Stop</button>
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card accent">
      <div class="stat-label">Mean</div>
      <div class="stat-value" id="s-mean">—</div>
      <div class="stat-unit">Mbps</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Median</div>
      <div class="stat-value" id="s-median">—</div>
      <div class="stat-unit">Mbps</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Mode</div>
      <div class="stat-value" id="s-mode">—</div>
      <div class="stat-unit">Mbps</div>
    </div>
    <div class="stat-card accent2">
      <div class="stat-label">Max</div>
      <div class="stat-value" id="s-max">—</div>
      <div class="stat-unit">Mbps</div>
    </div>
    <div class="stat-card danger">
      <div class="stat-label">Min</div>
      <div class="stat-value" id="s-min">—</div>
      <div class="stat-unit">Mbps</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Std Dev</div>
      <div class="stat-value" id="s-std">—</div>
      <div class="stat-unit">Mbps</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Busiest Hour</div>
      <div class="stat-value" id="s-hour">—</div>
      <div class="stat-unit">24h clock</div>
    </div>
  </div>

  <div class="chart-wrap">
    <div class="panel-title">// Throughput Trend</div>
    <div id="chart-container">
      <div class="empty-state">No chart data yet — start a session to collect data</div>
    </div>
  </div>

  <div class="action-bar">
    <button class="btn btn-refresh" id="btn-refresh">↻ Refresh Stats</button>
  </div>

</div>

<div id="toast"></div>

<script>
  let pollTimer = null;

  function toast(msg, isError) {
    const el = document.getElementById("toast");
    el.textContent = msg;
    el.className = "show" + (isError ? " error" : "");
    clearTimeout(el._t);
    el._t = setTimeout(function() { el.className = ""; }, 3000);
  }

  function setStatus(running) {
    const badge = document.getElementById("status-badge");
    badge.textContent = running ? "● LIVE" : "● IDLE";
    badge.className   = "badge " + (running ? "badge-running" : "badge-idle");
    document.getElementById("btn-start").disabled = running;
    document.getElementById("btn-stop").disabled  = !running;
  }

  function fillStats(data) {
    function fmt(v) { return (typeof v === "number") ? v.toFixed(2) : "—"; }
    document.getElementById("s-mean").textContent   = fmt(data.mean);
    document.getElementById("s-median").textContent = fmt(data.median);
    document.getElementById("s-mode").textContent   = fmt(data.mode);
    document.getElementById("s-max").textContent    = fmt(data.max);
    document.getElementById("s-min").textContent    = fmt(data.min);
    document.getElementById("s-std").textContent    = fmt(data.std_dev);
    document.getElementById("s-hour").textContent   = data.busiest_hour !== undefined ? data.busiest_hour : "—";
  }

  function loadReport() {
    return fetch("/api/report")
      .then(function(r) { if (r.ok) return r.json(); })
      .then(function(data) { if (data) fillStats(data); })
      .catch(function() {});
  }

  function loadChart() {
    var t = Date.now();
    return fetch("/api/chart?t=" + t)
      .then(function(r) {
        if (!r.ok) return;
        document.getElementById("chart-container").innerHTML =
          '<img src="/api/chart?t=' + Date.now() + '" alt="Throughput chart" />';
      })
      .catch(function() {});
  }

  function startMonitor() {
    var url      = document.getElementById("url-input").value.trim();
    var interval = parseInt(document.getElementById("interval-input").value) || 1;
    if (!url) { toast("Please enter a download URL", true); return; }

    fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url, interval: interval })
    })
    .then(function(r) { return r.json().then(function(data) { return { ok: r.ok, data: data }; }); })
    .then(function(res) {
      if (!res.ok) { toast(res.data.error, true); return; }
      toast(res.data.message);
      setStatus(true);
      pollTimer = setInterval(refreshData, 30000);
    });
  }

  function stopMonitor() {
    fetch("/api/stop", { method: "POST" })
    .then(function(r) { return r.json().then(function(data) { return { ok: r.ok, data: data }; }); })
    .then(function(res) {
      if (!res.ok) { toast(res.data.error, true); return; }
      toast(res.data.message);
      setStatus(false);
      clearInterval(pollTimer);
      refreshData();
    });
  }

  function refreshData() {
    fetch("/api/refresh", { method: "POST" })
    .then(function(r) {
      if (r.ok) {
        loadReport();
        loadChart();
      }
    });
  }

  // Wire up buttons
  document.getElementById("btn-start").addEventListener("click", startMonitor);
  document.getElementById("btn-stop").addEventListener("click", stopMonitor);
  document.getElementById("btn-refresh").addEventListener("click", refreshData);

  // Init on page load
  fetch("/api/status")
    .then(function(r) { return r.json(); })
    .then(function(data) {
      setStatus(data.running);
      if (data.running) pollTimer = setInterval(refreshData, 30000);
      loadReport();
      loadChart();
    });
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


if __name__ == "__main__":
    os.makedirs(BASE_DIR / "data", exist_ok=True)
    print("NetPulse server → http://localhost:5000")
    app.run(debug=False, port=5000)