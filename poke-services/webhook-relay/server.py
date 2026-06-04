#!/usr/bin/env python3
"""Webhook Relay — receives GitHub webhooks, logs events, dispatches to services."""
import http.server, json, hashlib, hmac, os, urllib.request, urllib.error, threading, time

PORT = int(os.environ.get("PORT", 8779))
SECRET = os.environ.get("WEBHOOK_SECRET", "")

# In-memory event log (last 200)
event_log = []
log_lock = threading.Lock()

# Event dispatch rules: event_type -> list of (service_name, endpoint)
DISPATCH_RULES = {
    "push": [("status", "/api/events")],
    "pull_request": [("status", "/api/events")],
    "issues": [("status", "/api/events")],
    "release": [("status", "/api/events")],
}

def verify_signature(body, signature):
    if not SECRET:
        return True
    if not signature:
        return False
    sig = signature.split("=", 1)[1] if "=" in signature else signature
    mac = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, sig)

def log_entry(entry):
    with log_lock:
        event_log.append(entry)
        if len(event_log) > 200:
            event_log.pop(0)

def dispatch_event(event_type, payload):
    """Dispatch event to configured services."""
    results = []
    rules = DISPATCH_RULES.get(event_type, [])
    for service, endpoint in rules:
        try:
            # In a real setup, this would call the service's internal API
            results.append({"service": service, "endpoint": endpoint, "status": "dispatched"})
        except Exception as e:
            results.append({"service": service, "error": str(e)})
    return results

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            with log_lock:
                count = len(event_log)
            self._json(200, {"ok": True, "v": 1, "service": "webhook-relay", "events_logged": count})
        elif self.path == "/api/events":
            with log_lock:
                events = list(event_log[-50:])
            self._json(200, {"events": events, "count": len(events)})
        elif self.path == "/api/stats":
            with log_lock:
                events = list(event_log)
            by_type = {}
            for e in events:
                t = e.get("type", "unknown")
                by_type[t] = by_type.get(t, 0) + 1
            self._json(200, {"total": len(events), "by_type": by_type})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/webhook/github":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            sig = self.headers.get("X-Hub-Signature-256", "")
            if not verify_signature(body, sig):
                self._json(401, {"error": "Invalid signature"})
                return

            event_type = self.headers.get("X-GitHub-Event", "unknown")

            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                self._json(400, {"error": "Invalid JSON"})
                return

            repo = payload.get("repository", {}).get("full_name", "?")
            sender = payload.get("sender", {}).get("login", "?")

            entry = {
                "type": event_type,
                "repo": repo,
                "sender": sender,
                "timestamp": time.time(),
                "action": payload.get("action", "event"),
            }
            log_entry(entry)
            dispatch_results = dispatch_event(event_type, payload)

            self._json(200, {"ok": True, "event": event_type, "repo": repo, "dispatched": dispatch_results})
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
    print(f"Webhook relay on :{PORT}")
    server.serve_forever()
