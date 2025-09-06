import os
import hashlib
import json
from datetime import datetime

# File where hash records will be stored
HASH_FILE = "hash_records.json"


def calculate_hash(filepath, algo="sha256"):
    """Calculate hash of a file using given algorithm."""
    h = hashlib.new(algo)
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def scan_directory(directory, algo="sha256"):
    """Scan directory and return {file: hash} dictionary."""
    file_hashes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                file_hashes[path] = calculate_hash(path, algo)
            except Exception as e:
                print(f"Skipping {path}: {e}")
    return file_hashes


def save_hashes(data, filename=HASH_FILE):
    """Save file hashes to JSON."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def load_hashes(filename=HASH_FILE):
    """Load file hashes from JSON."""
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as f:
        return json.load(f)


def verify_files(directory, algo="sha256"):
    """Compare current file hashes with stored ones."""
    old_hashes = load_hashes()
    new_hashes = scan_directory(directory, algo)

    changes = {"modified": [], "deleted": [], "new": []}

    for file, old_hash in old_hashes.items():
        if file not in new_hashes:
            changes["deleted"].append(file)
        elif new_hashes[file] != old_hash:
            changes["modified"].append(file)

    for file in new_hashes:
        if file not in old_hashes:
            changes["new"].append(file)

    return changes


if __name__ == "__main__":
    folder = input("Enter folder to scan: ")
    hashes = scan_directory(folder)
    save_hashes(hashes)
    print("Baseline created. Run again to verify changes.")

