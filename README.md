# Vertical Labs Multi-Agent System

A multi-agentic system using CrewAI for generating topics, creating pitches, and producing content at scale. Features parallel execution, performance monitoring, and results storage.

## Overview

The system consists of three interconnected crews:

1. **TopicsAI Crew**
   - Generates relevant topics for publishers
   - Analyzes trends and audience needs
   - Ensures topic diversity and quality
   - Agents:
     - Topic Researcher
     - Audience Analyst
     - Content Strategist
     - SEO Specialist
     - Quality Assurer
     - Topic Coordinator

2. **PitchAI Crew**
   - Creates compelling PR pitches
   - Matches brands with topics and publishers
   - Optimizes pitches for success
   - Agents:
     - Brand Analyst
     - Pitch Writer
     - Media Relations Specialist
     - Pitch Coordinator

3. **ContentAI Crew**
   - Produces high-quality content
   - Ensures editorial standards
   - Optimizes for engagement
   - Agents:
     - Content Researcher
     - Content Writer
     - Content Editor
     - Content Optimizer
     - Content Coordinator

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL_NAME=gpt-4o
APIFY_API_TOKEN=your_apify_token
DATAFORSEO_LOGIN=your_dataforseo_login
DATAFORSEO_PASSWORD=your_dataforseo_password
DIFFBOT_API_KEY=your_diffbot_key
```

## Usage

### Basic Usage

```python
from vertical_labs.orchestrator import VerticalLabsOrchestrator

# Create configuration
config = {
    "topics_ai": {"llm": "gpt-4"},
    "pitch_ai": {"llm": "gpt-4"},
    "content_ai": {"llm": "gpt-4"}
}

# Initialize orchestrator
orchestrator = VerticalLabsOrchestrator(config)

# Run individual crews
topics = orchestrator.run_topics_generation(topics_inputs)
pitches = orchestrator.run_pitch_generation(pitch_inputs)
content = orchestrator.run_content_generation(content_inputs)

# Or run the full pipeline
results = orchestrator.run_full_pipeline(inputs)
```

### Command Line

```bash
# Run the full pipeline with example inputs
python -m vertical_labs
```

## Architecture

The system uses a hierarchical structure:

1. **Orchestrator**: Coordinates all crews and manages the flow of data
2. **Crews**: Specialized teams focused on specific tasks
3. **Agents**: Individual AI agents with specific roles and tools
4. **Tools**: Custom implementations for various tasks

## Tools

- **News Tools**
  - TwitterTrendsTool: Fetches trending topics
  - NewsScraperTool: Gathers news articles
  - GoogleNewsTool: Searches Google News

- **Content Tools**
  - WebsiteAnalyzerTool: Analyzes website content
  - EditorialGuidelinesTool: Manages content guidelines
  - ContentDiversityTool: Ensures content variety

- **Pitch Tools**
  - PitchGeneratorTool: Creates PR pitches
  - BrandMatchingTool: Matches brands with opportunities
  - PitchOptimizationTool: Optimizes pitch success

## Advanced Features

### Parallel Execution

The system supports parallel execution of tasks using the WorkflowManager:

```python
from vertical_labs.workflow import WorkflowManager

workflow = WorkflowManager(orchestrator)
workflow.add_task("topics_1", "topics", inputs)
workflow.add_task("topics_2", "topics", inputs)
workflow.add_task("pitch_1", "pitch", inputs, dependencies=["topics_1"])

results = await workflow.run_workflow()
```

### Performance Monitoring

Monitor crew performance and collect metrics:

```python
from vertical_labs.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_monitoring("run_1", "topics", num_tasks=5)

# Log task completion
monitor.log_task_completion("run_1", "task_1", success=True, tokens=1000, cost=0.02)

# Get metrics
metrics = monitor.get_metrics("run_1")
stats = monitor.get_crew_stats("topics", days=30)
```

### Results Storage

Store and retrieve results using SQLite:

```python
from vertical_labs.storage import ResultsStorage

storage = ResultsStorage()

# Store results
storage.store_run("run_1", "topics")
result_id = storage.store_result("run_1", "topics", content)
storage.store_relationship(source_id, target_id, "derived_from")

# Retrieve results
results = storage.get_results(run_id="run_1")
related = storage.get_related_results(result_id)
workflow = storage.export_workflow_results(workflow_id)
```

## Testing

Run the test suite:

```bash
# Install test dependencies
poetry install --with=dev

# Run tests
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
