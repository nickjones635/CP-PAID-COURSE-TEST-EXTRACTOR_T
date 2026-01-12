from flask import Flask, send_from_directory
import os
from config import TMP_DIR

app = Flask(__name__)

@app.route("/")
def index():
    return "<h3>Classplus Mock Extractor Bot is running.</h3>"

@app.route("/tmp/<path:filename>")
def serve_file(filename):
    return send_from_directory(TMP_DIR, filename)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
