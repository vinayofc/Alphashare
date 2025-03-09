from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "2050125681:AAHQx3QVWs1CVlxDOgXjmWlTWaioHW7tWvw")
API_ID = int(os.getenv("API_ID", "7828653"))
API_HASH = os.getenv("API_HASH", "8a81215989c379cff068a88aa7b24f96")

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://zepixtech:zepix@cluster0rr.ilv5x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0rr")
DATABASE_NAME = os.getenv("DATABASE_NAME", "file_share_bot")

# Channel Configuration
DB_CHANNEL_ID = int(os.getenv("DB_CHANNEL_ID", "-1002439416325"))
FORCE_SUB_CHANNEL = int(os.getenv("FORCE_SUB_CHANNEL", "-1002300128227"))

# Bot Information
BOT_USERNAME = os.getenv("BOT_USERNAME", "Musicuploadxdownbot")
BOT_NAME = os.getenv("BOT_NAME", "Alpha File Share Bot")
BOT_VERSION = "1.1.1"  # Updated version number

# Links
CHANNEL_LINK = "https://t.me/+r2SFilDJgEsxNjY1"
DEVELOPER_LINK = "https://t.me/adarsh2626"
SUPPORT_LINK = "https://t.me/adarsh2626"

# Admin Configuration
ADMIN_IDS: List[int] = [
    2009509228,  # Main admin
]

# File Configuration
MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB in bytes

# Media Types Configuration
SUPPORTED_TYPES = [
    "document",
    "video",
    "audio",
    "photo",
    "voice",
    "video_note",
    "animation"
]

# Supported File Extensions
SUPPORTED_EXTENSIONS = [
    # Documents
    "pdf", "txt", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    # Programming Files
    "py", "js", "html", "css", "json", "xml", "yaml", "yml",
    # Archives
    "zip", "rar", "7z", "tar", "gz", "bz2",
    # Media Files
    "mp4", "mp3", "m4a", "wav", "avi", "mkv", "flv", "mov",
    "webm", "3gp", "m4v", "ogg", "opus",
    # Images
    "jpg", "jpeg", "png", "gif", "webp", "bmp", "ico",
    # Applications
    "apk", "exe", "msi", "deb", "rpm",
    # Other
    "txt", "text", "log", "csv", "md", "srt", "sub"
]

# MIME Types for Additional Validation
SUPPORTED_MIME_TYPES = [
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # Archives
    "application/zip",
    "application/x-rar-compressed",
    "application/x-7z-compressed",
    # Media
    "video/mp4",
    "audio/mpeg",
    "audio/mp4",
    "image/jpeg",
    "image/png",
    "image/gif",
    # Applications
    "application/vnd.android.package-archive",
    "application/x-executable",
]

# Message Templates
class Messages:
    START_TEXT = """
🎉 **Welcome to {bot_name}!** 🎉

Hello {user_mention}! I'm your secure file sharing assistant.

🔐 **Key Features:**
• Secure File Sharing
• Unique Download Links
• Multiple File Types Support
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

📝 **Supported File Types:**
• Documents (PDF, DOC, XLS, etc.)
• Videos (MP4, MKV, AVI, etc.)
• Audio (MP3, M4A, WAV, etc.)
• Images (JPG, PNG, GIF, etc.)
• Archives (ZIP, RAR, 7Z, etc.)
• Applications (APK, EXE, etc.)
• Other Formats

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
• Enhanced Security
• Automatic File Type Detection

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
