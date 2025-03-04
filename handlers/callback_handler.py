from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database import Database
from utils import ButtonManager, is_admin
import config

db = Database()
button_manager = ButtonManager()

@Client.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    if callback.data == "home":
        await button_manager.show_start(client, callback)
    
    elif callback.data == "help":
        await button_manager.show_help(client, callback)
    
    elif callback.data == "about":
        await button_manager.show_about(client, callback)
    
    elif callback.data.startswith("download_"):
        # Check force subscription
        if not await button_manager.check_force_sub(client, callback.from_user.id):
            await callback.answer(
                "Please join our channel to download files!",
                show_alert=True
            )
            return
            
        file_uuid = callback.data.split("_")[1]
        file_data = await db.get_file(file_uuid)
        
        if not file_data:
            await callback.answer("File not found!", show_alert=True)
            return
            
        try:
            await client.copy_message(
                chat_id=callback.message.chat.id,
                from_chat_id=config.DB_CHANNEL_ID,
                message_id=file_data["msg_id"]
            )
            await db.increment_downloads(file_uuid)
        except Exception as e:
            await callback.answer(f"Error: {str(e)}", show_alert=True)
    
    elif callback.data.startswith("share_"):
        file_uuid = callback.data.split("_")[1]
        share_link = f"https://t.me/{config.BOT_USERNAME}?start={file_uuid}"
        await callback.answer(
            f"Share Link: {share_link}",
            show_alert=True
        )
    
    await callback.answer()
