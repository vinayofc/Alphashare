from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import config
from typing import Dict, Any, Optional, List

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DATABASE_NAME]
        self.files = self.db.files
        self.users = self.db.users
        self.join_requests = self.db.join_requests
        print("Database Connected Successfully!")

    # File Operations
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
            "downloads": 0
        }
        await self.files.insert_one(file_doc)
        return file_doc["uuid"]

    async def get_file(self, uuid: str) -> Optional[Dict[str, Any]]:
        return await self.files.find_one({"uuid": uuid})

    async def increment_downloads(self, uuid: str) -> None:
        await self.files.update_one(
            {"uuid": uuid},
            {
                "$inc": {"downloads": 1},
                "$set": {"last_download": datetime.utcnow()}
            }
        )

    async def delete_file(self, uuid: str) -> bool:
        result = await self.files.delete_one({"uuid": uuid})
        return result.deleted_count > 0

    async def get_stats(self) -> Dict[str, Any]:
        total_files = await self.files.count_documents({})
        total_users = await self.users.count_documents({})
        
        total_size = 0
        total_downloads = 0
        
        async for file in self.files.find({}):
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

    # Join Request Operations
    async def store_join_request(self, data: Dict[str, Any]) -> bool:
        try:
            join_request = {
                "user_id": data["user_id"],
                "user_name": data.get("user_name"),
                "user_mention": data.get("user_mention"),
                "channel_id": data["channel_id"],
                "channel_title": data.get("channel_title"),
                "request_date": datetime.utcnow(),
                "status": "pending"
            }
            
            await self.join_requests.update_one(
                {
                    "user_id": data["user_id"],
                    "channel_id": data["channel_id"]
                },
                {"$set": join_request},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error storing join request: {str(e)}")
            return False

    async def get_join_request(self, user_id: int, channel_id: int) -> Optional[Dict[str, Any]]:
        return await self.join_requests.find_one({
            "user_id": user_id,
            "channel_id": channel_id
        })

    async def update_join_request_status(self, user_id: int, channel_id: int, status: str) -> bool:
        try:
            result = await self.join_requests.update_one(
                {
                    "user_id": user_id,
                    "channel_id": channel_id
                },
                {
                    "$set": {
                        "status": status,
                        "updated_date": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating join request: {str(e)}")
            return False
