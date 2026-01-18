from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from bot.config import Config
import secrets

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        
        # Collections
        self.users = self.db.users
        self.files = self.db.files
        self.fsub = self.db.fsub
        self.logs = self.db.logs
    
    # === USER MANAGEMENT ===
    async def add_user(self, user_id, username=None, is_premium=False):
        user = await self.users.find_one({"user_id": user_id})
        if not user:
            await self.users.insert_one({
                "user_id": user_id,
                "username": username,
                "is_premium": is_premium or user_id in Config.PREMIUM_USERS,
                "is_banned": False,
                "is_muted": False,
                "mute_until": None,
                "daily_files": 0,
                "daily_links": 0,
                "last_reset": datetime.utcnow().date().isoformat(),
                "joined_at": datetime.utcnow()
            })
            return True
        return False
    
    async def get_user(self, user_id):
        user = await self.users.find_one({"user_id": user_id})
        if user:
            # Reset daily limits if new day
            today = datetime.utcnow().date().isoformat()
            if user.get("last_reset") != today:
                await self.users.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "daily_files": 0,
                        "daily_links": 0,
                        "last_reset": today
                    }}
                )
                user["daily_files"] = 0
                user["daily_links"] = 0
        return user
    
    async def update_user(self, user_id, update_data):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    async def increment_file_count(self, user_id):
        await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"daily_files": 1}}
        )
    
    async def increment_link_count(self, user_id):
        await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"daily_links": 1}}
        )
    
    async def ban_user(self, user_id):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": True}}
        )
    
    async def unban_user(self, user_id):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": False}}
        )
    
    async def mute_user(self, user_id, hours=24):
        mute_until = datetime.utcnow() + timedelta(hours=hours)
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "is_muted": True,
                "mute_until": mute_until
            }}
        )
    
    async def unmute_user(self, user_id):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "is_muted": False,
                "mute_until": None
            }}
        )
    
    async def check_mute_status(self, user_id):
        user = await self.get_user(user_id)
        if user and user.get("is_muted"):
            if user.get("mute_until") and datetime.utcnow() > user["mute_until"]:
                await self.unmute_user(user_id)
                return False
            return True
        return False
    
    async def set_premium(self, user_id, status=True):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": status}}
        )
    
    async def get_all_users(self):
        return await self.users.find().to_list(None)
    
    # === FILE MANAGEMENT ===
    async def add_file(self, user_id, file_data):
        token = secrets.token_urlsafe(32)
        expiry_seconds = Config.PREMIUM_EXPIRY if file_data.get("is_premium") else Config.FREE_EXPIRY
        expiry = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        
        file_doc = {
            "user_id": user_id,
            "token": token,
            "file_id": file_data.get("file_id"),
            "file_name": file_data.get("file_name"),
            "file_size": file_data.get("file_size"),
            "mime_type": file_data.get("mime_type"),
            "password": file_data.get("password"),
            "key": file_data.get("key"),
            "is_premium": file_data.get("is_premium", False),
            "created_at": datetime.utcnow(),
            "expiry": expiry,
            "views": 0,
            "downloads": 0,
            "password_attempts": {}
        }
        
        result = await self.files.insert_one(file_doc)
        file_doc["_id"] = result.inserted_id
        return file_doc
    
    async def get_file_by_token(self, token):
        file_doc = await self.files.find_one({"token": token})
        if file_doc:
            # Check expiry
            if datetime.utcnow() > file_doc.get("expiry"):
                return None
        return file_doc
    
    async def increment_view(self, token):
        await self.files.update_one(
            {"token": token},
            {"$inc": {"views": 1}}
        )
    
    async def increment_download(self, token):
        await self.files.update_one(
            {"token": token},
            {"$inc": {"downloads": 1}}
        )
    
    async def increment_password_attempt(self, token, ip):
        await self.files.update_one(
            {"token": token},
            {"$inc": {f"password_attempts.{ip}": 1}}
        )
    
    async def get_password_attempts(self, token, ip):
        file_doc = await self.files.find_one({"token": token})
        if file_doc:
            return file_doc.get("password_attempts", {}).get(ip, 0)
        return 0
    
    # === FORCE SUBSCRIBE ===
    async def add_fsub(self, channel_id, channel_name):
        await self.fsub.update_one(
            {"channel_id": channel_id},
            {"$set": {
                "channel_id": channel_id,
                "channel_name": channel_name,
                "added_at": datetime.utcnow()
            }},
            upsert=True
        )
    
    async def remove_fsub(self, channel_id):
        await self.fsub.delete_one({"channel_id": channel_id})
    
    async def get_all_fsub(self):
        return await self.fsub.find().to_list(None)
    
    # === LOGS ===
    async def add_log(self, log_type, user_id, details=None):
        await self.logs.insert_one({
            "type": log_type,
            "user_id": user_id,
            "details": details,
            "timestamp": datetime.utcnow()
        })

db = Database()
