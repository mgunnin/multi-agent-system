"""TopicsAI crew implementation with self-evaluation loop."""

import logging
from typing import Dict, Optional, Callable

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, EXASearchTool

from vertical_labs.tools.content_tools import (
    ContentDiversityTool,
    EditorialGuidelinesTool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@CrewBase
class TopicsAICrew:
    """Crew for generating and managing content topics."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    progress_callback: Optional[Callable] = None

    def _update_progress(self, status: str, detail: str):
        """Update progress through callback if available."""
        logger.info(f"Progress Update - {status}: {detail}")
        if self.progress_callback:
            self.progress_callback("topics", status, detail)

    def _log_agent_task(self, agent_name: str, task_description: str):
        """Log agent task through progress callback."""
        message = f"""Agent: {agent_name}
Task: {task_description}"""
        logger.info(message)
        self._update_progress("In Progress", message)

    @agent
    def website_analyzer(self) -> Agent:
        """Agent for analyzing publisher websites."""
        logger.info("Creating Website Analysis Expert agent")
        return Agent(
            name="Website Analysis Expert",
            config=self.agents_config["website_analyzer"],
            tools=[
                ScrapeWebsiteTool(),
                EXASearchTool()
            ],
        )

    @agent
    def topic_researcher(self) -> Agent:
        """Agent for researching topics."""
        logger.info("Creating Topic Research Specialist agent")
        return Agent(
            name="Topic Research Specialist",
            config=self.agents_config["topic_researcher"],
            tools=[EXASearchTool()],
        )

    @agent
    def audience_analyst(self) -> Agent:
        """Agent for analyzing audience needs."""
        logger.info("Creating Audience Analysis Expert agent")
        return Agent(
            name="Audience Analysis Expert",
            config=self.agents_config["audience_analyst"],
            tools=[],
        )

    @agent
    def content_strategist(self) -> Agent:
        """Agent for strategic topic planning."""
        logger.info("Creating Content Strategy Specialist agent")
        return Agent(
            name="Content Strategy Specialist",
            config=self.agents_config["content_strategist"],
            tools=[EditorialGuidelinesTool()],
        )

    @agent
    def quality_assurer(self) -> Agent:
        """Agent for ensuring topic quality."""
        logger.info("Creating Quality Assurance Specialist agent")
        return Agent(
            name="Quality Assurance Specialist",
            config=self.agents_config["quality_assurer"],
            tools=[ContentDiversityTool()],
        )

    @agent
    def topic_coordinator(self) -> Agent:
        """Agent for coordinating topic generation."""
        logger.info("Creating Topic Coordination Manager agent")
        return Agent(
            name="Topic Coordination Manager",
            config=self.agents_config["topic_coordinator"],
        )

    @task
    def website_analysis_task(self) -> Task:
        """Task for analyzing publisher website."""
        logger.info("Starting website analysis task")
        self._log_agent_task(
            "Website Analysis Expert",
            "Analyzing publisher website to understand content strategy, audience, and topics."
        )
        return Task(
            name="website_analysis_task",
            config=self.tasks_config["website_analysis_task"],
            tools=[ScrapeWebsiteTool(), EXASearchTool()],
        )

    @task
    def guidelines_task(self) -> Task:
        """Task for establishing content guidelines."""
        logger.info("Starting guidelines task")
        self._log_agent_task(
            "Content Strategy Specialist",
            "Developing content guidelines based on website analysis."
        )
        return Task(
            name="guidelines_task",
            config=self.tasks_config["guidelines_task"],
            tools=[EditorialGuidelinesTool()],
        )

    @task
    def trends_research_task(self) -> Task:
        """Task for researching current trends."""
        logger.info("Starting trends research task")
        self._log_agent_task(
            "Topic Research Specialist",
            "Researching current trends and topics in the publisher's domain."
        )
        return Task(
            name="trends_research_task",
            config=self.tasks_config["trends_research_task"],
            tools=[EXASearchTool()],
        )

    @task
    def topic_generation_task(self) -> Task:
        """Task for generating topics."""
        logger.info("Starting topic generation task")
        self._log_agent_task(
            "Content Strategy Specialist",
            "Generating initial topic ideas based on research and guidelines."
        )
        return Task(
            name="topic_generation_task",
            config=self.tasks_config["topic_generation_task"],
        )

    @task
    def diversity_check_task(self) -> Task:
        """Task for checking topic diversity."""
        logger.info("Starting diversity check task")
        self._log_agent_task(
            "Quality Assurance Specialist",
            "Evaluating topic diversity and ensuring content balance."
        )
        return Task(
            name="diversity_check_task",
            config=self.tasks_config["diversity_check_task"],
            tools=[ContentDiversityTool()],
        )

    @task
    def final_compilation_task(self) -> Task:
        """Task for final compilation of topics."""
        logger.info("Starting final compilation task")
        self._log_agent_task(
            "Topic Coordination Manager",
            "Compiling and prioritizing final topic list."
        )
        return Task(
            name="final_compilation_task",
            config=self.tasks_config["final_compilation_task"],
        )

    @crew
    def topics_crew(self) -> Crew:
        """Crew for generating and managing topics."""
        logger.info("Creating topics crew")
        return Crew(
            name="topics_crew",
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def run(self, inputs: Dict) -> Dict:
        """Run the topics crew with the given inputs."""
        logger.info("Starting topics crew run")
        try:
            # Store progress callback if provided
            self.progress_callback = inputs.pop("progress_callback", None)
            
            self._update_progress("In Progress", "Starting publisher analysis")
            logger.info("Publisher analysis starting")
            
            # Update config with inputs
            self.config.update(inputs)
            logger.info("Config updated with inputs")

            # Get the crew instance
            logger.info("Getting crew instance")
            crew_instance = self.topics_crew()

            self._update_progress("In Progress", "Analyzing website and generating topics")
            logger.info("Starting crew kickoff")

            # Run the crew
            results = crew_instance.kickoff()
            logger.info("Crew kickoff completed")

            self._update_progress("Complete", "Topic generation completed")
            logger.info("Topic generation completed successfully")

            # Process and structure the results
            return {
                "topics": results.get("final_compilation_task", []),
                "metadata": {
                    "guidelines": results.get("guidelines_task", {}),
                    "trends": results.get("trends_research_task", []),
                    "analysis": results.get("website_analysis_task", {}),
                },
            }
        except Exception as e:
            logger.error(f"Error in topics crew run: {str(e)}", exc_info=True)
            self._update_progress("Error", f"Error in topic generation: {str(e)}")
            raise