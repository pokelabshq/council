#!/usr/bin/env python3
"""Password Generator — generates secure random passwords."""
import http.server, json, os, secrets, string

PORT = int(os.environ.get("PORT", 8772))

def generate_password(length=16, upper=True, lower=True, digits=True, symbols=True):
    chars = ""
    if upper: chars += string.ascii_uppercase
    if lower: chars += string.ascii_lowercase
    if digits: chars += string.digits
    if symbols: chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if not chars:
        chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

def entropy(length, charset_size):
    import math
    return length * math.log2(max(charset_size, 2))

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "password-generator"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            n = body.get("count", 1)
            pw_len = min(body.get("length", 16), 128)
            upper = body.get("upper", True)
            lower = body.get("lower", True)
            digits = body.get("digits", True)
            symbols = body.get("symbols", True)
            passwords = [generate_password(pw_len, upper, lower, digits, symbols) for _ in range(min(n, 10))]
            charset = 0
            if upper: charset += 26
            if lower: charset += 26
            if digits: charset += 10
            if symbols: charset += 25
            ent = entropy(pw_len, charset)
            strength = "weak" if ent < 40 else "moderate" if ent < 60 else "strong" if ent < 80 else "very strong"
            self._json(200, {"ok": True, "passwords": passwords, "entropy_bits": round(ent, 1), "strength": strength})
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
    print(f"Password generator on :{PORT}")
    server.serve_forever()
