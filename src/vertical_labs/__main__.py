"""Main entry point for Vertical Labs."""

import os

from dotenv import load_dotenv

from .orchestrator import VerticalLabsOrchestrator


def main():
    """Run the Vertical Labs system."""
    # Load environment variables
    load_dotenv()

    # Example configuration
    config = {
        "topics_ai": {
            "llm": os.getenv("OPENAI_MODEL_NAME", "gpt-4o"),
            "verbose": True
        },
        "pitch_ai": {
            "llm": os.getenv("OPENAI_MODEL_NAME", "gpt-4o"),
            "verbose": True
        },
        "content_ai": {
            "llm": os.getenv("OPENAI_MODEL_NAME", "gpt-4o"),
            "verbose": True
        }
    }

    # Example inputs
    inputs = {
        "publisher_info": {
            "name": "TechInsights",
            "url": "https://techinsights.com",
            "categories": ["Technology", "AI", "Business"],
            "audience": {
                "type": "B2B",
                "roles": ["CTO", "Tech Leaders", "Developers"],
                "industries": ["Software", "AI/ML", "Enterprise"]
            },
            "locations": ["USA", "Canada"],
            "preferences": {
                "content_length": "1000-1500 words",
                "tone": "professional",
                "style": "analytical",
                "prefers_brevity": True,
                "requires_data": True
            }
        },
        "brand_info": {
            "name": "AI Solutions Inc",
            "category": "AI/ML",
            "target_audience": "B2B",
            "locations": {"USA", "Canada"},
            "expert_name": "Dr. Sarah Smith",
            "expert_title": "Chief AI Officer",
            "unique_value": "Enterprise-grade AI solutions with human-centric design"
        },
        "requirements": {
            "content_types": ["thought_leadership", "technical_analysis"],
            "delivery_timeline": "2 weeks",
            "special_requirements": "Include case studies and ROI metrics"
        }
    }

    # Create and run orchestrator
    orchestrator = VerticalLabsOrchestrator(config)
    results = orchestrator.run_full_pipeline(inputs)

    # Print results summary
    print("\nResults Summary:")
    print(f"Topics Generated: {len(results['topics'].get('topics', []))}")
    print(f"Pitches Created: {len(results['pitches'].get('pitches', []))}")
    print(f"Content Pieces: {len(results['content'])}")


if __name__ == "__main__":
    main()
