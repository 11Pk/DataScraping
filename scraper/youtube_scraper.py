import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

from utils.language_detect import detect_language
from utils.chunking import chunk_text
from utils.tagging import extract_topics

from scoring.trust_score import calculate_trust_score

def extract_video_id(url):
    query = urlparse(url)
    return parse_qs(query.query)["v"][0]

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def scrape_youtube(url):
    try:
        video_id = extract_video_id(url)
        api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={YOUTUBE_API_KEY}&part=snippet,statistics"

        response = requests.get(api_url)
        data = response.json()

        snippet = data["items"][0]["snippet"]

        channel_name = snippet["channelTitle"]
        publish_date = snippet["publishedAt"]
        description = snippet["description"]

        video_stats = data["items"][0]["statistics"]
        views = int(video_stats.get("viewCount", 0))
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([t["text"] for t in transcript])
        except:
            transcript_text = ""
        full_content = description + " " + transcript_text

        language = detect_language(full_content)
        topics = extract_topics(full_content)
        #trust score
        trust_score = calculate_trust_score(
         author=channel_name,
          source_type="youtube",
         url=url,
         published_date=publish_date,
         content=full_content,
         extra_data={"views": views}
        )
        content_chunks = chunk_text(full_content)

        return {
            "source_url": url,
            "source_type": "youtube",
            "author": channel_name,
            "published_date": publish_date,
            "language": language,
            "region": None,
            "topic_tags": topics,
            "trust_score": trust_score,
            "content_chunks": content_chunks,
         
            
        }
    except Exception as e:
        print(f"Error scraping YouTube video: {e}")
        return None


