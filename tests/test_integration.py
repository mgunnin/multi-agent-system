"""Integration tests for Vertical Labs system."""

from datetime import datetime
from typing import Dict

import pytest

from vertical_labs.monitoring import PerformanceMonitor
from vertical_labs.orchestrator import VerticalLabsOrchestrator
from vertical_labs.storage import ResultsStorage
from vertical_labs.workflow import WorkflowManager


@pytest.fixture
def config() -> Dict:
    """Test configuration fixture."""
    return {
        "topics_ai": {
            "llm": "gpt-4",
            "verbose": True
        },
        "pitch_ai": {
            "llm": "gpt-4",
            "verbose": True
        },
        "content_ai": {
            "llm": "gpt-4",
            "verbose": True
        }
    }

@pytest.fixture
def test_inputs() -> Dict:
    """Test inputs fixture."""
    return {
        "publisher_info": {
            "name": "TechTest",
            "url": "https://techtest.com",
            "categories": ["Technology", "AI"],
            "audience": {
                "type": "B2B",
                "roles": ["CTO", "Developers"],
                "industries": ["Software"]
            },
            "locations": ["USA"],
            "preferences": {
                "content_length": "1000-1500",
                "tone": "professional",
                "style": "technical"
            }
        },
        "brand_info": {
            "name": "TestAI",
            "category": "AI/ML",
            "target_audience": "B2B",
            "locations": {"USA"},
            "expert_name": "Dr. Test",
            "expert_title": "CTO",
            "unique_value": "Testing AI solutions"
        },
        "requirements": {
            "content_types": ["technical"],
            "delivery_timeline": "1 week",
            "special_requirements": "Include code examples"
        }
    }

@pytest.fixture
def orchestrator(config: Dict) -> VerticalLabsOrchestrator:
    """Orchestrator fixture."""
    return VerticalLabsOrchestrator(config)

@pytest.fixture
def workflow_manager(orchestrator: VerticalLabsOrchestrator) -> WorkflowManager:
    """Workflow manager fixture."""
    return WorkflowManager(orchestrator, max_workers=2)

@pytest.fixture
def monitor() -> PerformanceMonitor:
    """Performance monitor fixture."""
    return PerformanceMonitor("./test_metrics")

@pytest.fixture
def storage() -> ResultsStorage:
    """Results storage fixture."""
    return ResultsStorage("./test_results.db")

def test_topics_generation(
    orchestrator: VerticalLabsOrchestrator,
    test_inputs: Dict,
    monitor: PerformanceMonitor,
    storage: ResultsStorage
):
    """Test topics generation."""
    run_id = f"test_topics_{datetime.now().timestamp()}"

    # Start monitoring
    monitor.start_monitoring(run_id, "topics", 1)

    # Store run
    storage.store_run(run_id, "topics")

    try:
        # Generate topics
        results = orchestrator.run_topics_generation(test_inputs)

        # Verify results
        assert results is not None
        assert "topics" in results
        assert isinstance(results["topics"], list)
        assert len(results["topics"]) > 0

        # Store results
        storage.store_result(
            run_id,
            "topics",
            results["topics"]
        )

        # Update run status
        storage.update_run_status(run_id, "completed")

        # Log completion
        monitor.log_task_completion(
            run_id,
            "topics_generation",
            True,
            1000,  # Example token count
            0.02  # Example cost
        )

    except Exception as e:
        storage.update_run_status(run_id, "failed")
        monitor.log_error(run_id, str(e))
        raise

    finally:
        # End monitoring
        metrics = monitor.end_monitoring(run_id)
        assert metrics["crew_type"] == "topics"
        assert metrics["num_completed"] > 0

@pytest.mark.asyncio
async def test_parallel_workflow(
    workflow_manager: WorkflowManager,
    test_inputs: Dict,
    monitor: PerformanceMonitor,
    storage: ResultsStorage
):
    """Test parallel workflow execution."""
    workflow_id = f"test_workflow_{datetime.now().timestamp()}"

    # Add tasks to workflow
    workflow_manager.add_task(
        "topics_1",
        "topics",
        test_inputs
    )

    workflow_manager.add_task(
        "topics_2",
        "topics",
        test_inputs
    )

    workflow_manager.add_task(
        "pitch_1",
        "pitch",
        test_inputs,
        dependencies=["topics_1"]
    )

    workflow_manager.add_task(
        "pitch_2",
        "pitch",
        test_inputs,
        dependencies=["topics_2"]
    )

    workflow_manager.add_task(
        "content_1",
        "content",
        test_inputs,
        dependencies=["pitch_1"]
    )

    # Run workflow
    results = await workflow_manager.run_workflow()

    # Verify results
    assert len(results) == 5
    assert all(r["status"] == "completed" for r in results.values())

    # Export workflow results
    workflow_results = storage.export_workflow_results(workflow_id)
    assert len(workflow_results["runs"]) == 5

def test_full_pipeline(
    orchestrator: VerticalLabsOrchestrator,
    test_inputs: Dict,
    monitor: PerformanceMonitor,
    storage: ResultsStorage
):
    """Test the complete pipeline."""
    workflow_id = f"test_pipeline_{datetime.now().timestamp()}"

    # Run full pipeline
    results = orchestrator.run_full_pipeline(test_inputs)

    # Verify results structure
    assert "topics" in results
    assert "pitches" in results
    assert "content" in results
    assert "metadata" in results

    # Verify topics
    assert len(results["topics"]["topics"]) > 0

    # Verify pitches
    assert len(results["pitches"]["pitches"]) > 0

    # Verify content
    assert len(results["content"]) > 0

    # Export results
    workflow_results = storage.export_workflow_results(workflow_id)
    assert len(workflow_results["runs"]) > 0

def test_error_handling(
    orchestrator: VerticalLabsOrchestrator,
    test_inputs: Dict,
    monitor: PerformanceMonitor,
    storage: ResultsStorage
):
    """Test error handling."""
    run_id = f"test_error_{datetime.now().timestamp()}"

    # Start monitoring
    monitor.start_monitoring(run_id, "topics", 1)

    # Store run
    storage.store_run(run_id, "topics")

    try:
        # Trigger an error by passing invalid inputs
        invalid_inputs = {}
        orchestrator.run_topics_generation(invalid_inputs)

    except Exception as e:
        # Verify error handling
        storage.update_run_status(run_id, "failed")
        monitor.log_error(run_id, str(e))

        # Check error was logged
        metrics = monitor.get_metrics(run_id)
        assert len(metrics["errors"]) > 0

        # Check run status
        run_info = storage.get_run(run_id)
        assert run_info["status"] == "failed"
