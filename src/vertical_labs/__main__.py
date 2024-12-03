"""Main entry point for Vertical Labs."""

import os
from dotenv import load_dotenv
from .flow import kickoff, plot

def main():
    """Run the Vertical Labs system."""
    # Load environment variables
    load_dotenv()

    # Example inputs
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
        domain=domain,
        target_audience=target_audience,
        content_goals=content_goals
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
