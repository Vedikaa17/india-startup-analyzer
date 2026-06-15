import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import os
from dotenv import load_dotenv

# .env file se API key load karo
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ============================================
# SECTOR KEYWORDS
# ============================================
SECTOR_KEYWORDS = {
    "Fintech"    : ["fintech", "payment", "banking", "loan",
                    "credit", "upi", "finance", "neobank"],
    "Healthtech" : ["health", "medical", "clinical", "hospital",
                    "pharma", "biotech", "cancer", "therapy", "wellness"],
    "Edtech"     : ["edtech", "education", "learning", "school",
                    "tutoring", "course", "upskill", "byju", "unacademy"],
    "AI"         : ["artificial intelligence", "machine learning",
                    "llm", "chatbot", "generative", "deep learning"],
    "EV"         : ["electric vehicle", "ev ", "battery",
                    "charging", "ather", "ola electric"],
    "Ecommerce"  : ["ecommerce", "shopping", "retail", "marketplace",
                    "meesho", "flipkart"],
    "Spacetech"  : ["space", "satellite", "rocket", "aerospace"],
    "Logistics"  : ["logistics", "delivery", "shipping", "supply chain"],
    "Deeptech"   : ["deeptech", "deep tech", "semiconductor", "robotics"],
    "Fitness"    : ["fitness", "workout", "gym", "fittr"],
    "D2C"        : ["d2c", "direct to consumer", "beauty", "fashion"],
    "SaaS"       : ["saas", "software", "cloud", "platform", "b2b"],
}

# ============================================
# FUNCTION 1: Check if FUNDING news
# ============================================
def is_funding_news(title):
    title_lower = title.lower()

    skip_patterns = [
        "from .* to ",
        "tech stocks",
        "stays jail",
        "tax demand",
        "weekly gains",
        "debuts on",
        "backs fitness",
        "backs .* startup",
    ]
    for pattern in skip_patterns:
        if re.search(pattern, title_lower):
            return False

    has_amount = "$" in title or "₹" in title
    is_just_backing = "backs" in title_lower and not has_amount
    if is_just_backing:
        return False

    funding_keywords = [
        "raises", "raised", "secures", "secured",
        "funding", "investment", "backs", "backed",
        "acquires", "acquisition", "launches fund",
        "closes", "bags", "$", "₹"
    ]
    for keyword in funding_keywords:
        if keyword in title_lower:
            return True

    return False

# ============================================
# FUNCTION 2: Extract Funding Amount
# ============================================
def extract_amount(title):
    dollar_pattern = r'\$[\d,.]+\s*(?:Mn|Bn|Million|Billion)?'
    rupee_pattern  = r'₹[\d,.]+\s*(?:Cr|Lakh|crore)?'

    dollar_match = re.search(dollar_pattern, title, re.IGNORECASE)
    if dollar_match:
        return dollar_match.group()

    rupee_match = re.search(rupee_pattern, title, re.IGNORECASE)
    if rupee_match:
        return rupee_match.group()

    return "Not mentioned"

# ============================================
# FUNCTION 3: Detect Sector
# ============================================
def detect_sector(title):
    title_lower = title.lower()

    if " ai" in title_lower or title_lower.startswith("ai "):
        return "AI"

    for sector, keywords in SECTOR_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return sector

    return "General"

# ============================================
# FUNCTION 4: Extract Company Name
# ============================================
def extract_company(title):
    noise_starts = ["to ", "for ", "relief for ",
                    "from ", "ipo-bound "]

    noise_ends = [
        "\u2019s board", "\u2019s",
        "'s board", "'s",
        " board", " to", " for", " co"
    ]

    action_words = ["raises", "secures", "gets", "receives",
                    "acquires", "launches", "closes", "bags",
                    "backs", "invests", "debuts", "approves",
                    "to acquire", "to raise"]

    title_lower = title.lower()

    for noise in noise_starts:
        if title_lower.startswith(noise):
            title = title[len(noise):]
            title_lower = title_lower[len(noise):]

    for word in action_words:
        if word in title_lower:
            position = title_lower.index(word)
            company = title[:position].strip()

            company_lower = company.lower()
            for noise in noise_ends:
                if company_lower.endswith(noise.lower()):
                    company = company[:len(company)-len(noise)].strip()
                    company_lower = company.lower()

            words = company.split()
            if len(words) > 4:
                company = " ".join(words[:4])

            return company

    words = title.split()
    return " ".join(words[:3])

# ============================================
# SCRAPER 1: Inc42
# ============================================
def scrape_inc42():
    print("\n🔍 Scraping Inc42...")
    print("-" * 50)

    url = "https://inc42.com/buzz/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    print(f"Website response: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("h2", class_="entry-title recommended-block-head")
    print(f"Total articles found: {len(articles)}")

    data = []
    skipped = 0

    for article in articles:
        link = article.find("a")
        if link:
            title = link.get_text(strip=True)
            url_link = link["href"]

            if not is_funding_news(title):
                skipped += 1
                continue

            data.append({
                "company"      : extract_company(title),
                "amount"       : extract_amount(title),
                "sector"       : detect_sector(title),
                "title"        : title,
                "url"          : url_link,
                "source"       : "Inc42",
                "scraped_date" : datetime.now().strftime("%Y-%m-%d")
            })

    print(f"✅ Inc42: {len(data)} funding articles found!")
    return data

# ============================================
# SCRAPER 2: NewsAPI
# ============================================
def scrape_newsapi():
    print("\n🔍 Fetching from NewsAPI...")
    print("-" * 50)

    if not NEWS_API_KEY:
        print("❌ NEWS_API_KEY not found in .env file!")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q"          : "India startup funding",
        "language"   : "en",
        "sortBy"     : "publishedAt",
        "pageSize"   : 30,
        "apiKey"     : NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    print(f"NewsAPI response: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ NewsAPI Error: {response.json()}")
        return []

    articles = response.json().get("articles", [])
    print(f"Total articles received: {len(articles)}")

    data = []
    for article in articles:
        title = article.get("title", "")

        if not title or not is_funding_news(title):
            continue

        data.append({
            "company"      : extract_company(title),
            "amount"       : extract_amount(title),
            "sector"       : detect_sector(title),
            "title"        : title,
            "url"          : article.get("url", ""),
            "source"       : article.get("source", {}).get("name", "NewsAPI"),
            "scraped_date" : datetime.now().strftime("%Y-%m-%d")
        })

    print(f"✅ NewsAPI: {len(data)} funding articles found!")
    return data

# ============================================
# MAIN FUNCTION — Combine Both Sources
# ============================================
def collect_all_data():
    print("=" * 50)
    print("   INDIA STARTUP FUNDING DATA COLLECTOR")
    print("=" * 50)

    # Collect from both sources
    inc42_data   = scrape_inc42()
    newsapi_data = scrape_newsapi()

    # Combine both
    all_data = inc42_data + newsapi_data

    # Remove duplicate titles
    df = pd.DataFrame(all_data)
    df = df.drop_duplicates(subset=["title"])

    # Save to CSV - append new data, don't delete old!
    csv_path = "data/inc42_articles.csv"

    if os.path.exists(csv_path):
        # File already exists - load old data
        old_df = pd.read_csv(csv_path)
        # Combine old + new data
        combined_df = pd.concat([old_df, df], ignore_index=True)
        # Remove duplicates
        combined_df = combined_df.drop_duplicates(subset=["title"])
        combined_df.to_csv(csv_path, index=False)
        df = combined_df
    else:
        # First time - create new file
        df.to_csv(csv_path, index=False)

    print("\n" + "=" * 50)
    print(f"📊 FINAL SUMMARY:")
    print(f"   Inc42 articles   : {len(inc42_data)}")
    print(f"   NewsAPI articles : {len(newsapi_data)}")
    print(f"   Total unique     : {len(df)}")
    print(f"✅ Saved to data/inc42_articles.csv")
    print("=" * 50)

    return df

if __name__ == "__main__":
    collect_all_data()