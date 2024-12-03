"""Pitch creation and optimization tools for Vertical Labs crews."""

from typing import Dict, List, Optional
from langchain.tools import BaseTool
import json
import os

class PitchGeneratorTool(BaseTool):
    """Tool for generating PR pitches based on topics."""
    
    name = "pitch_generator_tool"
    description = "Generates PR pitches based on topics and brand information"

    def _run(self, topic: Dict, brand_info: Dict) -> Dict:
        """Run the tool to generate a pitch.
        
        Args:
            topic: Dictionary with topic information
            brand_info: Dictionary with brand information
            
        Returns:
            Dictionary with generated pitch
        """
        # This would typically use an LLM to generate the pitch
        # For now returning a template structure
        return {
            "subject_line": self._generate_subject_line(topic, brand_info),
            "pitch_body": self._generate_pitch_body(topic, brand_info),
            "value_proposition": self._generate_value_prop(topic, brand_info),
            "call_to_action": self._generate_cta(topic, brand_info)
        }
        
    def _generate_subject_line(self, topic: Dict, brand_info: Dict) -> str:
        """Generate an attention-grabbing subject line."""
        return f"Story Idea: {topic['title']} - Expert Insights from {brand_info['name']}"
        
    def _generate_pitch_body(self, topic: Dict, brand_info: Dict) -> Dict:
        """Generate the main pitch content."""
        return {
            "hook": f"Given the recent {topic['trend']}...",
            "context": "Market context and relevance",
            "brand_angle": f"How {brand_info['name']} fits in",
            "expert_bio": f"About {brand_info['expert_name']}"
        }
        
    def _generate_value_prop(self, topic: Dict, brand_info: Dict) -> str:
        """Generate the value proposition for the publisher."""
        return f"Unique insights on {topic['title']} from industry leader"
        
    def _generate_cta(self, topic: Dict, brand_info: Dict) -> str:
        """Generate a clear call to action."""
        return "Would you be interested in speaking with our expert?"

class BrandMatchingTool(BaseTool):
    """Tool for matching brands with relevant topics and publishers."""
    
    name = "brand_matching_tool"
    description = "Matches brands with relevant topics and publishers"

    def _run(self, brand: Dict, topics: List[Dict], publishers: List[Dict]) -> Dict:
        """Run the tool to find matches.
        
        Args:
            brand: Dictionary with brand information
            topics: List of available topics
            publishers: List of publishers
            
        Returns:
            Dictionary with matching results
        """
        matches = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        for topic in topics:
            for publisher in publishers:
                score = self._calculate_match_score(brand, topic, publisher)
                match = {
                    "topic": topic,
                    "publisher": publisher,
                    "score": score,
                    "rationale": self._generate_match_rationale(brand, topic, publisher)
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
        # This would use more sophisticated scoring in production
        relevance_score = 0.5  # Base score
        
        # Check category match
        if brand["category"] == topic["category"]:
            relevance_score += 0.2
            
        # Check audience match
        if brand["target_audience"] == publisher["audience"]:
            relevance_score += 0.2
            
        # Check location match
        if brand["locations"].intersection(publisher["locations"]):
            relevance_score += 0.1
            
        return min(relevance_score, 1.0)
        
    def _generate_match_rationale(self, brand: Dict, topic: Dict, publisher: Dict) -> str:
        """Generate explanation for the match."""
        return f"Match based on category alignment ({brand['category']}) and audience fit"

class PitchOptimizationTool(BaseTool):
    """Tool for optimizing pitches based on publisher preferences and history."""
    
    name = "pitch_optimization_tool"
    description = "Optimizes pitches based on publisher data and success metrics"

    def _run(self, pitch: Dict, publisher_data: Dict) -> Dict:
        """Run the tool to optimize a pitch.
        
        Args:
            pitch: Dictionary with pitch content
            publisher_data: Dictionary with publisher preferences and history
            
        Returns:
            Dictionary with optimized pitch and recommendations
        """
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
                "body_metrics": body_metrics
            }
        }
        
    def _analyze_subject_line(self, subject: str, publisher_data: Dict) -> Dict:
        """Analyze subject line metrics."""
        return {
            "length": len(subject),
            "has_numbers": any(c.isdigit() for c in subject),
            "personalized": publisher_data["name"] in subject
        }
        
    def _analyze_pitch_body(self, body: Dict, publisher_data: Dict) -> Dict:
        """Analyze pitch body metrics."""
        return {
            "paragraphs": len(body),
            "has_stats": "%" in str(body),
            "has_quotes": '"' in str(body)
        }
        
    def _apply_publisher_preferences(self, pitch: Dict, publisher_data: Dict) -> Dict:
        """Apply publisher-specific preferences to the pitch."""
        if publisher_data.get("prefers_brevity"):
            # Truncate content
            pitch["pitch_body"] = {k: v[:200] for k, v in pitch["pitch_body"].items()}
            
        if publisher_data.get("requires_data"):
            # Add placeholder for data point
            pitch["pitch_body"]["data_point"] = "Industry statistic..."
            
        return pitch