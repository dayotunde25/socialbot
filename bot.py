"""
Main Telegram Bot for AI Social Media Agent
"""
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config
from post_manager import PostManager
from utils import validate_api_keys

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SocialMediaBot:
    def __init__(self):
        self.post_manager = PostManager()
        self.app = None
        
        # Validate API keys on startup
        self.api_validation = validate_api_keys()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **Welcome to AI Social Media Agent!**

I can help you create and post content across multiple social media platforms automatically!

**How it works:**
1. Send me an idea or topic (e.g., "AI in education")
2. I'll generate platform-specific posts using AI
3. I'll automatically post to Twitter, LinkedIn, and Reddit
4. You'll get a summary of all posts with links

**Commands:**
• `/start` - Show this welcome message
• `/status` - Check platform connectivity
• `/help` - Get detailed help
• Just send any message with your idea!

**Example:**
"The future of remote work"
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
🔧 **AI Social Media Agent Help**

**Basic Usage:**
Simply send me any text message with your idea, and I'll:
1. Generate tailored posts for each platform
2. Post them automatically
3. Send you confirmation with links

**Commands:**
• `/start` - Welcome message
• `/status` - Check if all platforms are working
• `/help` - This help message

**Platform-Specific Features:**
• **Twitter**: Concise, engaging posts with hashtags (280 chars)
• **LinkedIn**: Professional, insightful content (3000 chars)
• **Reddit**: Casual, discussion-worthy posts (10000 chars)

**Tips for Better Results:**
• Be specific with your ideas
• Include context or angle you want
• Mention target audience if relevant

**Examples:**
• "Benefits of meditation for productivity"
• "Latest trends in cryptocurrency"
• "How to start a small business in 2024"
• "The impact of AI on creative industries"

**Troubleshooting:**
If posts fail, check `/status` to see platform connectivity.
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        # Test all connections
        connection_results = self.post_manager.test_all_connections()
        platform_status = self.post_manager.get_platform_status()
        
        status_message = "🔍 **Platform Status Check**\n\n"
        
        # LLM Status
        llm_status = "✅" if connection_results.get('llm', False) else "❌"
        status_message += f"{llm_status} **LLM (OpenRouter)**: {'Connected' if connection_results.get('llm', False) else 'Disconnected'}\n\n"
        
        # Platform statuses
        for platform, status in platform_status.items():
            platform_name = platform.title()
            
            if status['enabled'] and status['configured'] and status['available']:
                emoji = "✅"
                status_text = "Ready"
            elif status['enabled'] and status['configured']:
                emoji = "⚠️"
                status_text = "Configured but connection failed"
            elif status['enabled']:
                emoji = "❌"
                status_text = "Not configured"
            else:
                emoji = "⏸️"
                status_text = "Disabled"
            
            status_message += f"{emoji} **{platform_name}**: {status_text}\n"
        
        # Add configuration help if needed
        if not all(connection_results.values()):
            status_message += "\n💡 **Need help?** Check your .env file and API credentials."
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages (ideas for posts)"""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Received idea from user {user_id}: {user_message[:50]}...")
        
        # Send initial processing message
        processing_msg = await update.message.reply_text(
            "🤖 Processing your idea...\n⏳ Generating posts and publishing to social media..."
        )
        
        try:
            # Process the idea
            results = await self.post_manager.process_idea(user_message, str(user_id))
            
            # Format and send response
            response_message = self.post_manager.format_telegram_response(results)
            
            # Add retry option if some posts failed
            keyboard = None
            if results.get("success", False):
                failed_platforms = [
                    platform for platform, result in results.get("results", {}).items()
                    if not result.get("success", False)
                ]
                
                if failed_platforms:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Retry Failed Posts", callback_data=f"retry:{user_message}")]
                    ])
            
            # Edit the processing message with results
            await processing_msg.edit_text(
                response_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        except Exception as e:
            error_message = f"❌ **Error**: {str(e)}\n\nPlease try again or check `/status` for platform issues."
            await processing_msg.edit_text(error_message, parse_mode='Markdown')
            logger.error(f"Error processing message: {str(e)}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries (button presses)"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("retry:"):
            original_idea = query.data[6:]  # Remove "retry:" prefix
            
            await query.edit_message_text(
                "🔄 Retrying failed posts...",
                parse_mode='Markdown'
            )
            
            try:
                # Get original results to identify failed platforms
                # For simplicity, we'll just retry all platforms
                results = await self.post_manager.process_idea(original_idea)
                response_message = self.post_manager.format_telegram_response(results)
                
                await query.edit_message_text(
                    f"🔄 **Retry Results:**\n\n{response_message}",
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                await query.edit_message_text(
                    f"❌ **Retry Failed**: {str(e)}",
                    parse_mode='Markdown'
                )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An unexpected error occurred. Please try again later."
            )
    
    def run(self):
        """Run the bot"""
        if not config.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not found. Please set it in your .env file.")
            return
        
        # Create application
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Add error handler
        self.app.add_error_handler(self.error_handler)
        
        # Start the bot
        logger.info("Starting AI Social Media Bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function"""
    bot = SocialMediaBot()
    bot.run()

if __name__ == "__main__":
    main()
