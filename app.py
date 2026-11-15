from flask import Flask, render_template
import os

app = Flask(__name__)

COUNTER_FILE = "counter.txt"

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

if __name__ == "__main__":
    app.run(debug=True)