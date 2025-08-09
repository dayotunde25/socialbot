"""
Twitter posting functionality using Tweepy
"""
import tweepy
import logging
from typing import Dict, Any, Optional
import config
from utils import log_post, truncate_content

logger = logging.getLogger(__name__)

class TwitterPoster:
    def __init__(self):
        self.api_key = config.TWITTER_API_KEY
        self.api_secret = config.TWITTER_API_SECRET
        self.access_token = config.TWITTER_ACCESS_TOKEN
        self.access_secret = config.TWITTER_ACCESS_SECRET
        self.bearer_token = config.TWITTER_BEARER_TOKEN
        
        self.client = None
        self.api = None
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            logger.warning("Twitter API credentials not complete. Twitter posting will be disabled.")
            return
        
        try:
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret,
                wait_on_rate_limit=True
            )
            
            # Initialize Twitter API v1.1 for additional features if needed
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_secret)
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            logger.info("Twitter API initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {str(e)}")
            self.client = None
            self.api = None
    
    def post_tweet(self, content: str, original_idea: str) -> Dict[str, Any]:
        """Post a tweet to Twitter"""
        if not self.client:
            error_msg = "Twitter API not initialized"
            log_post("twitter", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Ensure content fits Twitter's character limit
            content = truncate_content(content, 280, "twitter")
            
            # Post the tweet
            response = self.client.create_tweet(text=content)
            
            if response.data:
                tweet_id = response.data['id']
                tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                
                log_post("twitter", content, original_idea, "success", 
                        response_data={"tweet_id": tweet_id, "url": tweet_url})
                
                logger.info(f"Tweet posted successfully: {tweet_id}")
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "url": tweet_url,
                    "content": content
                }
            else:
                error_msg = "No data returned from Twitter API"
                log_post("twitter", content, original_idea, "failed", error_message=error_msg)
                return {"success": False, "error": error_msg}
                
        except tweepy.TooManyRequests:
            error_msg = "Twitter API rate limit exceeded"
            logger.error(error_msg)
            log_post("twitter", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
            
        except tweepy.Forbidden as e:
            error_msg = f"Twitter API access forbidden: {str(e)}"
            logger.error(error_msg)
            log_post("twitter", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
            
        except tweepy.BadRequest as e:
            error_msg = f"Twitter API bad request: {str(e)}"
            logger.error(error_msg)
            log_post("twitter", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error posting to Twitter: {str(e)}"
            logger.error(error_msg)
            log_post("twitter", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
    
    def test_connection(self) -> bool:
        """Test the connection to Twitter API"""
        if not self.client:
            return False
        
        try:
            # Try to get the authenticated user's information
            user = self.client.get_me()
            if user.data:
                logger.info(f"Twitter API connection successful. User: @{user.data.username}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Twitter API connection test failed: {str(e)}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get authenticated user information"""
        if not self.client:
            return None
        
        try:
            user = self.client.get_me()
            if user.data:
                return {
                    "id": user.data.id,
                    "username": user.data.username,
                    "name": user.data.name,
                    "followers_count": getattr(user.data, 'public_metrics', {}).get('followers_count', 0)
                }
        except Exception as e:
            logger.error(f"Failed to get Twitter user info: {str(e)}")
        
        return None
