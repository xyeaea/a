from pyrogram import Client, filters
import requests
import json
import uuid
from config import api_id, api_hash, bot_token, mongo_uri

bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Fungsi untuk mendapatkan QRIS
def get_qris():
    # URL endpoint API Tripay untuk QRIS
    url = "https://api.tripay.co.id/v1/transaction/create"  # Ganti dengan URL endpoint yang benar

    headers = {
        "Authorization": "Bearer YOUR_TRIPAY_API_KEY",  # Ganti dengan API Key Anda
        "Content-Type": "application/json"
    }

    # Membuat referensi unik secara otomatis
    merchant_ref = str(uuid.uuid4())  # Menghasilkan UUID sebagai referensi unik

    # Payload yang sangat minimalis
    payload = {
        "amount": 2000,  # Jumlah tetap untuk transaksi
        "merchant_ref": merchant_ref  # Referensi unik untuk transaksi
    }

    # Mengirim permintaan ke API
    response = requests.post(url, headers=headers, json=payload)

    # Mengembalikan hasil response
    return response.json()

@bot.on_message(filters.command("pay") & filters.private)
async def pay_handler(client, message):
    transaction = get_qris()  # Dapatkan QRIS dari API Tripay

    if transaction.get("success"):
        qris_url = transaction["data"]["qr_url"]  # Ambil URL QRIS
        merchant_ref = transaction["data"]["merchant_ref"]  # Ambil merchant reference
        caption = f"Silakan scan QRIS berikut untuk pembayaran.\nMerchant Ref: {merchant_ref}"

        # Kirim QRIS ke pengguna
        await message.reply_photo(qris_url, caption=caption)
    else:
        error_message = transaction.get("message", "Terjadi kesalahan saat membuat transaksi. Silakan coba lagi.")
        await message.reply_text(f"Gagal membuat transaksi: {error_message}")

bot.run()