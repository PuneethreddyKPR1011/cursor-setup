
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from supadata import Supadata

load_dotenv()

API_KEY = os.getenv("SUPADATA_API_KEY")
if not API_KEY:
    raise ValueError("Set SUPADATA_API_KEY environment variable")

supadata = Supadata(api_key=API_KEY)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LINKS_FILE = SCRIPT_DIR / "youtube_links.txt"
OUTPUT_DIR = REPO_ROOT / "research" / "youtube-transcripts"


def extract_video_id(url: str) -> str | None:
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def sanitize_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


if not LINKS_FILE.exists():
    raise FileNotFoundError(f"Missing input file: {LINKS_FILE}")

with LINKS_FILE.open("r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for link in links:
    video_id = extract_video_id(link)
    if not video_id:
        print(f"❌ Invalid URL: {link}")
        continue

    try:
        transcript = supadata.transcript(link)
    except Exception as e:
        print(f"❌ API error for {video_id}: {e}")
        continue
    if not hasattr(transcript, "content") or not transcript.content:
        print(f"❌ Invalid/empty transcript response for {video_id}")
        continue

    safe_video_id = sanitize_filename(video_id)
    file_path = OUTPUT_DIR / f"{safe_video_id}.md"

    try:
        with file_path.open("w", encoding="utf-8") as file:
            file.write(f"# Video: {link}\n\n")
            file.write("\n".join(chunk.text for chunk in transcript.content))
    except OSError as e:
        print(f"❌ Could not write transcript for {video_id}: {e}")
        continue

    print(f"✅ Saved: {video_id}")


