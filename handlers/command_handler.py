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
                "Please join Our Forcesub Channel and try again.",
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
                message_id=file_data["message_id"]
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

@Client.on_message(filters.command("broadcast") & filters.reply)
async def broadcast_command(client: Client, message: Message):
    if not is_admin(message):
        await message.reply_text("⚠️ You are not authorized to broadcast!")
        return

    replied_msg = message.reply_to_message
    if not replied_msg:
        await message.reply_text("❌ Please reply to a message or file to broadcast!")
        return
    
    status_msg = await message.reply_text("🔄 Broadcasting message...")

    users = await db.get_all_users()
    success = 0
    failed = 0
    
    for user in users:
        try:
            if replied_msg.text:
                await client.send_message(user["user_id"], replied_msg.text)
            elif replied_msg.media:
                await client.copy_message(
                    chat_id=user["user_id"],
                    from_chat_id=replied_msg.chat.id,
                    message_id=replied_msg.message_id
                )
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
    if not replied_msg:
        await message.reply_text("❌ Please reply to a valid file!")
        return
    
    status_msg = await message.reply_text("🔄 Processing...")
    
    try:
        # Forward the message to DB channel
        forwarded_msg = await replied_msg.forward(config.DB_CHANNEL_ID)
        
        # Initialize file data
        file_data = {
            "file_id": None,
            "file_name": "Unknown",
            "file_size": 0,
            "file_type": None,
            "uuid": str(uuid.uuid4()),
            "uploader_id": message.from_user.id,
            "message_id": forwarded_msg.id
        }

        # Check all possible media types
        if replied_msg.document:
            file_data.update({
                "file_id": replied_msg.document.file_id,
                "file_name": replied_msg.document.file_name or "document",
                "file_size": replied_msg.document.file_size,
                "file_type": "document"
            })
        elif replied_msg.video:
            file_data.update({
                "file_id": replied_msg.video.file_id,
                "file_name": replied_msg.video.file_name or "video.mp4",
                "file_size": replied_msg.video.file_size,
                "file_type": "video"
            })
        elif replied_msg.audio:
            file_data.update({
                "file_id": replied_msg.audio.file_id,
                "file_name": replied_msg.audio.file_name or "audio",
                "file_size": replied_msg.audio.file_size,
                "file_type": "audio"
            })
        elif replied_msg.photo:
            file_data.update({
                "file_id": replied_msg.photo.file_id,
                "file_name": f"photo_{file_data['uuid']}.jpg",
                "file_size": replied_msg.photo.file_size,
                "file_type": "photo"
            })
        elif replied_msg.voice:
            file_data.update({
                "file_id": replied_msg.voice.file_id,
                "file_name": f"voice_{file_data['uuid']}.ogg",
                "file_size": replied_msg.voice.file_size,
                "file_type": "voice"
            })
        elif replied_msg.video_note:
            file_data.update({
                "file_id": replied_msg.video_note.file_id,
                "file_name": f"video_note_{file_data['uuid']}.mp4",
                "file_size": replied_msg.video_note.file_size,
                "file_type": "video_note"
            })
        elif replied_msg.animation:
            file_data.update({
                "file_id": replied_msg.animation.file_id,
                "file_name": replied_msg.animation.file_name or f"animation_{file_data['uuid']}.gif",
                "file_size": replied_msg.animation.file_size,
                "file_type": "animation"
            })
        else:
            await status_msg.edit_text("❌ Unsupported file type!")
            return

        # Check if file_id was set
        if not file_data["file_id"]:
            await status_msg.edit_text("❌ Could not process file!")
            return

        # Check file size
        if file_data["file_size"] and file_data["file_size"] > config.MAX_FILE_SIZE:
            await status_msg.edit_text(f"❌ File too large! Maximum size: {humanbytes(config.MAX_FILE_SIZE)}")
            return

        # Add file to database
        await db.add_file(file_data)
        share_link = f"https://t.me/{config.BOT_USERNAME}?start={file_data['uuid']}"
        
        # Send success message
        await status_msg.edit_text(
            f"✅ File uploaded successfully!\n\n"
            f"📁 File Name: {file_data['file_name']}\n"
            f"📊 Size: {humanbytes(file_data['file_size'])}\n"
            f"📎 Type: {file_data['file_type']}\n"
            f"🔗 Share Link: {share_link}",
            reply_markup=button_manager.file_button(file_data['uuid'])
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
