# Intelligent Content Scraper & Trust Scoring System

##  Overview

This project is an intelligent scraping system that collects content from multiple sources and evaluates their reliability using a custom **Trust Scoring Algorithm**.

The system supports:

* Blog articles
* YouTube videos
* PubMed research papers

It extracts structured data, processes the content, and assigns a **trust score (0–1)** based on credibility factors.

---

## Tools & Libraries Used

### Core Technologies

* **Python 3**
* **Requests** – for HTTP requests
* **BeautifulSoup (bs4)** – HTML parsing
* **readability-lxml** – extracting main article content

### APIs & External Tools

* **YouTube Data API v3** – fetch video metadata
* **youtube-transcript-api** – extract video transcripts
* **BioPython (Entrez)** – fetch PubMed data

###  NLP Utilities

* Custom utilities:

  * `language_detect.py` – detects content language using **langdetect**
  * `chunking.py` – splits content into manageable chunks
  * `tagging.py` – extracts topic tags using **keyBERT**

---

##  Scraping Approach

### Blog Scraper

* Fetches HTML using `requests`
* Uses `readability` to remove navigation, ads, and unrelated page elements.
* Parses using `BeautifulSoup`:

  * Author (meta tags)
  * Publish date
  * Article content

---

### YouTube Scraper

* Extracts video ID from URL
* Uses `YouTube API` to fetch:

  * Channel name
  * Description
  * Publish date
* Uses `transcript API` to get full spoken content

---

### PubMed Scraper

* Extracts **PMID** from URL
* Uses **Entrez API** to fetch:

  * Title
  * Authors
  * Journal
  * Abstract
  * Publication year

---

##  Trust Score Design

The trust score is computed in the range **0 to 1** using:

```
Trust Score = f(
    author_credibility,
    citation_count,
    domain_authority,
    recency,
    medical_disclaimer_presence
)
```

### Factors Explained

* **Author Credibility**

  * Multiple authors → average score is used
    

* **Citation Count**

  * For PubMed using publication counts as proxy.
  * For Youtube using number of views.
  * No citation data for blog
    
* **Domain Authority**

  * Predefined scores for domains (e.g., .gov, .edu higher)
  * Penalazing Domains with lower authority

* **Recency**

  * Recent content gets higher weight

* **Medical Disclaimer Presence**

  * If content matches certain medical keywords,higher weight is assigned.

---

### Implementation

* Each factor is normalized between **0–1**
* Final score is computed using weighted averaging

---

## Limitations

* Some websites block scraping (Cloudflare, JS-heavy sites)
* Author extraction may fail due to inconsistent HTML
* Citation detection is not exact.
* YouTube transcripts may not always be available
* Domain authority is manually assigned (not dynamic)

---

## How to Run the Project

### 1️)Clone the repository

```
git clone <your-repo-link>
cd project
```

---

### 2)Create virtual environment

```
python -m venv venv
```

Activate:

* **Windows**

```
venv\Scripts\activate
```

* **Mac/Linux**

```
source venv/bin/activate
```

---

### 3️)Install dependencies

```
pip install -r requirements.txt
```

---

### 4️)Setup environment variables

Create a `.env` file:

```
YOUTUBE_API_KEY=your_api_key
EMAIL=your_email
```

---

### 5️)Run the project

```
python main.py
```

---

### 6️)Output

The final dataset will be generated in:

```
output/scraped_data.json
```

---

## Project Structure

```
project/
│
├── scraper/
│   ├── blog_scraper.py
│   ├── youtube_scraper.py
│   └── pubmed_scraper.py
│
├── scoring/
│   └── trust_score.py
│
├── utils/
│   ├── tagging.py
│   ├── chunking.py
│   └── language_detect.py
│
├── output/
│   └── scraped_data.json
│
├── main.py
├── requirements.txt
└── README.md
```

---


## Conclusion

This project demonstrates:

* Multi-source data scraping
* NLP-based content processing
* Real-world trust evaluation system

It can be extended into applications like:

* Fake news detection
* Research validation tools
* Content credibility analysis systems
