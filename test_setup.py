"""
Test script to verify the AI Social Media Agent setup
"""
import asyncio
import logging
from utils import validate_api_keys, init_database
from llm_generator import LLMGenerator
from post_to_twitter import TwitterPoster
from post_to_linkedin import LinkedInPoster
from post_to_reddit import RedditPoster
from post_manager import PostManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_keys():
    """Test if API keys are properly configured"""
    print("🔑 Testing API Key Configuration...")
    
    validation = validate_api_keys()
    
    for service, is_valid in validation.items():
        status = "✅ Valid" if is_valid else "❌ Missing/Invalid"
        print(f"  {service.title()}: {status}")
    
    return all(validation.values())

def test_database():
    """Test database initialization"""
    print("\n💾 Testing Database Setup...")
    
    try:
        init_database()
        print("  ✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"  ❌ Database error: {str(e)}")
        return False

def test_llm_connection():
    """Test LLM connection"""
    print("\n🧠 Testing LLM Connection...")
    
    try:
        generator = LLMGenerator()
        if generator.test_connection():
            print("  ✅ LLM connection successful")
            return True
        else:
            print("  ❌ LLM connection failed")
            return False
    except Exception as e:
        print(f"  ❌ LLM error: {str(e)}")
        return False

def test_social_platforms():
    """Test social media platform connections"""
    print("\n📱 Testing Social Media Platforms...")
    
    results = {}
    
    # Test Twitter
    try:
        twitter = TwitterPoster()
        results['twitter'] = twitter.test_connection()
        status = "✅ Connected" if results['twitter'] else "❌ Failed"
        print(f"  Twitter: {status}")
    except Exception as e:
        results['twitter'] = False
        print(f"  Twitter: ❌ Error - {str(e)}")
    
    # Test LinkedIn
    try:
        linkedin = LinkedInPoster()
        results['linkedin'] = linkedin.test_connection()
        status = "✅ Connected" if results['linkedin'] else "❌ Failed"
        print(f"  LinkedIn: {status}")
    except Exception as e:
        results['linkedin'] = False
        print(f"  LinkedIn: ❌ Error - {str(e)}")
    
    # Test Reddit
    try:
        reddit = RedditPoster()
        results['reddit'] = reddit.test_connection()
        status = "✅ Connected" if results['reddit'] else "❌ Failed"
        print(f"  Reddit: {status}")
    except Exception as e:
        results['reddit'] = False
        print(f"  Reddit: ❌ Error - {str(e)}")
    
    return results

async def test_post_generation():
    """Test post generation without actually posting"""
    print("\n📝 Testing Post Generation...")
    
    try:
        generator = LLMGenerator()
        test_idea = "The benefits of artificial intelligence in education"
        
        posts = generator.generate_posts(test_idea)
        
        for platform, content in posts.items():
            if content:
                print(f"  ✅ {platform.title()}: Generated ({len(content)} chars)")
                print(f"    Preview: {content[:100]}...")
            else:
                print(f"  ❌ {platform.title()}: Failed to generate")
        
        return any(posts.values())
        
    except Exception as e:
        print(f"  ❌ Post generation error: {str(e)}")
        return False

async def test_full_workflow():
    """Test the complete workflow without posting"""
    print("\n🔄 Testing Complete Workflow...")
    
    try:
        post_manager = PostManager()
        
        # Get platform status
        status = post_manager.get_platform_status()
        available_platforms = sum(1 for p in status.values() if p['available'])
        
        print(f"  Available platforms: {available_platforms}")
        
        if available_platforms > 0:
            print("  ✅ Workflow ready")
            return True
        else:
            print("  ⚠️ No platforms available for posting")
            return False
            
    except Exception as e:
        print(f"  ❌ Workflow error: {str(e)}")
        return False

def print_setup_summary(results):
    """Print a summary of the setup test results"""
    print("\n" + "="*50)
    print("🎯 SETUP SUMMARY")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your bot is ready to use.")
        print("\nNext steps:")
        print("1. Run: python bot.py")
        print("2. Start your Telegram bot")
        print("3. Send /start to begin")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        print("\nCommon fixes:")
        print("1. Verify all API keys in .env file")
        print("2. Check internet connection")
        print("3. Ensure API accounts have proper permissions")

async def main():
    """Run all tests"""
    print("🚀 AI Social Media Agent - Setup Test")
    print("="*50)
    
    results = {}
    
    # Run tests
    results['api_keys'] = test_api_keys()
    results['database'] = test_database()
    results['llm'] = test_llm_connection()
    
    social_results = test_social_platforms()
    results['social_platforms'] = any(social_results.values())
    
    results['post_generation'] = await test_post_generation()
    results['workflow'] = await test_full_workflow()
    
    # Print summary
    print_setup_summary(results)

if __name__ == "__main__":
    asyncio.run(main())
