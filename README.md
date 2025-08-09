# 🤖 AI Social Media Agent

An autonomous Telegram bot that generates and posts AI-powered content across multiple social media platforms.

## ✨ Features

- **🧠 AI-Powered Content Generation**: Uses OpenRouter API with free LLM models
- **📱 Multi-Platform Posting**: Automatically posts to Twitter, LinkedIn, and Reddit
- **🎯 Platform-Specific Optimization**: Tailored content for each platform's audience
- **📊 Post Tracking**: SQLite database logging with success/failure tracking
- **🔄 Retry Mechanism**: Automatic retry for failed posts
- **⚡ Concurrent Processing**: Fast, parallel posting to all platforms
- **🛡️ Error Handling**: Comprehensive error handling and user feedback

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd ai-social-agent
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials (see [API Setup Guide](#-api-setup-guide) below).

### 3. Run the Bot

```bash
python bot.py
```

### 4. Start Using

1. Open Telegram and find your bot
2. Send `/start` to begin
3. Send any message with your idea (e.g., "AI in education")
4. Watch as your content gets posted across platforms!

## 🔧 API Setup Guide

### OpenRouter (Required)
1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add to `.env`: `OPENROUTER_API_KEY=your_key_here`

### Telegram Bot (Required)
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Add to `.env`: `TELEGRAM_BOT_TOKEN=your_token_here`

### Twitter API (Optional)
1. Apply for [Twitter Developer Account](https://developer.twitter.com/)
2. Create a new app and get:
   - API Key & Secret
   - Access Token & Secret
   - Bearer Token
3. Add all to `.env`

### LinkedIn API (Optional)
1. Create app at [LinkedIn Developers](https://developer.linkedin.com/)
2. Get authorization and access token
3. Add to `.env`: `LINKEDIN_ACCESS_TOKEN=your_token_here`

### Reddit API (Optional)
1. Create app at [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Choose "script" type
3. Get client ID and secret
4. Add credentials to `.env`

## 📁 Project Structure

```
ai-social-agent/
├── bot.py                 # Main Telegram bot
├── config.py              # Configuration management
├── llm_generator.py       # OpenRouter LLM integration
├── post_manager.py        # Orchestrates posting workflow
├── post_to_twitter.py     # Twitter API integration
├── post_to_linkedin.py    # LinkedIn API integration
├── post_to_reddit.py      # Reddit API integration
├── utils.py               # Utilities and database functions
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🎯 Platform-Specific Features

### Twitter
- **Character Limit**: 280 characters
- **Tone**: Concise and engaging
- **Features**: Hashtags, emojis, shareability focus

### LinkedIn
- **Character Limit**: 3,000 characters
- **Tone**: Professional and insightful
- **Features**: Industry hashtags, business value, discussion starters

### Reddit
- **Character Limit**: 10,000 characters
- **Tone**: Casual and informative
- **Features**: Markdown formatting, community engagement, subreddit suggestions

## 🤖 Bot Commands

- `/start` - Welcome message and instructions
- `/help` - Detailed help and usage examples
- `/status` - Check platform connectivity and configuration
- Send any text - Generate and post content about that topic

## 📊 Database Schema

Posts are logged in SQLite with the following fields:
- `id` - Auto-incrementing primary key
- `platform` - Social media platform
- `content` - Generated post content
- `original_idea` - User's original input
- `timestamp` - When the post was created
- `status` - success/failed
- `response_data` - Platform response (JSON)
- `error_message` - Error details if failed

## 🔍 Monitoring and Logs

- **Console Logs**: Real-time status and error information
- **File Logs**: Persistent logging to `bot.log`
- **Database Logs**: All post attempts stored in `posts.db`
- **Telegram Feedback**: Success/failure messages with links

## 🛠️ Customization

### Adding New Platforms
1. Create new file: `post_to_newplatform.py`
2. Implement posting class with `post_to_platform()` method
3. Add to `post_manager.py` and `config.py`

### Changing LLM Models
Edit `config.py`:
```python
DEFAULT_MODEL = "mistralai/mixtral-8x7b-instruct"  # or any OpenRouter model
```

### Platform Settings
Modify `config.py` PLATFORMS dict:
```python
PLATFORMS = {
    "twitter": {
        "enabled": True,
        "max_length": 280,
        "tone": "your custom tone"
    }
}
```

## 🚨 Troubleshooting

### Common Issues

**Bot not responding**
- Check `TELEGRAM_BOT_TOKEN` in `.env`
- Verify bot is started with `/start`

**Posts not generating**
- Verify `OPENROUTER_API_KEY` in `.env`
- Check OpenRouter account credits
- Use `/status` command to test connection

**Platform posting fails**
- Check API credentials for specific platform
- Verify account permissions and rate limits
- Check logs for detailed error messages

**Database errors**
- Ensure write permissions in project directory
- Delete `posts.db` to reset database

### Getting Help

1. Use `/status` command to check connectivity
2. Check console logs for detailed errors
3. Verify all API keys are correctly set
4. Test with simple ideas first

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Happy posting! 🚀**
