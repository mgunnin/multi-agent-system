"""ContentAI crew implementation with self-evaluation loop."""

from typing import Dict

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from vertical_labs.tools.content_tools import (
    ContentDiversityTool,
    EditorialGuidelinesTool,
)

load_dotenv()


@CrewBase
class ContentAICrew:
    """Crew for creating and optimizing content with self-evaluation loop."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def content_researcher(self) -> Agent:
        """Agent for researching content."""
        return Agent(
            name="content_researcher",
            config=self.agents_config["content_researcher"],
            tools=[],
        )

    @agent
    def content_writer(self) -> Agent:
        """Agent for writing content."""
        return Agent(
            name="content_writer",
            config=self.agents_config["content_writer"],
            tools=[EditorialGuidelinesTool()],
        )

    @agent
    def content_editor(self) -> Agent:
        """Agent for editing content."""
        return Agent(
            name="content_editor",
            config=self.agents_config["content_editor"],
            tools=[EditorialGuidelinesTool()],
        )

    @agent
    def content_optimizer(self) -> Agent:
        """Agent for optimizing content."""
        return Agent(
            name="content_optimizer",
            config=self.agents_config["content_optimizer"],
            tools=[ContentDiversityTool()],
        )

    @agent
    def content_coordinator(self) -> Agent:
        """Agent for coordinating content."""
        return Agent(
            name="content_coordinator",
            config=self.agents_config["content_coordinator"],
        )

    @task
    def content_research(self) -> Task:
        """Task for researching content."""
        return Task(
            name="content_research",
            config=self.tasks_config["content_research"],
        )

    @task
    def content_writing_task(self) -> Task:
        """Task for writing content."""
        return Task(
            name="content_writing_task",
            config=self.tasks_config["content_writing_task"],
        )

    @task
    def editing_task(self) -> Task:
        """Task for editing content."""
        return Task(
            name="editing_task",
            config=self.tasks_config["editing_task"],
        )

    @task
    def optimization_task(self) -> Task:
        """Task for optimizing content."""
        return Task(
            name="optimization_task",
            config=self.tasks_config["optimization_task"],
        )

    @task
    def content_review(self) -> Task:
        """Task for final review of content."""
        return Task(
            name="content_review",
            config=self.tasks_config["content_review"],
        )

    @crew
    def content_crew(self) -> Crew:
        """Crew for creating and optimizing content."""
        return Crew(
            name="content_crew",
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def run(self, inputs: Dict) -> Dict:
        """Run the content crew with the given inputs.

        Args:
            inputs (Dict): Dictionary containing:
                - topic: The topic to create content for
                - description: Description of the topic
                - keywords: Keywords related to the topic
                - content_goals: Goals for the content

        Returns:
            Dict: Dictionary containing:
                - title: The title of the content
                - content: The generated content
                - metadata: Additional metadata about the content
        """
        # Update config with inputs
        self.config.update(inputs)

        # Get the crew instance
        crew_instance = self.content_crew()

        # Run the crew
        results = crew_instance.kickoff()

        # Process and structure the results
        return {
            "title": results.get("content_writing_task", {}).get("title", ""),
            "content": results.get("content_review", {}).get("content", ""),
            "metadata": {
                "research": results.get("content_research", {}),
                "optimization": results.get("optimization_task", {}),
                "keywords": inputs.get("keywords", []),
            },
        }
