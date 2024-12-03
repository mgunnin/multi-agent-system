"""Workflow manager for parallel crew execution."""

import asyncio
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class WorkflowTask:
    """Represents a task in the workflow."""
    name: str
    crew_type: str
    inputs: Dict
    dependencies: List[str]
    callback: Optional[Callable] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None

class WorkflowManager:
    """Manages parallel execution of crew tasks."""
    
    def __init__(self, orchestrator, max_workers: int = 3):
        """Initialize the workflow manager.
        
        Args:
            orchestrator: The VerticalLabsOrchestrator instance
            max_workers: Maximum number of parallel tasks
        """
        self.orchestrator = orchestrator
        self.max_workers = max_workers
        self.tasks: Dict[str, WorkflowTask] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(__name__)
        
    def add_task(
        self,
        name: str,
        crew_type: str,
        inputs: Dict,
        dependencies: Optional[List[str]] = None,
        callback: Optional[Callable] = None
    ) -> None:
        """Add a task to the workflow.
        
        Args:
            name: Unique task name
            crew_type: Type of crew to run (topics, pitch, content)
            inputs: Input parameters for the crew
            dependencies: List of task names this task depends on
            callback: Optional callback function to run after task completion
        """
        self.tasks[name] = WorkflowTask(
            name=name,
            crew_type=crew_type,
            inputs=inputs,
            dependencies=dependencies or [],
            callback=callback
        )
        
    async def run_task(self, task: WorkflowTask) -> None:
        """Run a single task.
        
        Args:
            task: The task to run
        """
        task.started_at = datetime.now()
        task.status = "running"
        self.logger.info(f"Starting task {task.name}")
        
        try:
            # Run the appropriate crew based on type
            if task.crew_type == "topics":
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.orchestrator.run_topics_generation,
                    task.inputs
                )
            elif task.crew_type == "pitch":
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.orchestrator.run_pitch_generation,
                    task.inputs
                )
            elif task.crew_type == "content":
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.orchestrator.run_content_generation,
                    task.inputs
                )
            else:
                raise ValueError(f"Unknown crew type: {task.crew_type}")
                
            task.result = result
            task.status = "completed"
            
            # Run callback if provided
            if task.callback:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    task.callback,
                    result
                )
                
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self.logger.error(f"Task {task.name} failed: {e}")
            
        task.completed_at = datetime.now()
        
    def get_ready_tasks(self) -> List[WorkflowTask]:
        """Get tasks that are ready to run (all dependencies completed)."""
        ready_tasks = []
        for task in self.tasks.values():
            if task.status == "pending":
                dependencies_met = all(
                    self.tasks[dep].status == "completed"
                    for dep in task.dependencies
                )
                if dependencies_met:
                    ready_tasks.append(task)
        return ready_tasks
        
    async def run_workflow(self) -> Dict[str, Dict]:
        """Run all tasks in the workflow respecting dependencies.
        
        Returns:
            Dictionary with results from all tasks
        """
        while True:
            ready_tasks = self.get_ready_tasks()
            if not ready_tasks:
                # Check if all tasks are completed
                if all(t.status in ["completed", "failed"] for t in self.tasks.values()):
                    break
                await asyncio.sleep(1)
                continue
                
            # Run ready tasks in parallel
            await asyncio.gather(
                *(self.run_task(task) for task in ready_tasks)
            )
            
        # Return results
        return {
            name: {
                "status": task.status,
                "result": task.result,
                "error": task.error,
                "started_at": task.started_at,
                "completed_at": task.completed_at
            }
            for name, task in self.tasks.items()
        }
        
    def get_task_status(self, task_name: str) -> Dict:
        """Get the status of a specific task.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Dictionary with task status information
        """
        task = self.tasks.get(task_name)
        if not task:
            raise ValueError(f"Task not found: {task_name}")
            
        return {
            "status": task.status,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "error": task.error
        }
        
    def get_workflow_status(self) -> Dict:
        """Get the status of the entire workflow.
        
        Returns:
            Dictionary with workflow status information
        """
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")
        running = sum(1 for t in self.tasks.values() if t.status == "running")
        pending = sum(1 for t in self.tasks.values() if t.status == "pending")
        
        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
            "tasks": {
                name: {
                    "status": task.status,
                    "dependencies": task.dependencies,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at
                }
                for name, task in self.tasks.items()
            }
        }