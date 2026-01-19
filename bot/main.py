from pyrogram import Client, idle
from bot.config import Config
from bot.utils.auto_delete import start_auto_delete
from bot.utils.rate_limiter import start_rate_limiter
from bot.utils.notifications import start_notification_manager
from bot.utils.error_handler import get_error_handler
import os
import asyncio
import sys

# Create downloads directory
os.makedirs(Config.STORAGE_PATH, exist_ok=True)

# Initialize bot with correct settings
app = Client(
    "abs_stream_fucker",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="bot.handlers"),  # Fixed: Use dot notation
    workdir=".",
    in_memory=True  # Don't save session file on Heroku
)

async def startup():
    """Initialize services on startup"""
    print("=" * 50)
    print("🔥 ABS_Stream_Fucker Bot Starting... 🔥")
    print("=" * 50)
    
    try:
        # Start bot
        await app.start()
        
        # Get bot info
        me = await app.get_me()
        print(f"\n✅ Bot Started Successfully!")
        print(f"📱 Bot Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print(f"👤 Bot Name: {me.first_name}")
        
        # Initialize error handler
        error_handler = get_error_handler(app)
        print("✅ Error handler initialized")
        
        # Start auto-delete service
        try:
            auto_delete = await start_auto_delete(app)
            print("✅ Auto-delete service started")
        except Exception as e:
            print(f"⚠️ Auto-delete service failed: {e}")
        
        # Start rate limiter
        try:
            await start_rate_limiter()
            print("✅ Rate limiter started")
        except Exception as e:
            print(f"⚠️ Rate limiter failed: {e}")
        
        # Start notification manager
        try:
            notification_manager = await start_notification_manager(app)
            print("✅ Notification manager started")
        except Exception as e:
            print(f"⚠️ Notification manager failed: {e}")
        
        print("\n" + "=" * 50)
        print("🚀 Bot is now LIVE and accepting commands!")
        print(f"💬 Test it: Open @{me.username} and send /start")
        print("=" * 50 + "\n")
        
        # Keep running
        await idle()
    
    except Exception as e:
        print(f"\n❌ Startup Error: {e}")
        print("⚠️ Check your configuration:")
        print("  - BOT_TOKEN is correct")
        print("  - API_ID and API_HASH are valid")
        print("  - MongoDB is accessible")
        sys.exit(1)

async def shutdown():
    """Cleanup on shutdown"""
    print("\n🛑 Shutting down...")
    try:
        await app.stop()
        print("✅ Bot stopped gracefully")
    except:
        pass

if __name__ == "__main__":
    try:
        # Run the bot
        asyncio.run(startup())
    except KeyboardInterrupt:
        print("\n⚠️ Received interrupt signal")
        asyncio.run(shutdown())
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        sys.exit(1)
