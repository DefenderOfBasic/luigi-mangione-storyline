import json
import os
from datetime import datetime
import requests
from pathlib import Path

def safe_get(dict_obj, key, default=""):
    """Safely get a value from a dictionary with a default fallback"""
    try:
        value = dict_obj.get(key, default)
        return value if value is not None else default
    except:
        return default

def create_markdown_content(comment):
    """Convert a comment to markdown format with safe key access"""
    try:
        # Safely get created_utc with a fallback to current timestamp
        created_utc = safe_get(comment, 'created_utc', datetime.now().timestamp())
        created_date = datetime.fromtimestamp(created_utc)
        
        # Build permalink
        permalink = safe_get(comment, 'permalink')
        full_permalink = f"https://reddit.com{permalink}" if permalink else "No permalink available"

        md_content = f"""# Comment in r/{safe_get(comment, 'subreddit', 'Unknown')}

Date: {created_date.strftime('%Y-%m-%d %H:%M:%S')}
Author: {safe_get(comment, 'author', 'Unknown')}
Subreddit: {safe_get(comment, 'subreddit', 'Unknown')}
Score: {safe_get(comment, 'score', 0)}
Permalink: {full_permalink}

## Content

{safe_get(comment, 'body', 'No content available')}

---
"""
        return md_content
    except Exception as e:
        print(f"Error creating markdown content: {e}")
        return f"""# Error in Comment Processing

Error occurred while processing this comment.
Raw data: {str(comment)}

---
"""

def save_to_archive(data, base_path="reddit_archive"):
    """Save comments to organized markdown files with error handling"""
    if not isinstance(data, dict) or 'data' not in data:
        print("❌ Invalid data format received")
        return

    for comment in data['data']:
        try:
            # Safely get created_utc
            created_utc = safe_get(comment, 'created_utc', datetime.now().timestamp())
            date = datetime.fromtimestamp(created_utc)
            year_month = date.strftime('%Y/%m')
            subreddit = safe_get(comment, 'subreddit', 'unknown_subreddit')
            
            # Create folder path
            folder_path = Path(base_path) / year_month / subreddit
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Safely get comment ID or generate a timestamp-based one
            comment_id = safe_get(comment, 'id', f"unknown_{int(datetime.now().timestamp())}")
            filename = f"{comment_id}.md"
            file_path = folder_path / filename
            
            # Generate and save markdown content
            md_content = create_markdown_content(comment)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
                
            print(f"✅ Saved: {file_path}")
            
        except Exception as e:
            print(f"❌ Error processing comment: {e}")
            # Optionally save error log
            error_path = Path(base_path) / "errors"
            error_path.mkdir(parents=True, exist_ok=True)
            error_file = error_path / f"error_{int(datetime.now().timestamp())}.txt"
            
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"Error: {str(e)}\nComment data: {json.dumps(comment, indent=2)}")

def fetch_reddit_data(username):
    """Fetch data from Reddit API with error handling"""
    try:
        url = f"https://api.pullpush.io/reddit/search/comment/?test&sort_type=created_utc&sort=desc&limit=100&author=Mister_cactus"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.RequestException as e:
        print(f"❌ API request failed: {e}")
        return {"data": []}  # Return empty data structure
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse API response: {e}")
        return {"data": []}

def main():
    username = "Mister_cactus"  # Replace with target username
    
    print(f"📥 Fetching data for u/{username}...")
    data = fetch_reddit_data(username)
    
    if not data.get('data'):
        print("❌ No data received")
        return
    
    print("💾 Saving to archive...")
    save_to_archive(data)
    
    print("✅ Archive complete!")

if __name__ == "__main__":
    main()

