#!/usr/bin/env python3
"""Gateway — single entry point that routes to all Council services."""
import http.server, json, os, urllib.request, urllib.error

PORT = int(os.environ.get("PORT", 8700))

# Service registry: prefix -> (host, port)
SERVICES = {
    "sentiment":       ("localhost", 8764),
    "link-preview":    ("localhost", 8765),
    "keyword-extract": ("localhost", 8766),
    "qr":              ("localhost", 8767),
    "dns":             ("localhost", 8768),
    "colors":          ("localhost", 8769),
    "summary":         ("localhost", 8770),
    "shorten":         ("localhost", 8771),
    "password":        ("localhost", 8772),
    "timestamp":       ("localhost", 8773),
    "json":            ("localhost", 8774),
    "base64":          ("localhost", 8775),
    "markdown":        ("localhost", 8776),
    "status":          ("localhost", 8778),
    "hash-gen":        ("localhost", 8779),
    "uuid-gen":        ("localhost", 8780),
    "timestamp-conv":  ("localhost", 8781),
    "barcode":         ("localhost", 8782),
    "status-dash":     ("localhost", 8790),
    "barcode":         ("localhost", 8782),
    "status-dash":     ("localhost", 8790),
    "barcode":         ("localhost", 8782),
    "status-dash":     ("localhost", 8790),
}

def proxy_request(method, service, path, body=None, headers=None):
    """Proxy a request to a backend service."""
    if service not in SERVICES:
        return None, None, None
    host, port = SERVICES[service]
    url = f"http://{host}:{port}{path}"
    try:
        req = urllib.request.Request(url, data=body, method=method)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return 503, {}, json.dumps({"error": f"Service unavailable: {e}"}).encode()

def check_all_health():
    """Check health of all registered services."""
    results = {}
    for name, (host, port) in SERVICES.items():
        try:
            with urllib.request.urlopen(f"http://{host}:{port}/api/health", timeout=2) as resp:
                data = json.loads(resp.read())
                results[name] = {"status": "up", **data}
        except Exception as e:
            results[name] = {"status": "down", "error": str(e)}
    return results

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/api":
            # API documentation
            routes = []
            for name in SERVICES:
                routes.append(f"  /api/{name}/<path>  -> {name}")
            doc = {
                "service": "Council Gateway",
                "version": 1,
                "routes": {f"/api/{name}/<path>": name for name in SERVICES},
                "health": "/api/health",
                "services": "/api/services",
            }
            self._json(200, doc)
        elif self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "gateway", "services": len(SERVICES)})
        elif self.path == "/api/services":
            health = check_all_health()
            up = sum(1 for v in health.values() if v["status"] == "up")
            self._json(200, {"services": health, "up": up, "total": len(health)})
        elif self.path.startswith("/api/"):
            parts = self.path[5:].split("/", 1)
            if len(parts) < 1:
                self._json(400, {"error": "Specify service: /api/<service>/<path>"})
                return
            service = parts[0]
            subpath = "/" + parts[1] if len(parts) > 1 else "/"
            status, headers, body = proxy_request("GET", service, subpath)
            if status is None:
                self._json(404, {"error": f"Unknown service: {service}", "available": list(SERVICES.keys())})
            else:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)
        else:
            self._json(404, {"error": "Not found. Try /api for documentation."})

    def do_POST(self):
        if self.path.startswith("/api/"):
            parts = self.path[5:].split("/", 1)
            service = parts[0]
            subpath = "/" + parts[1] if len(parts) > 1 else "/"
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else None
            status, headers, resp_body = proxy_request("POST", service, subpath, body, {"Content-Type": "application/json"})
            if status is None:
                self._json(404, {"error": f"Unknown service: {service}", "available": list(SERVICES.keys())})
            else:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(resp_body)
        else:
            self._json(404, {"error": "Not found"})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Gateway on :{PORT}")
    print(f"Routing to {len(SERVICES)} services")
    server.serve_forever()
