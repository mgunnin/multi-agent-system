import os
from typing import Dict, List

import requests
from crewai.tools import BaseTool


class DataForSEOGoogleNews(BaseTool):
    """Tool for fetching news from Google News using DataForSEO."""

    name: str = "dataforseo_google_news"
    description: str = "Fetches news articles from Google News for a specific keyword"

    def _run(self, keyword: str) -> List[Dict]:
        return self._execute(keyword)

    def _execute(self, keyword: str) -> List[Dict]:
        """Run the tool to get Google News articles.

        Args:
            keyword: Keyword to search for

        Returns:
            List of news articles with title, summary, source URL
        """
        api_login = os.getenv("DATAFORSEO_LOGIN")
        api_password = os.getenv("DATAFORSEO_PASSWORD")
        if not api_login or not api_password:
            raise ValueError(
                "DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD environment variables not set"
            )

        url = "https://api.dataforseo.com/v3/serp/google/news/live/advanced"
        auth = (api_login, api_password)
        data = {
            "keyword": keyword,
            "location_name": "United States",
            "language_name": "English",
        }
        response = requests.post(url, auth=auth, json=data)
        return response.json().get("tasks", [])


class DataForSEOToolGoogleNewsV2(BaseTool):
    name: str = "News Article Fetcher"
    description: str = "Fetches news articles using DataForSEO API"

    def _run(self, keyword: str) -> Dict:
        """
        Fetches news articles using DataForSEO API
        Args:
            keyword (str): Keyword to search for
        Returns:
            Dict: News articles and their metadata
        """
        headers = {"Authorization": f'Basic {os.environ["DATAFORSEO_API_KEY"]}'}

        response = requests.post(
            "https://api.dataforseo.com/v3/serp/google/news/live/advanced",
            headers=headers,
            json={"keyword": keyword, "language_code": "en", "location_code": 2840},
        )
        return response.json()
