"""
LinkedIn posting functionality using REST API
"""
import requests
import json
import logging
from typing import Dict, Any, Optional
import config
from utils import log_post, truncate_content

logger = logging.getLogger(__name__)

class LinkedInPoster:
    def __init__(self):
        self.access_token = config.LINKEDIN_ACCESS_TOKEN
        self.base_url = "https://api.linkedin.com/v2"
        
        if not self.access_token:
            logger.warning("LinkedIn access token not found. LinkedIn posting will be disabled.")
            return
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Get user profile information
        self.user_id = self._get_user_id()
        if self.user_id:
            logger.info("LinkedIn API initialized successfully")
        else:
            logger.error("Failed to get LinkedIn user ID")
    
    def _get_user_id(self) -> Optional[str]:
        """Get the authenticated user's LinkedIn ID"""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            user_data = response.json()
            return user_data.get('id')
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn user ID: {str(e)}")
            return None
    
    def post_to_linkedin(self, content: str, original_idea: str) -> Dict[str, Any]:
        """Post content to LinkedIn"""
        if not self.access_token or not self.user_id:
            error_msg = "LinkedIn API not properly initialized"
            log_post("linkedin", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Ensure content fits LinkedIn's limits
            content = truncate_content(content, 3000, "linkedin")
            
            # Prepare the post data
            post_data = {
                "author": f"urn:li:person:{self.user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Post to LinkedIn
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                headers=self.headers,
                json=post_data,
                timeout=30
            )
            response.raise_for_status()
            
            response_data = response.json()
            post_id = response_data.get('id')
            
            if post_id:
                # LinkedIn doesn't provide direct URLs in the response
                # The URL format is typically: https://www.linkedin.com/feed/update/{post_id}
                post_url = f"https://www.linkedin.com/feed/update/{post_id}"
                
                log_post("linkedin", content, original_idea, "success",
                        response_data={"post_id": post_id, "url": post_url})
                
                logger.info(f"LinkedIn post created successfully: {post_id}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "url": post_url,
                    "content": content
                }
            else:
                error_msg = "No post ID returned from LinkedIn API"
                log_post("linkedin", content, original_idea, "failed", error_message=error_msg)
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                error_msg = "LinkedIn API authentication failed. Please check your access token."
            elif e.response.status_code == 403:
                error_msg = "LinkedIn API access forbidden. Check your permissions."
            elif e.response.status_code == 429:
                error_msg = "LinkedIn API rate limit exceeded."
            else:
                error_msg = f"LinkedIn API HTTP error: {e.response.status_code}"
            
            logger.error(f"{error_msg}: {str(e)}")
            log_post("linkedin", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"LinkedIn API request failed: {str(e)}"
            logger.error(error_msg)
            log_post("linkedin", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error posting to LinkedIn: {str(e)}"
            logger.error(error_msg)
            log_post("linkedin", content, original_idea, "failed", error_message=error_msg)
            return {"success": False, "error": error_msg}
    
    def test_connection(self) -> bool:
        """Test the connection to LinkedIn API"""
        if not self.access_token:
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"LinkedIn API connection successful. User: {user_data.get('localizedFirstName', 'Unknown')}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"LinkedIn API connection test failed: {str(e)}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get authenticated user information"""
        if not self.access_token:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            user_data = response.json()
            return {
                "id": user_data.get('id'),
                "first_name": user_data.get('localizedFirstName'),
                "last_name": user_data.get('localizedLastName'),
                "headline": user_data.get('localizedHeadline')
            }
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn user info: {str(e)}")
        
        return None
