#AlphaShareBot Join @Thealphabotz
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
print("Database Connected Successfully!")

async def add_file(self, file_data: Dict[str, Any]) -> str:  
    file_doc = {  
        "file_id": file_data["file_id"],  
        "file_name": file_data["file_name"],  
        "file_size": file_data["file_size"],  
        "file_type": file_data["file_type"],  
        "uuid": file_data["uuid"],  
        "uploader_id": file_data["uploader_id"],  
        "message_id": file_data["message_id"],  # Changed from msg_id to message_id  
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
