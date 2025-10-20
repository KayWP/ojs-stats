#!/usr/bin/env python3
"""
CrossRef Journal Citation Counter - Streamlit Web App
"""

import streamlit as st
import requests
import time
import csv
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Optional
from io import StringIO, BytesIO

# Page configuration
st.set_page_config(
    page_title="CrossRef Citation Counter",
    page_icon="📚",
    layout="wide"
)

# API Configuration
BASE_URL = "https://api.crossref.org/works"

def get_headers(email: str, app_name: str = "JournalCitationCounter/1.0") -> dict:
    """Generate headers for API requests."""
    return {"User-Agent": f"{app_name} (mailto:{email})"}

def fetch_all_articles(issn: str, email: str, progress_bar, status_text) -> List[Dict]:
    """Fetch all articles from a journal by ISSN."""
    all_articles = []
    cursor = "*"
    has_more = True
    page_count = 0
    
    headers = get_headers(email)
    
    while has_more:
        try:
            page_count += 1
            status_text.text(f"Fetching page {page_count}...")
            
            params = {
                "filter": f"issn:{issn}",
                "rows": "1000",
                "cursor": cursor,
                "select": "DOI,title,is-referenced-by-count,published-print,published-online"
            }
            
            response = requests.get(BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("message", {}).get("items", [])
            
            for article in items:
                processed_article = {
                    "doi": article.get("DOI", ""),
                    "title": get_title(article),
                    "citation_count": article.get("is-referenced-by-count", 0),
                    "published_year": get_published_year(article)
                }
                all_articles.append(processed_article)
            
            cursor = data.get("message", {}).get("next-cursor")
            has_more = cursor and len(items) > 0
            
            progress_bar.progress(min(page_count / 10, 1.0))
            
            if has_more:
                time.sleep(1)
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching page {page_count}: {e}")
            has_more = False
        except Exception as e:
            st.error(f"Unexpected error on page {page_count}: {e}")
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
    for date_field in ["published-print", "published-online"]:
        date_info = article.get(date_field, {})
        date_parts = date_info.get("date-parts", [])
        if date_parts and date_parts[0]:
            return date_parts[0][0]
    return None

def create_citation_distribution_chart(articles: List[Dict]) -> go.Figure:
    """Create a bar chart for citation distribution."""
    citation_ranges = {
        "0": 0,
        "1-5": 0,
        "6-10": 0,
        "11-20": 0,
        "21-50": 0,
        "51+": 0
    }
    
    for article in articles:
        count = article["citation_count"]
        if count == 0:
            citation_ranges["0"] += 1
        elif count <= 5:
            citation_ranges["1-5"] += 1
        elif count <= 10:
            citation_ranges["6-10"] += 1
        elif count <= 20:
            citation_ranges["11-20"] += 1
        elif count <= 50:
            citation_ranges["21-50"] += 1
        else:
            citation_ranges["51+"] += 1
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(citation_ranges.keys()),
            y=list(citation_ranges.values()),
            marker_color='#1f77b4'
        )
    ])
    
    fig.update_layout(
        title="Citation Distribution",
        xaxis_title="Citation Range",
        yaxis_title="Number of Articles",
        height=400
    )
    
    return fig

def create_year_chart(articles: List[Dict]) -> go.Figure:
    """Create a chart showing publications and citations by year."""
    articles_with_years = [a for a in articles if a["published_year"]]
    
    if not articles_with_years:
        return None
    
    year_stats = {}
    for article in articles_with_years:
        year = article["published_year"]
        if year not in year_stats:
            year_stats[year] = {"count": 0, "total_citations": 0}
        year_stats[year]["count"] += 1
        year_stats[year]["total_citations"] += article["citation_count"]
    
    years = sorted(year_stats.keys())
    counts = [year_stats[y]["count"] for y in years]
    citations = [year_stats[y]["total_citations"] for y in years]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=counts,
        name="Articles Published",
        marker_color='#2ca02c'
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=citations,
        name="Total Citations",
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title="Publications and Citations by Year",
        xaxis_title="Year",
        yaxis_title="Count",
        barmode='group',
        height=400
    )
    
    return fig

def main():
    st.title("📚 CrossRef Journal Citation Counter")
    st.markdown("Analyze citation metrics for your journal using the CrossRef API")
    fetched_info = False
    
    # Sidebar for inputs
    if not fetched_info:
        st.header("Configuration")
        issn = st.text_input(
            "Journal ISSN",
            value="xxxx-xxxx",
            help="Enter the ISSN of the journal (e.g., 0167-9228)"
        )

        email = st.text_input(
            "Your Email",
            value="example@example.nl",
            help="Required to request data from CrossRef"
        )

        fetch_button = st.button("🔍 Fetch Articles", type="primary")
    
    # Main content area
    if fetch_button:
        if not issn or not email or "@" not in email:
            st.error("Please provide a valid ISSN and email address.")
            return
        
        with st.spinner("Fetching articles from CrossRef..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            articles = fetch_all_articles(issn, email, progress_bar, status_text)
            
            progress_bar.empty()
            status_text.empty()
        
        if not articles:
            st.warning("No articles found for this ISSN. Please check the ISSN and try again.")
            return
        
        # Store in session state
        st.session_state['articles'] = articles
        st.session_state['issn'] = issn
        fetched_info = True
    
    # Display results if we have data
    if 'articles' in st.session_state:
        articles = st.session_state['articles']
        issn = st.session_state['issn']
        
        # Key metrics
        total_articles = len(articles)
        total_citations = sum(article["citation_count"] for article in articles)
        avg_citations = total_citations / total_articles if total_articles > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Articles", f"{total_articles:,}")
        
        with col2:
            st.metric("Total Citations", f"{total_citations:,}")
        
        with col3:
            st.metric("Avg Citations/Article", f"{avg_citations:.2f}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_citation_distribution_chart(articles)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            year_fig = create_year_chart(articles)
            if year_fig:
                st.plotly_chart(year_fig, use_container_width=True)
            else:
                st.info("No publication year data available for visualization.")
        
        st.markdown("---")
        
        # Top cited articles
        st.subheader("🏆 Top 10 Most Cited Articles")
        
        top_cited = sorted(articles, key=lambda x: x["citation_count"], reverse=True)[:10]
        
        for i, article in enumerate(top_cited, 1):
            with st.expander(f"#{i} - {article['title'][:80]}{'...' if len(article['title']) > 80 else ''}"):
                st.markdown(f"**Citations:** {article['citation_count']}")
                st.markdown(f"**DOI:** [{article['doi']}](https://doi.org/{article['doi']})")
                if article['published_year']:
                    st.markdown(f"**Year:** {article['published_year']}")
        
        st.markdown("---")
        
        # Full data table
        st.subheader("📊 All Articles")
        
        df = pd.DataFrame(articles)
        df = df.rename(columns={
            'doi': 'DOI',
            'title': 'Title',
            'citation_count': 'Citations',
            'published_year': 'Year'
        })
        df = df.sort_values('Citations', ascending=False)
        
        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            column_config={
                "DOI": st.column_config.LinkColumn(
                    "DOI",
                    help="Click to view article",
                    display_text="View"
                )
            }
        )
        
        # Export options
        st.markdown("---")
        st.subheader("💾 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"journal-citations-{issn.replace('-', '')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # JSON export
            json_data = json.dumps(articles, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"journal-citations-{issn.replace('-', '')}.json",
                mime="application/json",
                use_container_width=True
            )

if __name__ == "__main__":
    main()