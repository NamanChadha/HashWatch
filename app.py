from flask import Flask, jsonify
import os
import main  # your hashwatch logic

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 HashWatch API is running!"

@app.route("/scan")
def scan():
    directory = "asset"  # sample folder in your repo
    file_hashes = main.scan_directory(directory)
    return jsonify(file_hashes)

@app.route("/verify")
def verify():
    directory = "asset"  # sample folder in your repo
    changes = main.verify_files(directory)
    return jsonify(changes)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

