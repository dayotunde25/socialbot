"""
Configuration settings for the AI Social Media Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Tokens
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Twitter API credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# LinkedIn API credentials
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = "ai-social-agent/1.0"

# OpenRouter settings
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "mistralai/mixtral-8x7b-instruct"

# Platform settings
PLATFORMS = {
    "twitter": {
        "enabled": True,
        "max_length": 280,
        "tone": "concise and engaging"
    },
    "linkedin": {
        "enabled": True,
        "max_length": 3000,
        "tone": "professional and insightful"
    },
    "reddit": {
        "enabled": True,
        "max_length": 10000,
        "tone": "casual and informative"
    }
}

# Database settings
DATABASE_PATH = "posts.db"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"
