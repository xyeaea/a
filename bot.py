from pyrogram import Client
from config import api_id, api_hash, bot_token

# Inisialisasi bot
bot = Client("button_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token, plugins=dict(root="plugins"))

# Menjalankan bot
bot.run()
