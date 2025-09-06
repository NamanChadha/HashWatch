from flask import Flask, request, jsonify
import main

app = Flask(__name__)

@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    folder = data.get("folder")
    if not folder:
        return jsonify({"error": "Folder path is required"}), 400
    
    hashes = main.scan_directory(folder)
    main.save_hashes(hashes)
    return jsonify({
        "message": f"Hashes saved for {len(hashes)} files",
        "files": hashes
    })

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    folder = data.get("folder")
    if not folder:
        return jsonify({"error": "Folder path is required"}), 400

    changes = main.verify_files(folder)
    return jsonify(changes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
