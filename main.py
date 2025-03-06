from pyrogram import Client, idle
from database import Database
from utils.force_sub import ForceSubscribe
import config
import asyncio
import os
from pathlib import Path
from datetime import datetime
from pyrogram.types import BotCommand

# Initialize bot client
class FileShareBot(Client):
    def __init__(self):
        super().__init__(
            name="FileShareBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="handlers")
        )
        self.db = Database()
        self.force_sub = None
        print("Bot Initialized!")

    async def start(self):
        await super().start()
        
        # Initialize force subscribe handler
        self.force_sub = ForceSubscribe(self, self.db)
        
        # Set bot commands
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get help"),
            BotCommand("about", "About the bot"),
            BotCommand("stats", "Get bot statistics"),
        ]
        
        if config.ADMIN_IDS:  # Add admin commands
            admin_commands = [
                BotCommand("broadcast", "Send broadcast message"),
                BotCommand("adduser", "Add a new user"),
                BotCommand("ban", "Ban a user"),
                BotCommand("unban", "Unban a user"),
                BotCommand("setforcesub", "Configure force subscribe"),
            ]
            commands.extend(admin_commands)
            
        await self.set_bot_commands(commands)
        
        # Create database indexes
        await self.create_indexes()
        
        # Initialize force subscribe settings
        await self.init_force_subscribe()
        
        me = await self.get_me()
        print(f"Bot Started as {me.first_name}")
        print(f"Username: @{me.username}")
        print(f"Start Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("----------------")

    async def stop(self):
        """Stop the bot and cleanup"""
        try:
            # Cleanup operations
            await self.cleanup_pending_tasks()
            await super().stop()
        except Exception as e:
            print(f"Error during shutdown: {str(e)}")
        finally:
            print("Bot Stopped. Bye!")

    async def create_indexes(self):
        """Create necessary database indexes"""
        try:
            # Create indexes for join requests
            await self.db.join_requests.create_index(
                [("user_id", 1), ("channel_id", 1)], 
                unique=True
            )
            await self.db.join_requests.create_index("request_time")
            
            # Create index for force sub settings
            await self.db.force_sub_settings.create_index("key", unique=True)
            
            # Create indexes for files
            await self.db.files.create_index("uuid", unique=True)
            await self.db.files.create_index("uploader_id")
            await self.db.files.create_index("upload_time")
            
            # Create indexes for users
            await self.db.users.create_index("user_id", unique=True)
            await self.db.users.create_index("username")
            
            print("Database indexes created successfully!")
        except Exception as e:
            print(f"Error creating indexes: {str(e)}")

    async def init_force_subscribe(self):
        """Initialize force subscribe settings"""
        try:
            # Save initial force subscribe settings
            await self.db.save_force_sub_settings(
                channel_id=config.FORCE_SUB_CHANNEL,
                is_private=bool(config.FORCE_SUB_WITH_JOIN_REQUEST)
            )
            
            if config.FORCE_SUB_CHANNEL:
                try:
                    channel = await self.get_chat(config.FORCE_SUB_CHANNEL)
                    print(f"Force Subscribe Channel: {channel.title}")
                except Exception as e:
                    print(f"Error getting force subscribe channel: {str(e)}")
                    
            if config.FORCE_SUB_WITH_JOIN_REQUEST:
                try:
                    channel = await self.get_chat(config.FORCE_SUB_WITH_JOIN_REQUEST)
                    print(f"Private Force Subscribe Channel: {channel.title}")
                except Exception as e:
                    print(f"Error getting private force subscribe channel: {str(e)}")
                    
        except Exception as e:
            print(f"Error initializing force subscribe: {str(e)}")

    async def cleanup_pending_tasks(self):
        """Cleanup any pending tasks before shutdown"""
        try:
            # Cleanup old join requests
            await self.db.cleanup_old_requests(days=7)
            
            # Update any pending join requests
            pending_requests = await self.db.join_requests.find(
                {"status": "pending"}
            ).to_list(None)
            
            for request in pending_requests:
                try:
                    # Check if request is still valid
                    chat_member = await self.get_chat_member(
                        request["channel_id"],
                        request["user_id"]
                    )
                    
                    if chat_member.status != "pending":
                        await self.db.update_join_request(
                            request["user_id"],
                            request["channel_id"],
                            "expired"
                        )
                except Exception:
                    continue
                    
            print("Cleanup completed successfully!")
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

async def main():
    """Main function to run the bot"""
    bot = FileShareBot()
    
    try:
        print("Starting Bot...")
        await bot.start()
        print("Bot is Running!")
        
        # Keep the bot running
        await idle()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    try:
        # Set event loop policy for Windows if needed
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Run the bot
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        
    except KeyboardInterrupt:
        print("\nBot Stopped by User!")
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
    finally:
        # Ensure the event loop is closed
        try:
            pending = asyncio.all_tasks(loop)
            loop.run_until_complete(asyncio.gather(*pending))
            loop.close()
        except Exception as e:
            print(f"Error closing event loop: {str(e)}")
