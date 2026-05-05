from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["messagebot"]

@app.route("/")
def home():
    return "OK"

# ===== USERS =====
@app.route("/save-user", methods=["POST"])
def save_user():
    data = request.json
    existing = db.users.find_one({"userId": data["userId"]})
    if not existing:
        db.users.insert_one(data)
    return jsonify({"status": "ok"})

@app.route("/get-users", methods=["GET"])
def get_users():
    users = list(db.users.find({}, {"_id": 0}))
    return jsonify(users)

@app.route("/get-user", methods=["GET"])
def get_user():
    userId = request.args.get("userId")
    user = db.users.find_one({"userId": userId}, {"_id": 0})
    if user:
        return jsonify(user)
    return jsonify(None)

# ===== ORDERS =====
@app.route("/save-order", methods=["POST"])
def save_order():
    data = request.json
    data["time"] = data.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.orders.insert_one(data)
    return jsonify({"status": "ok"})

@app.route("/get-orders", methods=["GET"])
def get_orders():
    orders = list(db.orders.find({}, {"_id": 0}))
    return jsonify(orders)

@app.route("/delete-order", methods=["POST"])
def delete_order():
    data = request.json
    db.orders.delete_one({"id": data["id"]})
    return jsonify({"status": "ok"})

@app.route("/clear-orders", methods=["POST"])
def clear_orders():
    db.orders.delete_many({})
    return jsonify({"status": "ok"})

# ===== DELETE USER =====
@app.route("/delete-user", methods=["POST"])
def delete_user():
    data = request.json
    db.users.delete_one({"userId": data["userId"]})
    return jsonify({"status": "ok"})

# ===== MAINTENANCE MODE =====
@app.route("/get-maintenance", methods=["GET"])
def get_maintenance():
    doc = db.settings.find_one({"key": "maintenance"}, {"_id": 0})
    return jsonify({"maintenance": doc["value"] if doc else False})

@app.route("/set-maintenance", methods=["POST"])
def set_maintenance():
    data = request.json
    db.settings.update_one(
        {"key": "maintenance"},
        {"$set": {"key": "maintenance", "value": data["value"]}},
        upsert=True
    )
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
