from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.auto_delete import AutoDeleteManager
import config
import uuid
import humanize
from datetime import datetime
import os
from typing import Dict, Any

# Initialize auto-delete manager
auto_delete_manager = AutoDeleteManager()

@Client.on_message(filters.command("upload") & filters.reply)
async def upload_file(client: Client, message: Message):
    """Handle file upload command"""
    # Check if user is admin
    if message.from_user.id not in config.ADMIN_IDS:
        await message.reply_text("⚠️ Only admins can upload files!")
        return

    replied_msg = message.reply_to_message
    if not replied_msg or not hasattr(replied_msg, 'media'):
        await message.reply_text("❌ Please reply to a media message!")
        return

    # Get file information
    file_type = get_file_type(replied_msg)
    if not file_type:
        await message.reply_text("❌ Unsupported file type!")
        return

    file_info = await get_file_info(replied_msg, file_type)
    if not file_info:
        await message.reply_text("❌ Could not process file!")
        return

    # Generate unique ID for file
    file_info["uuid"] = str(uuid.uuid4())
    file_info["uploader_id"] = message.from_user.id
    
    # Save to database
    try:
        await client.db.add_file(file_info)
        
        # Send file to storage channel
        stored_msg = await client.send_document(
            chat_id=config.DB_CHANNEL_ID,
            document=file_info["file_id"],
            caption=f"#FILE_ID: {file_info['uuid']}\nUploaded by: {message.from_user.mention}"
        )
        
        # Update message_id in database
        file_info["message_id"] = stored_msg.id
        
        # Create share link
        share_link = f"https://t.me/{config.BOT_USERNAME}?start={file_info['uuid']}"
        
        # Send confirmation with auto-delete warning
        reply_text = config.Messages.FILE_TEXT.format(
            file_name=file_info["file_name"],
            file_size=humanize.naturalsize(file_info["file_size"]),
            file_type=file_info["file_type"].upper(),
            downloads=0,
            upload_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            uploader=message.from_user.mention,
            share_link=share_link,
            auto_delete_time=config.AUTO_DELETE_TIMER
        )
        
        reply_markup = InlineKeyboardMarkup(config.Buttons.file_buttons(file_info["uuid"]))
        
        sent_msg = await message.reply_text(
            text=reply_text,
            reply_markup=reply_markup,
            quote=True
        )
        
        # Schedule auto-deletion
        await auto_delete_manager.schedule_delete(
            client,
            sent_msg.chat.id,
            sent_msg.id,
            file_info["uuid"]
        )
        
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        await message.reply_text("❌ Failed to upload file!")

@Client.on_callback_query(filters.regex(r"^download_(.+)$"))
async def handle_download(client: Client, callback_query: CallbackQuery):
    """Handle download button clicks"""
    file_uuid = callback_query.matches[0].group(1)
    
    # Get file info from database
    file_info = await client.db.get_file(file_uuid)
    if not file_info:
        await callback_query.answer("❌ File not found or has been deleted!", show_alert=True)
        return
    
    try:
        # Forward file from storage channel
        await client.copy_message(
            chat_id=callback_query.message.chat.id,
            from_chat_id=config.DB_CHANNEL_ID,
            message_id=file_info["message_id"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⏳ Check Timer", callback_data=f"check_time_{file_uuid}")
            ]])
        )
        
        # Increment download counter
        await client.db.increment_downloads(file_uuid)
        
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        await callback_query.answer("❌ Failed to download file!", show_alert=True)

@Client.on_callback_query(filters.regex(r"^check_time_(.+)$"))
async def check_time_remaining(client: Client, callback_query: CallbackQuery):
    """Handle check timer button clicks"""
    file_uuid = callback_query.matches[0].group(1)
    
    remaining_time = await auto_delete_manager.get_time_remaining(
        callback_query.message.chat.id,
        callback_query.message.id
    )
    
    if remaining_time is not None:
        await callback_query.answer(
            f"⏳ {remaining_time} minutes remaining before deletion",
            show_alert=True
        )
    else:
        await callback_query.answer(
            "⚠️ Timer information not available",
            show_alert=True
        )

@Client.on_callback_query(filters.regex(r"^share_(.+)$"))
async def share_file(client: Client, callback_query: CallbackQuery):
    """Handle share button clicks"""
    file_uuid = callback_query.matches[0].group(1)
    share_link = f"https://t.me/{config.BOT_USERNAME}?start={file_uuid}"
    
    await callback_query.answer(
        "Share link copied to clipboard!",
        show_alert=True
    )
    
    await callback_query.message.reply_text(
        f"🔗 **Share Link:**\n`{share_link}`\n\n"
        "⚠️ Note: This file will be automatically deleted after "
        f"{config.AUTO_DELETE_TIMER} minutes from now!",
        quote=True
    )

def get_file_type(message: Message) -> str:
    """Determine the type of file from message"""
    for file_type in config.SUPPORTED_TYPES:
        if hasattr(message, file_type):
            return file_type
    return None

async def get_file_info(message: Message, file_type: str) -> Dict[str, Any]:
    """Extract file information from message"""
    try:
        file_attr = getattr(message, file_type)
        
        return {
            "file_id": file_attr.file_id,
            "file_name": getattr(file_attr, "file_name", f"file_{file_type}"),
            "file_size": file_attr.file_size,
            "file_type": file_type,
            "mime_type": getattr(file_attr, "mime_type", None)
        }
    except Exception:
        return None

@Client.on_message(filters.command("setautodelete") & filters.user(config.ADMIN_IDS))
async def set_auto_delete_timer(client: Client, message: Message):
    """Allow admins to set auto-delete timer"""
    try:
        # Get time in minutes from command
        time_str = message.text.split()[1]
        new_time = int(time_str)
        
        if new_time < 1 or new_time > 10080:  # Max 1 week
            await message.reply_text(
                "⚠️ Timer must be between 1 minute and 10080 minutes (1 week)!"
            )
            return
            
        # Update config
        config.AUTO_DELETE_TIMER = new_time
        
        await message.reply_text(
            f"✅ Auto-delete timer has been set to {new_time} minutes!"
        )
        
    except (IndexError, ValueError):
        await message.reply_text(
            "❌ Please provide a valid time in minutes!\n"
            "Example: `/setautodelete 30`"
      )
