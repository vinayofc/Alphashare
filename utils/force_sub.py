from pyrogram import Client
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
import config
from database import Database

class ForceSubscribe:
    def __init__(self, client: Client, db: Database):
        self.client = client
        self.db = db

    async def check_subscription(self, user_id: int) -> bool:
        """Check if user is subscribed to required channels"""
        try:
            # Check main force sub channel
            if config.FORCE_SUB_CHANNEL != 0:
                try:
                    await self.client.get_chat_member(config.FORCE_SUB_CHANNEL, user_id)
                except UserNotParticipant:
                    return False

            # Check join request force sub channel
            if config.FORCE_SUB_WITH_JOIN_REQUEST != 0:
                try:
                    member = await self.client.get_chat_member(
                        config.FORCE_SUB_WITH_JOIN_REQUEST, 
                        user_id
                    )
                    # For private channels, check if join request is pending
                    if config.FORCE_SUB_TYPE == "private":
                        if member.status == "pending":
                            return False
                    return True
                except UserNotParticipant:
                    return False
            
            return True
        except Exception as e:
            print(f"Error checking subscription: {e}")
            return False

    async def handle_force_sub(self, user_id: int) -> tuple[bool, InlineKeyboardMarkup]:
        """Handle force subscription check and return status and appropriate keyboard"""
        is_subscribed = await self.check_subscription(user_id)
        
        if is_subscribed:
            return True, None
            
        buttons = []
        
        # Add main force sub channel button if configured
        if config.FORCE_SUB_CHANNEL != 0:
            channel = await self.client.get_chat(config.FORCE_SUB_CHANNEL)
            invite_link = await self.client.create_chat_invite_link(config.FORCE_SUB_CHANNEL)
            buttons.append([
                InlineKeyboardButton("📢 Join Channel", url=invite_link.invite_link)
            ])

        # Add join request force sub button if configured
        if config.FORCE_SUB_WITH_JOIN_REQUEST != 0:
            try:
                channel = await self.client.get_chat(config.FORCE_SUB_WITH_JOIN_REQUEST)
                if config.FORCE_SUB_TYPE == "private":
                    # For private channels, create join request link
                    invite_link = await self.client.create_chat_invite_link(
                        config.FORCE_SUB_WITH_JOIN_REQUEST,
                        creates_join_request=True
                    )
                else:
                    # For public channels, create normal invite link
                    invite_link = await self.client.create_chat_invite_link(
                        config.FORCE_SUB_WITH_JOIN_REQUEST
                    )
                buttons.append([
                    InlineKeyboardButton(
                        "🔒 Join Private Channel" if config.FORCE_SUB_TYPE == "private" else "📢 Join Channel",
                        url=invite_link.invite_link
                    )
                ])
            except ChatAdminRequired:
                print(f"Bot is not admin in channel {config.FORCE_SUB_WITH_JOIN_REQUEST}")

        buttons.append([
            InlineKeyboardButton("🔄 Check Access", callback_data=f"checksub_{user_id}")
        ])
        
        return False, InlineKeyboardMarkup(buttons)

    async def handle_join_request(self, client: Client, join_request: ChatJoinRequest) -> None:
        """Handle incoming join requests for private channels"""
        if str(join_request.chat.id) == str(config.FORCE_SUB_WITH_JOIN_REQUEST):
            # Store the join request in database for verification
            await self.db.add_pending_request(
                user_id=join_request.from_user.id,
                chat_id=join_request.chat.id,
                request_id=join_request.id,
                request_time=join_request.date
              )
