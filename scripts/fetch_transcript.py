from youtube_transcript_api import YouTubeTranscriptApi

video_id = "hyYCn_kAngI"

transcript = YouTubeTranscriptApi().fetch(video_id)

for entry in transcript:
    print(entry.text)