"""TopicsAI crew tasks."""

from typing import Dict, List
from crewai import Task
from .agents import (
    create_topic_researcher,
    create_audience_analyst,
    create_content_strategist,
    create_seo_specialist,
    create_quality_assurer,
    create_topic_coordinator
)

def create_guidelines_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for generating editorial guidelines."""
    return Task(
        description="Develop and store brand voice and content guidelines using the "
                   "EditorialGuidelinesTool. Consider the publisher's niche, audience, "
                   "and content strategy.",
        expected_output="A comprehensive set of brand voice guidelines stored for "
                       "consistent access by all agents.",
        agent=agents["content_strategist"]
    )

def create_website_analysis_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for analyzing publisher website."""
    return Task(
        description="Analyze the publisher's website content using WebsiteAnalyzerTool "
                   "to extract insights about content categories, audience indicators, "
                   "and content patterns.",
        expected_output="A detailed analysis of website content, including primary "
                       "categories and audience indicators.",
        agent=agents["topic_researcher"]
    )

def create_trends_research_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for researching current trends."""
    return Task(
        description="Research current trends and events relevant to the publisher using "
                   "TwitterTrendsTool, NewsScraperTool, and GoogleNewsTool. Focus on "
                   "trends that align with the publisher's niche.",
        expected_output="A list of current trends, upcoming events, and potential "
                       "content gaps in the publisher's niche.",
        agent=agents["topic_researcher"]
    )

def create_topic_generation_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for generating and scoring topics."""
    return Task(
        description="Generate and score initial topic ideas ensuring alignment with "
                   "audience interests and current trends. Consider the website analysis "
                   "and trends research results.",
        expected_output="A list of scored topic ideas with relevance, audience appeal, "
                       "and SEO potential ratings.",
        agent=agents["content_strategist"],
        context=[
            "website_analysis_task",
            "trends_research_task"
        ]
    )

def create_diversity_check_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for ensuring topic diversity."""
    return Task(
        description="Review topic suggestions using ContentDiversityTool to ensure "
                   "diversity in content types and subject matter. Check for duplicates "
                   "and overlapping themes.",
        expected_output="A validated list of topics ensuring diversity in content types "
                       "and subject matter.",
        agent=agents["quality_assurer"],
        context=[
            "topic_generation_task"
        ]
    )

def create_final_compilation_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for compiling final topic list."""
    return Task(
        description="Compile the final list of topic suggestions ensuring alignment "
                   "with guidelines and incorporating diversity check results. Prioritize "
                   "topics based on relevance and potential impact.",
        expected_output="A prioritized list of topic suggestions ready for implementation.",
        agent=agents["topic_coordinator"],
        context=[
            "diversity_check_task"
        ]
    )