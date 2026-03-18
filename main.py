import os
import json
from scraper.blog_scraper import scrape_blog
from scraper.youtube_scraper import scrape_youtube
from scraper.pubmed_scraper import scrape_pubmed

blog_urls = [
    "https://www.tutorialspoint.com/python/index.htm",
    "https://science.nasa.gov/climate-change/evidence/",
    "https://www.geeksforgeeks.org/machine-learning/machine-learning/"
]

youtube_urls = [
    "https://www.youtube.com/watch?v=d95J8yzvjbQ",
    "https://www.youtube.com/watch?v=RBSGKlAvoiM"
]

pubmed_urls = [
    "https://pubmed.ncbi.nlm.nih.gov/31452104/"
]



all_data = []

# Blogs
for url in blog_urls:
    data = scrape_blog(url)
    if data:
        all_data.append(data)

# YouTube
for url in youtube_urls:
    data = scrape_youtube(url)
    if data:
        all_data.append(data)

# PubMed
for url in pubmed_urls:
    data = scrape_pubmed(url)
    if data:
        all_data.append(data)


os.makedirs("output", exist_ok=True)

with open("output/scraped_data2.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=4, ensure_ascii=False)

print("Data successfully saved to output")

