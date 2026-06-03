#!/usr/bin/env python3
"""Link Preview API — extracts title, description, image from any URL.
Free tier (3/IP/day) + x402 USDC payments on Base."""
import http.server, json, os
from urllib.request import urlopen, Request
from urllib.parse import urljoin
from html.parser import HTMLParser

PORT = 8765
FREE_LIMIT = 3
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
USAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usage.json")

try:
    usage = json.load(open(USAGE_FILE))
except:
    usage = {}

def save():
    json.dump(usage, open(USAGE_FILE, "w"))

class M(HTMLParser):
    def __init__(self):
        super().__init__()
        self.t=self.d=self.i=self.sn=self.f=""
        self._it=False
    def handle_starttag(self,t,a):
        a=dict(a)
        if t=="title": self._it=True
        elif t=="meta":
            p=a.get("property","").lower(); n=a.get("name","").lower(); c=a.get("content","")
            if p=="og:title" or (n=="title" and not self.t): self.t=c
            elif p=="og:description" or (n=="description" and not self.d): self.d=c
            elif p=="og:image" and not self.i: self.i=c
            elif p=="og:site_name": self.sn=c
        elif t=="link" and "icon" in a.get("rel",""): self.f=a.get("href","")
    def handle_data(self,s):
        if self._it and not self.t: self.t=s.strip()
    def handle_endtag(self,t):
        if t=="title": self._it=False

def extract(url):
    try:
        r=urlopen(Request(url,headers={"User-Agent":"PokeBot/1.0","Accept":"text/html"}),timeout=10)
        h=r.read(50000).decode("utf-8","replace")
        p=M(); p.feed(h)
        if p.f and not p.f.startswith("http"): p.f=urljoin(url,p.f)
        if p.i and not p.i.startswith("http"): p.i=urljoin(url,p.i)
        return {"title":p.t or url,"description":p.d,"image":p.i,"site_name":p.sn,"favicon":p.f,"ok":True}
    except Exception as e:
        return {"title":url,"ok":False,"error":str(e)}

class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path!="/api/preview": return self.js(404,{"error":"not found"})
        ip=self.client_address[0]
        if usage.get(ip,0)>=FREE_LIMIT: return self.js(402,{"error":"limit exceeded","wallet":"0xca3d86e4EDE205E6d72496BC2919c88b994B6beF","used":usage.get(ip,0),"limit":FREE_LIMIT})
        try: body=json.loads(self.rfile.read(int(self.headers.get("Content-Length",0))))
        except: return self.js(400,{"error":"bad json"})
        url=body.get("url","").strip()
        if not url.startswith("http"): return self.js(400,{"error":"need http(s) url"})
        usage[ip]=usage.get(ip,0)+1; save()
        self.js(200,extract(url))
    def do_GET(self):
        if self.path=="/api/health": return self.js(200,{"ok":True,"v":4,"free_limit":FREE_LIMIT})
        if self.path=="/api/usage": return self.js(200,{"used":usage.get(self.client_address[0],0),"limit":FREE_LIMIT})
        # Serve static landing page
        if self.path=="/" or self.path=="/index.html":
            try:
                with open(os.path.join(PUBLIC_DIR,"index.html"),"rb") as f: html=f.read()
                self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(html)
            except: self.js(500,{"error":"landing page missing"})
            return
        self.js(404,{"error":"not found"})
    def js(self,code,data):
        b=json.dumps(data).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers(); self.wfile.write(b)
    def log_message(self,*a): pass

http.server.HTTPServer(("0.0.0.0",PORT),H).serve_forever()
