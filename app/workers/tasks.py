"""Celery tasks for workflow execution."""
from celery import Task
from app.workers.celery_app import celery_app
from app.core.logging import logger


class CallbackTask(Task):
    """Base task with callbacks."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Success callback."""
        logger.info(f"Task {task_id} succeeded with result: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback."""
        logger.error(f"Task {task_id} failed with error: {exc}")


@celery_app.task(base=CallbackTask, bind=True, name="app.workers.tasks.test_task")
def test_task(self, x: int, y: int):
    """
    Test task for Celery.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        int: Sum of x and y
    """
    logger.info(f"Executing test_task with x={x}, y={y}")
    result = x + y
    logger.info(f"Test task result: {result}")
    return result


@celery_app.task(base=CallbackTask, bind=True, name="app.workers.tasks.execute_workflow")
def execute_workflow(self, workflow_id: str, input_data: dict = None):
    """
    Execute a workflow.
    
    Args:
        workflow_id: UUID of the workflow to execute
        input_data: Input data for workflow execution
    
    Returns:
        dict: Execution result
    """
    import asyncio
    from app.workers.workflow_executor import execute_workflow_async
    
    logger.info(f"Starting workflow execution: {workflow_id}")
    
    try:
        # Run async workflow execution
        result = asyncio.run(execute_workflow_async(workflow_id, input_data))
        logger.info(f"Workflow execution completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        return {
            "workflow_id": workflow_id,
            "status": "failed",
            "error": str(e)
        }
