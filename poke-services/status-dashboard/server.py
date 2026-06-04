#!/usr/bin/env python3
"""Status Dashboard — Real-time health monitor for all Poke Labs services. Port: 8790."""
import http.server, json, urllib.parse, os, urllib.request, urllib.error, time, threading

PORT = int(os.environ.get("PORT", 8790))
GATEWAY = os.environ.get("GATEWAY_URL", "http://localhost:8700")

# Service registry: name -> (port, health_path)
SERVICES = {
    "gateway":       (8700, "/health"),
    "link-preview":  (8765, "/api/health"),
    "sentiment":     (8770, "/api/health"),
    "qr":            (8771, "/api/health"),
    "dns":           (8772, "/api/health"),
    "color":         (8773, "/api/health"),
    "url":           (8774, "/api/health"),
    "keyword":       (8775, "/api/health"),
    "summarize":     (8776, "/api/health"),
    "hash-gen":      (8777, "/api/health"),
    "uuid-gen":      (8778, "/api/health"),
    "timestamp-conv":(8781, "/api/health"),
    "barcode":       (8782, "/api/health"),
}

cache = {"results": {}, "ts": 0}
cache_lock = threading.Lock()
CACHE_TTL = 10  # seconds

def check_service(name, port, path):
    try:
        url = f"http://localhost:{port}{path}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            return {"status": "up", "port": port, "data": data}
    except Exception as e:
        return {"status": "down", "port": port, "error": str(e)}

def refresh_cache():
    while True:
        results = {}
        for name, (port, path) in SERVICES.items():
            results[name] = check_service(name, port, path)
        with cache_lock:
            cache["results"] = results
            cache["ts"] = time.time()
        time.sleep(CACHE_TTL)

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/api/health":
            self._respond(200, {"ok": True, "service": "status-dashboard", "v": 1})
        elif p.path == "/api/status":
            with cache_lock:
                results = cache["results"]
                ts = cache["ts"]
            up = sum(1 for r in results.values() if r["status"] == "up")
            total = len(results)
            self._respond(200, {
                "services": results,
                "summary": {"up": up, "down": total - up, "total": total},
                "cached_at": ts,
                "fresh": time.time() - ts < CACHE_TTL * 2
            })
        elif p.path == "/" or p.path == "/index.html":
            self._serve_dashboard()
        else:
            self._respond(404, {"error": "not found"})

    def _serve_dashboard(self):
        with cache_lock:
            results = dict(cache["results"])
            ts = cache["ts"]
        up = sum(1 for r in results.values() if r["status"] == "up")
        total = len(results) or 1

        rows = ""
        for name, info in sorted(results.items()):
            status = info["status"]
            emoji = "🟢" if status == "up" else "🔴"
            port = info["port"]
            detail = ""
            if status == "up" and "data" in info:
                d = info["data"]
                ver = d.get("v", d.get("version", "?"))
                detail = f"v{ver}"
            elif "error" in info:
                detail = info["error"][:40]
            rows += f'<tr><td>{emoji} {name}</td><td>{status}</td><td>{port}</td><td>{detail}</td></tr>\n'

        age = round(time.time() - ts, 1) if ts else "?"
        html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Poke Labs — Status</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:#0a0a0f;color:#fff;padding:2rem;line-height:1.6}}
h1{{font-family:'JetBrains Mono',monospace;margin-bottom:.5rem}}
.sub{{color:#666;margin-bottom:2rem}}
.summary{{display:flex;gap:2rem;margin-bottom:2rem;flex-wrap:wrap}}
.stat{{background:#111118;border:1px solid #1a1a24;border-radius:8px;padding:1rem 1.5rem;text-align:center}}
.stat .num{{font-size:2rem;font-weight:700;font-family:'JetBrains Mono',mono}}
.stat .label{{font-size:.8rem;color:#666}}
.up{{color:#27c93f}}.down{{color:#ff5f56}}
table{{width:100%;border-collapse:collapse;margin-top:1rem}}
th{{text-align:left;padding:.75rem;border-bottom:2px solid #1a1a24;font-family:'JetBrains Mono',mono;font-size:.85rem;color:#666}}
td{{padding:.65rem .75rem;border-bottom:1px solid #1a1a24;font-size:.9rem}}
tr:hover{{background:#111118}}
.refresh{{color:#666;font-size:.8rem;margin-top:1rem}}
a{{color:#00d4ff}}
</style></head><body>
<h1>⚡ Poke Labs Status</h1>
<p class="sub">Real-time health monitor for all Council services</p>
<div class="summary">
  <div class="stat"><div class="num up">{up}</div><div class="label">UP</div></div>
  <div class="stat"><div class="num down">{total-up}</div><div class="label">DOWN</div></div>
  <div class="stat"><div class="num">{total}</div><div class="label">TOTAL</div></div>
</div>
<table>
<tr><th>Service</th><th>Status</th><th>Port</th><th>Info</th></tr>
{rows}</table>
<p class="refresh">Refreshes every {CACHE_TTL}s · Last update: {age}s ago · <a href="/api/status">JSON</a></p>
<script>setTimeout(()=>location.reload(), {CACHE_TTL*1000});</script>
</body></html>'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _respond(self, s, b):
        self.send_response(s)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(b).encode())

if __name__ == "__main__":
    t = threading.Thread(target=refresh_cache, daemon=True)
    t.start()
    s = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Status Dashboard on port {PORT}")
    s.serve_forever()
