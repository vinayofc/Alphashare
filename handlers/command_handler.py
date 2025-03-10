from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils import ButtonManager, is_admin, humanbytes
import config
import uuid
import asyncio
import datetime

db = Database()
button_manager = ButtonManager()

@Client.on_message(filters.command("auto_del"))
async def auto_delete_command(client: Client, message: Message):
    if not is_admin(message):
        await message.reply_text("⚠️ You are not authorized to use this command!")
        return
    
    if len(message.command) != 2:
        await message.reply_text(
            "**📝 Auto Delete Command Usage**\n\n"
            "`/auto_del <minutes>`\n\n"
            "**Examples:**\n"
            "• `/auto_del 5` - Set auto-delete to 5 minutes\n"
            "• `/auto_del 60` - Set auto-delete to 1 hour\n"
            "• `/auto_del 1440` - Set auto-delete to 24 hours\n\n"
            "**Note:** Time must be between 1 and 10080 minutes (7 days)"
        )
        return
    
    try:
        delete_time = int(message.command[1])
        if not 1 <= delete_time <= 10080:
            await message.reply_text(
                "❌ **Invalid Time Range**\n\n"
                "Time must be between 1 and 10080 minutes (7 days)\n"
                "Examples:\n"
                "• 5 = 5 minutes\n"
                "• 60 = 1 hour\n"
                "• 1440 = 24 hours"
            )
            return
        
        config.DEFAULT_AUTO_DELETE = delete_time
        await message.reply_text(
            f"✅ **Auto-delete time updated**\n\n"
            f"New files will be automatically deleted after {delete_time} minutes\n"
            f"Time in other units:\n"
            f"• Hours: {delete_time/60:.1f}\n"
            f"• Days: {delete_time/1440:.1f}"
        )
    except ValueError:
        await message.reply_text(
            "❌ **Invalid Time Format**\n\n"
            "Please provide a valid number of minutes\n"
            "Example: `/auto_del 30` for 30 minutes"
        )

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
            await db.update_file_message_id(file_uuid, msg.id, message.chat.id)
            
            if file_data.get("auto_delete"):
                delete_time = file_data.get("auto_delete_time")
                if delete_time:
                    info_msg = await msg.reply_text(
                        f"⏳ **File Auto-Delete Information**\n\n"
                        f"This file will be automatically deleted in {delete_time} minutes\n"
                        f"• Delete Time: {delete_time} minutes\n"
                        f"• Time Left: {delete_time} minutes\n"
                        f"💡 **Save this file to your saved messages before it's deleted!**"
                    )
                    
                    asyncio.create_task(schedule_message_deletion(
                        client, file_uuid, message.chat.id, [msg.id, info_msg.id], delete_time
                    ))
                
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

async def schedule_message_deletion(client: Client, file_uuid: str, chat_id: int, message_ids: list, delete_time: int):
    await asyncio.sleep(delete_time * 60)
    try:
        await client.delete_messages(chat_id, message_ids)
        await client.send_message(
            chat_id=chat_id,
            text=(
                "🚫 **File Deleted Due to Copyright Protection**\n\n"
                "The file you received has been automatically deleted as part of our copyright protection measures.\n\n"
                "• If you need the file again, you can request it using the same link\n"
                "• Save important files to your saved messages before they're deleted\n"
                "• This helps us maintain a fair and legal file-sharing environment"
            )
        )
        for msg_id in message_ids:
            await db.remove_file_message(file_uuid, chat_id, msg_id)
    except Exception as e:
        print(f"Error in auto-delete: {str(e)}")

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "**📚 Bot Commands & Usage**\n\n"
        "Here are the available commands:\n\n"
        "👥 **User Commands:**\n"
        "• /start - Start the bot\n"
        "• /help - Show this help message\n"
        "• /about - About the bot\n\n"
        "👮‍♂️ **Admin Commands:**\n"
        "• /upload - Upload a file (reply to file)\n"
        "• /auto_del - Set auto-delete time\n"
        "• /stats - View bot statistics\n"
        "• /broadcast - Broadcast message to users\n\n"
        "💡 **Auto-Delete Feature:**\n"
        "Files are automatically deleted after the set time.\n"
        "Use /auto_del to change the deletion time."
    )
    await message.reply_text(help_text, reply_markup=button_manager.help_button())

@Client.on_message(filters.command("about"))
async def about_command(client: Client, message: Message):
    about_text = config.Messages.ABOUT_TEXT.format(
        bot_name=config.BOT_NAME,
        version=config.BOT_VERSION
    )
    await message.reply_text(about_text, reply_markup=button_manager.about_button())

@Client.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    if not is_admin(message):
        await message.reply_text("⚠️ You are not authorized to view stats!")
        return
    
    stats = await db.get_stats()
    stats_text = (
        "📊 **Bot Statistics**\n\n"
        f"📁 Files: {stats['total_files']}\n"
        f"👥 Users: {stats['total_users']}\n"
        f"📥 Downloads: {stats['total_downloads']}\n"
        f"💾 Size: {humanbytes(stats['total_size'])}\n"
        f"🕒 Auto-Delete Files: {stats.get('active_autodelete_files', 0)}\n\n"
        f"⏱ Current Auto-Delete Time: {getattr(config, 'DEFAULT_AUTO_DELETE', 30)} minutes"
    )
    await message.reply_text(stats_text)

@Client.on_message(filters.command("broadcast") & filters.reply)
async def broadcast_command(client: Client, message: Message):
    if not is_admin(message):
        await message.reply_text("⚠️ You are not authorized to broadcast!")
        return

    replied_msg = message.reply_to_message
    if not replied_msg:
        await message.reply_text("❌ Please reply to a message to broadcast!")
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
        await asyncio.sleep(0.1)
    
    broadcast_text = (
        "✅ **Broadcast Completed**\n\n"
        f"✓ Success: {success}\n"
        f"× Failed: {failed}\n"
        f"📊 Total: {success + failed}"
    )
    await status_msg.edit_text(broadcast_text)

@Client.on_message(filters.command("upload") & filters.reply)
async def upload_command(client: Client, message: Message):
    if not is_admin(message):
        await message.reply_text("⚠️ You are not authorized to upload files!")
        return
    
    replied_msg = message.reply_to_message
    if not replied_msg:
        await message.reply_text("❌ Please reply to a valid file!")
        return
    
    status_msg = await message.reply_text("🔄 **Processing Upload**\n\n⏳ Please wait...")
    
    try:
        forwarded_msg = await replied_msg.forward(config.DB_CHANNEL_ID)
        
        file_data = {
            "file_id": None,
            "file_name": "Unknown",
            "file_size": 0,
            "file_type": None,
            "uuid": str(uuid.uuid4()),
            "uploader_id": message.from_user.id,
            "message_id": forwarded_msg.id,
            "auto_delete": True,
            "auto_delete_time": getattr(config, 'DEFAULT_AUTO_DELETE', 30)
        }

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
            await status_msg.edit_text("❌ **Unsupported file type!**")
            return

        if not file_data["file_id"]:
            await status_msg.edit_text("❌ **Could not process file!**")
            return

        if file_data["file_size"] and file_data["file_size"] > config.MAX_FILE_SIZE:
            await status_msg.edit_text(f"❌ **File too large!**\nMaximum size: {humanbytes(config.MAX_FILE_SIZE)}")
            return

        file_uuid = await db.add_file(file_data)
        share_link = f"https://t.me/{config.BOT_USERNAME}?start={file_uuid}"
        
        upload_success_text = (
            f"✅ **File Upload Successful**\n\n"
            f"📁 **File Name:** `{file_data['file_name']}`\n"
            f"📊 **Size:** {humanbytes(file_data['file_size'])}\n"
            f"📎 **Type:** {file_data['file_type']}\n"
            f"⏱ **Auto-Delete:** {file_data['auto_delete_time']} minutes\n"
            f"🔗 **Share Link:** `{share_link}`\n\n"
            f"💡 Use `/auto_del <minutes>` to change auto-delete time"
        )
        
        await status_msg.edit_text(
            upload_success_text,
            reply_markup=button_manager.file_button(file_uuid)
        )

    except Exception as e:
        error_text = (
            "❌ **Upload Failed**\n\n"
            f"Error: {str(e)}\n\n"
            "Please try again or contact support if the issue persists."
        )
        await status_msg.edit_text(error_text)
