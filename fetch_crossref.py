#!/usr/bin/env python3
"""
CrossRef Journal Citation Counter Script
This script fetches all articles from a journal and their citation counts using the CrossRef API.
"""

import requests
import time
import csv
import json
from typing import List, Dict, Optional
from urllib.parse import urlencode

# Configuration
JOURNAL_ISSN = "0167-9228"  # Replace with your journal's ISSN
YOUR_EMAIL = "info@openjournals.nl"  # Replace with your email
APP_NAME = "JournalCitationCounter/1.0"

# API Configuration
BASE_URL = "https://api.crossref.org/works"
HEADERS = {
    "User-Agent": f"{APP_NAME} (mailto:{YOUR_EMAIL})"
}

def fetch_all_articles(issn: str) -> List[Dict]:
    """
    Fetch all articles from a journal by ISSN and return their citation data.
    
    Args:
        issn: The ISSN of the journal
        
    Returns:
        List of dictionaries containing article data
    """
    all_articles = []
    cursor = "*"
    has_more = True
    page_count = 0
    
    print(f"Starting to fetch articles for ISSN: {issn}")
    
    while has_more:
        try:
            page_count += 1
            print(f"Fetching page {page_count}...")
            
            # Build parameters
            params = {
                "filter": f"issn:{issn}",
                "rows": "1000",
                "cursor": cursor,
                "select": "DOI,title,is-referenced-by-count,published-print,published-online"
            }
            
            # Make the API request
            response = requests.get(BASE_URL, headers=HEADERS, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("message", {}).get("items", [])
            
            print(f"Found {len(items)} articles on this page")
            
            # Process each article
            for article in items:
                processed_article = {
                    "doi": article.get("DOI", ""),
                    "title": get_title(article),
                    "citation_count": article.get("is-referenced-by-count", 0),
                    "published_year": get_published_year(article)
                }
                all_articles.append(processed_article)
            
            # Check if there are more pages
            cursor = data.get("message", {}).get("next-cursor")
            has_more = cursor and len(items) > 0
            
            # Add delay between requests to be respectful to the API
            if has_more:
                time.sleep(1)  # 1 second delay
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_count}: {e}")
            has_more = False
        except Exception as e:
            print(f"Unexpected error on page {page_count}: {e}")
            has_more = False
    
    return all_articles

def get_title(article: Dict) -> str:
    """Extract title from article data."""
    title = article.get("title", [])
    if isinstance(title, list) and title:
        return title[0]
    elif isinstance(title, str):
        return title
    return "No title available"

def get_published_year(article: Dict) -> Optional[int]:
    """Extract publication year from article data."""
    # Try published-print first, then published-online
    for date_field in ["published-print", "published-online"]:
        date_info = article.get(date_field, {})
        date_parts = date_info.get("date-parts", [])
        if date_parts and date_parts[0]:
            return date_parts[0][0]  # First element is the year
    return None

def generate_report(articles: List[Dict]) -> Dict:
    """
    Generate a comprehensive report of citation statistics.
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        Dictionary containing report statistics
    """
    print("\n" + "=" * 60)
    print("JOURNAL CITATION REPORT")
    print("=" * 60)
    
    # Basic statistics
    total_articles = len(articles)
    total_citations = sum(article["citation_count"] for article in articles)
    avg_citations = total_citations / total_articles if total_articles > 0 else 0
    
    print(f"Journal ISSN: {JOURNAL_ISSN}")
    print(f"Total Articles: {total_articles}")
    print(f"Total Citations: {total_citations}")
    print(f"Average Citations per Article: {avg_citations:.2f}")
    
    # Top 10 most cited articles
    top_cited = sorted(articles, key=lambda x: x["citation_count"], reverse=True)[:10]
    
    print(f"\nTOP 10 MOST CITED ARTICLES:")
    print("-" * 60)
    for i, article in enumerate(top_cited, 1):
        title = article["title"]
        if len(title) > 50:
            title = title[:50] + "..."
        
        print(f"{i}. [{article['citation_count']} citations] {title}")
        print(f"   DOI: {article['doi']}")
        if article["published_year"]:
            print(f"   Year: {article['published_year']}")
        print()
    
    # Citation distribution
    citation_ranges = {
        "0 citations": 0,
        "1-5 citations": 0,
        "6-10 citations": 0,
        "11-20 citations": 0,
        "21-50 citations": 0,
        "51+ citations": 0
    }
    
    for article in articles:
        count = article["citation_count"]
        if count == 0:
            citation_ranges["0 citations"] += 1
        elif count <= 5:
            citation_ranges["1-5 citations"] += 1
        elif count <= 10:
            citation_ranges["6-10 citations"] += 1
        elif count <= 20:
            citation_ranges["11-20 citations"] += 1
        elif count <= 50:
            citation_ranges["21-50 citations"] += 1
        else:
            citation_ranges["51+ citations"] += 1
    
    print("CITATION DISTRIBUTION:")
    print("-" * 30)
    for range_name, count in citation_ranges.items():
        percentage = (count / total_articles) * 100 if total_articles > 0 else 0
        print(f"{range_name}: {count} articles ({percentage:.1f}%)")
    
    # Year-based analysis if we have publication years
    articles_with_years = [a for a in articles if a["published_year"]]
    if articles_with_years:
        print(f"\nYEAR-BASED ANALYSIS:")
        print("-" * 30)
        year_stats = {}
        for article in articles_with_years:
            year = article["published_year"]
            if year not in year_stats:
                year_stats[year] = {"count": 0, "total_citations": 0}
            year_stats[year]["count"] += 1
            year_stats[year]["total_citations"] += article["citation_count"]
        
        for year in sorted(year_stats.keys()):
            stats = year_stats[year]
            avg_cites = stats["total_citations"] / stats["count"]
            print(f"{year}: {stats['count']} articles, {stats['total_citations']} total citations, {avg_cites:.1f} avg")
    
    return {
        "total_articles": total_articles,
        "total_citations": total_citations,
        "avg_citations": avg_citations,
        "top_cited": top_cited,
        "citation_ranges": citation_ranges,
        "all_articles": articles
    }

def export_to_csv(articles: List[Dict], filename: str = None) -> str:
    """
    Export article data to CSV file.
    
    Args:
        articles: List of article dictionaries
        filename: Optional filename, defaults to journal-citations-{issn}.csv
        
    Returns:
        The filename that was created
    """
    if filename is None:
        filename = f"journal-citations-{JOURNAL_ISSN.replace('-', '')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['DOI', 'Title', 'Citations', 'Year']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for article in articles:
            writer.writerow({
                'DOI': article['doi'],
                'Title': article['title'],
                'Citations': article['citation_count'],
                'Year': article['published_year'] or 'Unknown'
            })
    
    print(f"\nData exported to: {filename}")
    return filename

def export_to_json(articles: List[Dict], filename: str = None) -> str:
    """
    Export article data to JSON file.
    
    Args:
        articles: List of article dictionaries
        filename: Optional filename, defaults to journal-citations-{issn}.json
        
    Returns:
        The filename that was created
    """
    if filename is None:
        filename = f"journal-citations-{JOURNAL_ISSN.replace('-', '')}.json"
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(articles, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"Data exported to: {filename}")
    return filename

def main():
    """Main function to run the citation analysis."""
    try:
        print("CrossRef Journal Citation Counter")
        print("=" * 40)
        
        # Validate configuration
        if JOURNAL_ISSN == "1234-5678" or YOUR_EMAIL == "your-email@example.com":
            print("⚠️  Please update the JOURNAL_ISSN and YOUR_EMAIL variables at the top of the script!")
            return
        
        # Fetch all articles
        articles = fetch_all_articles(JOURNAL_ISSN)
        
        if not articles:
            print("No articles found for this ISSN. Please check the ISSN and try again.")
            return
        
        # Generate report
        report_data = generate_report(articles)
        
        # Export data
        export_choice = input("\nExport data? (csv/json/both/no): ").lower().strip()
        
        if export_choice in ['csv', 'both']:
            export_to_csv(articles)
        
        if export_choice in ['json', 'both']:
            export_to_json(articles)
        
        print(f"\n✅ Analysis complete! Found {len(articles)} articles with {sum(a['citation_count'] for a in articles)} total citations.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()