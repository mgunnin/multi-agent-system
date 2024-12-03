"""TopicsAI crew agents."""

from typing import Dict, List, Optional
from crewai import Agent
from ..tools.news_tools import TwitterTrendsTool, NewsScraperTool, GoogleNewsTool
from ..tools.content_tools import WebsiteAnalyzerTool, EditorialGuidelinesTool, ContentDiversityTool

def create_topic_researcher(config: Dict) -> Agent:
    """Create the Topic Researcher agent."""
    return Agent(
        role="Lead Topic Researcher",
        goal="Investigate current trends and popular topics in the publisher's niche",
        backstory="As the Lead Topic Researcher, you specialize in uncovering trending topics "
                "and emerging issues. Your expertise in data analysis and SEO ensures that "
                "you can identify content gaps and opportunities.",
        tools=[
            TwitterTrendsTool(),
            NewsScraperTool(),
            GoogleNewsTool(),
            WebsiteAnalyzerTool()
        ],
        verbose=True
    )

def create_audience_analyst(config: Dict) -> Agent:
    """Create the Audience Analysis Expert agent."""
    return Agent(
        role="Audience Analysis Expert",
        goal="Analyze audience demographics and behavior to suggest relevant topics",
        backstory="With a strong background in demographic analysis and user behavior interpretation, "
                "you excel at understanding target audiences and providing insights that drive "
                "content relevance.",
        tools=[WebsiteAnalyzerTool()],
        verbose=True
    )

def create_content_strategist(config: Dict) -> Agent:
    """Create the Content Strategy Specialist agent."""
    return Agent(
        role="Content Strategy Specialist",
        goal="Align potential topics with content strategy and goals",
        backstory="As a Content Strategy Specialist, you have a keen sense for evaluating "
                "topic relevance and ensuring alignment with voice and style. You are adept "
                "at balancing editorial judgment with strategic goals.",
        tools=[EditorialGuidelinesTool()],
        verbose=True
    )

def create_seo_specialist(config: Dict) -> Agent:
    """Create the SEO Optimization Expert agent."""
    return Agent(
        role="SEO Optimization Expert",
        goal="Optimize topic ideas for search engine visibility",
        backstory="Your skills in keyword analysis and search intent interpretation make "
                "you the go-to expert for ensuring that topic ideas have strong SEO potential, "
                "driving visibility and engagement.",
        tools=[],  # Add SEO tools as needed
        verbose=True
    )

def create_quality_assurer(config: Dict) -> Agent:
    """Create the Quality Assurance Specialist agent."""
    return Agent(
        role="Quality Assurance Specialist",
        goal="Ensure that proposed topics meet standards and requirements",
        backstory="With an eye for detail and a knack for quality control, you review and "
                "validate topic suggestions to ensure they meet necessary standards and offer "
                "a diverse range of content.",
        tools=[ContentDiversityTool()],
        verbose=True
    )

def create_topic_coordinator(config: Dict) -> Agent:
    """Create the Topic Coordination Manager agent."""
    return Agent(
        role="Topic Coordination Manager",
        goal="Oversee the topic generation process and compile final topic suggestions",
        backstory="Leading the coordination of topic generation, you manage the workflow "
                "and ensure collaboration between agents to produce a well-prioritized "
                "list of topic suggestions.",
        tools=[],
        verbose=True
    )