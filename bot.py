from pyrogram import Client, filters
from pymongo import MongoClient
import requests
import time
import config

# Setup MongoDB connection
client = MongoClient(config.mongo_uri)
db = client[config.database_name]
transactions = db["transactions"]

bot = Client("payment_bot", api_id=config.api_id, api_hash=config.api_hash, bot_token=config.bot_token)

# Function to create QRIS payment
def create_qris_payment(user_id, amount=10000):
    url = "https://tripay.co.id/api-sandbox/transaction/create"
    headers = {"Authorization": f"Bearer {config.tripay_api_key}"}
    data = {
        "method": "QRIS",
        "merchant_ref": f"{user_id}-{int(time.time())}",
        "amount": amount,
        "customer_name": "Pengguna",
        "customer_email": "user@example.com"
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if result["success"]:
        transactions.insert_one({
            "user_id": user_id,
            "reference": result["data"]["reference"],
            "amount": amount,
            "status": "pending"
        })
        return result["data"]["checkout_url"]
    else:
        return None

# Command /pay
@bot.on_message(filters.command("pay"))
async def pay_handler(client, message):
    user_id = message.from_user.id
    checkout_url = create_qris_payment(user_id)
    
    if checkout_url:
        await message.reply(f"Silakan lakukan pembayaran sebesar Rp10.000 melalui tautan berikut:\n{checkout_url}")
    else:
        await message.reply("Terjadi kesalahan saat membuat pembayaran. Silakan coba lagi nanti.")

# Command /check_payment
@bot.on_message(filters.command("check_payment"))
async def check_payment(client, message):
    user_id = message.from_user.id
    transaction = transactions.find_one({"user_id": user_id, "status": "pending"})
    
    if transaction:
        url = f"https://tripay.co.id/api-sandbox/transaction/detail?reference={transaction['reference']}"
        headers = {"Authorization": f"Bearer {config.tripay_api_key}"}
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result["success"] and result["data"]["status"] == "PAID":
            transactions.update_one({"_id": transaction["_id"]}, {"$set": {"status": "paid"}})
            group_link = "https://t.me/joinchat/xxxxxx"
            await message.reply(f"Pembayaran berhasil! Berikut adalah link grup: {group_link}")
        else:
            await message.reply("Pembayaran belum dikonfirmasi atau masih diproses.")
    else:
        await message.reply("Anda tidak memiliki transaksi yang tertunda.")

bot.run()
