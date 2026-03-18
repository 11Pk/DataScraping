import requests
from bs4 import BeautifulSoup
from readability import Document
from utils.language_detect import detect_language
from utils.chunking import chunk_text
from utils.tagging import extract_topics
from scoring.trust_score import calculate_trust_score
def scrape_blog(url):
    try:
        response = requests.get(url)
        
        doc = Document(response.text)
        html = doc.summary()
        title = doc.short_title()  #incase needed later
        
        soup = BeautifulSoup(html, "html.parser")
        #Author
        author = soup.find("meta", {"name": "author"})
        author = author.get("content") if author else None

        # Publish date
        date = soup.find("meta", {"property": "article:published_time"})
        date = date.get("content") if date else None
        
        #Content
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join([p.text for p in paragraphs])

        #language
        language = detect_language(content)

        #region
        locale = soup.find("meta", {"property": "og:locale"})
        region = locale.get("content") if locale else None

        #topics
        topics = extract_topics(content)

        #chunks
        content_chunks = chunk_text(content)

        #trust score
        trust_score = calculate_trust_score(
         author=author,
         source_type="blog",
         url=url,
         published_date=date,
         content=content,
         extra_data=None
)

        return {
        "source_url": url,
        "source_type": "blog",
        "author": author,
        "published_date": date,
        "language": language,
        "region": region,
        "topic_tags": topics,
        "trust_score": trust_score,
        "content_chunks": content_chunks,
       
        }  
    except requests.exceptions.RequestException as e:
        print(f"Error scraping the blog post: {e}")
        return None

