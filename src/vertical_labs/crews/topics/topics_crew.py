"""TopicsAI crew implementation with self-evaluation loop."""

from typing import Dict, List, Optional

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel

from vertical_labs.tools.content_tools import (
    ContentDiversityTool,
    EditorialGuidelinesTool,
    PublisherInfo
)


class TopicsInput(BaseModel):
    """Input schema for TopicsAICrew."""
    domain: str
    target_audience: str
    publisher_name: Optional[str] = None
    publisher_url: Optional[str] = None
    categories: Optional[List[str]] = None
    audience: Optional[str] = None
    locations: Optional[List[str]] = None


@CrewBase
class TopicsAICrew:
    """Crew for generating and managing content topics."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def topic_researcher(self) -> Agent:
        """Agent for researching topics."""
        return Agent(
            name="topic_researcher",
            config=self.agents_config["topic_researcher"],
            tools=[],
        )

    @agent
    def audience_analyst(self) -> Agent:
        """Agent for analyzing audience needs."""
        return Agent(
            name="audience_analyst",
            config=self.agents_config["audience_analyst"],
            tools=[],
        )

    @agent
    def content_strategist(self) -> Agent:
        """Agent for strategic topic planning."""
        return Agent(
            name="content_strategist",
            config=self.agents_config["content_strategist"],
            tools=[EditorialGuidelinesTool()],
        )

    @agent
    def quality_assurer(self) -> Agent:
        """Agent for ensuring topic quality."""
        return Agent(
            name="quality_assurer",
            config=self.agents_config["quality_assurer"],
            tools=[ContentDiversityTool()],
        )

    @agent
    def topic_coordinator(self) -> Agent:
        """Agent for coordinating topic generation."""
        return Agent(
            name="topic_coordinator",
            config=self.agents_config["topic_coordinator"],
        )

    @task
    def guidelines_task(self) -> Task:
        """Task for establishing content guidelines."""
        return Task(
            name="guidelines_task",
            config=self.tasks_config["guidelines_task"],
            tools=[EditorialGuidelinesTool()],
        )

    @task
    def website_analysis_task(self) -> Task:
        """Task for analyzing website content."""
        return Task(
            name="website_analysis_task",
            config=self.tasks_config["website_analysis_task"],
            tools=[],
        )

    @task
    def trends_research_task(self) -> Task:
        """Task for researching current trends."""
        return Task(
            name="trends_research_task",
            config=self.tasks_config["trends_research_task"],
            tools=[],
        )

    @task
    def topic_generation_task(self) -> Task:
        """Task for generating topics."""
        return Task(
            name="topic_generation_task",
            config=self.tasks_config["topic_generation_task"],
        )

    @task
    def diversity_check_task(self) -> Task:
        """Task for checking topic diversity."""
        return Task(
            name="diversity_check_task",
            config=self.tasks_config["diversity_check_task"],
            tools=[ContentDiversityTool()],
        )

    @task
    def final_compilation_task(self) -> Task:
        """Task for final compilation of topics."""
        return Task(
            name="final_compilation_task",
            config=self.tasks_config["final_compilation_task"],
        )

    @crew
    def topics_crew(self) -> Crew:
        """Crew for generating and managing topics."""
        return Crew(
            name="topics_crew",
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def _create_publisher_info(self, inputs: Dict) -> PublisherInfo:
        """Create a PublisherInfo instance from input dictionary."""
        return PublisherInfo(
            name=inputs.get("publisher_name", "Generic Publisher"),
            type="B2B" if "B2B" in inputs.get("target_audience", "").upper() else "B2C",
            categories=inputs.get("categories", []),
            audience=inputs.get("audience", inputs.get("target_audience", "")),
            locations=inputs.get("locations", ["global"])
        )

    def run(self, inputs: Dict) -> Dict:
        """Run the topics crew with the given inputs."""
        # Validate inputs
        validated_inputs = TopicsInput(**inputs)
        
        # Update config with validated inputs
        self.config.update(validated_inputs.model_dump())

        # Create publisher info
        publisher_info = self._create_publisher_info(validated_inputs.model_dump())
        
        # Add publisher info to config for tasks
        self.config["publisher_info"] = publisher_info.model_dump()

        # Get the crew instance
        crew_instance = self.topics_crew()

        # Run the crew
        results = crew_instance.kickoff()

        # Process and structure the results
        return {
            "topics": results.get("final_compilation_task", []),
            "metadata": {
                "guidelines": results.get("guidelines_task", {}),
                "trends": results.get("trends_research_task", []),
                "analysis": results.get("website_analysis_task", {}),
            },
        }