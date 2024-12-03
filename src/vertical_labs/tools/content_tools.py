"""Content analysis and generation tools for Vertical Labs crews."""

import os
from typing import Dict, List, Optional

import requests
from langchain.tools import BaseTool


class WebsiteAnalyzerTool(BaseTool):
    """Tool for analyzing website content using Diffbot."""

    name = "website_analyzer_tool"
    description = "Analyzes website content to extract key information and insights"

    def _run(self, url: str) -> Dict:
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

class EditorialGuidelinesTool(BaseTool):
    """Tool for generating and managing editorial guidelines."""

    name = "editorial_guidelines_tool"
    description = "Generates and manages editorial guidelines for publishers"

    def _run(self, publisher_info: Dict) -> Dict:
        """Run the tool to generate editorial guidelines.

        Args:
            publisher_info: Dictionary with publisher information including:
                - name: Publisher name
                - type: Type of business
                - categories: Content categories
                - audience: Target audience
                - locations: Target locations

        Returns:
            Dictionary with generated editorial guidelines
        """
        # This would typically use an LLM to generate guidelines
        # For now returning a template
        return {
            "tone_of_voice": self._generate_tone_guidelines(publisher_info),
            "content_structure": self._generate_structure_guidelines(publisher_info),
            "style_rules": self._generate_style_rules(publisher_info),
            "seo_guidelines": self._generate_seo_guidelines(publisher_info)
        }

    def _generate_tone_guidelines(self, info: Dict) -> Dict:
        """Generate tone of voice guidelines based on publisher info."""
        return {
            "formality": "professional" if info["type"] == "B2B" else "conversational",
            "personality": "authoritative" if info["type"] == "B2B" else "friendly",
            "language": "technical" if info["type"] == "B2B" else "simple"
        }

    def _generate_structure_guidelines(self, info: Dict) -> Dict:
        """Generate content structure guidelines."""
        return {
            "sections": ["introduction", "main points", "examples", "conclusion"],
            "paragraph_length": "2-3 sentences",
            "total_length": "800-1200 words"
        }

    def _generate_style_rules(self, info: Dict) -> Dict:
        """Generate writing style rules."""
        return {
            "active_voice": True,
            "oxford_comma": True,
            "numbers": "spell out one through nine",
            "abbreviations": "define on first use"
        }

    def _generate_seo_guidelines(self, info: Dict) -> Dict:
        """Generate SEO guidelines."""
        return {
            "keyword_density": "1-2%",
            "meta_description": "150-160 characters",
            "title_length": "50-60 characters",
            "heading_structure": "one H1, multiple H2s and H3s"
        }

class ContentDiversityTool(BaseTool):
    """Tool for ensuring content diversity and originality."""

    name = "content_diversity_tool"
    description = "Analyzes content to ensure diversity and avoid duplication"

    def _run(self, content_list: List[Dict], existing_content: Optional[List[Dict]] = None) -> Dict:
        """Run the tool to analyze content diversity.

        Args:
            content_list: List of content items to analyze
            existing_content: Optional list of existing content to check against

        Returns:
            Dictionary with diversity analysis results
        """
        results = {
            "duplicate_topics": [],
            "topic_clusters": {},
            "diversity_score": 0.0,
            "recommendations": []
        }

        # Analyze topic diversity
        topics = [content["topic"] for content in content_list]
        unique_topics = set(topics)
        results["diversity_score"] = len(unique_topics) / len(topics)

        # Check for duplicates with existing content
        if existing_content:
            existing_topics = [content["topic"] for content in existing_content]
            duplicates = set(topics).intersection(existing_topics)
            results["duplicate_topics"] = list(duplicates)

        # Add recommendations
        if results["diversity_score"] < 0.8:
            results["recommendations"].append("Increase topic variety")
        if len(results["duplicate_topics"]) > 0:
            results["recommendations"].append("Remove duplicate topics")

        return results
