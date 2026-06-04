#!/usr/bin/env python3
"""Markdown Renderer — converts Markdown to HTML."""
import http.server, json, os, re

PORT = int(os.environ.get("PORT", 8776))

def render_md(text):
    # Code blocks
    text = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', text, flags=re.DOTALL)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Headers
    text = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', text, flags=re.M)
    text = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', text, flags=re.M)
    text = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', text, flags=re.M)
    text = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', text, flags=re.M)
    text = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', text, flags=re.M)
    text = re.sub(r'^#\s+(.+)$', r'<h1>\h1>', text, flags=re.M)
    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Unordered lists
    text = re.sub(r'^\s*[-*]\s+(.+)$', r'<li>\1</li>', text, flags=re.M)
    # Ordered lists
    text = re.sub(r'^\s*\d+\.\s+(.+)$', r'<li>\1</li>', text, flags=re.M)
    # Blockquotes
    text = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', text, flags=re.M)
    # Horizontal rule
    text = re.sub(r'^---+$', r'<hr/>', text, flags=re.M)
    # Paragraphs (wrap non-tag lines)
    lines = text.split('\n')
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            out.append(f'<p>{stripped}</p>')
        else:
            out.append(line)
    return '\n'.join(out)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "markdown-render"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/render":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            md = body.get("markdown", "")
            if not md:
                self._json(400, {"error": "markdown required"})
                return
            html = render_md(md)
            self._json(200, {"ok": True, "html": html, "input_length": len(md), "output_length": len(html)})
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
    print(f"Markdown renderer on :{PORT}")
    server.serve_forever()
