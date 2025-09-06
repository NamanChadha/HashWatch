import os
import hashlib
import json
from datetime import datetime
from flask import Flask, request, jsonify

# --- Configuration ---
# The directory to be scanned is set to the current directory '.',
# which is suitable for a containerized environment like Railway.
SCAN_DIRECTORY = "."
HASH_FILE = "hash_records.json"

# --- Flask App Initialization ---
app = Flask(__name__)


# --- Core Hashing and File I/O Functions (from original script) ---
def calculate_hash(filepath, algo="sha256"):
    try:
        h = hashlib.new(algo)
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except (IOError, FileNotFoundError) as e:
        app.logger.error(f"Could not read {filepath}: {e}")
        return None


def scan_directory(directory, algo="sha256"):
    file_hashes = {}
    for root, _, files in os.walk(directory):
        # Skip .git directory to avoid hashing repository metadata
        if '.git' in root:
            continue
        for file in files:
            path = os.path.join(root, file)
            file_hash = calculate_hash(path, algo)
            if file_hash:
                file_hashes[path] = file_hash
    return file_hashes


def save_hashes(data, filename=HASH_FILE):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except IOError as e:
        app.logger.error(f"Could not save baseline to {filename}: {e}")
        return False


def load_hashes(filename=HASH_FILE):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        app.logger.error(f"Could not load or parse {filename}: {e}")
        return {}


def verify_files(directory, algo="sha256"):
    old_hashes = load_hashes()
    if not old_hashes:
        return {"error": "Baseline not found. Please run a scan first."}

    new_hashes = scan_directory(directory, algo)
    changes = {"modified": [], "deleted": [], "new": []}

    old_files = set(old_hashes.keys())
    new_files = set(new_hashes.keys())

    for file in old_files:
        if file not in new_files:
            changes["deleted"].append(file)
        elif old_hashes.get(file) != new_hashes.get(file):
            changes["modified"].append(file)

    for file in new_files:
        if file not in old_files:
            changes["new"].append(file)

    # Add a summary status
    if not any(changes.values()):
        changes["status"] = "OK"
        changes["message"] = "No changes detected."
    else:
        changes["status"] = "CHANGED"
        changes["message"] = "File changes detected."


    return changes


# --- API Endpoints ---
@app.route('/scan', methods=['POST'])
def create_baseline():
    """API endpoint to scan the directory and create a new baseline."""
    app.logger.info(f"Starting scan for directory: {SCAN_DIRECTORY}")
    hashes = scan_directory(SCAN_DIRECTORY)
    if hashes and save_hashes(hashes):
        return jsonify({
            "status": "success",
            "message": f"Baseline created successfully with {len(hashes)} files.",
            "file": HASH_FILE
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to create baseline."
        }), 500


@app.route('/verify', methods=['POST'])
def check_integrity():
    """API endpoint to verify the directory against the baseline."""
    app.logger.info(f"Starting verification for directory: {SCAN_DIRECTORY}")
    result = verify_files(SCAN_DIRECTORY)
    if "error" in result:
        return jsonify(result), 404 # Not Found, as baseline is missing
    return jsonify(result), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint to show that the service is running."""
    return jsonify({
        "status": "running",
        "message": "File Integrity Checker API is active.",
        "endpoints": {
            "create_baseline": "POST /scan",
            "verify_integrity": "POST /verify"
        }
    })

# --- Main Execution ---
if __name__ == "__main__":
    # Railway provides the PORT environment variable. Default to 8080 for local dev.
    port = int(os.environ.get('PORT', 8080))
    # Host '0.0.0.0' is required to be accessible in a container
    app.run(host='0.0.0.0', port=port)
