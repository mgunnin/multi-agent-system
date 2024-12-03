"""ContentAI crew implementation."""

from typing import Dict, List
from crewai import Crew, Process
from .agents import (
    create_content_researcher,
    create_content_writer,
    create_content_editor,
    create_content_optimizer,
    create_content_coordinator
)
from .tasks import (
    create_research_task,
    create_content_writing_task,
    create_editing_task,
    create_optimization_task,
    create_final_review_task
)

class ContentAICrew:
    """Crew for creating and optimizing content."""
    
    def __init__(self, config: Dict):
        """Initialize the ContentAI crew.
        
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
            "content_researcher": create_content_researcher(self.config),
            "content_writer": create_content_writer(self.config),
            "content_editor": create_content_editor(self.config),
            "content_optimizer": create_content_optimizer(self.config),
            "content_coordinator": create_content_coordinator(self.config)
        }
        
    def _create_tasks(self) -> List:
        """Create all required tasks."""
        context = {"config": self.config}
        return [
            create_research_task(self.agents, context),
            create_content_writing_task(self.agents, context),
            create_editing_task(self.agents, context),
            create_optimization_task(self.agents, context),
            create_final_review_task(self.agents, context)
        ]
        
    def _create_crew(self) -> Crew:
        """Create the ContentAI crew."""
        return Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        
    def run(self, inputs: Dict) -> Dict:
        """Run the ContentAI crew.
        
        Args:
            inputs: Dictionary with input parameters including:
                - topic: Topic information from TopicsAI
                - guidelines: Editorial guidelines
                - brand_info: Brand information if applicable
                - publisher: Publisher information
                
        Returns:
            Dictionary with generated content and metadata
        """
        # Update config with inputs
        self.config.update(inputs)
        
        # Run the crew
        results = self.crew.kickoff()
        
        # Process and structure the results
        return {
            "content": results.get("final_review_task", {}),
            "metadata": {
                "research": results.get("research_task", {}),
                "optimization": results.get("optimization_task", {})
            }
        }