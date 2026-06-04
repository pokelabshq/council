#!/usr/bin/env python3
"""Sentiment Analysis Service — Poke Labs"""
import http.server, json, re, urllib.parse, os

PORT = int(os.environ.get("PORT", 8777))

# Simple lexicon-based sentiment (no external API needed)
POSITIVE = {
    "good": 2, "great": 3, "excellent": 4, "amazing": 4, "awesome": 4,
    "love": 3, "like": 1, "happy": 3, "joy": 3, "wonderful": 4,
    "fantastic": 4, "brilliant": 4, "best": 3, "perfect": 4, "nice": 2,
    "cool": 2, "fun": 2, "excited": 3, "beautiful": 3, "smart": 2,
    "helpful": 2, "easy": 1, "fast": 1, "reliable": 2, "solid": 2,
    "impressive": 3, "outstanding": 4, "superb": 4, "incredible": 4,
    "thank": 2, "thanks": 2, "yes": 1, "win": 3, "winning": 3,
    "success": 3, "successful": 3, "recommend": 2, "recommended": 2,
}

NEGATIVE = {
    "bad": -2, "terrible": -4, "awful": -4, "horrible": -4, "hate": -3,
    "dislike": -2, "sad": -3, "angry": -3, "worst": -4, "ugly": -3,
    "stupid": -3, "dumb": -3, "boring": -2, "slow": -1, "broken": -3,
    "bug": -2, "bugs": -2, "error": -2, "fail": -3, "failed": -3,
    "failure": -3, "crash": -3, "crashed": -3, "useless": -3,
    "waste": -2, "worst": -4, "wrong": -2, "problem": -2, "issues": -2,
    "difficult": -1, "hard": -1, "confusing": -2, "frustrating": -3,
    "annoying": -2, "disappointed": -3, "disappointing": -3, "no": -1,
    "never": -2, "nothing": -1, "none": -1, "missing": -2, "lack": -2,
}

EMOTIONS = {
    "joy": ["happy", "joy", "excited", "wonderful", "fantastic", "love", "amazing", "great", "awesome"],
    "anger": ["angry", "hate", "furious", "annoyed", "frustrated", "mad", "irritated"],
    "sadness": ["sad", "disappointed", "depressed", "unhappy", "miserable", "sorry"],
    "fear": ["afraid", "scared", "worried", "anxious", "nervous", "terrified"],
    "surprise": ["surprised", "shocked", "amazed", "astonished", "unexpected"],
    "trust": ["trust", "reliable", "dependable", "confident", "sure", "certain"],
}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json(200, {"ok": True, "v": 1, "service": "sentiment"})
        elif self.path == "/api/emotions":
            self._json(200, {"emotions": list(EMOTIONS.keys())})
        else:
            self._json(404, {"error": "Not found. POST /api/analyze with {\"text\": \"...\"}"})

    def do_POST(self):
        if self.path != "/api/analyze":
            self._json(404, {"error": "Not found"})
            return
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            text = body.get("text", "")
        except Exception:
            self._json(400, {"error": "Invalid JSON"})
            return

        if not text.strip():
            self._json(400, {"error": "text is required"})
            return

        words = re.findall(r'\b[a-z]+\b', text.lower())

        score = 0
        pos_words = []
        neg_words = []
        for w in words:
            if w in POSITIVE:
                score += POSITIVE[w]
                pos_words.append(w)
            if w in NEGATIVE:
                score += NEGATIVE[w]
                neg_words.append(w)

        # Normalize to -1..1
        max_possible = max(len(words), 1) * 4
        normalized = max(-1, min(1, score / max(max_possible * 0.3, 1)))

        if normalized > 0.1:
            label = "positive"
        elif normalized < -0.1:
            label = "negative"
        else:
            label = "neutral"

        # Detect emotions
        detected_emotions = []
        for emotion, keywords in EMOTIONS.items():
            if any(w in keywords for w in words):
                detected_emotions.append(emotion)

        self._json(200, {
            "text": text[:200],
            "sentiment": {
                "label": label,
                "score": round(normalized, 3),
                "raw_score": score,
            },
            "emotions": detected_emotions,
            "words_analyzed": len(words),
            "positive_words": list(set(pos_words)),
            "negative_words": list(set(neg_words)),
        })

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, fmt, *args):
        pass  # quiet

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Sentiment service on :{PORT}")
    server.serve_forever()
