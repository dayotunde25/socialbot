"""
LLM Integration for generating platform-specific social media content
"""
import requests
import json
import logging
from typing import Dict, List, Optional
import config

logger = logging.getLogger(__name__)

class LLMGenerator:
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = config.DEFAULT_MODEL
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file")
    
    def generate_posts(self, idea: str) -> Dict[str, str]:
        """Generate posts for all enabled platforms"""
        posts = {}
        
        for platform, settings in config.PLATFORMS.items():
            if settings['enabled']:
                try:
                    post_content = self._generate_single_post(idea, platform, settings)
                    posts[platform] = post_content
                    logger.info(f"Generated {platform} post successfully")
                except Exception as e:
                    logger.error(f"Failed to generate {platform} post: {str(e)}")
                    posts[platform] = None
        
        return posts
    
    def _generate_single_post(self, idea: str, platform: str, settings: Dict) -> str:
        """Generate a single post for a specific platform"""
        prompt = self._create_prompt(idea, platform, settings)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert social media content creator. Create engaging, authentic posts that resonate with each platform's audience."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # Ensure content fits platform limits
            max_length = settings['max_length']
            if len(content) > max_length:
                content = content[:max_length - 3] + "..."
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")
        except KeyError as e:
            logger.error(f"Unexpected API response format: {str(e)}")
            raise Exception("Invalid response from LLM API")
    
    def _create_prompt(self, idea: str, platform: str, settings: Dict) -> str:
        """Create a platform-specific prompt"""
        base_prompt = f"Create a {settings['tone']} social media post about: {idea}"
        
        platform_specific = {
            "twitter": f"""
{base_prompt}

Requirements for Twitter:
- Maximum {settings['max_length']} characters
- Use relevant hashtags (2-3 max)
- Make it engaging and shareable
- Include emojis where appropriate
- Be concise but impactful
""",
            "linkedin": f"""
{base_prompt}

Requirements for LinkedIn:
- Professional tone suitable for business audience
- Maximum {settings['max_length']} characters
- Include relevant industry hashtags
- Add value or insights
- Encourage professional discussion
- Use line breaks for readability
""",
            "reddit": f"""
{base_prompt}

Requirements for Reddit:
- Casual, conversational tone
- Maximum {settings['max_length']} characters
- Be informative and discussion-worthy
- Use markdown formatting where helpful
- Avoid overly promotional language
- Encourage community engagement
"""
        }
        
        return platform_specific.get(platform, base_prompt)
    
    def test_connection(self) -> bool:
        """Test the connection to OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, this is a test message."
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
