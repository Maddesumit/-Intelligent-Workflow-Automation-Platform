"""Workflow execution engine."""
from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Workflow, Task, WorkflowExecution
from app.workers.task_executors import get_task_executor
from app.core.logging import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class WorkflowExecutor:
    """Executes workflows with dependency resolution."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def execute_workflow(
        self,
        workflow_id: UUID,
        input_data: Dict[str, Any] = None
    ) -> WorkflowExecution:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of workflow to execute
            input_data: Input data for workflow execution
            
        Returns:
            WorkflowExecution record
        """
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status="running",
            started_at=datetime.utcnow(),
            result={}
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        logger.info(f"Starting workflow execution {execution.id} for workflow {workflow_id}")
        
        try:
            # Load workflow with tasks
            query = (
                select(Workflow)
                .options(selectinload(Workflow.tasks))
                .where(Workflow.id == workflow_id)
            )
            result = await self.db.execute(query)
            workflow = result.scalar_one_or_none()
            
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if not workflow.is_active:
                raise ValueError(f"Workflow {workflow_id} is not active")
            
            # Execute tasks
            execution_result = await self._execute_tasks(
                workflow.tasks,
                input_data or {}
            )
            
            # Update execution record
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.execution_time = int(
                (execution.completed_at - execution.started_at).total_seconds()
            )
            execution.result = execution_result
            
            logger.info(f"Workflow execution {execution.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow execution {execution.id} failed: {str(e)}")
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            execution.execution_time = int(
                (execution.completed_at - execution.started_at).total_seconds()
            )
        
        await self.db.commit()
        await self.db.refresh(execution)
        return execution
    
    async def _execute_tasks(
        self,
        tasks: List[Task],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tasks in order.
        
        Args:
            tasks: List of tasks to execute
            input_data: Input data for execution
            
        Returns:
            Execution result
        """
        # Sort tasks by order_index
        sorted_tasks = sorted(tasks, key=lambda t: t.order_index)
        
        # Execution context to store results
        context = {"input": input_data}
        task_results = {}
        
        for task in sorted_tasks:
            logger.info(f"Executing task {task.name} (type: {task.type})")
            
            try:
                # Get executor for task type
                executor = get_task_executor(task.type)
                
                # Execute task
                task_result = await executor.execute(task.configuration, context)
                
                # Store result in context
                task_results[task.name] = task_result
                context[task.name] = task_result
                
                logger.info(f"Task {task.name} completed successfully")
                
            except Exception as e:
                logger.error(f"Task {task.name} failed: {str(e)}")
                task_results[task.name] = {
                    "success": False,
                    "error": str(e)
                }
                # Continue with other tasks or fail entire workflow?
                # For now, we'll continue
        
        return {
            "tasks": task_results,
            "context": context
        }


async def execute_workflow_async(
    workflow_id: str,
    input_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Execute workflow asynchronously (for Celery tasks).
    
    Args:
        workflow_id: Workflow ID as string
        input_data: Input data for execution
        
    Returns:
        Execution result
    """
    from app.core.database import AsyncSessionLocal
    from uuid import UUID
    
    async with AsyncSessionLocal() as db:
        executor = WorkflowExecutor(db)
        execution = await executor.execute_workflow(
            UUID(workflow_id),
            input_data
        )
        
        return {
            "execution_id": str(execution.id),
            "status": execution.status,
            "result": execution.result,
            "error": execution.error_message
        }
