import os
import hashlib
import json
import argparse
from datetime import datetime

HASH_FILE = "hash_records.json"


def calculate_hash(filepath, algo="sha256"):
    try:
        h = hashlib.new(algo)
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except (IOError, FileNotFoundError) as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return None


def scan_directory(directory, algo="sha256"):
    file_hashes = {}
    print(f"Scanning directory: {directory}...")
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            file_hash = calculate_hash(path, algo)
            if file_hash:
                file_hashes[path] = file_hash
    print(f"Scan complete. Found {len(file_hashes)} files.")
    return file_hashes


def save_hashes(data, filename=HASH_FILE):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Baseline saved to {filename}")
    except IOError as e:
        print(f"Error: Could not save baseline to {filename}: {e}")


def load_hashes(filename=HASH_FILE):
    if not os.path.exists(filename):
        print(f"Warning: Baseline file {filename} not found. Assuming no prior records.")
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error: Could not load or parse {filename}: {e}")
        return {}


def verify_files(directory, algo="sha256"):
    print("Verifying files against the baseline...")
    old_hashes = load_hashes()
    if not old_hashes:
        print("No baseline to compare against. Please run the 'scan' command first.")
        return None

    new_hashes = scan_directory(directory, algo)

    changes = {"modified": [], "deleted": [], "new": []}

    old_files = set(old_hashes.keys())
    new_files = set(new_hashes.keys())

    for file in old_files:
        if file not in new_files:
            changes["deleted"].append(file)
        elif old_hashes[file] != new_hashes[file]:
            changes["modified"].append(file)

    for file in new_files:
        if file not in old_files:
            changes["new"].append(file)

    return changes

def print_report(changes):
    print("\n--- File Integrity Report ---")
    if not any(changes.values()):
        print("OK: No changes detected.")
        return

    if changes["new"]:
        print(f"\n[+] NEW FILES ({len(changes['new'])}):")
        for file in changes["new"]:
            print(f"  - {file}")

    if changes["modified"]:
        print(f"\n[*] MODIFIED FILES ({len(changes['modified'])}):")
        for file in changes["modified"]:
            print(f"  - {file}")

    if changes["deleted"]:
        print(f"\n[-] DELETED FILES ({len(changes['deleted'])}):")
        for file in changes["deleted"]:
            print(f"  - {file}")
    print("\n--- End of Report ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Integrity Checker.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a directory and create a baseline hash file.")
    scan_parser.add_argument("directory", help="The directory to scan.")

    verify_parser = subparsers.add_parser("verify", help="Verify a directory against the baseline.")
    verify_parser.add_argument("directory", help="The directory to verify.")

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: Directory not found at '{args.directory}'")
    elif args.command == "scan":
        hashes = scan_directory(args.directory)
        if hashes:
            save_hashes(hashes)
    elif args.command == "verify":
        result = verify_files(args.directory)
        if result:
            print_report(result)

