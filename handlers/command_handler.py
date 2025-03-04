from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils import ButtonManager, is_admin, humanbytes
import config
import uuid
import asyncio

db = Database()
button_manager = ButtonManager()

@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await db.add_user(message.from_user.id, message.from_user.username)
    
    if len(message.command) > 1:
        file_uuid = message.command[1]
        
        if not await button_manager.check_force_sub(client, message.from_user.id):
            await message.reply_text(
                "**⚠️ You must join our channel to use this bot!**\n\n"
                "Please join @Thealphabotz and try again.",
                reply_markup=button_manager.force_sub_button()
            )
            return
        
        file_data = await db.get_file(file_uuid)
        if not file_data:
            await message.reply_text("❌ File not found or has been deleted!")
            return
        
        try:
            msg = await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=config.DB_CHANNEL_ID,
                message_id=file_data["message_id"]  # Using message_id instead of msg_id
            )
            await db.increment_downloads(file_uuid)
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")
        return
    
    await message.reply_text(
        config.Messages.START_TEXT.format(
            bot_name=config.BOT_NAME,
            user_mention=message.from_user.mention
        ),
        reply_markup=button_manager.start_button()
    )

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
        config.Messages.HELP_TEXT,
        reply_markup=button_manager.help_button()
    )

@Client.on_message(filters.command("about"))
async def about_command(client: Client, message: Message):
    await message.reply_text(
        config.Messages.ABOUT_TEXT.format(
            bot_name=config.BOT_NAME,
            version=config.BOT_VERSION
        ),
        reply_markup=button_manager.about_button()
    )

@Client.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    if not is_admin(message):
        await message.reply_text("⚠️ You are not authorized to view stats!")
        return
    
    stats = await db.get_stats()
    
    await message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"📁 Total Files: {stats['total_files']}\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"📥 Total Downloads: {stats['total_downloads']}\n"
        f"💾 Total Size: {humanbytes(stats['total_size'])}"
    )

@Client.on_message(filters.command("broadcast") & filters.user(config.ADMIN_IDS))
async def broadcast_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a message to broadcast!")
        return
    
    broadcast_msg = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔄 Broadcasting message...")
    
    users = await db.get_all_users()
    success = 0
    failed = 0
    
    for user in users:
        try:
            await client.send_message(user["user_id"], broadcast_msg)
            success += 1
        except:
            failed += 1
        await asyncio.sleep(0.1)  # To avoid flooding
    
    await status_msg.edit_text(
        f"✅ Broadcast completed!\n\n"
        f"✓ Success: {success}\n"
        f"× Failed: {failed}"
    )

@Client.on_message(filters.command("upload") & filters.reply)
async def upload_command(client: Client, message: Message):
    if not is_admin(message):
        await message.reply_text("⚠️ You are not authorized to upload files!")
        return
    
    replied_msg = message.reply_to_message
    if not replied_msg or not hasattr(replied_msg, 'media'):
        await message.reply_text("❌ Please reply to a valid media file!")
        return
    
    status_msg = await message.reply_text("🔄 Processing...")
    
    try:
        forwarded_msg = await replied_msg.forward(config.DB_CHANNEL_ID)
        
        file_type = None
        for media_type in config.SUPPORTED_TYPES:
            if hasattr(replied_msg, media_type):
                file_type = media_type
                break
        
        if not file_type:
            await status_msg.edit_text("❌ Unsupported file type!")
            return
        
        file_info = getattr(replied_msg, file_type)
        file_uuid = str(uuid.uuid4())
        
        file_data = {
            "file_id": file_info.file_id,
            "file_name": getattr(file_info, 'file_name', 'Unknown'),
            "file_size": getattr(file_info, 'file_size', 0),
            "file_type": file_type,
            "uuid": file_uuid,
            "uploader_id": message.from_user.id,
            "message_id": forwarded_msg.id  # Using message_id consistently
        }
        
        await db.add_file(file_data)
        share_link = f"https://t.me/{config.BOT_USERNAME}?start={file_uuid}"
        
        await status_msg.edit_text(
            f"✅ File uploaded successfully!\n\n"
            f"📁 File Name: {file_data['file_name']}\n"
            f"📊 Size: {humanbytes(file_data['file_size'])}\n"
            f"🔗 Share Link: {share_link}",
            reply_markup=button_manager.file_button(file_uuid)
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
