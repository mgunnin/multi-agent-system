import os
from typing import Dict

import requests
from crewai.tools import BaseTool


class DiffbotWebsiteAnalysis(BaseTool):
    """Tool for analyzing website content using Diffbot."""

    name: str = "website_analyzer_tool"
    description: str = (
        "Analyzes website content to extract key information and insights"
    )

    def _run(self, url: str) -> Dict:
        return self._execute(url)

    def _execute(self, url: str) -> Dict:
        """Run the tool to analyze a website.

        Args:
            url: Website URL to analyze

        Returns:
            Dictionary with website analysis results
        """
        api_token = os.getenv("DIFFBOT_API_TOKEN")
        if not api_token:
            raise ValueError("DIFFBOT_API_TOKEN environment variable not set")

        diffbot_url = f"https://api.diffbot.com/v3/analyze?token={api_token}&url={url}"
        response = requests.get(diffbot_url)
        return response.json()


# DiffbotTool
class DiffbotContentAnalyzer(BaseTool):
    name: str = "Content Analyzer"
    description: str = "Analyzes content using Diffbot API"

    def _run(self, url: str) -> Dict:
        """
        Analyzes content using Diffbot API

        Args:
            url (str): URL to analyze

        Returns:
            Dict: Content analysis results
        """
        headers = {"Authorization": f'Token {os.environ["DIFFBOT_API_KEY"]}'}

        response = requests.get(
            f"https://api.diffbot.com/v3/analyze?url={url}", headers=headers
        )
        return response.json()
