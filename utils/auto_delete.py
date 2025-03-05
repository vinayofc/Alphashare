import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
import config

class AutoDeleteManager:
    def __init__(self):
        self.pending_deletions: Dict[str, Dict] = {}
        
    async def schedule_delete(self, client, chat_id: int, message_id: int, file_uuid: str) -> None:
        """Schedule a message for deletion after the configured time"""
        deletion_time = datetime.utcnow() + timedelta(minutes=config.AUTO_DELETE_TIMER)
        
        # Store deletion info
        key = f"{chat_id}:{message_id}"
        self.pending_deletions[key] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "file_uuid": file_uuid,
            "deletion_time": deletion_time
        }
        
        # Start deletion task
        asyncio.create_task(self._delete_after_timeout(client, key))
        
    async def _delete_after_timeout(self, client, key: str) -> None:
        """Handle the actual deletion after timeout"""
        if key not in self.pending_deletions:
            return
            
        deletion_info = self.pending_deletions[key]
        wait_time = (deletion_info["deletion_time"] - datetime.utcnow()).total_seconds()
        
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            
            try:
                # Delete the original message
                await client.delete_messages(
                    chat_id=deletion_info["chat_id"],
                    message_ids=deletion_info["message_id"]
                )
                
                # Send expiration notification
                await client.send_message(
                    chat_id=deletion_info["chat_id"],
                    text=config.Messages.AUTO_DELETE_EXPIRED
                )
                
                # Update database to mark file as deleted
                await client.db.mark_file_deleted(deletion_info["file_uuid"])
                
            except Exception as e:
                print(f"Error in auto-deletion: {str(e)}")
            finally:
                # Clean up
                del self.pending_deletions[key]
                
    async def get_time_remaining(self, chat_id: int, message_id: int) -> Optional[int]:
        """Get remaining time for a scheduled deletion in minutes"""
        key = f"{chat_id}:{message_id}"
        if key in self.pending_deletions:
            remaining = (self.pending_deletions[key]["deletion_time"] - datetime.utcnow())
            return max(0, int(remaining.total_seconds() / 60))
        return None

    def is_scheduled(self, chat_id: int, message_id: int) -> bool:
        """Check if a message is scheduled for deletion"""
        return f"{chat_id}:{message_id}" in self.pending_deletions

    async def restore_pending_deletions(self, client, db) -> None:
        """Restore pending deletions from database after bot restart"""
        pending = await db.get_pending_deletions()
        for deletion in pending:
            await self.schedule_delete(
                client,
                deletion["chat_id"],
                deletion["message_id"],
                deletion["file_uuid"]
            )
