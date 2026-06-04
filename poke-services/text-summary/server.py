#!/usr/bin/env python3
"""Text Summary — extracts key sentences from text."""
import http.server, json, os, re
from collections import Counter

PORT = int(os.environ.get("PORT", 8770))

STOP_WORDS = {"the","a","an","is","are","was","were","be","been","being","have","has","had","do","does","did","will","would","could","should","may","might","shall","can","to","of","in","for","on","with","at","by","from","as","into","through","during","before","after","above","below","between","out","off","over","under","again","further","then","once","here","there","when","where","why","how","all","each","every","both","few","more","most","other","some","such","no","nor","not","only","own","same","so","than","too","very","just","because","but","and","or","if","while","about","up","it","its","this","that","these","those","i","me","my","we","our","you","your","he","him","his","she","her","they","them","their","what","which","who","whom"}

def summarize(text, num_sentences=3):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sentences) <= num_sentences:
        return {"summary": text, "sentences": sentences, "compression": 1.0}
    
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    word_freq = Counter(w for w in words if w not in STOP_WORDS)
    
    scores = []
    for sent in sentences:
        sent_words = re.findall(r'\b[a-z]{3,}\b', sent.lower())
        score = sum(word_freq.get(w, 0) for w in sent_words) / max(len(sent_words), 1)
        scores.append(score)
    
    # Pick top sentences by score, preserving order
    ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
    selected = sorted(ranked[:num_sentences])
    summary = " ".join(sentences[i] for i in selected)
    
    return {
        "summary": summary,
        "sentences": [sentences[i] for i in selected],
        "compression": len(summary) / len(text),
        "original_sentences": len(sentences),
    }

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "text-summary"})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/summarize":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            text = body.get("text", "")
            num = body.get("sentences", 3)
            if not text:
                self._json(400, {"error": "text required"})
                return
            result = summarize(text, num)
            self._json(200, {"ok": True, **result})
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
    print(f"Text summary on :{PORT}")
    server.serve_forever()
