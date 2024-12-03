"""TopicsAI crew implementation."""

from typing import Dict, List

from crewai import Crew, Process

from .agents import (create_audience_analyst, create_content_strategist,
                     create_quality_assurer, create_seo_specialist,
                     create_topic_coordinator, create_topic_researcher)
from .tasks import (create_diversity_check_task, create_final_compilation_task,
                    create_guidelines_task, create_topic_generation_task,
                    create_trends_research_task, create_website_analysis_task)


class TopicsAICrew:
    """Crew for generating and managing content topics."""

    def __init__(self, config: Dict):
        """Initialize the TopicsAI crew.

        Args:
            config: Configuration dictionary with settings for the crew
        """
        self.config = config
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        self.crew = self._create_crew()

    def _create_agents(self) -> Dict:
        """Create all required agents."""
        return {
            "topic_researcher": create_topic_researcher(self.config),
            "audience_analyst": create_audience_analyst(self.config),
            "content_strategist": create_content_strategist(self.config),
            "seo_specialist": create_seo_specialist(self.config),
            "quality_assurer": create_quality_assurer(self.config),
            "topic_coordinator": create_topic_coordinator(self.config)
        }

    def _create_tasks(self) -> List:
        """Create all required tasks."""
        context = {"config": self.config}
        return [
            create_guidelines_task(self.agents, context),
            create_website_analysis_task(self.agents, context),
            create_trends_research_task(self.agents, context),
            create_topic_generation_task(self.agents, context),
            create_diversity_check_task(self.agents, context),
            create_final_compilation_task(self.agents, context)
        ]

    def _create_crew(self) -> Crew:
        """Create the TopicsAI crew."""
        return Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    def run(self, inputs: Dict) -> Dict:
        """Run the TopicsAI crew.

        Args:
            inputs: Dictionary with input parameters including:
                - publisher_name: Name of the publisher
                - publisher_url: URL of publisher's website
                - categories: List of content categories
                - audience: Target audience information
                - locations: Target locations

        Returns:
            Dictionary with generated topics and metadata
        """
        # Update config with inputs
        self.config.update(inputs)

        # Run the crew
        results = self.crew.kickoff()

        # Process and structure the results
        return {
            "topics": results.get("final_compilation_task", []),
            "metadata": {
                "guidelines": results.get("guidelines_task", {}),
                "trends": results.get("trends_research_task", []),
                "analysis": results.get("website_analysis_task", {})
            }
        }
