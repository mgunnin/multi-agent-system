"""Streamlit dashboard for CrewAI content generation."""

import streamlit as st
from dotenv import load_dotenv

from vertical_labs.main import kickoff

# Load environment variables
load_dotenv()


def main():
    st.title("CrewAI Content Generation Dashboard")
    st.write("Generate content ideas and pitches for publishers")

    # Create tabs for different sections
    setup_tab, results_tab = st.tabs(["Setup", "Results"])

    with setup_tab:
        st.header("Publisher Information")

        # Publisher details form
        with st.form("publisher_form"):
            col1, col2 = st.columns(2)

            with col1:
                publisher_name = st.text_input(
                    "Publisher Name", value="TechCrunch", help="Name of the publisher"
                )
                publisher_url = st.text_input(
                    "Publisher Website",
                    value="https://techcrunch.com",
                    help="URL of the publisher's website",
                )
                publisher_audience = st.text_input(
                    "Target Audience",
                    value="Tech professionals, entrepreneurs, investors",
                    help="Who is the publisher's target audience?",
                )

            with col2:
                publisher_categories = st.text_area(
                    "Content Categories",
                    value="Technology\nStartups\nAI/ML\nEnterprise",
                    help="One category per line",
                )
                publisher_locations = st.text_area(
                    "Geographic Locations",
                    value="Global\nUSA\nEurope",
                    help="One location per line",
                )

            st.header("Content Strategy")
            domain = st.text_input(
                "Domain/Industry",
                value="Enterprise AI Solutions",
                help="The specific domain or industry to focus on",
            )

            content_goals = st.text_area(
                "Content Goals",
                value="""Create thought leadership and technical analysis content that:
- Demonstrates expertise in enterprise-grade AI solutions
- Includes case studies and ROI metrics
- Maintains professional tone and analytical style
- Targets content length of 1000-1500 words
- Emphasizes human-centric design in AI implementations""",
                help="Goals and requirements for the content",
            )

            submitted = st.form_submit_button("Generate Content")

            if submitted:
                # Store the inputs in session state
                st.session_state.inputs = {
                    "publisher_name": publisher_name,
                    "publisher_url": publisher_url,
                    "publisher_categories": [
                        cat.strip()
                        for cat in publisher_categories.split("\n")
                        if cat.strip()
                    ],
                    "publisher_audience": publisher_audience,
                    "publisher_locations": [
                        loc.strip()
                        for loc in publisher_locations.split("\n")
                        if loc.strip()
                    ],
                    "domain": domain,
                    "content_goals": content_goals,
                }

                # Show a spinner while processing
                with st.spinner("Running CrewAI..."):
                    try:
                        results = kickoff(
                            publisher_name=publisher_name,
                            publisher_url=publisher_url,
                            publisher_categories=st.session_state.inputs[
                                "publisher_categories"
                            ],
                            publisher_audience=publisher_audience,
                            publisher_locations=st.session_state.inputs[
                                "publisher_locations"
                            ],
                            domain=domain,
                            content_goals=content_goals,
                        )
                        st.session_state.results = results
                        st.success("Content generation complete!")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

    with results_tab:
        if "results" in st.session_state:
            results = st.session_state.results

            # Display Topics
            st.header("Generated Topics")
            for i, topic in enumerate(results.topics, 1):
                with st.expander(f"Topic {i}: {topic.title}"):
                    st.write("**Description:**", topic.description)
                    st.write("**Keywords:**", ", ".join(topic.keywords))

            # Display Content Items
            st.header("Generated Content")
            for i, content in enumerate(results.content_items, 1):
                with st.expander(f"Content {i}: {content.title}"):
                    st.write("**Content:**")
                    st.markdown(content.content)
                    if content.metadata:
                        st.write("**Metadata:**")
                        st.json(content.metadata)

            # Display Pitches
            st.header("Generated Pitches")
            for i, pitch in enumerate(results.pitches, 1):
                with st.expander(f"Pitch {i}: {pitch.title}"):
                    st.write("**Pitch:**")
                    st.markdown(pitch.pitch)
                    st.write("**Target Audience:**", pitch.target_audience)

        else:
            st.info("Submit the form to generate content and see results here.")


if __name__ == "__main__":
    main()
