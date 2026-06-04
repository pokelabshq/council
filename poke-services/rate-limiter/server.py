#!/usr/bin/env python3
"""Rate Limiter — token bucket rate limiting service for the Council platform."""
import http.server, json, os, time, threading

PORT = int(os.environ.get("PORT", 8780))

# In-memory store: key -> {tokens, last_refill, max_tokens, refill_rate}
buckets = {}
lock = threading.Lock()

def get_bucket(key, max_tokens=60, refill_rate=1.0):
    """Get or create a token bucket for the given key."""
    now = time.time()
    with lock:
        if key not in buckets:
            buckets[key] = {
                "tokens": max_tokens,
                "last_refill": now,
                "max_tokens": max_tokens,
                "refill_rate": refill_rate,
            }
            return True, max_tokens - 1, max_tokens
        
        b = buckets[key]
        # Refill tokens based on elapsed time
        elapsed = now - b["last_refill"]
        new_tokens = min(b["max_tokens"], b["tokens"] + elapsed * b["refill_rate"])
        b["tokens"] = new_tokens
        b["last_refill"] = now
        
        if b["tokens"] >= 1:
            b["tokens"] -= 1
            return True, int(b["tokens"]), b["max_tokens"]
        else:
            retry_after = (1 - b["tokens"]) / b["refill_rate"]
            return False, 0, b["max_tokens"], retry_after

def cleanup_buckets(max_age=300):
    """Remove buckets older than max_age seconds."""
    now = time.time()
    with lock:
        stale = [k for k, v in buckets.items() if now - v["last_refill"] > max_age]
        for k in stale:
            del buckets[k]
        return len(stale)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            with lock:
                count = len(buckets)
            self._json(200, {"ok": True, "v": 1, "service": "rate-limiter", "active_buckets": count})
        elif self.path == "/api/stats":
            with lock:
                stats = {
                    "total_buckets": len(buckets),
                    "keys": {k: {"tokens": int(v["tokens"]), "max": v["max_tokens"]} for k, v in list(buckets.items())[:50]}
                }
            self._json(200, stats)
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/check":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            key = body.get("key", "default")
            max_tokens = body.get("max_tokens", 60)
            refill_rate = body.get("refill_rate", 1.0)
            
            result = get_bucket(key, max_tokens, refill_rate)
            allowed = result[0]
            remaining = result[1]
            limit = result[2]
            
            resp = {
                "ok": True,
                "allowed": allowed,
                "remaining": remaining,
                "limit": limit,
                "key": key,
            }
            if not allowed:
                resp["retry_after_seconds"] = round(result[3], 2)
                self._json(429, resp)
            else:
                self._json(200, resp)
        elif self.path == "/api/reset":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            key = body.get("key")
            with lock:
                if key:
                    buckets.pop(key, None)
                else:
                    buckets.clear()
            self._json(200, {"ok": True, "reset": key or "all"})
        elif self.path == "/api/cleanup":
            removed = cleanup_buckets()
            self._json(200, {"ok": True, "removed": removed})
        else:
            self._json(404, {"error": "Not found"})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        if code == 429:
            self.send_header("Retry-After", str(data.get("retry_after_seconds", 1)))
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Rate limiter on :{PORT}")
    server.serve_forever()
