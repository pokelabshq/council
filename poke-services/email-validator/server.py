#!/usr/bin/env python3
"""Email Validator — validates email format, MX records, and checks disposable domains."""
import http.server, json, os, re, socket, dns.resolver

PORT = int(os.environ.get("PORT", 8781))

# Common disposable email domains
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
    "yopmail.com", "sharklasers.com", "guerrillamailblock.com", "grr.la",
    "dispostable.com", "mailnesia.com", "maildrop.cc", "discard.email",
    "temp-mail.org", "fakeinbox.com", "trashmail.com", "trashmail.me",
    "trashmail.net", "tempail.com", "tempr.email", "temp-mail.io",
    "mohmal.com", "burnermail.io", "mailsac.com", "harakirimail.com",
    "getnada.com", "emailondeck.com", "10minutemail.com", "minutemail.com",
}

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

def validate_format(email):
    return bool(EMAIL_REGEX.match(email))

def check_mx(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return True, [str(r.exchange).rstrip('.') for r in records]
    except Exception:
        return False, []

def is_disposable(domain):
    return domain.lower() in DISPOSABLE_DOMAINS

def get_domain_info(domain):
    mx_exists, mx_records = check_mx(domain)
    disposable = is_disposable(domain)
    
    # Check for SPF
    has_spf = False
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        for r in txt_records:
            txt = str(r).lower()
            if 'v=spf1' in txt:
                has_spf = True
                break
    except Exception:
        pass
    
    # Check for DMARC
    has_dmarc = False
    try:
        dmarc_records = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
        for r in dmarc_records:
            if 'v=dmarc1' in str(r).lower():
                has_dmarc = True
                break
    except Exception:
        pass
    
    return {
        "mx_exists": mx_exists,
        "mx_records": mx_records[:5],
        "has_spf": has_spf,
        "has_dmarc": has_dmarc,
        "disposable": disposable,
    }

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "email-validator"})
        elif self.path == "/api/disposable-list":
            self._json(200, {"domains": sorted(DISPOSABLE_DOMAINS), "count": len(DISPOSABLE_DOMAINS)})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/validate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            email = body.get("email", "").strip()
            
            if not email:
                self._json(400, {"error": "email required"})
                return
            
            email_lower = email.lower()
            domain = email_lower.split("@")[1] if "@" in email_lower else ""
            
            # Format check
            format_valid = validate_format(email)
            
            # Domain checks
            domain_info = {}
            if format_valid and domain:
                domain_info = get_domain_info(domain)
            
            # Overall score
            score = 0
            if format_valid: score += 25
            if domain_info.get("mx_exists"): score += 25
            if domain_info.get("has_spf"): score += 15
            if domain_info.get("has_dmarc"): score += 15
            if not domain_info.get("disposable"): score += 20
            
            risk = "low" if score >= 80 else "medium" if score >= 50 else "high"
            
            result = {
                "ok": True,
                "email": email_lower,
                "valid": format_valid and domain_info.get("mx_exists", False) and not domain_info.get("disposable", True),
                "score": score,
                "risk": risk,
                "checks": {
                    "format_valid": format_valid,
                    "mx_exists": domain_info.get("mx_exists", False),
                    "has_spf": domain_info.get("has_spf", False),
                    "has_dmarc": domain_info.get("has_dmarc", False),
                    "is_disposable": domain_info.get("disposable", False),
                },
                "domain_info": domain_info,
            }
            self._json(200, result)
        else:
            self._json(404, {"error": "Not found"})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Email validator on :{PORT}")
    server.serve_forever()
