"""ContentAI crew agents."""

from typing import Dict

from crewai import Agent

from ..tools.content_tools import (ContentDiversityTool,
                                   EditorialGuidelinesTool,
                                   WebsiteAnalyzerTool)


def create_content_researcher(config: Dict) -> Agent:
    """Create the Content Research Specialist agent."""
    return Agent(
        role="Content Research Specialist",
        goal="Research and gather comprehensive information for content creation",
        backstory=(
            "As a Content Research Specialist, you excel at finding and validating "
            "information from multiple sources. Your research skills ensure content "
            "is accurate, current, and valuable to readers."
        ),
        tools=[WebsiteAnalyzerTool()],
        verbose=True
    )

def create_content_writer(config: Dict) -> Agent:
    """Create the Content Writing Expert agent."""
    return Agent(
        role="Content Writing Expert",
        goal=(
            "Create engaging, high-quality content that meets editorial standards"
        ),
        backstory=(
            "You are a skilled writer who can adapt to different styles and tones. "
            "Your content is engaging, well-structured, and optimized for both readers "
            "and search engines."
        ),
        tools=[EditorialGuidelinesTool()],
        verbose=True
    )

def create_content_editor(config: Dict) -> Agent:
    """Create the Content Editor agent."""
    return Agent(
        role="Content Editor",
        goal=(
            "Ensure content quality, accuracy, and alignment with guidelines"
        ),
        backstory=(
            "With a sharp eye for detail and strong editorial judgment, you ensure "
            "all content meets quality standards and editorial guidelines while "
            "maintaining consistency."
        ),
        tools=[EditorialGuidelinesTool()],
        verbose=True
    )

def create_content_optimizer(config: Dict) -> Agent:
    """Create the Content Optimization Specialist agent."""
    return Agent(
        role="Content Optimization Specialist",
        goal=(
            "Optimize content for maximum impact and engagement"
        ),
        backstory=(
            "You specialize in optimizing content for both search engines and "
            "reader engagement. Your expertise ensures content performs well across "
            "all relevant metrics."
        ),
        tools=[ContentDiversityTool()],
        verbose=True
    )

def create_content_coordinator(config: Dict) -> Agent:
    """Create the Content Coordination Manager agent."""
    return Agent(
        role="Content Coordination Manager",
        goal=(
            "Oversee content creation process and ensure timely delivery"
        ),
        backstory=(
            "You manage the end-to-end content creation process, ensuring all "
            "pieces come together smoothly and meet deadlines while maintaining "
            "quality standards."
        ),
        tools=[],
        verbose=True
    )
