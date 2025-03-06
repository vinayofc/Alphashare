from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import config
from typing import Dict, Any, Optional, List, Tuple

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DATABASE_NAME]
        
        # Collections
        self.files = self.db.files
        self.users = self.db.users
        self.pending_deletions = self.db.pending_deletions
        self.join_requests = self.db.join_requests
        self.force_sub_settings = self.db.force_sub_settings
        
        print("Database Connected Successfully!")

    # File Management Methods
    async def add_file(self, file_data: Dict[str, Any]) -> str:
        """Add a new file to database"""
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
        """Get file details by UUID"""
        return await self.files.find_one({"uuid": uuid, "is_deleted": False})

    async def increment_downloads(self, uuid: str) -> None:
        """Increment download count for a file"""
        await self.files.update_one(
            {"uuid": uuid},
            {
                "$inc": {"downloads": 1},
                "$set": {"last_download": datetime.utcnow()}
            }
        )

    async def delete_file(self, uuid: str) -> bool:
        """Mark a file as deleted"""
        result = await self.files.update_one(
            {"uuid": uuid},
            {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0

    # Auto-Delete Management Methods
    async def mark_file_deleted(self, uuid: str) -> None:
        """Mark file as deleted with timestamp"""
        await self.files.update_one(
            {"uuid": uuid},
            {"$set": {"is_deleted": True, "delete_time": datetime.utcnow()}}
        )

    async def save_pending_deletion(self, chat_id: int, message_id: int, file_uuid: str, deletion_time: datetime) -> None:
        """Save a file for pending deletion"""
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
        """Get all pending deletions"""
        return await self.pending_deletions.find({}).to_list(None)

    async def remove_pending_deletion(self, file_uuid: str) -> None:
        """Remove a pending deletion"""
        await self.pending_deletions.delete_one({"file_uuid": file_uuid})

    # User Management Methods
    async def add_user(self, user_id: int, username: str = None) -> None:
        """Add or update user in database"""
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
        """Get all users"""
        return await self.users.find({}).to_list(None)

    async def update_user_activity(self, user_id: int) -> None:
        """Update user's last activity time"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )

    # Force Subscribe Methods
    async def save_force_sub_settings(self, channel_id: int, is_private: bool = False) -> None:
        """Save force subscribe settings"""
        await self.force_sub_settings.update_one(
            {"key": "settings"},
            {
                "$set": {
                    "channel_id": channel_id,
                    "is_private": is_private,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    async def get_force_sub_settings(self) -> Optional[Dict[str, Any]]:
        """Get force subscribe settings"""
        return await self.force_sub_settings.find_one({"key": "settings"})

    # Join Request Management Methods
    async def add_join_request(self, user_id: int, channel_id: int, request_id: str) -> None:
        """Add a new join request"""
        await self.join_requests.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {
                "$set": {
                    "request_id": request_id,
                    "status": "pending",
                    "request_time": datetime.utcnow(),
                    "last_checked": datetime.utcnow()
                }
            },
            upsert=True
        )

    async def update_join_request(self, user_id: int, channel_id: int, status: str) -> None:
        """Update join request status"""
        await self.join_requests.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    async def get_join_request(self, user_id: int, channel_id: int) -> Optional[Dict[str, Any]]:
        """Get join request details"""
        return await self.join_requests.find_one(
            {"user_id": user_id, "channel_id": channel_id}
        )

    async def check_join_request_status(self, user_id: int, channel_id: int) -> str:
        """Check join request status"""
        request = await self.get_join_request(user_id, channel_id)
        return request["status"] if request else "not_found"

    # Statistics Methods
    async def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
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

    # Cleanup Methods
    async def cleanup_old_requests(self, days: int = 7) -> None:
        """Clean up old join requests"""
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
        await self.join_requests.delete_many({
            "request_time": {"$lt": cutoff_date},
            "status": {"$in": ["approved", "rejected", "cancelled"]}
        })

    async def remove_user_data(self, user_id: int) -> None:
        """Remove all data associated with a user"""
        await self.users.delete_one({"user_id": user_id})
        await self.join_requests.delete_many({"user_id": user_id})
        await self.files.update_many(
            {"uploader_id": user_id},
            {"$set": {"uploader_id": None}}
        )
