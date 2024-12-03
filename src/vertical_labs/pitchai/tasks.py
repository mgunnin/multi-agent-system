"""PitchAI crew tasks."""

from typing import Dict, List
from crewai import Task
from .agents import (
    create_brand_analyst,
    create_pitch_writer,
    create_media_relations_specialist,
    create_pitch_coordinator
)

def create_brand_analysis_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for analyzing brand-publisher fit."""
    return Task(
        description="Analyze the brand's fit with available topics and publishers using "
                   "the BrandMatchingTool. Consider brand values, target market, and "
                   "unique selling propositions.",
        expected_output="A prioritized list of brand-topic-publisher matches with "
                       "detailed rationale for each match.",
        agent=agents["brand_analyst"]
    )

def create_pitch_writing_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for writing initial pitches."""
    return Task(
        description="Create compelling PR pitches for the high-priority matches using "
                   "PitchGeneratorTool. Ensure each pitch highlights the unique value "
                   "proposition and aligns with the topic.",
        expected_output="A set of initial PR pitches with subject lines, body content, "
                       "and calls to action.",
        agent=agents["pitch_writer"],
        context=["brand_analysis_task"]
    )

def create_pitch_optimization_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for optimizing pitches."""
    return Task(
        description="Optimize each pitch using PitchOptimizationTool based on publisher "
                   "preferences and historical data. Refine language, structure, and "
                   "timing for maximum impact.",
        expected_output="A set of optimized pitches with publisher-specific adjustments "
                       "and timing recommendations.",
        agent=agents["media_relations_specialist"],
        context=["pitch_writing_task"]
    )

def create_final_review_task(agents: Dict[str, Agent], context: Dict) -> Task:
    """Create task for final pitch review and preparation."""
    return Task(
        description="Review and finalize all pitches ensuring quality, consistency, and "
                   "strategic alignment. Prepare delivery schedule and tracking system.",
        expected_output="Final pitch package with delivery schedule and success metrics "
                       "tracking plan.",
        agent=agents["pitch_coordinator"],
        context=["pitch_optimization_task"]
    )