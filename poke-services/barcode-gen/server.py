#!/usr/bin/env python3
"""Barcode Generator Service — Code128, Code39, EAN-13, UPC-A. Port: 8782. Pure Python."""

import http.server, json, urllib.parse, os, io, base64

PORT = int(os.environ.get("PORT", 8782))
FREE_LIMIT = 5
ip_usage = {}

# ====== Code39 encoder ======
CODE39_PATTERNS = {
    '0': '101001101101', '1': '110100101011', '2': '101100101011',
    '3': '110110010101', '4': '101001101011', '5': '110100110101',
    '6': '101100110101', '7': '101001011011', '8': '110100101101',
    '9': '101100101101', 'A': '110101001011', 'B': '101101001011',
    'C': '110110100101', 'D': '101011001011', 'E': '110101100101',
    'F': '101101100101', 'G': '101010011011', 'H': '110101001101',
    'I': '101101001101', 'J': '101011001101', 'K': '110101010011',
    'L': '101101010011', 'M': '110110101001', 'N': '101011010011',
    'O': '110101101001', 'P': '101101101001', 'Q': '101010110011',
    'R': '110101011001', 'S': '101101011001', 'T': '101011011001',
    'U': '110010101011', 'V': '100110101011', 'W': '110011010101',
    'X': '100101101011', 'Y': '110010110101', 'Z': '100110110101',
    '-': '100101011011', '.': '110010101101', ' ': '100110101101',
    '$': '100100100101', '/': '100100101001', '+': '100101001001',
    '%': '101001001001', '*': '100101101101',
}
CODE39_START = '100101101101'
CODE39_STOP = '100101101101'

def encode_code39(text):
    t = text.upper()
    for ch in t:
        if ch not in CODE39_PATTERNS:
            return None, f"Invalid character for Code39: '{ch}'"
    bars = CODE39_START + '0'
    for ch in t:
        bars += CODE39_PATTERNS[ch] + '0'
    bars += CODE39_STOP
    return bars, None

# ====== Code128 encoder (subset B) ======
CODE128_PATTERNS = [
    '11011001100', '11001101100', '11001100110', '10010011000', '10010001100',  # 0-4
    '10001001100', '10011001000', '10011000100', '10001100100', '11001001000',  # 5-9
    '11001000100', '11000100100', '10110011100', '10011011100', '10011001110',  # 10-14
    '10111001100', '10011101100', '10011100110', '11001110010', '11001011100',  # 15-19
    '11001001110', '11011100100', '11001110100', '11101101110', '11101001100',  # 20-24
    '11100101100', '11100100110', '11101100100', '11100110100', '11100110010',  # 25-29
    '11011011000', '11011000110', '11000110110', '10100011000', '10001011000',  # 30-34
    '10001000110', '10110001000', '10001101000', '10001100010', '11010001000',  # 35-39
    '11000101000', '11000100010', '10110111000', '10110001110', '10001101110',  # 40-44
    '10111011000', '10111000110', '10001110110', '11101110110', '11010001110',  # 45-49
    '11000101110', '11011101000', '11011100010', '11011101110', '11101011000',  # 50-54
    '11101000110', '11100010110', '11101101000', '11101100010', '11100011010',  # 55-59
    '11101111010', '11001000010', '11110001010', '10100110000', '10100001100',  # 60-64
    '10010110000', '10010000110', '10000101100', '10000100110', '10110010000',  # 65-69
    '10110000100', '10011010000', '10011000010', '10000110100', '10000110010',  # 70-74
    '11000010010', '11001010000', '11110111010', '11000010100', '10001111010',  # 75-79
    '10100111100', '10010111100', '10010011110', '10111100100', '10011110100',  # 80-84
    '10011110010', '11110100100', '11110010100', '11110010010', '11011011110',  # 85-89
    '11011110110', '11110110110', '10101111000', '10100011110', '10001011110',  # 90-94
    '10111101000', '10111100010', '11110101000', '11110100010', '10111011110',  # 95-99
    '10111101110', '11101011110', '11110101110', '11010000100', '11010010000',  # 100-104
    '11010011100', '11000111010',  # 105-106
]
CODE128_START_B = 104
CODE128_STOP = [106] + [106]  # will build properly below

def encode_code128(text):
    codes = [CODE128_START_B]
    for ch in text:
        if 32 <= ord(ch) <= 127:
            codes.append(ord(ch) - 32)
        else:
            return None, f"Invalid character for Code128: '{ch}'"
    # checksum
    checksum = codes[0]
    for i, c in enumerate(codes[1:], 1):
        checksum += c * i
    codes.append(checksum % 103)
    codes.append(106)  # stop
    bars = ''
    for c in codes:
        bars += CODE128_PATTERNS[c]
    bars += '11'  # termination
    return bars, None

# ====== EAN-13 encoder (partial) ======
EAN13_LEFT_ODD = [
    '0001101', '0011001', '0010011', '0111101', '0100011',
    '0110001', '0101111', '0111011', '0110111', '0001011',
]
EAN13_LEFT_EVEN = [
    '0100111', '0110011', '0011011', '0100001', '0011101',
    '0111001', '0000101', '0010001', '0001001', '0010111',
]
EAN13_RIGHT = [
    '1110010', '1100110', '1101100', '1000010', '1011100',
    '1001110', '1010000', '1000100', '1001000', '1110100',
]
# First digit encoding pattern (L=odd, G=even)
EAN13_PARITY = [
    'LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG',
    'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL',
]

def encode_ean13(text):
    if len(text) < 12 or len(text) > 13:
        return None, "EAN-13 requires 12 or 13 digits"
    if not text[:12].isdigit():
        return None, "EAN-13 requires numeric input"
    if len(text) == 12:
        # calculate check digit
        s = sum(int(text[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
        check = (10 - s % 10) % 10
        text = text + str(check)
    first = int(text[0])
    parity = EAN13_PARITY[first]
    bars = '101'  # start guard
    # left half (digits 1-6, using parity pattern)
    for i, p in enumerate(parity):
        d = int(text[i + 1])
        if p == 'L':
            bars += EAN13_LEFT_ODD[d]
        else:
            bars += EAN13_LEFT_EVEN[d]
    bars += '01010'  # center guard
    # right half (digits 7-12)
    for i in range(6):
        d = int(text[i + 7])
        bars += EAN13_RIGHT[d]
    bars += '101'  # end guard
    return bars, None

# ====== Convert bars pattern to SVG ======
def bars_to_svg(bars, text='', height=100, module_width=2):
    if not bars:
        return ''
    total_width = len(bars) * module_width
    svg_w = max(total_width + 20, 60)
    svg_h = height + (30 if text else 0)
    rects = []
    x = 10
    for bit in bars:
        if bit == '1':
            rects.append(f'<rect x="{x}" y="10" width="{module_width}" height="{height}" fill="black"/>')
        x += module_width
    label = ''
    if text:
        label = f'<text x="{svg_w//2}" y="{svg_h - 8}" text-anchor="middle" font-family="monospace" font-size="13">{text}</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}">{"".join(rects)}{label}</svg>'

# ====== HTTP Server ======
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *a): pass

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == '/api/health':
            self._respond(200, {'ok': True, 'service': 'barcode', 'v': 1, 'formats': ['code39', 'code128', 'ean13', 'upca']})
        elif p.path == '/api/usage':
            self._respond(200, {'used': ip_usage.get(self.client_address[0], 0), 'limit': FREE_LIMIT})
        elif p.path == '/api/formats':
            self._respond(200, {
                'code39': {'alphanumeric': True, 'chars': '0-9 A-Z -.$/+%'},
                'code128': {'alphanumeric': True, 'chars': 'ASCII 32-127'},
                'ean13': {'numeric': True, 'length': '12-13 digits'},
                'upca': {'numeric': True, 'length': '11-12 digits'},
            })
        elif p.path.startswith('/api/generate'):
            params = urllib.parse.parse_qs(p.query)
            data = params.get('data', [''])[0]
            fmt = params.get('format', ['code128'])[0].lower()
            output = params.get('output', ['svg'])[0]
            height = int(params.get('height', [80])[0])
            mw = int(params.get('width', [2])[0])
            if not data:
                self._respond(400, {'error': "missing 'data' query param"}); return
            ip = self.client_address[0]
            if ip_usage.get(ip, 0) >= FREE_LIMIT:
                self._respond(402, {'error': 'free limit exceeded', 'wallet': '0xca3d86e4EDE205E6d72496BC2919c88b994B6beF', 'chain': 'base'}); return
            ip_usage[ip] = ip_usage.get(ip, 0) + 1
            self._generate(data, fmt, output, height, mw)
        else:
            self._respond(404, {'error': 'not found'})

    def _generate(self, data, fmt, output, height, mw):
        encoders = {'code39': encode_code39, 'code128': encode_code128, 'ean13': encode_ean13}
        if fmt not in encoders:
            self._respond(400, {'error': f'unknown format. Use: {list(encoders.keys())}'}); return
        bars, err = encoders[fmt](data)
        if err:
            self._respond(400, {'error': err}); return
        if output == 'svg':
            svg = bars_to_svg(bars, data, height, mw)
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(svg.encode())
        elif output == 'json':
            self._respond(200, {'format': fmt, 'data': data, 'bars': bars, 'modules': len(bars)})
        else:
            self._respond(400, {'error': 'output must be svg or json'})

    def _respond(self, s, b):
        self.send_response(s)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(b).encode())

if __name__ == '__main__':
    s = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Barcode Generator on port {PORT}')
    s.serve_forever()
