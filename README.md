<h1 align="center">
  <b>Alpha Share Bot</b>
</h1>

<p align="center">
  <a href="https://github.com/utkarshdubey2008/AlphaShareBot">
    <img src="https://envs.sh/SlS.jpg" alt="Alpha Share Bot" width="500">
  </a>
  <br>
  <b>A Powerful File Sharing Bot for Telegram</b>
</p>

<p align="center">
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.11.6-blue?style=for-the-badge&logo=python" alt="Python Version">
  </a>
  <a href="https://github.com/utkarshdubey2008/AlphaShareBot/stargazers">
    <img src="https://img.shields.io/github/stars/utkarshdubey2008/AlphaShareBot?style=for-the-badge" alt="GitHub Stars">
  </a>
  <a href="https://github.com/utkarshdubey2008/AlphaShareBot/fork">
    <img src="https://img.shields.io/github/forks/utkarshdubey2008/AlphaShareBot?style=for-the-badge" alt="GitHub Forks">
  </a>
  <br>
  <a href="https://github.com/utkarshdubey2008/AlphaShareBot/issues">
    <img src="https://img.shields.io/github/issues/utkarshdubey2008/AlphaShareBot?style=for-the-badge" alt="GitHub Issues">
  </a>
  <a href="https://github.com/utkarshdubey2008/AlphaShareBot/network/members">
    <img src="https://img.shields.io/github/last-commit/utkarshdubey2008/AlphaShareBot?style=for-the-badge" alt="Last Commit">
  </a>
  <a href="https://t.me/Thealphabotz">
    <img src="https://img.shields.io/badge/Updates-Channel-blue?style=for-the-badge&logo=telegram" alt="Updates Channel">
  </a>
</p>

## 🌟 Features

- 🔐 **Admin-Only Uploads**
  - Only authorized admins can upload files
  - Secure file management system
  - Multi-admin support

- 🌐 **Universal File Support**
  - Images, Videos, Documents
  - Audio files & Voice messages
  - All telegram supported files

- 🎯 **Unique File Sharing**
  - UUID-based unique links
  - One-click file access
  - Real-time download tracking

- 📊 **Advanced Statistics**
  - Track total downloads
  - Monitor storage usage
  - User engagement metrics

- 💫 **Professional UI**
  - Clean message formatting
  - Interactive inline buttons
  - Real-time progress bars

- 🔒 **Security Features**
  - Admin verification
  - Download monitoring
  - File access control

## 🛠️ Installation

### Local Deployment

```bash
# Clone the repository
git clone https://github.com/utkarshdubey2008/AlphaShareBot.git

# Navigate to directory
cd AlphaShareBot

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

### 🚀 Heroku Deployment

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/utkarshdubey2008/AlphaShareBot)

### 🔧 Required Variables

```
BOT_TOKEN - Get from @BotFather
API_ID - Get from my.telegram.org
API_HASH - Get from my.telegram.org
MONGO_URI - Your MongoDB connection string
DB_CHANNEL_ID - Channel ID for file storage
ADMIN_IDS - List of admin user IDs
```

## 📚 Commands

### 👤 User Commands
```
/start - Start the bot
/help - Show help message
/about - About the bot
```

### 👑 Admin Commands
```
/upload - Upload files (reply to file)
/stats - Get bot statistics
/broadcast - Send message to all users
/delete - Delete a file
/fileinfo - Get file information
```

## 📦 Tech Stack

- [**Python**](https://www.python.org/) - Programming Language
- [**Pyrogram**](https://docs.pyrogram.org/) - Telegram MTProto API Framework
- [**MongoDB**](https://www.mongodb.com/) - Database
- [**Motor**](https://motor.readthedocs.io/) - Async MongoDB Driver
- [**aiofiles**](https://github.com/Tinche/aiofiles) - Async File Operations

## 📋 Dependencies

- `pyrogram==2.0.106`
- `tgcrypto==1.2.5`
- `motor==3.3.1`
- `dnspython==2.4.2`
- `humanize==4.9.0`
- `python-dotenv==1.0.0`
- `aiofiles==23.2.1`
- `pytz==2023.3`
- `pymongo==4.5.0`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- Channel: [@Thealphabotz](https://t.me/Thealphabotz)
- Developer: [@adarsh2626](https://t.me/adarsh2626)

## 🙏 Credits

- [Pyrogram](https://github.com/pyrogram/pyrogram)
- [Adarsh](https://github.com/adarsh2626)
- [All Contributors](https://github.com/utkarshdubey2008/AlphaShareBot/graphs/contributors)

<p align="center">
  <b>Last Updated: 2025-03-04 05:03:33 UTC</b>
  <br>
  <i>Made with ❤️ by <a href="https://t.me/adarsh2626">Adarsh</a></i>
</p>
