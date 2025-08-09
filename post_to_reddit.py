"""
Reddit posting functionality using PRAW
"""
import praw
import logging
from typing import Dict, Any, Optional, List
import config
from utils import log_post, truncate_content

logger = logging.getLogger(__name__)

class RedditPoster:
    def __init__(self):
        self.client_id = config.REDDIT_CLIENT_ID
        self.client_secret = config.REDDIT_SECRET
        self.username = config.REDDIT_USERNAME
        self.password = config.REDDIT_PASSWORD
        self.user_agent = config.REDDIT_USER_AGENT
        
        self.reddit = None
        
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            logger.warning("Reddit API credentials not complete. Reddit posting will be disabled.")
            return
        
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                password=self.password,
                user_agent=self.user_agent
            )
            
            # Test authentication
            if self.reddit.user.me():
                logger.info("Reddit API initialized successfully")
            else:
                logger.error("Reddit authentication failed")
                self.reddit = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API: {str(e)}")
            self.reddit = None
    
    def post_to_reddit(self, content: str, original_idea: str, 
                      subreddit_name: str = "test", 
                      title: Optional[str] = None) -> Dict[str, Any]:
        """Post content to Reddit"""
        if not self.reddit:
            error_msg = "Reddit API not initialized"
            log_post("reddit", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Ensure content fits Reddit's limits
            content = truncate_content(content, 10000, "reddit")
            
            # Generate title if not provided
            if not title:
                title = self._generate_title(original_idea)
            
            # Get the subreddit
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Submit the post
            submission = subreddit.submit(
                title=title,
                selftext=content,
                send_replies=True
            )
            
            if submission:
                post_url = f"https://reddit.com{submission.permalink}"
                
                log_post("reddit", content, original_idea, "success",
                        response_data={
                            "submission_id": submission.id,
                            "url": post_url,
                            "subreddit": subreddit_name,
                            "title": title
                        })
                
                logger.info(f"Reddit post created successfully: {submission.id}")
                return {
                    "success": True,
                    "submission_id": submission.id,
                    "url": post_url,
                    "subreddit": subreddit_name,
                    "title": title,
                    "content": content
                }
            else:
                error_msg = "No submission returned from Reddit API"
                log_post("reddit", content, original_idea, "failed", error_message=error_msg)
                return {"success": False, "error": error_msg}
                
        except praw.exceptions.RedditAPIException as e:
            error_msg = f"Reddit API error: {str(e)}"
            logger.error(error_msg)
            log_post("reddit", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
            
        except praw.exceptions.InvalidSubreddit:
            error_msg = f"Invalid subreddit: {subreddit_name}"
            logger.error(error_msg)
            log_post("reddit", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error posting to Reddit: {str(e)}"
            logger.error(error_msg)
            log_post("reddit", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
    
    def _generate_title(self, idea: str) -> str:
        """Generate a title for the Reddit post based on the idea"""
        # Simple title generation - could be enhanced with LLM
        if len(idea) <= 100:
            return f"Discussion: {idea}"
        else:
            return f"Discussion: {idea[:97]}..."
    
    def test_connection(self) -> bool:
        """Test the connection to Reddit API"""
        if not self.reddit:
            return False
        
        try:
            user = self.reddit.user.me()
            if user:
                logger.info(f"Reddit API connection successful. User: u/{user.name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Reddit API connection test failed: {str(e)}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get authenticated user information"""
        if not self.reddit:
            return None
        
        try:
            user = self.reddit.user.me()
            if user:
                return {
                    "name": user.name,
                    "id": user.id,
                    "comment_karma": user.comment_karma,
                    "link_karma": user.link_karma,
                    "created_utc": user.created_utc
                }
        except Exception as e:
            logger.error(f"Failed to get Reddit user info: {str(e)}")
        
        return None
    
    def get_suitable_subreddits(self, topic: str) -> List[str]:
        """Get a list of suitable subreddits for a given topic"""
        # This is a basic implementation - could be enhanced with search
        topic_lower = topic.lower()
        
        # Common subreddits for different topics
        subreddit_mapping = {
            "ai": ["artificial", "MachineLearning", "singularity", "technology"],
            "technology": ["technology", "programming", "coding", "tech"],
            "business": ["business", "entrepreneur", "startups", "investing"],
            "education": ["education", "teaching", "learning", "studytips"],
            "science": ["science", "askscience", "EverythingScience"],
            "programming": ["programming", "coding", "learnprogramming", "webdev"],
            "finance": ["personalfinance", "investing", "financialindependence"],
            "health": ["health", "fitness", "nutrition", "wellness"],
            "gaming": ["gaming", "games", "pcgaming", "nintendo"],
            "music": ["music", "WeAreTheMusicMakers", "edmproduction"],
            "art": ["art", "drawing", "painting", "design"],
            "photography": ["photography", "photocritique", "itookapicture"]
        }
        
        # Find matching subreddits
        suitable_subreddits = []
        for key, subreddits in subreddit_mapping.items():
            if key in topic_lower:
                suitable_subreddits.extend(subreddits)
        
        # Default subreddits if no specific match
        if not suitable_subreddits:
            suitable_subreddits = ["test", "CasualConversation", "discussion"]
        
        return suitable_subreddits[:3]  # Return top 3 suggestions
