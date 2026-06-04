#!/usr/bin/env python3
"""
Council Service Generator — scaffolds a new micro-service from template.

Usage:
    python3 scripts/new-service.py <name> <port> <description>

Example:
    python3 scripts/new-service.py emoji-picker 8781 "Returns emoji suggestions for text"
"""
import sys, os, textwrap

TEMPLATE = '''#!/usr/bin/env python3
"""SERVICE_DESC"""
import http.server, json, os

PORT = int(os.environ.get("PORT", SERVICE_PORT))

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "SERVICE_NAME"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/process":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            text = body.get("text", "")
            # TODO: implement your logic here
            result = {{"ok": True, "input": text, "output": "TODO"}}
            self._json(200, result)
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
    print(f"SERVICE_NAME on :{{PORT}}")
    server.serve_forever()
'''

DOCKER_TEMPLATE = """FROM python:3.12-slim
WORKDIR /app
COPY server.py .
EXPOSE SERVICE_PORT
CMD ["python3", "server.py"]
"""

COMPOSE_TEMPLATE = """
  SERVICE_NAME:
    build: ./poke-services/SERVICE_NAME
    ports:
      - "SERVICE_PORT:SERVICE_PORT"
    restart: unless-stopped
"""

def generate(name, port, description):
    svc_dir = f"poke-services/{name}"
    if os.path.exists(svc_dir):
        print(f"❌ Directory {svc_dir} already exists!")
        sys.exit(1)
    
    os.makedirs(svc_dir)
    
    # Write server.py
    code = TEMPLATE
    code = code.replace("SERVICE_NAME", name)
    code = code.replace("SERVICE_PORT", str(port))
    code = code.replace("SERVICE_DESC", description)
    with open(f"{svc_dir}/server.py", "w") as f:
        f.write(code)
    
    # Write Dockerfile
    docker = DOCKER_TEMPLATE.replace("SERVICE_PORT", str(port))
    with open(f"{svc_dir}/Dockerfile", "w") as f:
        f.write(docker)
    
    print(f"✅ Created {svc_dir}/")
    print(f"   server.py — {description}")
    print(f"   Dockerfile — port {port}")
    print(f"")
    print(f"Next steps:")
    print(f"  1. Edit {svc_dir}/server.py to implement your logic")
    print(f"  2. Add to docker-compose.yml:")
    print(COMPOSE_TEMPLATE.replace("SERVICE_NAME", name).replace("SERVICE_PORT", str(port)))
    print(f"  3. Add to gateway/server.py SERVICES dict:")
    print(f'    "{name}": ("localhost", {port}),')
    print(f"  4. Test: cd {svc_dir} && python3 server.py")
    print(f"  5. Commit: git add {svc_dir} && git commit -m 'feat: add {name} service'")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1]
    port = int(sys.argv[2])
    description = sys.argv[3]
    generate(name, port, description)
