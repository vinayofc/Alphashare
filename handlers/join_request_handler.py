from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from database import Database
import config
from datetime import datetime

db = Database()

@Client.on_chat_join_request()
async def handle_join_request(client: Client, join_request: ChatJoinRequest):
    if not config.PRIVATE_REQUEST:
        return

    try:
        # Prepare join request data
        request_data = {
            "user_id": join_request.from_user.id,
            "user_name": join_request.from_user.username,
            "user_mention": join_request.from_user.mention,
            "channel_id": join_request.chat.id,
            "channel_title": join_request.chat.title
        }

        # Store join request in database
        await db.store_join_request(request_data)

        # If JOIN_REQUEST_CHANNEL is set, send notification
        if config.JOIN_REQUEST_CHANNEL:
            notification_text = (
                "📱 **New Join Request**\n\n"
                f"👤 **User:** {request_data['user_mention']}\n"
                f"🆔 **User ID:** `{request_data['user_id']}`\n"
                f"📢 **Channel:** {request_data['channel_title']}\n"
                f"🆔 **Channel ID:** `{request_data['channel_id']}`\n"
                f"⏰ **Request Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )

            await client.send_message(
                chat_id=config.JOIN_REQUEST_CHANNEL,
                text=notification_text,
                reply_markup=get_request_buttons(request_data['user_id'], request_data['channel_id'])
            )

    except Exception as e:
        print(f"Error handling join request: {str(e)}")

def get_request_buttons(user_id: int, channel_id: int):
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_join_{user_id}_{channel_id}"
            ),
            InlineKeyboardButton(
                "❌ Decline",
                callback_data=f"decline_join_{user_id}_{channel_id}"
            )
        ]
    ])

@Client.on_callback_query(filters.regex(r'^(approve|decline)_join_(\d+)_(-?\d+)$'))
async def handle_join_request_action(client, callback_query):
    if callback_query.from_user.id not in config.ADMIN_IDS:
        await callback_query.answer("You are not authorized to perform this action!", show_alert=True)
        return

    action, user_id, channel_id = callback_query.data.split("_")[0:3]
    user_id, channel_id = int(user_id), int(channel_id)

    try:
        if action == "approve":
            await client.approve_chat_join_request(channel_id, user_id)
            status = "approved"
            status_text = "✅ Approved"
        else:
            await client.decline_chat_join_request(channel_id, user_id)
            status = "declined"
            status_text = "❌ Declined"

        # Update request status in database
        await db.update_join_request_status(user_id, channel_id, status)

        # Update the message
        await callback_query.message.edit_text(
            callback_query.message.text + f"\n\n**Status:** {status_text}",
            reply_markup=None
        )

        await callback_query.answer(f"Join request {status}!", show_alert=True)

    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)
