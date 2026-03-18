import os
from Bio import Entrez
from dotenv import load_dotenv
import time
import tldextract

load_dotenv()
Entrez.email =os.getenv("Email")

#search for papers by author name
def search_author_pubmed(author_name):
    try:
        handle = Entrez.esearch(
            db="pubmed",
            term=f"{author_name}[Author]",
            retmax=5
        )
        record = Entrez.read(handle)
        return record["IdList"]
    except:
        return []

#fetch paper details
def fetch_papers(paper_ids):
    if not paper_ids:
        return []
    
    try:
        handle = Entrez.efetch(
            db="pubmed",
            id=",".join(paper_ids),
            rettype="xml"
        )
        return Entrez.read(handle)
    except:
        return []

#extract affiliations for a given author
def extract_author_affiliations(pubmed_data, target_author):
    affiliations = []

    try:
        for article in pubmed_data.get("PubmedArticle", []):
            authors = article["MedlineCitation"]["Article"].get("AuthorList", [])

            for author in authors:
                name = ""
                if "ForeName" in author and "LastName" in author:
                    name = author["ForeName"] + " " + author["LastName"]

                if target_author.lower() in name.lower():
                    for aff in author.get("AffiliationInfo", []):
                        affiliations.append(aff.get("Affiliation", ""))
    except:
        pass

    return affiliations

#checking for fake authors
def verify_author_pubmed(author_name, claimed_affiliation=None):
 

    paper_ids = search_author_pubmed(author_name)
    
    # No publications → low trust
    if not paper_ids:
        return 0.2

    time.sleep(0.3)  # to prevent rate limiting

    papers = fetch_papers(paper_ids)
    affiliations = extract_author_affiliations(papers, author_name)

    # If affiliation provided, check match
    if claimed_affiliation:
        for aff in affiliations:
            if claimed_affiliation.lower() in aff.lower():
                return 0.9  # strong match

        return 0.7  # author exists but affiliation mismatch

    # If no affiliation provided, just existence matters
    return 0.7


#scoring a single author
def score_single_author(author, source_type="blog"):

    if not author:
        return 0.3

    #for blog and youtube
    if source_type in ["blog", "youtube"]:
        score = 0.4

        if isinstance(author, str) and len(author.split()) >= 2:
            score += 0.2

        return min(score, 0.6)  

    # for Pubmed Verification
    elif source_type == "pubmed":
        if isinstance(author, dict):
            name = author.get("name", "")
            affiliation = author.get("affiliation", None)
        else:
            name = author
            affiliation = None

        if not name:
            return 0.3

        return verify_author_pubmed(name, affiliation)

    return 0.3





#Author Credibility Score
def get_author_credibility(author, source_type="blog"):
    #No Author
    if not author:
        return 0.3

    # Multiple authors
    if isinstance(author, list):
        scores = [
            score_single_author(a, source_type)
            for a in author if a
        ]
        return sum(scores) / len(scores) if scores else 0.3
    #Single Author
    return score_single_author(author, source_type)


#Citation Score
def get_citation_score(data, source_type):


    #PubMed
    if source_type == "pubmed":
        # Use publication count as proxy
        count = data.get("paper_count")

        if count is None:
            return 0.3
        
        return min(count / 50, 1)

    #Youtube
    elif source_type == "youtube":
        views = data.get("views")

        if views is None:
            return 0.3
        
        return min(views / 100000, 1)

    # Blog
    elif source_type == "blog":
            return 0.3   #usually no citation data

    return 0.3

#domain authority
def get_domain_authority(url):
    ext = tldextract.extract(url)
    domain = ext.domain
    suffix = ext.suffix
    full_domain = f"{domain}.{suffix}"

    high_trust = ["nature.com", "nih.gov", "who.int", "cdc.gov"]
    medium_trust = ["medium.com", "towardsdatascience.com"]

    if full_domain in high_trust:
        return 0.9
    elif full_domain in medium_trust:
        return 0.7
    elif suffix == "gov":
        return 0.85   
    elif suffix == "edu":
        return 0.8
    else:
        return 0.5    #penalizing domains with low authority
    
#recency
import datetime

def get_recency_score(published_date):
    try:
        year = int(str(published_date)[:4])
        current_year = datetime.datetime.now().year
        diff = current_year - year

        if diff <= 1:
            return 1.0
        elif diff <= 3:
            return 0.8
        elif diff <= 5:
            return 0.6
        else:
            return 0.3
    except:
        return 0.5
    
#medical disclaimer
def get_disclaimer_score(content):
    keywords = [
        "not medical advice",
        "consult a doctor",
        "for informational purposes",
        "educational purposes only",
        "not a substitute for professional advice",
        "seek professional advice"
    ]

    content_lower = content.lower()
    matches = sum(1 for k in keywords if k in content_lower)

    if matches >= 2:
        return 1.0
    elif matches == 1:
        return 0.7
    else:
        return 0.5   


#OVERALL TRUST SCORE FUNCTION
def calculate_trust_score(
    author,
    source_type,
    url,
    published_date,
    content,
    extra_data=None
):

    data = extra_data or {}

    author_score = get_author_credibility(author, source_type)
    citation_score = get_citation_score(data, source_type)
    domain_score = get_domain_authority(url)
    recency_score = get_recency_score(published_date)
    disclaimer_score = get_disclaimer_score(content)

    trust_score = (
        0.25 * author_score +
        0.20 * citation_score +
        0.20 * domain_score +
        0.20 * recency_score +
        0.15 * disclaimer_score
    )

    return round(trust_score, 2)