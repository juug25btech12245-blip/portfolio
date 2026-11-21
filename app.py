from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
import hmac
import json
import os
import re

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COUNTER_FILE = os.path.join(BASE_DIR, "counter.txt")
MESSAGES_FILE = os.path.join(BASE_DIR, "messages.txt")


# ---------- visitor counter ----------
def get_visits():
    if not os.path.exists(COUNTER_FILE):
        return 0
    with open(COUNTER_FILE, "r") as f:
        try:
            return int(f.read())
        except ValueError:
            return 0


def save_visits(count):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))


@app.route("/")
def home():
    count = get_visits() + 1
    save_visits(count)
    return render_template("index.html", visits=count)


# ---------- contact form ----------
@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()[:100]
    email = str(data.get("email", "")).strip()[:150]
    topic = str(data.get("topic", "")).strip()[:60]
    message = str(data.get("message", "")).strip()[:1000]

    valid_email = re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email)
    if len(name) < 2 or not valid_email or len(message) < 10:
        return jsonify(ok=False, error="Please fill in every field correctly."), 400

    entry = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "name": name,
        "email": email,
        "topic": topic,
        "message": message,
    }
    with open(MESSAGES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("NEW MESSAGE:", json.dumps(entry, ensure_ascii=False), flush=True)
    return jsonify(ok=True)


# ---------- private page to read messages ----------
# Works only if you set an ADMIN_KEY value in Render. Open /messages?key=YOUR_KEY
@app.route("/messages")
def messages():
    admin_key = os.environ.get("ADMIN_KEY", "")
    given = request.args.get("key", "")
    if not admin_key or not hmac.compare_digest(admin_key, given):
        return "Not found", 404
    if not os.path.exists(MESSAGES_FILE):
        return jsonify([])
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True)
