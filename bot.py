from pyrogram import Client, filters
from pymongo import MongoClient
import requests
import json
import hmac
import hashlib
from config import mongo_uri, db_name, api_id, api_hash, bot_token, tripay_api_key, tripay_private_key

# Inisialisasi MongoDB
client = MongoClient(mongo_uri)
db = client[db_name]
transactions_collection = db['transactions']  # Ganti nama koleksi jika perlu

# Inisialisasi bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def generate_qris(merchant_ref):
    url = "https://api.tripay.co.id/v1/transaction/create"
    payload = {
        "method": "qris",
        "merchant_ref": merchant_ref,
        "amount": 2000,  # Jumlah pembayaran
        "currency": "IDR",
        "order_id": merchant_ref,  # Menggunakan merchant_ref sebagai order_id
        "description": "Pembayaran QRIS",
        "callback_url": "https://157.230.39.144/callback",  # Ganti dengan URL callback Anda
        "expiry": 3600,  # Waktu kadaluarsa dalam detik
    }

    # Membuat signature
    payload_encoded = json.dumps(payload).encode('utf-8')
    signature = hmac.new(tripay_private_key.encode('utf-8'), payload_encoded, hashlib.sha256).hexdigest()

    headers = {
        "Authorization": f"Bearer {tripay_api_key}",
        "Content-Type": "application/json",
        "X-Callback-Signature": signature
    }

    response = requests.post(url, headers=headers, data=payload_encoded)
    return response.json()

def create_merchant_ref(user_id):
    # Menggunakan ID pengguna dan timestamp untuk membuat merchant_ref yang unik
    timestamp = int(time.time())
    return f"INV{user_id}{timestamp}"

@app.on_message(filters.command("pay"))
def handle_pay(client, message):
    merchant_ref = create_merchant_ref(message.from_user.id)  # Buat merchant_ref otomatis
    response = generate_qris(merchant_ref)

    if response['success']:
        qris_image_url = response['data']['qris']  # Ambil URL QRIS dari respons
        client.send_photo(
            chat_id=message.chat.id,
            photo=qris_image_url,
            caption="Silakan lakukan pembayaran sebesar Rp 2.000\nSetelah pembayaran, ketik /done untuk mengonfirmasi."
        )
        
        # Simpan transaksi ke MongoDB
        transactions_collection.insert_one({
            "merchant_ref": merchant_ref,
            "user_id": message.from_user.id,
            "status": "PENDING",
            "amount": 2000
        })
    else:
        client.send_message(
            chat_id=message.chat.id,
            text="Terjadi kesalahan saat membuat QRIS. Silakan coba lagi."
        )

@app.on_message(filters.command("done"))
def handle_done(client, message):
    # Proses konfirmasi pembayaran (misalnya, periksa status di Tripay)
    # Anda bisa menambahkan logika untuk mengecek status transaksi di sini
    client.send_message(chat_id=message.chat.id, text="Terima kasih! Pembayaran Anda telah kami terima.")

if __name__ == "__main__":
    app.run()