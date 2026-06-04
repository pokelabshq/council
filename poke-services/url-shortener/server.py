#!/usr/bin/env python3
"""URL Shortener — creates short codes for long URLs."""
import http.server, json, os, hashlib, threading

PORT = int(os.environ.get("PORT", 8771))
urls = {}
lock = threading.Lock()

def short_code(url):
    h = hashlib.md5(url.encode()).hexdigest()[:6]
    return h

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            with lock:
                count = len(urls)
            self._json(200, {"ok": True, "v": 1, "service": "url-shortener", "count": count})
        elif self.path.startswith("/s/"):
            code = self.path[3:]
            with lock:
                url = urls.get(code)
            if url:
                self.send_response(302)
                self.send_header("Location", url)
                self.end_headers()
            else:
                self._json(404, {"error": "Not found"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/shorten":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            url = body.get("url", "")
            if not url:
                self._json(400, {"error": "url required"})
                return
            code = short_code(url)
            with lock:
                urls[code] = url
            self._json(200, {"ok": True, "code": code, "short_url": f"/s/{code}", "original": url})
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
    print(f"URL shortener on :{PORT}")
    server.serve_forever()
