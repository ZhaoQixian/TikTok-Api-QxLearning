from TikTokApi import TikTokApi
import asyncio
import os

async def search_popular_hashtags():
    """
    Search for popular hashtags on TikTok.
    This approach tends to be more reliable than trying to get trending data directly.
    """
    # Popular search terms that often have trending hashtags associated
    search_terms = ["fyp", "trending", "viral", "dance", "challenge"]
    
    # Get ms_token from environment (if available)
    ms_token = os.environ.get("ms_token", None)
    
    print("Initializing TikTokApi...")
    async with TikTokApi() as api:
        try:
            # Create session
            if ms_token:
                print(f"Creating session with ms_token...")
                await api.create_sessions(ms_tokens=[ms_token], num_sessions=1)
            else:
                print("Creating session without ms_token (limited functionality)...")
                await api.create_sessions(num_sessions=1)
            
            print("\nSearching for popular hashtags...")
            all_hashtags = []
            
            for term in search_terms:
                print(f"\nSearching for term: {term}")
                try:
                    # Search for hashtags
                    count = 0
                    async for hashtag in api.search.hashtags(term):
                        all_hashtags.append({
                            "title": hashtag.title,
                            "views": hashtag.view_count,
                            "videos": getattr(hashtag, "video_count", "N/A")
                        })
                        count += 1
                        if count >= 5:  # Limit to 5 hashtags per term
                            break
                    
                    print(f"Found {count} hashtags for '{term}'")
                except Exception as e:
                    print(f"Error searching for '{term}': {str(e)}")
            
            if all_hashtags:
                # Sort by view count (most popular first)
                all_hashtags.sort(key=lambda x: x["views"] if isinstance(x["views"], int) else 0, reverse=True)
                
                print("\n==== Popular Hashtags Found ====")
                for i, tag in enumerate(all_hashtags):
                    print(f"{i+1}. #{tag['title']} - {tag['views']} views")
                    
                return all_hashtags
            else:
                print("\nNo hashtags found. Try using a valid ms_token.")
                return []
                
        except Exception as e:
            print(f"Error in TikTokApi: {str(e)}")
            return []

if __name__ == "__main__":
    asyncio.run(search_popular_hashtags())