#!/usr/bin/env python3
"""Timestamp Converter — converts between Unix timestamps and human dates."""
import http.server, json, os, datetime

PORT = int(os.environ.get("PORT", 8773))

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "timestamp-converter"})
        elif self.path == "/api/now":
            now = datetime.datetime.utcnow()
            self._json(200, {"ok": True, "unix": int(now.timestamp()), "utc": now.isoformat() + "Z", "iso": now.isoformat()})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/convert":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            ts = body.get("timestamp")
            if ts is None:
                self._json(400, {"error": "timestamp required"})
                return
            try:
                ts = float(ts)
                dt = datetime.datetime.utcfromtimestamp(ts)
                self._json(200, {"ok": True, "unix": ts, "utc": dt.isoformat() + "Z", "iso": dt.isoformat(), "date": dt.strftime("%Y-%m-%d"), "time": dt.strftime("%H:%M:%S")})
            except (ValueError, OSError) as e:
                self._json(400, {"error": f"Invalid timestamp: {e}"})
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
    print(f"Timestamp converter on :{PORT}")
    server.serve_forever()
