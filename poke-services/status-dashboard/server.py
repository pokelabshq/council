#!/usr/bin/env python3
"""Status Dashboard — Live health monitor for all Council services"""
import http.server, json, urllib.request, os, threading, time

PORT = int(os.environ.get("PORT", 8778))

SERVICES = [
    ("link-preview", 8765),
    ("keyword", 8766),
    ("summarize", 8767),
    ("qr", 8768),
    ("dns", 8769),
    ("portal", 8770),
    ("color", 8771),
    ("url", 8772),
    ("template-gen", 8773),
    ("health-agg", 8774),
    ("json2ts", 8775),
    ("github-webhook", 8776),
    ("sentiment", 8777),
]

def check_service(name, port):
    try:
        req = urllib.request.urlopen(f"http://localhost:{port}/api/health", timeout=3)
        data = json.loads(req.read())
        return {"name": name, "port": port, "ok": True, "info": data}
    except Exception as e:
        return {"name": name, "port": port, "ok": False, "error": str(e)}

def get_all_status():
    results = []
    threads = []
    lock = threading.Lock()

    def check(svc):
        r = check_service(*svc)
        with lock:
            results.append(r)

    for svc in SERVICES:
        t = threading.Thread(target=check, args=(svc,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=5)

    return sorted(results, key=lambda x: x["port"])

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Council Status — Poke Labs</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'JetBrains Mono','Fira Code',monospace;background:#0a0a0f;color:#fff;min-height:100vh;padding:2rem}
h1{font-size:1.5rem;margin-bottom:0.5rem}
.sub{color:#666;font-size:0.8rem;margin-bottom:2rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}
.card{background:#111;border:1px solid #1a1a1a;border-radius:8px;padding:1.2rem;transition:border-color 0.3s}
.card.ok{border-color:#22c55e33}
.card.fail{border-color:#ef444433}
.card h3{font-size:0.9rem;margin-bottom:0.3rem}
.card .port{color:#555;font-size:0.7rem;margin-bottom:0.8rem}
.card .badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.65rem;font-weight:bold;text-transform:uppercase}
.badge.ok{background:#22c55e22;color:#22c55e}
.badge.fail{background:#ef444422;color:#ef4444}
.card .error{color:#ef4444;font-size:0.7rem;margin-top:0.5rem;word-break:break-all}
.stats{display:flex;gap:2rem;margin-bottom:2rem;padding:1rem;background:#111;border-radius:8px;border:1px solid #1a1a1a}
.stat{text-align:center}
.stat .num{font-size:2rem;font-weight:bold}
.stat .label{color:#666;font-size:0.7rem}
.num.ok{color:#22c55e}
.num.fail{color:#ef4444}
.refresh{color:#444;font-size:0.7rem;margin-top:2rem}
</style>
</head>
<body>
<h1>🏛️ Council Status</h1>
<p class="sub">Poke Labs Micro-Services Dashboard · Auto-refreshes every 10s</p>
<div class="stats" id="stats"></div>
<div class="grid" id="grid"></div>
<p class="refresh">Last check: <span id="time"></span></p>
<script>
async function fetchStatus(){
  try{
    const r=await fetch('/api/status');
    const data=await r.json();
    const services=data.services||[];
    const ok=services.filter(s=>s.ok).length;
    const fail=services.length-ok;
    document.getElementById('stats').innerHTML=`
      <div class="stat"><div class="num ok">${ok}</div><div class="label">HEALTHY</div></div>
      <div class="stat"><div class="num ${fail>0?'fail':'ok'}">${fail}</div><div class="label">DOWN</div></div>
      <div class="stat"><div class="num">${services.length}</div><div class="label">TOTAL</div></div>
      <div class="stat"><div class="num ok">${services.length?Math.round(ok/services.length*100):0}%</div><div class="label">UPTIME</div></div>
    `;
    document.getElementById('grid').innerHTML=services.map(s=>`
      <div class="card ${s.ok?'ok':'fail'}">
        <h3>${s.ok?'✅':'❌'} ${s.name}</h3>
        <div class="port">:${s.port}</div>
        <span class="badge ${s.ok?'ok':'fail'}">${s.ok?'healthy':'down'}</span>
        ${s.error?`<div class="error">${s.error}</div>`:''}
      </div>
    `).join('');
    document.getElementById('time').textContent=new Date().toLocaleTimeString();
  }catch(e){
    document.getElementById('grid').innerHTML=`<p style="color:#ef4444">Failed to fetch status: ${e.message}</p>`;
  }
}
fetchStatus();
setInterval(fetchStatus,10000);
</script>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "status-dashboard"})
        elif self.path == "/api/status":
            services = get_all_status()
            ok = sum(1 for s in services if s.ok)
            self._json(200, {
                "services": services,
                "summary": {"total": len(services), "ok": ok, "fail": len(services) - ok}
            })
        elif self.path == "/" or self.path == "/dashboard":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        else:
            self._json(404, {"error": "Not found"})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Status dashboard on :{PORT}")
    server.serve_forever()
