from pyrogram import Client
from bot.config import Config
import os

# Create downloads directory
os.makedirs(Config.STORAGE_PATH, exist_ok=True)

# Initialize bot
app = Client(
    "abs_stream_fucker",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="bot/handlers")
)

if __name__ == "__main__":
    print("🔥 ABS_Stream_Fucker Bot Starting... 🔥")
    app.run()
