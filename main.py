#AlphaShare bot join @Thealphabotz
from pyrogram import Client, idle
from flask import Flask, jsonify
from database import Database
import config
import asyncio
import os
from pathlib import Path
import threading

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

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
        print("Bot Initialized!")

    async def start(self):
        await super().start()
        me = await self.get_me()
        print(f"Bot Started as {me.first_name}")
        print(f"Username: @{me.username}")
        print("----------------")

    async def stop(self):
        await super().stop()
        print("Bot Stopped. Bye!")

async def main():
    bot = FileShareBot()
    
    try:
        print("Starting Bot...")
        await bot.start()
        print("Bot is Running!")
        await idle()
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        await bot.stop()
        print("Bot Stopped!")

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    try:
        # Set event loop policy for Windows if needed
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        threading.Thread(target=run_flask).start()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot Stopped by User!")
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
