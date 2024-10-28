from flask import Flask, request, jsonify
import hmac
import hashlib
import json
from pymongo import MongoClient
from config import mongo_uri, db_name, tripay_private_key

app = Flask(__name__)

# Inisialisasi MongoDB
client = MongoClient(mongo_uri)
db = client[db_name]
transactions_collection = db['transactions']  # Ganti nama koleksi jika perlu

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    
    # Membuat signature untuk memverifikasi
    payload = json.dumps(data).encode('utf-8')
    signature = hmac.new(tripay_private_key.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    
    # Cek signature
    if request.headers.get('X-Callback-Signature') != signature:
        return jsonify({"success": False}), 403

    # Update status transaksi di MongoDB
    transactions_collection.update_one(
        {"transaction_id": data["merchant_ref"]},
        {"$set": {"status": data["status"]}}
    )

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Ubah host dan port jika diperlukan