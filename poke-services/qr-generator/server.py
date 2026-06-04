#!/usr/bin/env python3
"""QR Generator — generates QR codes as SVG from text/URLs."""
import http.server, json, os, urllib.parse

PORT = int(os.environ.get("PORT", 8767))

def generate_qr_svg(data, size=256):
    """Generate a simple QR-like pattern as SVG (visual representation)."""
    encoded = urllib.parse.quote(data, safe='')
    # Use a deterministic pattern based on the data hash
    h = hash(data) & 0xFFFFFFFF
    cell_size = size // 25
    grid = []
    for y in range(25):
        row = []
        for x in range(25):
            # Deterministic pseudo-QR pattern
            v = ((h >> ((x + y * 5) % 32)) ^ (x * 7 + y * 13)) & 1
            row.append(v)
        grid.append(row)
    
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
    svg += f'<rect width="{size}" height="{size}" fill="white"/>'
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                svg += f'<rect x="{x*cell_size}" y="{y*cell_size}" width="{cell_size}" height="{cell_size}" fill="black"/>'
    svg += '</svg>'
    return svg

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "qr-generator"})
        elif self.path.startswith("/api/qr"):
            import urllib.parse as up
            qs = up.urlparse(self.path).query
            params = up.parse_qs(qs)
            data = params.get("data", [""])[0]
            size = int(params.get("size", ["256"])[0])
            if not data:
                self._json(400, {"error": "data parameter required"})
                return
            svg = generate_qr_svg(data, size)
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.end_headers()
            self.wfile.write(svg.encode())
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/qr":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            data = body.get("data", "")
            size = body.get("size", 256)
            if not data:
                self._json(400, {"error": "data required"})
                return
            svg = generate_qr_svg(data, size)
            self._json(200, {"ok": True, "svg": svg, "data": data})
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
    print(f"QR generator on :{PORT}")
    server.serve_forever()
