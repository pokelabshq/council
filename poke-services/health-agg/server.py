#!/usr/bin/env python3
"""Health Aggregator — unified health check for all Council services. Port: 8791."""
import http.server, json, os, urllib.request, urllib.error, time, threading

PORT = int(os.environ.get("PORT", 8791))

SERVICES = {
    "link-preview":  ("localhost", 8765, "/api/health"),
    "sentiment":     ("localhost", 8770, "/api/health"),
    "qr":            ("localhost", 8771, "/api/health"),
    "dns":           ("localhost", 8772, "/api/health"),
    "color":         ("localhost", 8773, "/api/health"),
    "url":           ("localhost", 8774, "/api/health"),
    "keyword":       ("localhost", 8775, "/api/health"),
    "summarize":     ("localhost", 8776, "/api/health"),
    "hash-gen":      ("localhost", 8777, "/api/health"),
    "uuid-gen":      ("localhost", 8778, "/api/health"),
    "timestamp-conv":("localhost", 8781, "/api/health"),
    "barcode":       ("localhost", 8782, "/api/health"),
    "status-dash":   ("localhost", 8790, "/api/health"),
}

cache = {"results": {}, "ts": 0}
lock = threading.Lock()
TTL = 15

def check(host, port, path):
    try:
        url = f"http://{host}:{port}{path}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read())
            return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}

def refresh():
    while True:
        r = {}
        for name, (h, p, path) in SERVICES.items():
            r[name] = check(h, p, path)
        with lock:
            cache["results"] = r
            cache["ts"] = time.time()
        time.sleep(TTL)

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        from urllib.parse import urlparse
        p = urlparse(self.path)
        if p.path == "/api/health":
            self._respond(200, {"ok": True, "service": "health-agg", "v": 1})
        elif p.path == "/api/status":
            with lock:
                results, ts = dict(cache["results"]), cache["ts"]
            up = sum(1 for v in results.values() if v.get("ok"))
            total = len(results)
            overall = "healthy" if up == total else "degraded" if up > 0 else "down"
            self._respond(200, {
                "status": overall,
                "up": up, "down": total - up, "total": total,
                "services": results,
                "checked_at": ts
            })
        else:
            self._respond(404, {"error": "not found"})

    def _respond(self, s, b):
        self.send_response(s)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(b).encode())

if __name__ == "__main__":
    threading.Thread(target=refresh, daemon=True).start()
    s = http.server.HTTPServer(("0.0.0.0", PORT), H)
    print(f"Health Aggregator on port {PORT}")
    s.serve_forever()
