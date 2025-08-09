"""
Utility functions for the AI Social Media Bot
"""
import logging
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def init_database():
    """Initialize the SQLite database for storing posts"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            original_idea TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            response_data TEXT,
            error_message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def log_post(platform: str, content: str, original_idea: str, 
             status: str, response_data: Optional[Dict] = None, 
             error_message: Optional[str] = None):
    """Log a post attempt to the database"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO posts (platform, content, original_idea, status, response_data, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        platform, 
        content, 
        original_idea, 
        status, 
        json.dumps(response_data) if response_data else None,
        error_message
    ))
    
    conn.commit()
    conn.close()
    logger.info(f"Logged {status} post for {platform}")

def format_success_message(results: Dict[str, Any]) -> str:
    """Format a success message for Telegram"""
    message = "🚀 **Posts Generated and Published!**\n\n"
    
    for platform, result in results.items():
        if result['success']:
            message += f"✅ **{platform.title()}**: Posted successfully\n"
            if 'url' in result:
                message += f"   🔗 {result['url']}\n"
        else:
            message += f"❌ **{platform.title()}**: Failed\n"
            message += f"   Error: {result.get('error', 'Unknown error')}\n"
        message += "\n"
    
    return message

def format_error_message(error: str) -> str:
    """Format an error message for Telegram"""
    return f"❌ **Error**: {error}\n\nPlease try again or contact support."

def truncate_content(content: str, max_length: int, platform: str) -> str:
    """Truncate content to fit platform limits"""
    if len(content) <= max_length:
        return content
    
    # For Twitter, we need to be more careful with truncation
    if platform == "twitter":
        # Leave space for "..." and potential hashtags
        truncated = content[:max_length - 10] + "..."
        return truncated
    
    # For other platforms, simple truncation
    return content[:max_length - 3] + "..."

def validate_api_keys() -> Dict[str, bool]:
    """Validate that required API keys are present"""
    validation = {}
    
    # Check OpenRouter
    validation['openrouter'] = bool(config.OPENROUTER_API_KEY)
    
    # Check Telegram
    validation['telegram'] = bool(config.TELEGRAM_BOT_TOKEN)
    
    # Check Twitter
    validation['twitter'] = all([
        config.TWITTER_API_KEY,
        config.TWITTER_API_SECRET,
        config.TWITTER_ACCESS_TOKEN,
        config.TWITTER_ACCESS_SECRET
    ])
    
    # Check LinkedIn
    validation['linkedin'] = bool(config.LINKEDIN_ACCESS_TOKEN)
    
    # Check Reddit
    validation['reddit'] = all([
        config.REDDIT_CLIENT_ID,
        config.REDDIT_SECRET,
        config.REDDIT_USERNAME,
        config.REDDIT_PASSWORD
    ])
    
    return validation
