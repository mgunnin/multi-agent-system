"""ContentAI crew tasks."""

from typing import Dict, List
from crewai import Task
from .agents import (
    create_content_researcher,
    create_content_writer,
    create_content_editor,
    create_content_optimizer,
    create_content_coordinator
)

def create_research_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for content research."""
    return Task(
        description="Research the topic thoroughly using multiple sources. Gather key "
                   "information, statistics, examples, and expert insights. Validate "
                   "all information for accuracy.",
        expected_output="A comprehensive research package including key points, "
                       "statistics, examples, and verified sources.",
        agent=agents["content_researcher"]
    )

def create_content_writing_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for content writing."""
    return Task(
        description="Write engaging content based on the research package and editorial "
                   "guidelines. Structure content for readability and impact while "
                   "maintaining the required tone and style.",
        expected_output="A well-structured draft that incorporates research findings "
                       "and follows editorial guidelines.",
        agent=agents["content_writer"],
        context=["research_task"]
    )

def create_editing_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for content editing."""
    return Task(
        description="Review and edit the content for clarity, accuracy, and style. "
                   "Ensure compliance with editorial guidelines and brand standards. "
                   "Check grammar, tone, and flow.",
        expected_output="An edited version of the content with tracked changes and "
                       "editorial comments.",
        agent=agents["content_editor"],
        context=["content_writing_task"]
    )

def create_optimization_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for content optimization."""
    return Task(
        description="Optimize the content for search engines and reader engagement. "
                   "Analyze readability, keyword usage, and structure. Suggest "
                   "improvements for better performance.",
        expected_output="An optimized version of the content with SEO improvements "
                       "and engagement enhancements.",
        agent=agents["content_optimizer"],
        context=["editing_task"]
    )

def create_final_review_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for final content review."""
    return Task(
        description="Conduct final review of the optimized content. Ensure all elements "
                   "are in place and the content is ready for publication. Prepare "
                   "content package with metadata.",
        expected_output="Publication-ready content package with all necessary metadata "
                       "and supporting materials.",
        agent=agents["content_coordinator"],
        context=["optimization_task"]
    )