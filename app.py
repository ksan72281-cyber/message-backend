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

# ===== USER ROUTES =====

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").lower().strip()
    pw = data.get("pw", "")
    if not username or not pw:
        return jsonify({"status": "error", "msg": "username/pw required"}), 400
    existing = db.users.find_one({"username": username})
    if existing:
        return jsonify({"status": "exists"})
    db.users.insert_one({
        "username": username,
        "displayName": data.get("displayName", username),
        "pw": pw,
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "ok"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").lower().strip()
    pw = data.get("pw", "")
    user = db.users.find_one({"username": username}, {"_id": 0})
    if not user:
        return jsonify({"status": "notfound"})
    if user["pw"] != pw:
        return jsonify({"status": "wrongpw"})
    return jsonify({"status": "ok", "displayName": user.get("displayName", username)})

@app.route("/get-users", methods=["GET"])
def get_users():
    users = list(db.users.find({}, {"_id": 0}))
    return jsonify(users)

# ===== ORDER ROUTES =====

@app.route("/save-order", methods=["POST"])
def save_order():
    data = request.json
    data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.orders.insert_one(data)
    return jsonify({"status": "ok"})

@app.route("/get-orders", methods=["GET"])
def get_orders():
    orders = list(db.orders.find({}, {"_id": 0}))
    return jsonify(orders)

@app.route("/delete-order", methods=["POST"])
def delete_order():
    data = request.json
    db.orders.delete_one({"time": data["time"], "contact": data.get("contact")})
    return jsonify({"status": "ok"})

@app.route("/clear-orders", methods=["POST"])
def clear_orders():
    db.orders.delete_many({})
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
