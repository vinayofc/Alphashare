from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, ChatJoinRequest, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
import config
from database import Database

class ForceSubscribe:
    def __init__(self, client: Client):
        self.client = client
        self.db = Database()

    async def check_subscription(self, user_id: int) -> bool:
        """Check if user is subscribed to all required channels"""
        try:
            # Check main force sub channel
            if config.FORCE_SUB_CHANNEL:
                try:
                    await self.client.get_chat_member(config.FORCE_SUB_CHANNEL, user_id)
                except UserNotParticipant:
                    return False

            # Check private force sub channel
            if config.PRIVATE_FORCE_SUB_CHANNEL:
                try:
                    member = await self.client.get_chat_member(
                        config.PRIVATE_FORCE_SUB_CHANNEL, 
                        user_id
                    )
                    # Check if join request is pending
                    if member.status == "pending":
                        return False
                except UserNotParticipant:
                    return False

            return True
        except Exception as e:
            print(f"Error checking subscription: {e}")
            return False

    async def get_invite_links(self) -> tuple[str, str]:
        """Get invite links for both channels"""
        main_invite = None
        private_invite = None
        
        try:
            if config.FORCE_SUB_CHANNEL:
                main_invite = (await self.client.create_chat_invite_link(
                    config.FORCE_SUB_CHANNEL
                )).invite_link
        except Exception as e:
            print(f"Error creating main channel invite: {e}")

        try:
            if config.PRIVATE_FORCE_SUB_CHANNEL:
                private_invite = (await self.client.create_chat_invite_link(
                    config.PRIVATE_FORCE_SUB_CHANNEL,
                    creates_join_request=True
                )).invite_link
        except Exception as e:
            print(f"Error creating private channel invite: {e}")

        return main_invite, private_invite

    async def handle_force_sub(self, message: Message) -> bool:
        """Handle force subscription check"""
        user_id = message.from_user.id
        
        if await self.check_subscription(user_id):
            return True
            
        main_invite, private_invite = await self.get_invite_links()
        
        buttons = config.Buttons.force_sub_buttons(main_invite, private_invite)
        
        text = config.Messages.FORCE_SUB_TEXT
        if private_invite:
            text += "\n\n" + config.Messages.PRIVATE_FORCE_SUB_TEXT
            
        await message.reply(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return False

    async def handle_join_request(self, join_request: ChatJoinRequest):
        """Handle incoming join requests for private channel"""
        if str(join_request.chat.id) == str(config.PRIVATE_FORCE_SUB_CHANNEL):
            user_id = join_request.from_user.id
            chat_id = join_request.chat.id
            
            # Store join request in database
            await self.db.add_pending_request(
                user_id=user_id,
                chat_id=chat_id,
                request_id=join_request.id
            )

force_sub = None

@Client.on_message(filters.private)
async def force_sub_check(client: Client, message: Message):
    global force_sub
    if force_sub is None:
        force_sub = ForceSubscribe(client)
        
    if not await force_sub.handle_force_sub(message):
        return

    # Continue processing message if subscribed
    await message.continue_propagation()

@Client.on_callback_query(filters.regex("^checksub$"))
async def check_subscription_callback(client: Client, callback: CallbackQuery):
    global force_sub
    if force_sub is None:
        force_sub = ForceSubscribe(client)
    
    user_id = callback.from_user.id
    
    if await force_sub.check_subscription(user_id):
        await callback.answer("✅ Access granted! You can use the bot now.", show_alert=True)
        await callback.message.delete()
    else:
        # Check if there's a pending join request
        if config.PRIVATE_FORCE_SUB_CHANNEL:
            request = await force_sub.db.check_join_request(
                user_id, 
                config.PRIVATE_FORCE_SUB_CHANNEL
            )
            if request and request["status"] == "pending":
                await callback.answer(
                    "Your join request is still pending. Please wait for approval.",
                    show_alert=True
                )
                return
                
        await callback.answer(
            "❌ You haven't joined the required channel(s) yet!",
            show_alert=True
        )

@Client.on_chat_join_request()
async def handle_join_request(client: Client, join_request: ChatJoinRequest):
    global force_sub
    if force_sub is None:
        force_sub = ForceSubscribe(client)
    
    await force_sub.handle_join_request(join_request)
