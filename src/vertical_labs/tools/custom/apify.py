import os
from typing import Dict, List

import requests
from crewai.tools import BaseTool


class ApifyNewsScraper(BaseTool):
    """Tool for fetching news using Ultimate News Scraper."""

    name: str = "apify_news_scraper"
    description: str = "Fetches news articles based on keywords and date range"

    def _run(self, keywords: List[str], start_date: str, end_date: str) -> List[Dict]:
        return self._execute(keywords, start_date, end_date)

    def _execute(
        self, keywords: List[str], start_date: str, end_date: str
    ) -> List[Dict]:
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
        response = requests.post(
            url, json={"keywords": keywords, "dateFrom": start_date, "dateTo": end_date}
        )
        return response.json()


class ApifyTwitterTrendsScraper(BaseTool):
    """Tool for fetching Twitter trends using Apify API."""

    name: str = "apify_twitter_trends_scraper"
    description: str = "Fetches trending topics from Twitter for a specific country"

    def _run(self, country: str = "USA") -> List[Dict]:
        return self._execute(country)

    def _execute(self, country: str = "USA") -> List[Dict]:
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


# UltimateNewsTool
class ApifyUltimateNewsTool(BaseTool):
    name: str = "Recent News Fetcher"
    description: str = "Fetches recent news using Ultimate News Scraper"

    def _run(self, date_range: str) -> Dict:
        """
        Fetches recent news using Ultimate News Scraper
        Args:
            date_range (str): Date range in format YYYY-MM-DD/YYYY-MM-DD
        Returns:
            Dict: Recent news articles and their metadata
        """
        headers = {"Authorization": f'Bearer {os.environ["APIFY_API_KEY"]}'}

        response = requests.post(
            "https://api.apify.com/v2/acts/glitch_404~ultimate-news-scraper/runs",
            headers=headers,
            json={"dateRange": date_range},
        )
        return response.json()
