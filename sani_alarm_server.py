
from flask import Flask, request, jsonify
import uuid
import time
import os

app = Flask(__name__)

# Zwischenspeicher (in Memory)
devices = {}
alarms = {}

@app.route("/register", methods=["POST"])
def register():
    name = request.json.get("name")
    device_id = str(uuid.uuid4())
    devices[device_id] = {"name": name, "registered": time.time()}
    alarms[device_id] = None
    return jsonify({"device_id": device_id})

@app.route("/send", methods=["POST"])
def send():
    data = request.json
    message = data.get("message")
    targets = data.get("targets")  # Liste von device_ids

    for device_id in targets:
        if device_id in devices:
            alarms[device_id] = {
                "message": message,
                "timestamp": time.time()
            }

    return jsonify({"status": "ok", "sent": len(targets)})

@app.route("/poll/<device_id>")
def poll(device_id):
    if device_id not in alarms:
        return jsonify({"error": "unknown device"}), 404

    alarm = alarms[device_id]
    if alarm:
        alarms[device_id] = None  # Nach Abfrage zurücksetzen
        return jsonify({"alarm": alarm})
    else:
        return jsonify({"alarm": None})

@app.route("/devices")
def list_devices():
    return jsonify([
        {"id": d_id, "name": info["name"]}
        for d_id, info in devices.items()
    ])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
