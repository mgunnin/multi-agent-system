"""News and trends tools for Vertical Labs crews."""

from typing import Dict, List, Optional
from langchain.tools import BaseTool
import requests
import os

class TwitterTrendsTool(BaseTool):
    """Tool for fetching Twitter trends using Apify API."""
    
    name = "twitter_trends_tool"
    description = "Fetches trending topics from Twitter for a specific country"

    def _run(self, country: str = "USA") -> List[Dict]:
        """Run the tool to get Twitter trends.
        
        Args:
            country: Country to get trends for (default: USA)
            
        Returns:
            List of trends with hashtag, volume and date
        """
        api_token = os.getenv("APIFY_API_TOKEN")
        if not api_token:
            raise ValueError("APIFY_API_TOKEN environment variable not set")
            
        url = f"https://api.apify.com/v2/acts/karamelo~twitter-trends-scraper/run-sync-get-dataset-items?token={api_token}"
        response = requests.post(url, json={"country": country})
        return response.json()

class NewsScraperTool(BaseTool):
    """Tool for fetching news using Ultimate News Scraper."""
    
    name = "news_scraper_tool"
    description = "Fetches news articles based on keywords and date range"

    def _run(self, keywords: List[str], start_date: str, end_date: str) -> List[Dict]:
        """Run the tool to get news articles.
        
        Args:
            keywords: List of keywords to search for
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of news articles with title, summary, source, etc.
        """
        api_token = os.getenv("APIFY_API_TOKEN")
        if not api_token:
            raise ValueError("APIFY_API_TOKEN environment variable not set")
            
        url = f"https://api.apify.com/v2/acts/glitch_404~ultimate-news-scraper/run-sync-get-dataset-items?token={api_token}"
        response = requests.post(url, json={
            "keywords": keywords,
            "dateFrom": start_date,
            "dateTo": end_date
        })
        return response.json()

class GoogleNewsTool(BaseTool):
    """Tool for fetching news from Google News using DataForSEO."""
    
    name = "google_news_tool"
    description = "Fetches news articles from Google News for a specific keyword"

    def _run(self, keyword: str) -> List[Dict]:
        """Run the tool to get Google News articles.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of news articles with title, summary, source URL
        """
        api_login = os.getenv("DATAFORSEO_LOGIN")
        api_password = os.getenv("DATAFORSEO_PASSWORD")
        if not api_login or not api_password:
            raise ValueError("DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD environment variables not set")
            
        url = "https://api.dataforseo.com/v3/serp/google/news/live/advanced"
        auth = (api_login, api_password)
        data = {
            "keyword": keyword,
            "location_name": "United States",
            "language_name": "English"
        }
        response = requests.post(url, auth=auth, json=data)
        return response.json().get("tasks", [])