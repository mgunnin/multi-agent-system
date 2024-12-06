"""Content analysis and generation tools for Vertical Labs crews."""

from typing import Dict, List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PublisherInfo(BaseModel):
    """Publisher information schema."""

    name: Optional[str] = Field(
        default="Generic Publisher", description="Publisher name"
    )
    type: Optional[str] = Field(
        default="B2C", description="Type of business (B2B or B2C)"
    )
    categories: Optional[List[str]] = Field(
        default_factory=list, description="Content categories"
    )
    audience: Optional[str] = Field(default="general", description="Target audience")
    locations: Optional[List[str]] = Field(
        default_factory=lambda: ["global"], description="Target locations"
    )


class EditorialGuidelinesSchema(BaseModel):
    """Schema for EditorialGuidelinesTool arguments."""

    publisher_info: PublisherInfo = Field(
        description="Dictionary with publisher information including name, type, categories, audience, and locations"
    )


class EditorialGuidelinesTool(BaseTool):
    """Tool for generating and managing editorial guidelines."""

    name: str = "editorial_guidelines_tool"
    description: str = "Generates and manages editorial guidelines for publishers"
    args_schema: type[EditorialGuidelinesSchema] = EditorialGuidelinesSchema

    def _run(self, publisher_info: PublisherInfo) -> Dict:
        """Run the tool with proper error handling."""
        return self._execute(publisher_info.model_dump())

    def _execute(self, publisher_info: Dict) -> Dict:
        """Run the tool to generate editorial guidelines."""
        return {
            "tone_of_voice": self._generate_tone_guidelines(publisher_info),
            "content_structure": self._generate_structure_guidelines(publisher_info),
            "style_rules": self._generate_style_rules(publisher_info),
            "seo_guidelines": self._generate_seo_guidelines(publisher_info),
        }

    def _generate_tone_guidelines(self, info: Dict) -> Dict:
        """Generate tone of voice guidelines based on publisher info."""
        return {
            "formality": "professional" if info["type"] == "B2B" else "conversational",
            "personality": "authoritative" if info["type"] == "B2B" else "friendly",
            "language": "technical" if info["type"] == "B2B" else "simple",
        }

    def _generate_structure_guidelines(self, info: Dict) -> Dict:
        """Generate content structure guidelines."""
        return {
            "sections": ["introduction", "main points", "examples", "conclusion"],
            "paragraph_length": "2-3 sentences",
            "total_length": "800-1200 words",
        }

    def _generate_style_rules(self, info: Dict) -> Dict:
        """Generate writing style rules."""
        return {
            "active_voice": True,
            "oxford_comma": True,
            "numbers": "spell out one through nine",
            "abbreviations": "define on first use",
        }

    def _generate_seo_guidelines(self, info: Dict) -> Dict:
        """Generate SEO guidelines."""
        return {
            "keyword_density": "1-2%",
            "meta_description": "150-160 characters",
            "title_length": "50-60 characters",
            "heading_structure": "one H1, multiple H2s and H3s",
        }


class ContentItem(BaseModel):
    """Content item schema."""

    title: str = Field(description="The title of the content")
    content: Optional[str] = Field(default="", description="The content text")
    metadata: Optional[Dict] = Field(
        default_factory=dict, description="Additional metadata about the content"
    )

    @property
    def topic(self) -> str:
        """Get the topic from the title."""
        return self.title


class ContentDiversitySchema(BaseModel):
    """Schema for ContentDiversityTool arguments."""

    content_list: List[ContentItem] = Field(
        description="List of content items to analyze"
    )
    existing_content: Optional[List[ContentItem]] = Field(
        default=None, description="Optional list of existing content to check against"
    )


class ContentDiversityTool(BaseTool):
    """Tool for ensuring content diversity and originality."""

    name: str = "content_diversity_tool"
    description: str = "Analyzes content to ensure diversity and avoid duplication"
    args_schema: type[ContentDiversitySchema] = ContentDiversitySchema

    def _run(
        self,
        content_list: List[ContentItem],
        existing_content: Optional[List[ContentItem]] = None,
    ) -> Dict:
        """Run the tool with proper error handling."""
        return self._execute(content_list, existing_content)

    def _execute(
        self,
        content_list: List[ContentItem],
        existing_content: Optional[List[ContentItem]] = None,
    ) -> Dict:
        """Run the tool to analyze content diversity."""
        results = {
            "duplicate_topics": [],
            "topic_clusters": {},
            "diversity_score": 0.0,
            "recommendations": [],
        }

        if not content_list:
            results["recommendations"].append("No content provided for analysis")
            return results

        # Analyze topic diversity
        topics = [item.topic for item in content_list]
        unique_topics = set(topics)
        results["diversity_score"] = len(unique_topics) / len(topics) if topics else 0.0

        # Check for duplicates with existing content
        if existing_content:
            existing_topics = [item.topic for item in existing_content]
            duplicates = set(topics).intersection(existing_topics)
            results["duplicate_topics"] = list(duplicates)

        # Group similar topics into clusters
        results["topic_clusters"] = self._cluster_topics(topics)

        # Generate recommendations
        if results["diversity_score"] < 0.8:
            results["recommendations"].append("Increase topic variety")
        if results["duplicate_topics"]:
            results["recommendations"].append("Remove duplicate topics")
        if len(results["topic_clusters"]) < len(topics) / 2:
            results["recommendations"].append("Diversify topic areas")

        return results

    def _cluster_topics(self, topics: List[str]) -> Dict[str, List[str]]:
        """Group similar topics into clusters."""
        clusters = {}
        for topic in topics:
            words = set(topic.lower().split())
            assigned = False
            for cluster_name, cluster_topics in clusters.items():
                cluster_words = set(cluster_name.lower().split())
                if len(words.intersection(cluster_words)) > 0:
                    cluster_topics.append(topic)
                    assigned = True
                    break
            if not assigned:
                clusters[topic] = [topic]
        return clusters
