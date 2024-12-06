"""PitchAI crew implementation with self-evaluation loop."""

from typing import Dict

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from vertical_labs.tools.pitch_tools import (
    BrandMatchingTool,
    PitchGeneratorTool,
    PitchOptimizationTool,
)

load_dotenv()


@CrewBase
class PitchAICrew:
    """Crew for generating and optimizing PR pitches."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def brand_analyst(self) -> Agent:
        """Agent for analyzing brand fit."""
        return Agent(
            name="brand_analyst",
            config=self.agents_config["brand_analyst"],
            tools=[BrandMatchingTool()],
        )

    @agent
    def pitch_writer(self) -> Agent:
        """Agent for writing pitches."""
        return Agent(
            name="pitch_writer",
            config=self.agents_config["pitch_writer"],
            tools=[PitchGeneratorTool()],
        )

    @agent
    def media_relations_specialist(self) -> Agent:
        """Agent for optimizing pitches."""
        return Agent(
            name="media_relations_specialist",
            config=self.agents_config["media_relations_specialist"],
            tools=[PitchOptimizationTool()],
        )

    @agent
    def pitch_coordinator(self) -> Agent:
        """Agent for coordinating pitches."""
        return Agent(
            name="pitch_coordinator",
            config=self.agents_config["pitch_coordinator"],
        )

    @task
    def brand_analysis_task(self) -> Task:
        """Task for analyzing brand fit."""
        return Task(
            name="brand_analysis_task",
            config=self.tasks_config["brand_analysis_task"],
        )

    @task
    def pitch_writing_task(self) -> Task:
        """Task for writing pitches."""
        return Task(
            name="pitch_writing_task",
            config=self.tasks_config["pitch_writing_task"],
        )

    @task
    def pitch_optimization_task(self) -> Task:
        """Task for optimizing pitches."""
        return Task(
            name="pitch_optimization_task",
            config=self.tasks_config["pitch_optimization_task"],
        )

    @task
    def pitch_review(self) -> Task:
        """Task for final review of pitches."""
        return Task(
            name="pitch_review",
            config=self.tasks_config["pitch_review"],
        )

    @crew
    def pitch_crew(self) -> Crew:
        """Crew for creating and optimizing pitches."""
        return Crew(
            name="pitch_crew",
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
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

        # Get the crew instance
        crew_instance = self.pitch_crew()

        # Run the crew
        results = crew_instance.kickoff()

        # Process and structure the results
        return {
            "pitches": results.get("pitch_review", []),
            "metadata": {
                "brand_matches": results.get("brand_analysis_task", {}),
                "optimization_insights": results.get("pitch_optimization_task", {}),
            },
        }
