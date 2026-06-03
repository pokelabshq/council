#!/usr/bin/env python3
"""Poke Labs Gateway — unified API gateway. Port 8700."""
import http.server, json, urllib.request, urllib.error

PORT = 8700
PROXIES = {
    "link-preview": 8765,
    "keyword": 8766,
    "summarize": 8767,
    "qr": 8768,
    "dns": 8769,
    "portal": 8770,
    "color": 8771,
    "url": 8772,
    "template-gen": 8773,
    "health-agg": 8774,
    "json2ts": 8775,
    "github-webhook": 8776,
}

LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Poke Labs — API Gateway</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0a0a0f;color:#e0e0e0;min-height:100vh}
.header{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:3rem 2rem;text-align:center;border-bottom:1px solid #2a2a4a}
.header h1{font-size:2.5rem;background:linear-gradient(90deg,#00d4ff,#7b2ff7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.header p{color:#888;margin-top:.5rem}
.container{max-width:900px;margin:0 auto;padding:2rem}
.services{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;margin:2rem 0}
.card{background:#141428;border:1px solid #2a2a4a;border-radius:12px;padding:1.5rem;transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-2px);border-color:#7b2ff7}
.card h3{color:#00d4ff;margin-bottom:.5rem}
.card p{color:#888;font-size:.9rem;margin-bottom:1rem}
.card a{color:#7b2ff7;text-decoration:none;font-size:.85rem}
.card a:hover{text-decoration:underline}
.footer{text-align:center;padding:2rem;color:#555;font-size:.85rem}
</style>
</head>
<body>
<div class="header">
<h1>🦉 Poke Labs</h1>
<p>Open-source micro-services for developers</p>
</div>
<div class="container">
<h2 style="text-align:center;margin-bottom:.5rem">Services</h2>
<div class="services">
<div class="card"><h3>🔗 Link Preview</h3><p>Extract title, description, and image from any URL.</p><a href="/link-preview/api/health">/link-preview</a></div>
<div class="card"><h3>🔑 Keyword Extractor</h3><p>TF-IDF keyword extraction from text.</p><a href="/keyword/api/health">/keyword</a></div>
<div class="card"><h3>📝 Summarizer</h3><p>Extractive text summarization.</p><a href="/summarize/api/health">/summarize</a></div>
<div class="card"><h3>📱 QR Code</h3><p>Generate QR codes from any text or URL.</p><a href="/qr/api/health">/qr</a></div>
<div class="card"><h3>🔍 DNS Checker</h3><p>Query any DNS record type.</p><a href="/dns/api/health">/dns</a></div>
<div class="card"><h3>🎨 Color Palette</h3><p>Generate harmonious color palettes.</p><a href="/color/api/health">/color</a></div>
<div class="card"><h3>🔗 URL Shortener</h3><p>Short URLs with click tracking.</p><a href="/url/api/health">/url</a></div>
<div class="card"><h3>🏗️ Template Gen</h3><p>Scaffold new micro-services.</p><a href="/template-gen/api/health">/template-gen</a></div>
<div class="card"><h3>💪 Health Agg</h3><p>Unified health check for all services.</p><a href="/health-agg/api/status">/health-agg</a></div>
<div class="card"><h3>📋 JSON→TS</h3><p>Convert JSON to TypeScript types.</p><a href="/json2ts/api/health">/json2ts</a></div>
<div class="card"><h3>🪝 GitHub Webhook</h3><p>Receive GitHub webhooks for auto-PR-review.</p><a href="/github-webhook/api/health">/github-webhook</a></div>
</div>
</div>
<div class="footer">Poke Labs — MIT License — Built by Poke for Alexander Wondwossen</div>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p=self.path.rstrip("/") or "/"
        if p=="/" or p=="/index.html":
            self.send_response(200)
            self.send_header("Content-Type","text/html")
            self.end_headers()
            self.wfile.write(LANDING_HTML.encode())
            return
        for prefix,port in PROXIES.items():
            if p==f"/{prefix}" or p.startswith(f"/{prefix}/"):
                return self._proxy(port,p[len(prefix)+1:] or "/")
        self._json(404,{"error":"not found","available":list(PROXIES.keys())})

    def do_POST(self):
        for prefix,port in PROXIES.items():
            if self.path.startswith(f"/{prefix}/"):
                return self._proxy(port,self.path)
        self._json(404,{"error":"not found","available":list(PROXIES.keys())})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()

    def _proxy(self,port,path):
        if not path.startswith("/"): path="/"+path
        cl=int(self.headers.get("Content-Length",0))
        body=self.rfile.read(cl) if cl else None
        req=urllib.request.Request(f"http://127.0.0.1:{port}{path}",data=body,method=self.command)
        ct=self.headers.get("Content-Type")
        if ct: req.add_header("Content-Type",ct)
        try:
            resp=urllib.request.urlopen(req,timeout=30)
            self.send_response(resp.status)
            self.send_header("Content-Type",resp.headers.get("Content-Type","application/json"))
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers()
            self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type","application/json")
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self._json(502,{"error":"upstream unavailable","detail":str(e)})

    def _json(self,code,data):
        body=json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self,*a): pass

if __name__=="__main__":
    server=http.server.HTTPServer(("0.0.0.0",PORT),Handler)
    print(f"Gateway on {PORT}")
    server.serve_forever()
