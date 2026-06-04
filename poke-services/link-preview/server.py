#!/usr/bin/env python3
"""Link Preview — extracts title, description, image from URLs."""
import http.server, json, os, re, urllib.request, urllib.parse

PORT = int(os.environ.get("PORT", 8765))

def extract_meta(html):
    title = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
    desc = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
    if not desc:
        desc = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']', html, re.I)
    img = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
    if not img:
        img = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html, re.I)
    return {
        "title": title.group(1).strip() if title else "",
        "description": desc.group(1).strip() if desc else "",
        "image": img.group(1).strip() if img else "",
    }

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "link-preview"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/preview":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            url = body.get("url", "")
            if not url:
                self._json(400, {"error": "url required"})
                return
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "PokeBot/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                meta = extract_meta(html)
                self._json(200, {"ok": True, "url": url, **meta})
            except Exception as e:
                self._json(500, {"error": str(e)})
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
    print(f"Link preview on :{PORT}")
    server.serve_forever()
