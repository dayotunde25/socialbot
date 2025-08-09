"""
Post Management System for coordinating social media posts
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import config
from utils import init_database, format_success_message, format_error_message
from llm_generator import LLMGenerator
from post_to_twitter import TwitterPoster
from post_to_linkedin import LinkedInPoster
from post_to_reddit import RedditPoster

logger = logging.getLogger(__name__)

class PostManager:
    def __init__(self):
        # Initialize database
        init_database()
        
        # Initialize components
        self.llm_generator = LLMGenerator()
        self.twitter_poster = TwitterPoster()
        self.linkedin_poster = LinkedInPoster()
        self.reddit_poster = RedditPoster()
        
        # Track which platforms are available
        self.available_platforms = self._check_platform_availability()
        
        logger.info(f"PostManager initialized. Available platforms: {list(self.available_platforms.keys())}")
    
    def _check_platform_availability(self) -> Dict[str, bool]:
        """Check which platforms are properly configured and available"""
        availability = {}
        
        # Check Twitter
        availability['twitter'] = (
            config.PLATFORMS['twitter']['enabled'] and 
            self.twitter_poster.client is not None
        )
        
        # Check LinkedIn
        availability['linkedin'] = (
            config.PLATFORMS['linkedin']['enabled'] and 
            self.linkedin_poster.access_token is not None and
            self.linkedin_poster.user_id is not None
        )
        
        # Check Reddit
        availability['reddit'] = (
            config.PLATFORMS['reddit']['enabled'] and 
            self.reddit_poster.reddit is not None
        )
        
        return availability
    
    async def process_idea(self, idea: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process an idea and post to all available platforms"""
        logger.info(f"Processing idea: {idea[:50]}...")
        
        try:
            # Step 1: Generate posts for all platforms
            logger.info("Generating posts using LLM...")
            posts = self.llm_generator.generate_posts(idea)
            
            if not any(posts.values()):
                error_msg = "Failed to generate any posts"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Step 2: Post to all available platforms concurrently
            logger.info("Posting to social media platforms...")
            results = await self._post_to_platforms(posts, idea)
            
            # Step 3: Compile results
            success_count = sum(1 for result in results.values() if result.get('success', False))
            total_platforms = len([p for p, available in self.available_platforms.items() if available])
            
            return {
                "success": success_count > 0,
                "results": results,
                "summary": {
                    "successful_posts": success_count,
                    "total_platforms": total_platforms,
                    "idea": idea
                }
            }
            
        except Exception as e:
            error_msg = f"Error processing idea: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def _post_to_platforms(self, posts: Dict[str, str], original_idea: str) -> Dict[str, Any]:
        """Post to all platforms concurrently"""
        results = {}
        
        # Use ThreadPoolExecutor for concurrent posting
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_platform = {}
            
            for platform, content in posts.items():
                if content and self.available_platforms.get(platform, False):
                    future = executor.submit(self._post_to_single_platform, platform, content, original_idea)
                    future_to_platform[future] = platform
                elif not content:
                    results[platform] = {"success": False, "error": "No content generated"}
                else:
                    results[platform] = {"success": False, "error": "Platform not available"}
            
            # Collect results as they complete
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    result = future.result(timeout=60)  # 60 second timeout per platform
                    results[platform] = result
                except Exception as e:
                    error_msg = f"Exception posting to {platform}: {str(e)}"
                    logger.error(error_msg)
                    results[platform] = {"success": False, "error": error_msg}
        
        return results
    
    def _post_to_single_platform(self, platform: str, content: str, original_idea: str) -> Dict[str, Any]:
        """Post to a single platform"""
        try:
            if platform == "twitter":
                return self.twitter_poster.post_tweet(content, original_idea)
            elif platform == "linkedin":
                return self.linkedin_poster.post_to_linkedin(content, original_idea)
            elif platform == "reddit":
                # For Reddit, we might want to suggest subreddits or use a default
                subreddits = self.reddit_poster.get_suitable_subreddits(original_idea)
                subreddit = subreddits[0] if subreddits else "test"
                return self.reddit_poster.post_to_reddit(content, original_idea, subreddit)
            else:
                return {"success": False, "error": f"Unknown platform: {platform}"}
                
        except Exception as e:
            error_msg = f"Error posting to {platform}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test connections to all platforms"""
        results = {}
        
        # Test LLM
        results['llm'] = self.llm_generator.test_connection()
        
        # Test social platforms
        results['twitter'] = self.twitter_poster.test_connection() if self.twitter_poster.client else False
        results['linkedin'] = self.linkedin_poster.test_connection() if self.linkedin_poster.access_token else False
        results['reddit'] = self.reddit_poster.test_connection() if self.reddit_poster.reddit else False
        
        return results
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get detailed status of all platforms"""
        status = {}
        
        for platform in ['twitter', 'linkedin', 'reddit']:
            status[platform] = {
                "enabled": config.PLATFORMS[platform]['enabled'],
                "available": self.available_platforms.get(platform, False),
                "configured": False
            }
            
            # Check if properly configured
            if platform == "twitter":
                status[platform]["configured"] = all([
                    config.TWITTER_API_KEY,
                    config.TWITTER_API_SECRET,
                    config.TWITTER_ACCESS_TOKEN,
                    config.TWITTER_ACCESS_SECRET
                ])
            elif platform == "linkedin":
                status[platform]["configured"] = bool(config.LINKEDIN_ACCESS_TOKEN)
            elif platform == "reddit":
                status[platform]["configured"] = all([
                    config.REDDIT_CLIENT_ID,
                    config.REDDIT_SECRET,
                    config.REDDIT_USERNAME,
                    config.REDDIT_PASSWORD
                ])
        
        return status
    
    def format_telegram_response(self, results: Dict[str, Any]) -> str:
        """Format results for Telegram response"""
        if not results.get("success", False):
            return format_error_message(results.get("error", "Unknown error"))
        
        return format_success_message(results.get("results", {}))
    
    async def retry_failed_posts(self, original_results: Dict[str, Any], idea: str) -> Dict[str, Any]:
        """Retry posts that failed in the original attempt"""
        failed_platforms = []
        
        for platform, result in original_results.get("results", {}).items():
            if not result.get("success", False):
                failed_platforms.append(platform)
        
        if not failed_platforms:
            return {"success": True, "message": "No failed posts to retry"}
        
        logger.info(f"Retrying failed posts for platforms: {failed_platforms}")
        
        # Generate new posts for failed platforms only
        posts = {}
        for platform in failed_platforms:
            if self.available_platforms.get(platform, False):
                try:
                    platform_posts = self.llm_generator.generate_posts(idea)
                    posts[platform] = platform_posts.get(platform)
                except Exception as e:
                    logger.error(f"Failed to regenerate post for {platform}: {str(e)}")
        
        # Retry posting
        retry_results = await self._post_to_platforms(posts, idea)
        
        return {
            "success": any(result.get("success", False) for result in retry_results.values()),
            "results": retry_results,
            "retried_platforms": failed_platforms
        }
