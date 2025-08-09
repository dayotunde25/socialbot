"""
Simple launcher script for the AI Social Media Agent
"""
import sys
import os
import asyncio
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import telegram
        import requests
        import tweepy
        import praw
        import dotenv
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your API keys:")
        print("  cp .env.example .env")
        return False
    return True

def main():
    """Main launcher function"""
    print("🤖 AI Social Media Agent Launcher")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check .env file
    if not check_env_file():
        sys.exit(1)
    
    # Import and run the bot
    try:
        from bot import main as run_bot
        print("✅ Starting AI Social Media Agent...")
        print("Press Ctrl+C to stop the bot")
        print("-" * 40)
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Run: python test_setup.py")
        print("3. Verify your API keys are correct")

if __name__ == "__main__":
    main()
