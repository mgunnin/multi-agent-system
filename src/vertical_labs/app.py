"""Streamlit dashboard for CrewAI content generation."""

import streamlit as st
from dotenv import load_dotenv

from vertical_labs.main import kickoff

# Load environment variables
load_dotenv()


def initialize_session_state():
    """Initialize session state variables."""
    if "step" not in st.session_state:
        st.session_state.step = 1  # 1: Initial Input, 2: Topics, 3: Pitches, 4: Content
    if "progress" not in st.session_state:
        st.session_state.progress = {
            "topics": {"status": "Not Started", "details": []},
            "content": {"status": "Not Started", "details": []},
            "pitches": {"status": "Not Started", "details": []},
        }
    if "selected_topics" not in st.session_state:
        st.session_state.selected_topics = []
    if "selected_pitches" not in st.session_state:
        st.session_state.selected_pitches = []
    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = []


def show_step_indicator():
    """Display the current step in the process."""
    steps = {
        1: "Publisher Analysis",
        2: "Topic Selection",
        3: "Pitch Selection",
        4: "Content Generation",
    }

    cols = st.columns(len(steps))
    for step_num, step_name in steps.items():
        with cols[step_num - 1]:
            if step_num == st.session_state.step:
                st.markdown(f"**:blue[{step_name}]**")
            elif step_num < st.session_state.step:
                st.markdown(f"~~{step_name}~~")
            else:
                st.markdown(step_name)


def update_progress(stage: str, status: str, detail: str):
    """Update the progress state in Streamlit."""
    if stage in st.session_state.progress:
        st.session_state.progress[stage]["status"] = status
        st.session_state.progress[stage]["details"].append(detail)

        # Add agent message to conversation
        if "Agent:" in detail:
            agent_name = detail.split("Agent:")[1].split("\n")[0].strip()
            message = detail.split("Task:")[1].strip() if "Task:" in detail else detail
            st.session_state.agent_messages.append(
                {"agent": agent_name, "message": message}
            )


def show_agent_conversation():
    """Display the agent conversation in a chat-like interface."""
    st.header("Agent Conversation")

    for msg in st.session_state.agent_messages:
        with st.chat_message(msg["agent"]):
            st.write(msg["message"])


def show_progress():
    """Show the progress sidebar."""
    st.header("Progress")

    # Topics Progress
    st.subheader("Topics Discovery")
    st.write(f"Status: {st.session_state.progress['topics']['status']}")
    if st.session_state.progress["topics"]["details"]:
        for detail in st.session_state.progress["topics"]["details"]:
            st.write(f"- {detail}")

    # Content Progress
    st.subheader("Content Generation")
    st.write(f"Status: {st.session_state.progress['content']['status']}")
    if st.session_state.progress["content"]["details"]:
        for detail in st.session_state.progress["content"]["details"]:
            st.write(f"- {detail}")

    # Pitches Progress
    st.subheader("Pitch Creation")
    st.write(f"Status: {st.session_state.progress['pitches']['status']}")
    if st.session_state.progress["pitches"]["details"]:
        for detail in st.session_state.progress["pitches"]["details"]:
            st.write(f"- {detail}")


def publisher_input():
    """Show the initial publisher input form."""
    st.header("Publisher Information")

    with st.form("publisher_form"):
        publisher_name = st.text_input(
            "Publisher Name", value="TechCrunch", help="Name of the publisher"
        )
        publisher_url = st.text_input(
            "Publisher Website",
            value="https://techcrunch.com",
            help="URL of the publisher's website",
        )

        submitted = st.form_submit_button("Analyze Publisher")

        if submitted:
            # Clear previous progress and messages
            st.session_state.progress = {
                "topics": {"status": "Not Started", "details": []},
                "content": {"status": "Not Started", "details": []},
                "pitches": {"status": "Not Started", "details": []},
            }
            st.session_state.agent_messages = []

            with st.spinner("Analyzing publisher website..."):
                try:
                    # Start with topics discovery
                    st.session_state.progress["topics"]["status"] = "In Progress"
                    st.session_state.progress["topics"]["details"].append(
                        "Starting publisher analysis..."
                    )

                    results = kickoff(
                        publisher_name=publisher_name,
                        publisher_url=publisher_url,
                        publisher_categories=[],  # Will be determined by analysis
                        publisher_audience="",  # Will be determined by analysis
                        publisher_locations=[],  # Will be determined by analysis
                        progress_callback=update_progress,
                    )

                    st.session_state.results = results
                    st.session_state.step = 2  # Move to topic selection
                    st.rerun()

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


def topic_selection():
    """Show the topic selection interface."""
    st.header("Select Topics to Develop")

    if "results" in st.session_state and st.session_state.results.topics:
        topics = st.session_state.results.topics

        # Create checkboxes for each topic
        selected_topics = []
        for topic in topics:
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                if st.checkbox("", key=f"topic_{topic.title}"):
                    selected_topics.append(topic)
            with col2:
                with st.expander(topic.title):
                    st.write("**Description:**", topic.description)
                    st.write("**Keywords:**", ", ".join(topic.keywords))

        if st.button("Generate Pitches for Selected Topics") and selected_topics:
            st.session_state.selected_topics = selected_topics
            st.session_state.step = 3  # Move to pitch selection
            st.rerun()
    else:
        st.info("No topics generated yet. Please analyze a publisher first.")


def pitch_selection():
    """Show the pitch selection interface."""
    st.header("Select Pitches to Develop")

    if "results" in st.session_state and st.session_state.results.pitches:
        pitches = st.session_state.results.pitches

        # Create checkboxes for each pitch
        selected_pitches = []
        for pitch in pitches:
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                if st.checkbox("", key=f"pitch_{pitch.title}"):
                    selected_pitches.append(pitch)
            with col2:
                with st.expander(pitch.title):
                    st.write("**Pitch:**", pitch.pitch)
                    st.write("**Target Audience:**", pitch.target_audience)

        if st.button("Generate Content for Selected Pitches") and selected_pitches:
            st.session_state.selected_pitches = selected_pitches
            st.session_state.step = 4  # Move to content generation
            st.rerun()
    else:
        st.info("No pitches generated yet. Please select topics first.")


def content_generation():
    """Show the content generation results."""
    st.header("Generated Content")

    if "results" in st.session_state and st.session_state.results.content_items:
        for content in st.session_state.results.content_items:
            with st.expander(content.title):
                st.write("**Content:**")
                st.markdown(content.content)
                if content.metadata:
                    st.write("**Metadata:**")
                    st.json(content.metadata)
    else:
        st.info("No content generated yet. Please select pitches first.")


def main():
    st.title("CrewAI Content Generation Dashboard")

    # Initialize session state
    initialize_session_state()

    # Show step indicator
    show_step_indicator()

    # Create two columns: main content and progress
    col1, col2 = st.columns([2, 1])

    with col1:
        # Show the appropriate interface based on the current step
        if st.session_state.step == 1:
            publisher_input()
        elif st.session_state.step == 2:
            topic_selection()
        elif st.session_state.step == 3:
            pitch_selection()
        elif st.session_state.step == 4:
            content_generation()

    with col2:
        show_progress()
        show_agent_conversation()


if __name__ == "__main__":
    main()
