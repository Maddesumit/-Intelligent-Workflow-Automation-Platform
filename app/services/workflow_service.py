"""Workflow service for business logic."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Workflow, Task, WorkflowExecution
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    TaskCreate,
)
from app.core.logging import logger


class WorkflowService:
    """Service for workflow operations."""
    
    @staticmethod
    async def create_workflow(
        db: AsyncSession,
        workflow_data: WorkflowCreate,
        user_id: UUID
    ) -> Workflow:
        """
        Create a new workflow with tasks.
        
        Args:
            db: Database session
            workflow_data: Workflow creation data
            user_id: ID of the user creating the workflow
            
        Returns:
            Created workflow
        """
        # Create workflow
        workflow = Workflow(
            user_id=user_id,
            name=workflow_data.name,
            description=workflow_data.description,
            configuration=workflow_data.configuration,
            is_active=workflow_data.is_active,
        )
        
        db.add(workflow)
        await db.flush()
        
        # Create tasks
        for task_data in workflow_data.tasks:
            task = Task(
                workflow_id=workflow.id,
                name=task_data.name,
                type=task_data.type,
                configuration=task_data.configuration,
                order_index=task_data.order_index,
            )
            db.add(task)
        
        await db.commit()
        await db.refresh(workflow)
        
        # Load tasks relationship
        query = (
            select(Workflow)
            .options(selectinload(Workflow.tasks))
            .where(Workflow.id == workflow.id)
        )
        result = await db.execute(query)
        workflow = result.scalar_one()
        
        logger.info(f"Created workflow {workflow.id} with {len(workflow_data.tasks)} tasks")
        return workflow
    
    @staticmethod
    async def get_workflow(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID
    ) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        
        Args:
            db: Database session
            workflow_id: Workflow ID
            user_id: User ID for authorization
            
        Returns:
            Workflow or None
        """
        query = (
            select(Workflow)
            .options(selectinload(Workflow.tasks))
            .where(Workflow.id == workflow_id, Workflow.user_id == user_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_workflows(
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> tuple[List[Workflow], int]:
        """
        List workflows with pagination.
        
        Args:
            db: Database session
            user_id: User ID for filtering
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            
        Returns:
            Tuple of (workflows list, total count)
        """
        # Build query
        query = select(Workflow).where(Workflow.user_id == user_id)
        
        if is_active is not None:
            query = query.where(Workflow.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get workflows with tasks
        query = (
            query
            .options(selectinload(Workflow.tasks))
            .offset(skip)
            .limit(limit)
            .order_by(Workflow.created_at.desc())
        )
        
        result = await db.execute(query)
        workflows = result.scalars().all()
        
        return list(workflows), total
    
    @staticmethod
    async def update_workflow(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID,
        workflow_data: WorkflowUpdate
    ) -> Optional[Workflow]:
        """
        Update a workflow.
        
        Args:
            db: Database session
            workflow_id: Workflow ID
            user_id: User ID for authorization
            workflow_data: Update data
            
        Returns:
            Updated workflow or None
        """
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return None
        
        # Update fields
        update_data = workflow_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        await db.commit()
        await db.refresh(workflow)
        
        logger.info(f"Updated workflow {workflow_id}")
        return workflow
    
    @staticmethod
    async def delete_workflow(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a workflow.
        
        Args:
            db: Database session
            workflow_id: Workflow ID
            user_id: User ID for authorization
            
        Returns:
            True if deleted, False if not found
        """
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return False
        
        await db.delete(workflow)
        await db.commit()
        
        logger.info(f"Deleted workflow {workflow_id}")
        return True
    
    @staticmethod
    async def get_workflow_executions(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[WorkflowExecution], int]:
        """
        Get execution history for a workflow.
        
        Args:
            db: Database session
            workflow_id: Workflow ID
            user_id: User ID for authorization
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (executions list, total count)
        """
        # Verify workflow belongs to user
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return [], 0
        
        # Get total count
        count_query = select(func.count()).where(WorkflowExecution.workflow_id == workflow_id)
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get executions
        query = (
            select(WorkflowExecution)
            .where(WorkflowExecution.workflow_id == workflow_id)
            .offset(skip)
            .limit(limit)
            .order_by(WorkflowExecution.created_at.desc())
        )
        
        result = await db.execute(query)
        executions = result.scalars().all()
        
        return list(executions), total
