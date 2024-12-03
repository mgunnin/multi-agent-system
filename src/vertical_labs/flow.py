from typing import List, Optional
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start

from vertical_labs.contentai.crew import ContentCrew
from vertical_labs.pitchai.crew import PitchCrew
from vertical_labs.topicsai.crew import TopicsCrew

class ContentItem(BaseModel):
    title: str
    content: str
    metadata: dict

class Topic(BaseModel):
    title: str
    description: str
    keywords: List[str]

class Pitch(BaseModel):
    title: str
    pitch: str
    target_audience: str

class VerticalLabsState(BaseModel):
    topics: List[Topic] = []
    content_items: List[ContentItem] = []
    pitches: List[Pitch] = []
    domain: str = ""
    target_audience: str = ""
    content_goals: str = ""

class VerticalLabsFlow(Flow[VerticalLabsState]):
    initial_state = VerticalLabsState

    @start()
    def discover_topics(self):
        print("Starting Topics Discovery")
        output = (
            TopicsCrew()
            .crew()
            .kickoff(inputs={
                "domain": self.state.domain,
                "target_audience": self.state.target_audience
            })
        )
        
        self.state.topics = output["topics"]
        return self.state.topics

    @listen(discover_topics)
    async def generate_content(self):
        print("Generating Content")
        content_tasks = []
        
        for topic in self.state.topics:
            output = (
                ContentCrew()
                .crew()
                .kickoff(inputs={
                    "topic": topic.title,
                    "description": topic.description,
                    "keywords": topic.keywords,
                    "content_goals": self.state.content_goals
                })
            )
            
            content_item = ContentItem(
                title=output["title"],
                content=output["content"],
                metadata=output["metadata"]
            )
            self.state.content_items.append(content_item)

        return self.state.content_items

    @listen(generate_content)
    async def create_pitches(self):
        print("Creating Pitches")
        
        for content_item in self.state.content_items:
            output = (
                PitchCrew()
                .crew()
                .kickoff(inputs={
                    "content_title": content_item.title,
                    "content": content_item.content,
                    "target_audience": self.state.target_audience
                })
            )
            
            pitch = Pitch(
                title=output["title"],
                pitch=output["pitch"],
                target_audience=output["target_audience"]
            )
            self.state.pitches.append(pitch)

        return self.state.pitches

def kickoff(domain: str, target_audience: str, content_goals: str):
    flow = VerticalLabsFlow()
    flow.state.domain = domain
    flow.state.target_audience = target_audience
    flow.state.content_goals = content_goals
    return flow.kickoff()

def plot():
    flow = VerticalLabsFlow()
    flow.plot()