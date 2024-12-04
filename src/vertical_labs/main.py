"""Main entry point for Vertical Labs."""

from typing import Callable, Dict, List, Optional

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from vertical_labs.crews.content.content_crew import ContentAICrew
from vertical_labs.crews.pitch.pitch_crew import PitchAICrew
from vertical_labs.crews.topics.topics_crew import TopicsAICrew


class Topic(BaseModel):
    title: str
    description: str
    keywords: List[str]


class ContentItem(BaseModel):
    title: str
    content: str
    metadata: Dict


class Pitch(BaseModel):
    title: str
    pitch: str
    target_audience: str


class PublisherInfo(BaseModel):
    """Publisher information for content analysis and targeting."""

    name: str = Field(description="Name of the publisher")
    url: str = Field(description="Publisher's website URL")
    categories: List[str] = Field(
        description="Content categories covered by the publisher"
    )
    audience: str = Field(description="Publisher's target audience")
    locations: List[str] = Field(description="Geographic locations covered")
    preferences: Optional[Dict] = Field(
        default_factory=dict, description="Publisher's content preferences"
    )


class VerticalLabsState(BaseModel):
    topics: List[Topic] = []
    content_items: List[ContentItem] = []
    pitches: List[Pitch] = []
    domain: str = ""
    target_audience: str = ""
    content_goals: str = ""
    publisher: Optional[PublisherInfo] = None


class VerticalLabsFlow(Flow[VerticalLabsState]):
    initial_state = VerticalLabsState

    def __init__(self, progress_callback: Optional[Callable] = None):
        super().__init__()
        # Initialize crews with proper configuration paths
        self.topics_crew = None
        self.content_crew = None
        self.pitch_crew = None
        self.progress_callback = progress_callback

    def _update_progress(self, stage: str, status: str, detail: str):
        """Update progress through callback if available."""
        if self.progress_callback:
            self.progress_callback(stage, status, detail)

    def _init_crews(self):
        """Initialize crews with proper configuration."""
        if not self.topics_crew:
            self.topics_crew = TopicsAICrew()
            self.topics_crew.config = {
                "domain": self.state.domain,
                "target_audience": self.state.target_audience,
                "publisher": (
                    self.state.publisher.model_dump() if self.state.publisher else None
                ),
                "agents_config": "agents.yaml",
                "tasks_config": "tasks.yaml",
                "progress_callback": self.progress_callback,
            }

        if not self.content_crew:
            self.content_crew = ContentAICrew()
            self.content_crew.config = {
                "content_goals": self.state.content_goals,
                "publisher": (
                    self.state.publisher.model_dump() if self.state.publisher else None
                ),
                "agents_config": "agents.yaml",
                "tasks_config": "tasks.yaml",
                "progress_callback": self.progress_callback,
            }

        if not self.pitch_crew:
            self.pitch_crew = PitchAICrew()
            self.pitch_crew.config = {
                "target_audience": self.state.target_audience,
                "publisher": (
                    self.state.publisher.model_dump() if self.state.publisher else None
                ),
                "agents_config": "agents.yaml",
                "tasks_config": "tasks.yaml",
                "progress_callback": self.progress_callback,
            }

    @start()
    def discover_topics(self):
        """Start the topic discovery process."""
        self._update_progress("topics", "In Progress", "Starting Topics Discovery")
        print("Starting Topics Discovery")
        self._init_crews()

        try:
            result = self.topics_crew.run(
                {
                    "domain": self.state.domain,
                    "target_audience": self.state.target_audience,
                    "publisher": (
                        self.state.publisher.model_dump()
                        if self.state.publisher
                        else None
                    ),
                    "progress_callback": self.progress_callback,
                }
            )

            # Convert dictionary topics to Topic objects
            self.state.topics = [
                Topic(
                    title=topic["title"],
                    description=topic["description"],
                    keywords=topic["keywords"],
                )
                for topic in result["topics"]
            ]
            self._update_progress(
                "topics", "Complete", f"Generated {len(self.state.topics)} topics"
            )
            return self.state.topics
        except Exception as e:
            self._update_progress(
                "topics", "Error", f"Error in topic discovery: {str(e)}"
            )
            raise

    @listen(discover_topics)
    async def generate_content(self):
        """Generate content for discovered topics."""
        self._update_progress("content", "In Progress", "Starting Content Generation")
        print("Generating Content")
        self._init_crews()
        content_items = []

        try:
            for i, topic in enumerate(self.state.topics, 1):
                self._update_progress(
                    "content",
                    "In Progress",
                    f"Generating content for topic {i}/{len(self.state.topics)}",
                )
                output = self.content_crew.run(
                    {
                        "topic": topic.title,
                        "description": topic.description,
                        "keywords": topic.keywords,
                        "content_goals": self.state.content_goals,
                        "publisher": (
                            self.state.publisher.model_dump()
                            if self.state.publisher
                            else None
                        ),
                        "progress_callback": self.progress_callback,
                    }
                )

                content_item = ContentItem(
                    title=output["title"],
                    content=output["content"],
                    metadata=output["metadata"],
                )
                content_items.append(content_item)

            self.state.content_items = content_items
            self._update_progress(
                "content", "Complete", f"Generated {len(content_items)} content pieces"
            )
            return self.state.content_items
        except Exception as e:
            self._update_progress(
                "content", "Error", f"Error in content generation: {str(e)}"
            )
            raise

    @listen(discover_topics)
    async def create_pitches(self):
        """Create pitches for generated content."""
        self._update_progress("pitches", "In Progress", "Starting Pitch Creation")
        print("Creating Pitches")
        self._init_crews()
        pitches = []

        try:
            for i, content_item in enumerate(self.state.content_items, 1):
                self._update_progress(
                    "pitches",
                    "In Progress",
                    f"Creating pitch {i}/{len(self.state.content_items)}",
                )
                output = self.pitch_crew.run(
                    {
                        "content_title": content_item.title,
                        "content": content_item.content,
                        "target_audience": self.state.target_audience,
                        "publisher": (
                            self.state.publisher.model_dump()
                            if self.state.publisher
                            else None
                        ),
                        "progress_callback": self.progress_callback,
                    }
                )

                pitch = Pitch(
                    title=output["title"],
                    pitch=output["pitch"],
                    target_audience=output["target_audience"],
                )
                pitches.append(pitch)

            self.state.pitches = pitches
            self._update_progress(
                "pitches", "Complete", f"Created {len(pitches)} pitches"
            )
            return self.state.pitches
        except Exception as e:
            self._update_progress(
                "pitches", "Error", f"Error in pitch creation: {str(e)}"
            )
            raise


def kickoff(
    publisher_name: str,
    publisher_url: str,
    publisher_categories: List[str],
    publisher_audience: str,
    publisher_locations: List[str],
    domain: str = "Enterprise AI Solutions",
    target_audience: str = "B2B audience including CTOs, Tech Leaders, and Developers",
    content_goals: str = """
    Create thought leadership and technical analysis content that:
    - Demonstrates expertise in enterprise-grade AI solutions
    - Includes case studies and ROI metrics
    - Maintains professional tone and analytical style
    """,
    progress_callback: Optional[Callable] = None,
):
    """Kickoff the Vertical Labs flow."""
    flow = VerticalLabsFlow(progress_callback=progress_callback)
    flow.state.domain = domain
    flow.state.target_audience = target_audience
    flow.state.content_goals = content_goals
    flow.state.publisher = PublisherInfo(
        name=publisher_name,
        url=publisher_url,
        categories=publisher_categories,
        audience=publisher_audience,
        locations=publisher_locations,
    )
    return flow.kickoff()


def plot():
    """Generate a visualization of the flow."""
    flow = VerticalLabsFlow()
    flow.plot()


def main():
    """Run the Vertical Labs system."""
    # Load environment variables
    load_dotenv()

    # Example publisher
    publisher_name = "TechCrunch"
    publisher_url = "https://techcrunch.com"
    publisher_categories = ["Technology", "Startups", "AI/ML", "Enterprise"]
    publisher_audience = "Tech professionals, entrepreneurs, investors"
    publisher_locations = ["Global", "USA", "Europe"]

    # Example domain and goals
    domain = "Enterprise AI Solutions"
    target_audience = """
    B2B audience including CTOs, Tech Leaders, and Developers
    in Software and AI/ML industries, primarily in USA and Canada.
    Looking for professional, analytical content with data-backed insights.
    """
    content_goals = """
    Create thought leadership and technical analysis content that:
    - Demonstrates expertise in enterprise-grade AI solutions
    - Includes case studies and ROI metrics
    - Maintains professional tone and analytical style
    - Targets content length of 1000-1500 words
    - Emphasizes human-centric design in AI implementations
    """

    # Run the flow
    results = kickoff(
        publisher_name=publisher_name,
        publisher_url=publisher_url,
        publisher_categories=publisher_categories,
        publisher_audience=publisher_audience,
        publisher_locations=publisher_locations,
        domain=domain,
        target_audience=target_audience,
        content_goals=content_goals,
    )

    # Print results summary
    print("\nResults Summary:")
    print(f"Topics Generated: {len(results.topics)}")
    print(f"Content Pieces: {len(results.content_items)}")
    print(f"Pitches Created: {len(results.pitches)}")

    # Generate flow visualization
    plot()


if __name__ == "__main__":
    main()
