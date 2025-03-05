from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import config
from typing import Dict, Any, Optional, List, Tuple

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DATABASE_NAME]
        self.files = self.db.files
        self.users = self.db.users
        self.pending_deletions = self.db.pending_deletions
        print("Database Connected Successfully!")

    async def add_file(self, file_data: Dict[str, Any]) -> str:
        file_doc = {
            "file_id": file_data["file_id"],
            "file_name": file_data["file_name"],
            "file_size": file_data["file_size"],
            "file_type": file_data["file_type"],
            "uuid": file_data["uuid"],
            "uploader_id": file_data["uploader_id"],
            "message_id": file_data["message_id"],
            "upload_time": datetime.utcnow(),
            "downloads": 0,
            "is_deleted": False,
            "auto_delete": True,
            "auto_delete_time": config.AUTO_DELETE_TIMER
        }
        await self.files.insert_one(file_doc)
        return file_doc["uuid"]

    async def get_file(self, uuid: str) -> Optional[Dict[str, Any]]:
        return await self.files.find_one({"uuid": uuid, "is_deleted": False})

    async def increment_downloads(self, uuid: str) -> None:
        await self.files.update_one(
            {"uuid": uuid},
            {
                "$inc": {"downloads": 1},
                "$set": {"last_download": datetime.utcnow()}
            }
        )

    async def delete_file(self, uuid: str) -> bool:
        result = await self.files.update_one(
            {"uuid": uuid},
            {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0

    async def mark_file_deleted(self, uuid: str) -> None:
        await self.files.update_one(
            {"uuid": uuid},
            {"$set": {"is_deleted": True, "delete_time": datetime.utcnow()}}
        )

    async def save_pending_deletion(self, chat_id: int, message_id: int, file_uuid: str, deletion_time: datetime) -> None:
        await self.pending_deletions.update_one(
            {"file_uuid": file_uuid},
            {
                "$set": {
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "deletion_time": deletion_time
                }
            },
            upsert=True
        )

    async def get_pending_deletions(self) -> List[Dict[str, Any]]:
        return await self.pending_deletions.find({}).to_list(None)

    async def remove_pending_deletion(self, file_uuid: str) -> None:
        await self.pending_deletions.delete_one({"file_uuid": file_uuid})

    async def get_stats(self) -> Dict[str, Any]:
        total_files = await self.files.count_documents({"is_deleted": False})
        total_users = await self.users.count_documents({})
        
        total_size = 0
        total_downloads = 0
        
        async for file in self.files.find({"is_deleted": False}):
            total_size += file.get("file_size", 0)
            total_downloads += file.get("downloads", 0)
            
        return {
            "total_files": total_files,
            "total_users": total_users,
            "total_size": total_size,
            "total_downloads": total_downloads
        }

    async def add_user(self, user_id: int, username: str = None) -> None:
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "username": username,
                    "joined_date": datetime.utcnow(),
                    "last_active": datetime.utcnow()
                }
            },
            upsert=True
        )

    async def get_all_users(self) -> List[Dict[str, Any]]:
        return await self.users.find({}).to_list(None)
