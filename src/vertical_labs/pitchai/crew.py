"""PitchAI crew implementation."""

from typing import Dict, List
from crewai import Crew, Process
from .agents import (
    create_brand_analyst,
    create_pitch_writer,
    create_media_relations_specialist,
    create_pitch_coordinator
)
from .tasks import (
    create_brand_analysis_task,
    create_pitch_writing_task,
    create_pitch_optimization_task,
    create_final_review_task
)

class PitchAICrew:
    """Crew for generating and optimizing PR pitches."""
    
    def __init__(self, config: Dict):
        """Initialize the PitchAI crew.
        
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
            "brand_analyst": create_brand_analyst(self.config),
            "pitch_writer": create_pitch_writer(self.config),
            "media_relations_specialist": create_media_relations_specialist(self.config),
            "pitch_coordinator": create_pitch_coordinator(self.config)
        }
        
    def _create_tasks(self) -> List:
        """Create all required tasks."""
        context = {"config": self.config}
        return [
            create_brand_analysis_task(self.agents, context),
            create_pitch_writing_task(self.agents, context),
            create_pitch_optimization_task(self.agents, context),
            create_final_review_task(self.agents, context)
        ]
        
    def _create_crew(self) -> Crew:
        """Create the PitchAI crew."""
        return Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        
    def run(self, inputs: Dict) -> Dict:
        """Run the PitchAI crew.
        
        Args:
            inputs: Dictionary with input parameters including:
                - topics: List of topics from TopicsAI
                - brand_info: Information about the brand
                - publishers: List of target publishers
                - preferences: Publisher preferences and requirements
                
        Returns:
            Dictionary with generated pitches and metadata
        """
        # Update config with inputs
        self.config.update(inputs)
        
        # Run the crew
        results = self.crew.kickoff()
        
        # Process and structure the results
        return {
            "pitches": results.get("final_review_task", []),
            "metadata": {
                "brand_matches": results.get("brand_analysis_task", {}),
                "optimization_insights": results.get("pitch_optimization_task", {})
            }
        }