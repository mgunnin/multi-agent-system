"""Pitch creation and optimization tools for Vertical Labs crews."""

from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class TopicInfo(BaseModel):
    """Topic information schema."""
    title: str = Field(description="Title of the topic")
    category: str = Field(description="Category of the topic")
    trend: Optional[str] = Field(default="", description="Related trend")
    description: Optional[str] = Field(default="", description="Topic description")


class BrandInfo(BaseModel):
    """Brand information schema."""
    name: str = Field(description="Brand name")
    category: str = Field(description="Brand category")
    expert_name: Optional[str] = Field(default="", description="Expert name")
    target_audience: str = Field(description="Target audience")
    locations: Set[str] = Field(default_factory=set, description="Target locations")


class PitchGeneratorSchema(BaseModel):
    """Schema for PitchGeneratorTool arguments."""
    topic: TopicInfo = Field(description="Topic information")
    brand_info: BrandInfo = Field(description="Brand information")


class PublisherInfo(BaseModel):
    """Publisher information schema."""
    name: str = Field(description="Publisher name")
    audience: str = Field(description="Target audience")
    locations: Set[str] = Field(default_factory=set, description="Coverage locations")
    prefers_brevity: Optional[bool] = Field(default=False, description="Prefers brief pitches")
    requires_data: Optional[bool] = Field(default=False, description="Requires data points")


class BrandMatchingSchema(BaseModel):
    """Schema for BrandMatchingTool arguments."""
    brand: BrandInfo = Field(description="Brand information")
    topics: List[TopicInfo] = Field(description="Available topics")
    publishers: List[PublisherInfo] = Field(description="Target publishers")


class PitchContent(BaseModel):
    """Pitch content schema."""
    subject_line: str = Field(description="Email subject line")
    pitch_body: Dict = Field(description="Main pitch content")
    value_proposition: str = Field(description="Value proposition")
    call_to_action: str = Field(description="Call to action")


class PitchOptimizationSchema(BaseModel):
    """Schema for PitchOptimizationTool arguments."""
    pitch: PitchContent = Field(description="Pitch to optimize")
    publisher_data: PublisherInfo = Field(description="Publisher preferences and history")


class PitchGeneratorTool(BaseTool):
    """Tool for generating PR pitches based on topics."""

    name: str = "pitch_generator_tool"
    description: str = "Generates PR pitches based on topics and brand information"
    args_schema: type[PitchGeneratorSchema] = PitchGeneratorSchema

    def _run(self, topic: TopicInfo, brand_info: BrandInfo) -> Dict:
        return self._execute(topic.model_dump(), brand_info.model_dump())

    def _execute(self, topic: Dict, brand_info: Dict) -> Dict:
        """Run the tool to generate a pitch."""
        return {
            "subject_line": self._generate_subject_line(topic, brand_info),
            "pitch_body": self._generate_pitch_body(topic, brand_info),
            "value_proposition": self._generate_value_prop(topic, brand_info),
            "call_to_action": self._generate_cta(topic, brand_info),
        }

    def _generate_subject_line(self, topic: Dict, brand_info: Dict) -> str:
        """Generate an attention-grabbing subject line."""
        return f"Story Idea: {topic['title']} - Expert Insights from {brand_info['name']}"

    def _generate_pitch_body(self, topic: Dict, brand_info: Dict) -> Dict:
        """Generate the main pitch content."""
        return {
            "hook": f"Given the recent {topic.get('trend', 'developments')}...",
            "context": "Market context and relevance",
            "brand_angle": f"How {brand_info['name']} fits in",
            "expert_bio": f"About {brand_info.get('expert_name', 'our expert')}",
        }

    def _generate_value_prop(self, topic: Dict, brand_info: Dict) -> str:
        """Generate the value proposition for the publisher."""
        return f"Unique insights on {topic['title']} from industry leader"

    def _generate_cta(self, topic: Dict, brand_info: Dict) -> str:
        """Generate a clear call to action."""
        return "Would you be interested in speaking with our expert?"


class BrandMatchingTool(BaseTool):
    """Tool for matching brands with relevant topics and publishers."""

    name: str = "brand_matching_tool"
    description: str = "Matches brands with relevant topics and publishers"
    args_schema: type[BrandMatchingSchema] = BrandMatchingSchema

    def _run(self, brand: BrandInfo, topics: List[TopicInfo], publishers: List[PublisherInfo]) -> Dict:
        return self._execute(
            brand.model_dump(),
            [t.model_dump() for t in topics],
            [p.model_dump() for p in publishers]
        )

    def _execute(self, brand: Dict, topics: List[Dict], publishers: List[Dict]) -> Dict:
        """Run the tool to find matches."""
        matches = {"high_priority": [], "medium_priority": [], "low_priority": []}

        for topic in topics:
            for publisher in publishers:
                score = self._calculate_match_score(brand, topic, publisher)
                match = {
                    "topic": topic,
                    "publisher": publisher,
                    "score": score,
                    "rationale": self._generate_match_rationale(brand, topic, publisher),
                }

                if score >= 0.8:
                    matches["high_priority"].append(match)
                elif score >= 0.6:
                    matches["medium_priority"].append(match)
                else:
                    matches["low_priority"].append(match)

        return matches

    def _calculate_match_score(self, brand: Dict, topic: Dict, publisher: Dict) -> float:
        """Calculate a match score between 0 and 1."""
        relevance_score = 0.5  # Base score

        # Check category match
        if brand["category"] == topic["category"]:
            relevance_score += 0.2

        # Check audience match
        if brand["target_audience"] == publisher["audience"]:
            relevance_score += 0.2

        # Check location match
        brand_locations = set(brand["locations"])
        publisher_locations = set(publisher["locations"])
        if brand_locations.intersection(publisher_locations):
            relevance_score += 0.1

        return min(relevance_score, 1.0)

    def _generate_match_rationale(self, brand: Dict, topic: Dict, publisher: Dict) -> str:
        """Generate explanation for the match."""
        return f"Match based on category alignment ({brand['category']}) and audience fit"


class PitchOptimizationTool(BaseTool):
    """Tool for optimizing pitches based on publisher preferences and history."""

    name: str = "pitch_optimization_tool"
    description: str = "Optimizes pitches based on publisher data and success metrics"
    args_schema: type[PitchOptimizationSchema] = PitchOptimizationSchema

    def _run(self, pitch: PitchContent, publisher_data: PublisherInfo) -> Dict:
        return self._execute(pitch.model_dump(), publisher_data.model_dump())

    def _execute(self, pitch: Dict, publisher_data: Dict) -> Dict:
        """Run the tool to optimize a pitch."""
        optimized = pitch.copy()
        recommendations = []

        # Analyze subject line
        subject_metrics = self._analyze_subject_line(pitch["subject_line"], publisher_data)
        if subject_metrics["length"] > 50:
            recommendations.append("Shorten subject line")

        # Analyze pitch body
        body_metrics = self._analyze_pitch_body(pitch["pitch_body"], publisher_data)
        if body_metrics["paragraphs"] > 4:
            recommendations.append("Reduce pitch length")

        # Apply publisher preferences
        optimized = self._apply_publisher_preferences(optimized, publisher_data)

        return {
            "optimized_pitch": optimized,
            "recommendations": recommendations,
            "metrics": {
                "subject_metrics": subject_metrics,
                "body_metrics": body_metrics,
            },
        }

    def _analyze_subject_line(self, subject: str, publisher_data: Dict) -> Dict:
        """Analyze subject line metrics."""
        return {
            "length": len(subject),
            "has_numbers": any(c.isdigit() for c in subject),
            "personalized": publisher_data["name"] in subject,
        }

    def _analyze_pitch_body(self, body: Dict, publisher_data: Dict) -> Dict:
        """Analyze pitch body metrics."""
        return {
            "paragraphs": len(body),
            "has_stats": "%" in str(body),
            "has_quotes": '"' in str(body),
        }

    def _apply_publisher_preferences(self, pitch: Dict, publisher_data: Dict) -> Dict:
        """Apply publisher-specific preferences to the pitch."""
        if publisher_data.get("prefers_brevity"):
            # Truncate content while preserving structure
            pitch["pitch_body"] = {k: v[:200] for k, v in pitch["pitch_body"].items()}

        if publisher_data.get("requires_data"):
            # Add placeholder for data point
            pitch["pitch_body"]["data_point"] = "Industry statistic..."

        return pitch