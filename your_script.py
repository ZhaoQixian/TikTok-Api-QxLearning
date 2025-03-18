from TikTokApi import TikTokApi
import asyncio
import os
import json

async def search_popular_hashtags():
    """
    Search for popular hashtags on TikTok using the updated TikTokApi interface.
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
                    # Use the updated search method syntax
                    search_results = api.search
                    count = 0
                    
                    # Check if there's a direct method to search hashtags
                    if hasattr(search_results, "hashtags"):
                        async for hashtag in search_results.hashtags(term):
                            process_hashtag(hashtag, all_hashtags)
                            count += 1
                            if count >= 5:
                                break
                    # If not, try using the general search method and filter for hashtags
                    else:
                        print(f"Using general search for '{term}'...")
                        async for result in search_results.search(term):
                            # Check if this is a challenge/hashtag result
                            if hasattr(result, "title") and hasattr(result, "view_count"):
                                process_hashtag(result, all_hashtags)
                                count += 1
                                if count >= 5:
                                    break
                    
                    print(f"Found {count} hashtags for '{term}'")
                except Exception as e:
                    print(f"Error searching for '{term}': {str(e)}")
                    # Print available methods on search_results for debugging
                    try:
                        print(f"Available search methods: {dir(search_results)}")
                    except:
                        pass
            
            if all_hashtags:
                # Sort by view count (most popular first)
                all_hashtags.sort(key=lambda x: x["views"] if isinstance(x["views"], int) else 0, reverse=True)
                
                print("\n==== Popular Hashtags Found ====")
                for i, tag in enumerate(all_hashtags):
                    print(f"{i+1}. #{tag['title']} - {tag['views']:,} views, {tag['videos']:,} videos")
                    
                # Save results to a JSON file
                with open("popular_hashtags.json", "w") as f:
                    json.dump(all_hashtags, f, indent=2)
                print(f"\nResults saved to popular_hashtags.json")
                
                return all_hashtags
            else:
                print("\nNo hashtags found. Try using a valid ms_token or check the TikTokApi documentation for updated methods.")
                return []
                
        except Exception as e:
            print(f"Error in TikTokApi: {str(e)}")
            return []

def process_hashtag(hashtag, all_hashtags):
    """Process a hashtag object and add its data to the all_hashtags list."""
    # Get the video count from statsV2 if available, otherwise fallback to old method
    video_count = 0
    
    # Try to access the raw data to get statsV2
    raw_data = getattr(hashtag, "as_dict", None)
    if raw_data and callable(raw_data):
        data_dict = raw_data()
        # Check if statsV2 is available in the challenge info
        challenge_info = data_dict.get("challengeInfo", {})
        stats_v2 = challenge_info.get("statsV2", {})
        if stats_v2 and "videoCount" in stats_v2:
            try:
                # Convert from string to integer
                video_count = int(stats_v2["videoCount"])
            except (ValueError, TypeError):
                pass
    
    # If we couldn't get it from statsV2, try the traditional method
    if video_count == 0:
        video_count = getattr(hashtag, "video_count", 0)
    
    all_hashtags.append({
        "title": hashtag.title,
        "views": hashtag.view_count,
        "videos": video_count
    })
    
    # Print debug info
    print(f"Found #{hashtag.title}: {hashtag.view_count:,} views, {video_count:,} videos")

# Alternative approach - directly search for specific hashtags
async def get_specific_hashtags():
    """
    Get information for specific predefined hashtags.
    This can be used as an alternative when search doesn't work.
    """
    # List of popular hashtags to check
    hashtag_list = ["fyp", "trending", "viral", "dance", "challenge", 
                   "comedy", "food", "music", "fitness", "travel"]
    
    ms_token = os.environ.get("ms_token", None)
    
    print("Initializing TikTokApi for specific hashtags...")
    async with TikTokApi() as api:
        try:
            # Create session
            if ms_token:
                print(f"Creating session with ms_token...")
                await api.create_sessions(ms_tokens=[ms_token], num_sessions=1)
            else:
                print("Creating session without ms_token (limited functionality)...")
                await api.create_sessions(num_sessions=1)
            
            all_hashtags = []
            
            print("\nFetching specific hashtags...")
            for tag in hashtag_list:
                try:
                    print(f"Fetching #{tag}...")
                    # Try using challenge_detail method if available
                    if hasattr(api, "challenge_detail"):
                        challenge = await api.challenge_detail(tag)
                        if challenge:
                            process_challenge(challenge, all_hashtags)
                    # Try alternative method
                    elif hasattr(api, "hashtag"):
                        challenge = await api.hashtag(tag)
                        if challenge:
                            process_challenge(challenge, all_hashtags)
                except Exception as e:
                    print(f"Error fetching #{tag}: {str(e)}")
            
            if all_hashtags:
                # Sort and display
                all_hashtags.sort(key=lambda x: x["views"] if isinstance(x["views"], int) else 0, reverse=True)
                print("\n==== Popular Hashtags ====")
                for i, tag in enumerate(all_hashtags):
                    print(f"{i+1}. #{tag['title']} - {tag['views']:,} views, {tag['videos']:,} videos")
                
                # Save results
                with open("specific_hashtags.json", "w") as f:
                    json.dump(all_hashtags, f, indent=2)
                print(f"\nResults saved to specific_hashtags.json")
                
                return all_hashtags
            else:
                print("\nNo hashtags found. Try using a valid ms_token.")
                return []
                
        except Exception as e:
            print(f"Error in TikTokApi: {str(e)}")
            return []

def process_challenge(challenge, all_hashtags):
    """Process a challenge object and add its data to the all_hashtags list."""
    title = getattr(challenge, "title", "unknown")
    views = getattr(challenge, "view_count", 0)
    
    # Try to get video count from different possible attributes
    video_count = 0
    if hasattr(challenge, "video_count"):
        video_count = challenge.video_count
    elif hasattr(challenge, "stats") and hasattr(challenge.stats, "video_count"):
        video_count = challenge.stats.video_count
    
    # Try to get from raw dictionary
    raw_data = getattr(challenge, "as_dict", None)
    if raw_data and callable(raw_data):
        data_dict = raw_data()
        # Check if statsV2 is available
        stats_v2 = data_dict.get("statsV2", {})
        if stats_v2 and "videoCount" in stats_v2:
            try:
                video_count = int(stats_v2["videoCount"])
            except (ValueError, TypeError):
                pass
    
    all_hashtags.append({
        "title": title,
        "views": views,
        "videos": video_count
    })
    
    print(f"Found #{title}: {views:,} views, {video_count:,} videos")

if __name__ == "__main__":
    # Try the main search approach first
    result = asyncio.run(search_popular_hashtags())
    
    # If no results, try the alternative approach
    if not result:
        print("\n===== Trying Alternative Approach =====")
        asyncio.run(get_specific_hashtags())