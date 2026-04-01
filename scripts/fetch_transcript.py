
import os
import re
from supadata import Supadata

from dotenv import load_dotenv
load_dotenv()
# Get API key
API_KEY = os.getenv("SUPADATA_API_KEY")
if not API_KEY:
    raise ValueError("Set SUPADATA_API_KEY environment variable")

supadata = Supadata(api_key=API_KEY)

# 📌 Function to extract video ID from YouTube URL
def extract_video_id(url):
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",       # normal youtube link
        r"youtu\.be/([a-zA-Z0-9_-]{11})",  # short link
        r"embed/([a-zA-Z0-9_-]{11})"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

# 📂 Read links from file
with open("scripts\youtube_links.txt", "r") as f:
    links = [line.strip() for line in f if line.strip()]

# 📁 Create output folder
os.makedirs("research/youtube-transcript", exist_ok=True)

# 🚀 Process each link
for link in links:
    video_id = extract_video_id(link)

    if not video_id:
        print(f"❌ Invalid URL: {link}")
        continue

    try:
        transcript = supadata.youtube.transcript(
            video_id=video_id,
            text=True
        )

        file_path = f"research/youtube-transcripts/{video_id}.md"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"# Video: {link}\n\n")
            file.write(transcript.content)

        print(f"✅ Saved: {video_id}")

    except Exception as e:
        print(f"❌ Error for {video_id}: {e}")


