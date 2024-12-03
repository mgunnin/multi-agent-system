"""Content analysis and generation tools for Vertical Labs crews."""

from typing import Dict, List, Optional, Union

from crewai.tools import BaseTool, Tool


class EditorialGuidelinesTool(BaseTool):
    """Tool for generating and managing editorial guidelines."""

    name: str = "editorial_guidelines_tool"
    description: str = "Generates and manages editorial guidelines for publishers"
    args_schema: Dict = {
        "publisher_info": {
            "type": "dict",
            "description": "Dictionary with publisher information",
            "required": True,
            "schema": {
                "name": {"type": "string", "required": False},
                "type": {"type": "string", "required": False},
                "categories": {"type": "list", "required": False},
                "audience": {"type": "string", "required": False},
                "locations": {"type": "list", "required": False}
            }
        }
    }

    def _run(self, publisher_info: Dict) -> Dict:
        """Run the tool with proper error handling."""
        # Ensure publisher_info has default values
        publisher_info = self._sanitize_publisher_info(publisher_info)
        return self._execute(publisher_info)

    def _sanitize_publisher_info(self, publisher_info: Dict) -> Dict:
        """Ensure all required fields exist with default values."""
        defaults = {
            "name": "Generic Publisher",
            "type": "B2C",
            "categories": [],
            "audience": "general",
            "locations": ["global"]
        }
        
        if not publisher_info:
            return defaults
            
        # Merge provided info with defaults for missing fields
        return {
            **defaults,
            **{k: v for k, v in publisher_info.items() if v is not None}
        }

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


class ContentDiversityTool(BaseTool):
    """Tool for ensuring content diversity and originality."""

    name: str = "content_diversity_tool"
    description: str = "Analyzes content to ensure diversity and avoid duplication"
    args_schema: Dict = {
        "content_list": {
            "type": "list",
            "description": "List of content items to analyze. Each item should be a dictionary containing at least a 'topic' field.",
            "required": True,
            "schema": {
                "type": "dict",
                "schema": {
                    "topic": {"type": "string", "required": True},
                    "content": {"type": "string", "required": False},
                    "metadata": {"type": "dict", "required": False}
                }
            }
        },
        "existing_content": {
            "type": "list",
            "description": "Optional list of existing content items to check against. Each item should follow the same schema as content_list.",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "topic": {"type": "string", "required": True},
                    "content": {"type": "string", "required": False},
                    "metadata": {"type": "dict", "required": False}
                }
            }
        }
    }

    def _run(
        self, content_list: List[Dict], existing_content: Optional[List[Dict]] = None
    ) -> Dict:
        """Run the tool with proper error handling."""
        # Validate and sanitize inputs
        content_list = self._sanitize_content_list(content_list)
        if existing_content:
            existing_content = self._sanitize_content_list(existing_content)
        return self._execute(content_list, existing_content)

    def _sanitize_content_list(self, content_list: List[Dict]) -> List[Dict]:
        """Ensure all content items have required fields."""
        if not content_list:
            return []

        sanitized_list = []
        for item in content_list:
            if isinstance(item, dict):
                # Ensure each item has at least a topic
                sanitized_item = {
                    "topic": item.get("topic", "Untitled"),
                    "content": item.get("content", ""),
                    "metadata": item.get("metadata", {})
                }
                sanitized_list.append(sanitized_item)
            else:
                # If item is not a dict, create a minimal valid item
                sanitized_list.append({
                    "topic": "Untitled",
                    "content": "",
                    "metadata": {}
                })
        return sanitized_list

    def _execute(
        self, content_list: List[Dict], existing_content: Optional[List[Dict]] = None
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
        topics = [item["topic"] for item in content_list]
        unique_topics = set(topics)
        results["diversity_score"] = len(unique_topics) / len(topics) if topics else 0.0

        # Check for duplicates with existing content
        if existing_content:
            existing_topics = [item["topic"] for item in existing_content]
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
        # Simple clustering based on common words
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