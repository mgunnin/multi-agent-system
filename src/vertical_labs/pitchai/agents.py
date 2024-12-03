"""PitchAI crew agents."""

from typing import Dict

from crewai import Agent

from ..tools.pitch_tools import (BrandMatchingTool, PitchGeneratorTool,
                                 PitchOptimizationTool)


def create_brand_analyst(config: Dict) -> Agent:
    """Create the Brand Analysis Specialist agent."""
    return Agent(
        role="Brand Analysis Specialist",
        goal="Analyze brands and their potential fit with topics and publishers",
        backstory=(
            "As a Brand Analysis Specialist, you excel at understanding brand values, "
            "target markets, and unique selling propositions. You identify the best "
            "opportunities for brand-publisher matches."
        ),
        tools=[BrandMatchingTool()],
        verbose=True
    )

def create_pitch_writer(config: Dict) -> Agent:
    """Create the Pitch Writing Expert agent."""
    return Agent(
        role="Pitch Writing Expert",
        goal="Create compelling PR pitches that resonate with publishers",
        backstory=(
            "You are a master of crafting persuasive pitches that highlight the "
            "unique value proposition of brands while meeting publisher needs. Your "
            "writing is clear, engaging, and tailored to each opportunity."
        ),
        tools=[PitchGeneratorTool()],
        verbose=True
    )

def create_media_relations_specialist(config: Dict) -> Agent:
    """Create the Media Relations Specialist agent."""
    return Agent(
        role="Media Relations Specialist",
        goal="Optimize pitches based on publisher preferences and relationships",
        backstory=(
            "With years of experience in media relations, you understand what makes "
            "publishers tick. You know how to tailor communication styles and timing "
            "to maximize success rates."
        ),
        tools=[PitchOptimizationTool()],
        verbose=True
    )

def create_pitch_coordinator(config: Dict) -> Agent:
    """Create the Pitch Coordination Manager agent."""
    return Agent(
        role="Pitch Coordination Manager",
        goal="Oversee the pitch creation process and ensure quality delivery",
        backstory=(
            "You manage the end-to-end pitch creation process, ensuring that all "
            "pitches meet quality standards and are optimized for success. Your "
            "attention to detail and process management skills are exceptional."
        ),
        tools=[],
        verbose=True
    )
