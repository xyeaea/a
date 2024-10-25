from flask import Flask, request, jsonify
from pymongo import MongoClient
import hmac
import hashlib
import config

app = Flask(__name__)

# Setup MongoDB connection
client = MongoClient(config.mongo_uri)
db = client[config.database_name]
transactions = db["transactions"]

# Verify signature from Tripay
def verify_signature(payload, signature):
    computed_signature = hmac.new(
        bytes(config.tripay_api_key, 'utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    signature = request.headers.get("X-Callback-Signature", "")
    
    if not verify_signature(request.data, signature):
        return jsonify({"success": False, "message": "Invalid signature"}), 400
    
    if data["status"] == "PAID":
        reference = data["reference"]
        
        transaction = transactions.find_one({"reference": reference})
        if transaction:
            transactions.update_one({"_id": transaction["_id"]}, {"$set": {"status": "paid"}})
            return jsonify({"success": True, "message": "Transaction updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Transaction not found"}), 404
    else:
        return jsonify({"success": False, "message": "Transaction not processed"}), 400

if __name__ == "__main__":
    app.run(port=5000)
