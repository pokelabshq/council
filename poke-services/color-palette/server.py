#!/usr/bin/env python3
"""Color Palette — generates harmonious color palettes."""
import http.server, json, os, colorsys, random

PORT = int(os.environ.get("PORT", 8769))

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_palette(base_hex=None, count=5, mode="analogous"):
    if base_hex:
        r, g, b = hex_to_rgb(base_hex)
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    else:
        h, l, s = random.random(), 0.5, 0.7

    colors = []
    for i in range(count):
        if mode == "analogous":
            nh = (h + i * 0.05) % 1.0
            nl = max(0.2, min(0.8, l + (i - count//2) * 0.1))
            ns = s
        elif mode == "complementary":
            nh = (h + (i % 2) * 0.5 + i * 0.02) % 1.0
            nl = max(0.2, min(0.8, l + (i - count//2) * 0.08))
            ns = s
        elif mode == "triadic":
            nh = (h + i * 0.333) % 1.0
            nl = max(0.2, min(0.8, l + (i - count//2) * 0.1))
            ns = s
        else:  # random
            nh = (h + i * 0.15 + random.uniform(-0.05, 0.05)) % 1.0
            nl = max(0.2, min(0.8, l + random.uniform(-0.2, 0.2)))
            ns = max(0.3, min(1.0, s + random.uniform(-0.2, 0.2)))
        
        r, g, b = colorsys.hls_to_rgb(nh, nl, ns)
        hex_color = rgb_to_hex(int(r*255), int(g*255), int(b*255))
        colors.append({"hex": hex_color, "rgb": [int(r*255), int(g*255), int(b*255)]})
    
    return colors

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "color-palette"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            base = body.get("base", None)
            count = min(body.get("count", 5), 12)
            mode = body.get("mode", "analogous")
            if mode not in ("analogous", "complementary", "triadic", "random"):
                mode = "analogous"
            palette = generate_palette(base, count, mode)
            self._json(200, {"ok": True, "palette": palette, "mode": mode, "count": count})
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
    print(f"Color palette on :{PORT}")
    server.serve_forever()
