#!/usr/bin/env python3
"""DNS Lookup — resolves domain names to IP addresses."""
import http.server, json, os, socket

PORT = int(os.environ.get("PORT", 8768))

def resolve_dns(domain):
    results = {}
    try:
        ipv4 = socket.getaddrinfo(domain, None, socket.AF_INET)
        results["ipv4"] = list(set(r[4][0] for r in ipv4))
    except socket.gaierror:
        results["ipv4"] = []
    try:
        ipv6 = socket.getaddrinfo(domain, None, socket.AF_INET6)
        results["ipv6"] = list(set(r[4][0] for r in ipv6))
    except socket.gaierror:
        results["ipv6"] = []
    try:
        canonical = socket.getfqdn(domain)
        results["fqdn"] = canonical
    except Exception:
        results["fqdn"] = domain
    return results

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "dns-lookup"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/resolve":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            domain = body.get("domain", "").strip().rstrip(".")
            if not domain:
                self._json(400, {"error": "domain required"})
                return
            results = resolve_dns(domain)
            self._json(200, {"ok": True, "domain": domain, **results})
        else:
            self._json(404, {"error": "Not found"})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"DNS lookup on :{PORT}")
    server.serve_forever()
