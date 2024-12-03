"""Main orchestrator for Vertical Labs crews."""

from typing import Dict

from vertical_labs.crews.content.content_crew import ContentAICrew
from vertical_labs.crews.pitch.pitch_crew import PitchAICrew
from vertical_labs.crews.topics.topics_crew import TopicsAICrew


class VerticalLabsOrchestrator:
    """Orchestrator for managing all Vertical Labs crews."""

def __init__(self, config: Dict):
    """Initialize the orchestrator.

    Args:
        config (Dict): Configuration dictionary with settings for all crews.
            - "topics_ai" (dict, optional): Configuration for the TopicsAICrew.
            - "pitch_ai" (dict, optional): Configuration for the PitchAICrew.
            - "content_ai" (dict, optional): Configuration for the ContentAICrew.
    """
    self.config = config
    self.topics_crew = TopicsAICrew(config.get("topics_ai", {}))
    self.pitch_crew = PitchAICrew(config.get("pitch_ai", {}))
    self.content_crew = ContentAICrew(config.get("content_ai", {}))

    def run_topics_generation(self, inputs: Dict) -> Dict:
        """Run the TopicsAI crew to generate topics.

        Args:
            inputs: Dictionary with input parameters for TopicsAI

        Returns:
            Dictionary with generated topics and metadata
        """
        return self.topics_crew.run(inputs)

    def run_pitch_generation(self, inputs: Dict) -> Dict:
        """Run the PitchAI crew to generate pitches.

        Args:
            inputs: Dictionary with input parameters for PitchAI

        Returns:
            Dictionary with generated pitches and metadata
        """
        return self.pitch_crew.run(inputs)

    def run_content_generation(self, inputs: Dict) -> Dict:
        """Run the ContentAI crew to generate content.

        Args:
            inputs: Dictionary with input parameters for ContentAI

        Returns:
            Dictionary with generated content and metadata
        """
        return self.content_crew.run(inputs)

    def run_full_pipeline(self, inputs: Dict) -> Dict:
        """Run the complete pipeline from topics to content.

        Args:
            inputs: Dictionary with all required input parameters including:
                - publisher_info: Information about the publisher
                - brand_info: Information about the brand
                - requirements: Specific requirements for the content

        Returns:
            Dictionary with all generated outputs and metadata
        """
        # Generate topics
        topics_result = self.run_topics_generation({
            "publisher_name": inputs["publisher_info"]["name"],
            "publisher_url": inputs["publisher_info"]["url"],
            "categories": inputs["publisher_info"]["categories"],
            "audience": inputs["publisher_info"]["audience"],
            "locations": inputs["publisher_info"]["locations"]
        })

        # Generate pitches for the topics
        pitch_result = self.run_pitch_generation({
            "topics": topics_result["topics"],
            "brand_info": inputs["brand_info"],
            "publishers": [inputs["publisher_info"]],
            "preferences": inputs["publisher_info"].get("preferences", {})
        })

        # Generate content for accepted pitches
        content_results = []
        for pitch in pitch_result["pitches"]:
            if pitch.get("status") == "accepted":
                content_result = self.run_content_generation({
                    "topic": pitch["topic"],
                    "guidelines": topics_result["metadata"]["guidelines"],
                    "brand_info": inputs["brand_info"],
                    "publisher": inputs["publisher_info"]
                })
                content_results.append(content_result)

        return {
            "topics": topics_result,
            "pitches": pitch_result,
            "content": content_results,
            "metadata": {
                "publisher": inputs["publisher_info"],
                "brand": inputs["brand_info"],
                "requirements": inputs["requirements"]
            }
        }
