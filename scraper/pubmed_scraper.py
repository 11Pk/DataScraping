import os
import re
from dotenv import load_dotenv
from Bio import Entrez
from utils.language_detect import detect_language
from utils.chunking import chunk_text
from utils.tagging import extract_topics
from scoring.trust_score import calculate_trust_score

load_dotenv()
Entrez.email =os.getenv("Email")

def extract_authors(author_list):
    authors = []
    
    for author in author_list:
        if "LastName" in author and "ForeName" in author:
            name = f"{author['ForeName']} {author['LastName']}"
            
        affiliation = None
        if "AffiliationInfo" in author and author["AffiliationInfo"]:
                affiliation = author["AffiliationInfo"][0].get("Affiliation", None)

        authors.append({
                "name": name,
                "affiliation": affiliation
            })

    return authors
def extract_pmid(url):
    match = re.search(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)', url)
    if match:
        return match.group(1)
    return None

def scrape_pubmed(url):
    pmid = extract_pmid(url)

    if not pmid:
        print("Invalid PubMed URL")
        return None
    try:

        handle = Entrez.efetch(
            db="pubmed",
            id=pmid,
            retmode="xml"
        )

        records = Entrez.read(handle)

        article = records["PubmedArticle"][0]["MedlineCitation"]["Article"]

        # Title
        title = article.get("ArticleTitle", None)

        # Authors
        author_list = article.get("AuthorList", [])
        authors = extract_authors(author_list)

        # Journal
        journal = article["Journal"]["Title"]

        # Publication year
        pub_date = article["Journal"]["JournalIssue"]["PubDate"]
        year = pub_date.get("Year", None)

        # Abstract
        abstract = ""
        if "Abstract" in article:
            abstract_parts = article["Abstract"]["AbstractText"]
            abstract = " ".join(str(a) for a in abstract_parts)

        # Language detection
        language = detect_language(abstract)

        # Topic tagging
        topics = extract_topics(abstract)
        
        #Trust score
            #author ki affilation and name in dictionary
        paper_count = len(authors)
        trust_score = calculate_trust_score(
         author=authors,
         source_type="pubmed",
         url=url,
         published_date=year,
         content=abstract,
         extra_data={"paper_count": len(authors)}
        )
        
        # Chunking
        content_chunks = chunk_text(abstract)

        return {
            "source_url": url,
            "source_type": "pubmed",
            "author": authors,
            "published_date": year,
            "language": language,
            "region": None,
            "topic_tags": topics,
            "trust_score": trust_score,
            "content_chunks": content_chunks,
           
        }

    except Exception as e:
        print(f"Error fetching PubMed article: {e}")
        return None