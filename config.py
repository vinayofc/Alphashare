from typing import List, Dict
import os
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN", "2050125681:AAHQx3QVWs1CVlxDOgXjmWlTWaioHW7tWvw")
API_ID = int(os.getenv("API_ID", "7828653"))
API_HASH = os.getenv("API_HASH", "8a81215989c379cff068a88aa7b24f96")


MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://zepixtech:zepix@cluster0rr.ilv5x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0rr")
DATABASE_NAME = os.getenv("DATABASE_NAME", "file_share_bot")

# Channel Configuration
DB_CHANNEL_ID = int(os.getenv("DB_CHANNEL_ID", "-1002439416325")) # this is required for forcesub channel
FORCE_SUB_CHANNEL = int(os.getenv("FORCE_SUB_CHANNEL", "-1001800664082"))

# Bot Information
BOT_USERNAME = os.getenv("BOT_USERNAME", "Musicuploadxdownbot")
BOT_NAME = os.getenv("BOT_NAME", "Alpha File Share Bot")
BOT_VERSION = "1.0.0"

# Links
CHANNEL_LINK = "https://t.me/Thealphabotz" # this is for forcesub channel link
DEVELOPER_LINK = "https://t.me/adarsh2626"
SUPPORT_LINK = "https://t.me/adarsh2626" #put your support chat link here

# Admin Configuration
ADMIN_IDS: List[int] = [
    2009509228,  
]

# File Configuration
MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB in bytes
SUPPORTED_TYPES = [
    "document",
    "video",
    "audio",
    "photo",
    "voice",
    "video_note",
    "animation"
    "mp4",
    "mp3",
    "m4a",
    "apk",
    "zip",
    "txt",
    "py",
    "pdf",
    "text",
    "link",
    "jpg",
    "jpeg",
    "png"
]

# Message Templates
class Messages:
    START_TEXT = """
🎉 **Welcome to {bot_name}!** 🎉

Hello {user_mention}! I'm your secure file sharing assistant.

🔐 **Key Features:**
• Secure File Sharing
• Unique Download Links
• Multiple File Types
• Real-time Tracking
• Force Subscribe

📢 Join @Thealphabotz for updates!
👨‍💻 Contact @adarsh2626 for support

Use /help to see available commands!
"""

    HELP_TEXT = """
📚 **Available Commands** 

👤 **User Commands:**
• /start - Start bot
• /help - Show this help
• /about - About bot

👑 **Admin Commands:**
• /upload - Upload file (reply to file)
• /stats - View statistics
• /broadcast - Send broadcast
• /delete - Delete file
• /fileinfo - File details

📝 **How to use:**
1. Admins can upload by replying /upload
2. Users can download via shared links
3. Must join channel to download
4. Each file has unique link

⚠️ For support: @adarsh2626
"""

    ABOUT_TEXT = """
ℹ️ **About {bot_name}**

**Version:** `{version}`
**Developer:** @adarsh2626
**Language:** Python
**Framework:** Pyrogram

📢 **Updates:** @Thealphabotz
🛠 **Support:** @adarsh2626

**Features:**
• Secure File Sharing
• Force Subscribe
• Admin Controls
• Real-time Stats
• Multiple File Types

Made with ❤️ by @adarsh2626
"""

    FILE_TEXT = """
📁 **File Details**

**Name:** `{file_name}`
**Size:** {file_size}
**Type:** {file_type}
**Downloads:** {downloads}
**Uploaded:** {upload_time}
**By:** {uploader}

🔗 **Share Link:**
`{share_link}`
"""

    FORCE_SUB_TEXT = """
⚠️ **Access Restricted!**

Please join our channel to use this bot:
Bot By @Thealphabotz

Click button below, then try again!
"""

# Button Templates
class Buttons:
    def start_buttons() -> List[List[Dict[str, str]]]:
        return [
            [
                {"text": "Help 📚", "callback_data": "help"},
                {"text": "About ℹ️", "callback_data": "about"}
            ],
            [
                {"text": "Channel 📢", "url": CHANNEL_LINK},
                {"text": "Developer 👨‍💻", "url": DEVELOPER_LINK}
            ]
        ]

    def help_buttons() -> List[List[Dict[str, str]]]:
        return [
            [
                {"text": "Home 🏠", "callback_data": "home"},
                {"text": "About ℹ️", "callback_data": "about"}
            ],
            [
                {"text": "Channel 📢", "url": CHANNEL_LINK}
            ]
        ]

    def about_buttons() -> List[List[Dict[str, str]]]:
        return [
            [
                {"text": "Home 🏠", "callback_data": "home"},
                {"text": "Help 📚", "callback_data": "help"}
            ],
            [
                {"text": "Channel 📢", "url": CHANNEL_LINK}
            ]
        ]

    def file_buttons(file_uuid: str) -> List[List[Dict[str, str]]]:
        return [
            [
                {"text": "Download 📥", "callback_data": f"download_{file_uuid}"},
                {"text": "Share 🔗", "callback_data": f"share_{file_uuid}"}
            ],
            [
                {"text": "Channel 📢", "url": CHANNEL_LINK}
            ]
        ]

# Progress Bar Configuration
class Progress:
    PROGRESS_BAR = "█"
    EMPTY_PROGRESS_BAR = "░"
    PROGRESS_TEXT = """
**{0}** {1}% 

**⚡️ Speed:** {2}/s
**💫 Done:** {3}
**💭 Total:** {4}
**⏰ Time Left:** {5}
"""
    
