from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "2050125681:AAHQx3QVWs1CVlxDOgXjmWlTWaioHW7tWvw")
API_ID = int(os.getenv("API_ID", "7828653"))
API_HASH = os.getenv("API_HASH", "8a81215989c379cff068a88aa7b24f96")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://zepixtech:zepix@cluster0rr.ilv5x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0rr")
DATABASE_NAME = os.getenv("DATABASE_NAME", "file_share_bot")

# Auto Delete Configuration
AUTO_DELETE_ENABLED = True
AUTO_DELETE_TIMER = int(os.getenv("AUTO_DELETE_TIMER", "5"))  # Default 5 minutes

# Channel Configuration
DB_CHANNEL_ID = int(os.getenv("DB_CHANNEL_ID", "-1002439416325"))
FORCE_SUB_CHANNEL = int(os.getenv("FORCE_SUB_CHANNEL", "-1001800664082"))

# New Force Subscribe Configuration
FORCE_SUB_WITH_JOIN_REQUEST = int(os.getenv("FORCE_SUB_WITH_JOIN_REQUEST", "0"))  # Default 0 (disabled)
PRIVATE_FORCE_SUB_CHANNEL = int(os.getenv("PRIVATE_FORCE_SUB_CHANNEL", "0"))  # Default 0 (disabled)

# Bot Information
BOT_USERNAME = os.getenv("BOT_USERNAME", "Musicuploadxdownbot")
BOT_NAME = os.getenv("BOT_NAME", "Alpha File Share Bot")
BOT_VERSION = "1.0.0"

# Links
CHANNEL_LINK = "https://t.me/Thealphabotz"
DEVELOPER_LINK = "https://t.me/adarsh2626"
SUPPORT_LINK = "https://t.me/adarsh2626"

# Admin Configuration
ADMIN_IDS: List[int] = [
    2009509228,  # Main Admin
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
• Auto-Delete Timer

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
• /setautodelete - Set auto-delete timer

📝 **How to use:**
1. Admins can upload by replying /upload
2. Users can download via shared links
3. Must join required channels
4. Each file has unique link
5. Copyright files auto-delete after timer

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
• Auto-Delete Timer

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

⏳ **Auto-Delete Timer:** {auto_delete_time} minutes

🔗 **Share Link:**
`{share_link}`

⚠️ This file will be automatically deleted after {auto_delete_time} minutes!
"""

    FORCE_SUB_TEXT = """
⚠️ **Access Restricted!**

Please join our required channels to use the bot:

1️⃣ Main Channel: @Thealphabotz
{private_channel}

Click the buttons below to join, then try again!
"""

    PRIVATE_FORCE_SUB_TEXT = """
2️⃣ Special Channel: Join request required
• Click "Join Private Channel"
• Send join request
• Wait for approval
• Click "Check Access"
"""

    WAIT_FOR_APPROVAL = """
⏳ **Waiting for Approval**

Your join request is pending.
Please wait for admin approval.

Click "Check Access" once approved!
"""

    JOIN_REQUEST_APPROVED = """
✅ **Access Granted!**

Your join request was approved.
You can now use the bot!

Thank you for joining!
"""

    AUTO_DELETE_WARNING = """
⚠️ **Copyright Notice**
This file will be automatically deleted in {minutes} minutes due to copyright issues.
Please save it before it expires!

⏳ **Time Remaining:** {minutes} minutes
"""

    AUTO_DELETE_EXPIRED = """
🚨 **File Deleted**
Your file has been automatically deleted due to copyright issues.
You can request it again using the same link.
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

    def force_sub_buttons(main_invite: str = None, private_invite: str = None) -> List[List[Dict[str, str]]]:
        buttons = []
        
        if main_invite:
            buttons.append([
                {"text": "Join Main Channel 📢", "url": main_invite}
            ])
            
        if private_invite:
            buttons.append([
                {"text": "Join Private Channel 🔒", "url": private_invite}
            ])
            
        buttons.append([
            {"text": "Check Access 🔄", "callback_data": "checksub"}
        ])
        
        return buttons

    def file_buttons(file_uuid: str) -> List[List[Dict[str, str]]]:
        return [
            [
                {"text": "Download 📥", "callback_data": f"download_{file_uuid}"},
                {"text": "Share 🔗", "callback_data": f"share_{file_uuid}"}
            ],
            [
                {"text": "Check Timer ⏳", "callback_data": f"check_time_{file_uuid}"}
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
