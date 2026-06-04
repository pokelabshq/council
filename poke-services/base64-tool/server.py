#!/usr/bin/env python3
"""Base64 Tool — encodes/decodes base64 and URL-safe base64."""
import http.server, json, os, base64

PORT = int(os.environ.get("PORT", 8775))

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "base64-tool"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/encode":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            text = body.get("text", "")
            url_safe = body.get("url_safe", False)
            try:
                encoded = base64.urlsafe_b64encode(text.encode()).decode() if url_safe else base64.b64encode(text.encode()).decode()
                self._json(200, {"ok": True, "encoded": encoded, "original_length": len(text), "encoded_length": len(encoded)})
            except Exception as e:
                self._json(400, {"error": str(e)})
        elif self.path == "/api/decode":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            encoded = body.get("encoded", "")
            url_safe = body.get("url_safe", False)
            try:
                decoded = base64.urlsafe_b64decode(encoded.encode()).decode() if url_safe else base64.b64decode(encoded.encode()).decode()
                self._json(200, {"ok": True, "decoded": decoded})
            except Exception as e:
                self._json(400, {"error": f"Decode failed: {e}"})
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
    print(f"Base64 tool on :{PORT}")
    server.serve_forever()
