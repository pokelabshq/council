#!/usr/bin/env python3
"""JSON Formatter — validates, formats, and minifies JSON."""
import http.server, json, os

PORT = int(os.environ.get("PORT", 8774))

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "json-formatter"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/format":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            data = body.get("data")
            if data is None:
                self._json(400, {"error": "data required"})
                return
            indent = body.get("indent", 2)
            try:
                parsed = data if isinstance(data, (dict, list)) else json.loads(data)
                formatted = json.dumps(parsed, indent=indent, ensure_ascii=False)
                minified = json.dumps(parsed, separators=(",", ":"), ensure_ascii=False)
                self._json(200, {"ok": True, "formatted": formatted, "minified": minified, "size_original": len(str(data)), "size_formatted": len(formatted), "size_minified": len(minified)})
            except json.JSONDecodeError as e:
                self._json(400, {"error": f"Invalid JSON: {e}"})
        elif self.path == "/api/validate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            data = body.get("data", "")
            try:
                parsed = json.loads(data) if isinstance(data, str) else data
                self._json(200, {"ok": True, "valid": True, "type": type(parsed).__name__})
            except json.JSONDecodeError as e:
                self._json(200, {"ok": True, "valid": False, "error": str(e)})
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
    print(f"JSON formatter on :{PORT}")
    server.serve_forever()
