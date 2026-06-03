#!/usr/bin/env python3
"""Poke Labs — Health Check Aggregator. Port 8774.
Monitors all Poke Labs services and returns unified health status.
Free tier: 5/day. Paid via x402."""
import http.server, json, urllib.request, urllib.parse, socket
from datetime import date, datetime

PORT = 8774
FREE_LIMIT = 5
USAGE_FILE = "/tmp/health_agg_usage.json"

SERVICES = [
    {"name": "gateway", "port": 8700, "path": "/api/health"},
    {"name": "link-preview", "port": 8765, "path": "/api/health"},
    {"name": "keyword", "port": 8766, "path": "/api/health"},
    {"name": "summarize", "port": 8767, "path": "/api/health"},
    {"name": "qr", "port": 8768, "path": "/api/health"},
    {"name": "dns", "port": 8769, "path": "/api/health"},
    {"name": "portal", "port": 8770, "path": "/api/health"},
    {"name": "color", "port": 8771, "path": "/api/health"},
    {"name": "url-shortener", "port": 8772, "path": "/api/health"},
    {"name": "template-gen", "port": 8773, "path": "/api/health"},
]

def load_usage():
    try:
        with open(USAGE_FILE) as f: return json.load(f)
    except: return {}

def save_usage(u):
    with open(USAGE_FILE, "w") as f: json.dump(u, f)

def client_ip(h):
    xff = h.get("X-Forwarded-For","")
    return xff.split(",")[0].strip() if xff else h.get("Remote-Addr","127.0.0.1")

def check_limit(ip):
    u = load_usage(); today = str(date.today())
    if u.get("_date") != today: u = {"_date": today}
    used = u.get(ip, 0)
    if used >= FREE_LIMIT:
        return False, used
    u[ip] = used + 1; save_usage(u); return True, used + 1

def check_service(svc):
    try:
        url = f"http://localhost:{svc['port']}{svc['path']}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            return {"status": "up", "response": data, "port": svc["port"]}
    except Exception as e:
        return {"status": "down", "error": str(e), "port": svc["port"]}

WALLET = "0xca3d86e4EDE205E6d72496BC2919c88b994B6beF"

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path in ("/", "/index.html"):
            self._html(LANDING); return
        if p.path == "/api/health":
            self._j({"ok":True,"v":1,"service":"health-agg","free_limit":FREE_LIMIT}); return
        if p.path == "/api/status":
            ok, used = check_limit(client_ip(self.headers))
            if not ok:
                self._x402(); return
            results = []
            up_count = 0
            for svc in SERVICES:
                r = check_service(svc)
                r["name"] = svc["name"]
                if r["status"] == "up": up_count += 1
                results.append(r)
            self._j({
                "timestamp": datetime.now().isoformat(),
                "total": len(SERVICES),
                "up": up_count,
                "down": len(SERVICES) - up_count,
                "services": results,
                "remaining": FREE_LIMIT - used
            }); return
        self._j({"error":"not found"}, 404)

    def _j(self, data, code=200):
        b = json.dumps(data).encode()
        self.send_response(code); self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*"); self.end_headers(); self.wfile.write(b)

    def _x402(self):
        body = json.dumps({"error":"free limit exceeded","wallet":WALLET,"chain":"base","token":"USDC","x402":True}).encode()
        self.send_response(402); self.send_header("Content-Type","application/json")
        self.send_header("X-Payment-Required","USDC"); self.send_header("X-Payment-Wallet", WALLET)
        self.send_header("Access-Control-Allow-Origin","*"); self.end_headers(); self.wfile.write(body)

    def _html(self, content):
        self.send_response(200); self.send_header("Content-Type","text/html")
        self.end_headers(); self.wfile.write(content.encode())

    def log_message(self, *a): pass

LANDING = '''<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Health Check — Poke Labs</title>
<style>body{font-family:system-ui,sans-serif;background:#0a0a0f;color:#e0e0e0;padding:2rem;max-width:800px;margin:0 auto}
h1{color:#7b2ff7}.up{color:#4ade80}.down{color:#ef4444}
.card{background:#141428;border:1px solid #2a2a4a;border-radius:8px;padding:1rem;margin:.5rem 0}
.row{display:flex;justify-content:space-between;align-items:center}
.badge{padding:.2rem .6rem;border-radius:4px;font-size:.8rem}
.badge.up{background:#052e16;color:#4ade80}.badge.down{background:#450a0a;color:#ef4444}
code{background:#0a0a1a;padding:.2rem .4rem;border-radius:4px;font-size:.8rem}
.free{color:#4ade80}.paid{color:#fbbf24}</style></head><body>
<h1>🏥 Health Check Aggregator</h1>
<p>Monitors all Poke Labs services. Returns unified status.</p>
<div class="card">
<h3>API</h3>
<code>GET /api/status</code> — Check all services health
</div>
<div id="status">Loading...</div>
<p><span class="free">✓ 5 free/day</span> · <span class="paid">💰 Unlimited via x402</span></p>
<p>Wallet: <code>0xca3d86e4EDE205E6d72496BC2919c88b994B6beF</code></p>
<script>
async function check(){
  const r = await fetch('/api/status');
  const d = await r.json();
  let html = `<div class="card"><div class="row"><span>Total: ${d.total}</span><span class="up">↑ ${d.up} up</span><span class="down">↓ ${d.down} down</span></div></div>`;
  for(const s of d.services){
    html += `<div class="card"><div class="row"><strong>${s.name}</strong><span class="badge ${s.status}">${s.status}</span></div><code>port ${s.port}</code></div>`;
  }
  document.getElementById('status').innerHTML = html;
}
check();
</script></body></html>'''

if __name__ == "__main__":
    s = http.server.HTTPServer(("0.0.0.0", PORT), H)
    print(f"Health Agg on {PORT}"); s.serve_forever()
