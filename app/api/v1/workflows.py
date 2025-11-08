"""Workflow API endpoints."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.workflow_service import WorkflowService
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowExecutionListResponse,
)
from app.workers.tasks import execute_workflow as execute_workflow_task
from app.workers.workflow_executor import WorkflowExecutor


router = APIRouter()


# Temporary user ID (will be replaced with actual auth in Phase 7)
TEMP_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new workflow.
    
    - **name**: Workflow name
    - **description**: Optional description
    - **tasks**: List of tasks to include in the workflow
    - **configuration**: Additional configuration options
    - **is_active**: Whether the workflow is active
    """
    created_workflow = await WorkflowService.create_workflow(
        db=db,
        workflow_data=workflow,
        user_id=TEMP_USER_ID
    )
    return created_workflow


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all workflows with pagination.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **is_active**: Optional filter by active status
    """
    workflows, total = await WorkflowService.list_workflows(
        db=db,
        user_id=TEMP_USER_ID,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return WorkflowListResponse(
        workflows=workflows,
        total=total,
        page=page,
        page_size=limit
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific workflow by ID.
    
    - **workflow_id**: UUID of the workflow
    """
    workflow = await WorkflowService.get_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=TEMP_USER_ID
    )
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_update: WorkflowUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a workflow.
    
    - **workflow_id**: UUID of the workflow
    - **name**: Updated name (optional)
    - **description**: Updated description (optional)
    - **configuration**: Updated configuration (optional)
    - **is_active**: Updated active status (optional)
    """
    workflow = await WorkflowService.update_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=TEMP_USER_ID,
        workflow_data=workflow_update
    )
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a workflow.
    
    - **workflow_id**: UUID of the workflow to delete
    """
    deleted = await WorkflowService.delete_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=TEMP_USER_ID
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: UUID,
    execution_request: WorkflowExecutionRequest = WorkflowExecutionRequest(),
    background: bool = Query(False, description="Execute in background with Celery"),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a workflow.
    
    - **workflow_id**: UUID of the workflow to execute
    - **input_data**: Optional input data for the workflow
    - **background**: If true, execute in background using Celery
    """
    # Verify workflow exists
    workflow = await WorkflowService.get_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=TEMP_USER_ID
    )
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    if background:
        # Execute in background with Celery
        task = execute_workflow_task.delay(
            str(workflow_id),
            execution_request.input_data
        )
        
        # Return a pending execution response
        return WorkflowExecutionResponse(
            id=UUID(task.id) if task.id else UUID("00000000-0000-0000-0000-000000000000"),
            workflow_id=workflow_id,
            status="pending",
            result={"task_id": task.id, "message": "Workflow execution started in background"},
            created_at=workflow.created_at
        )
    else:
        # Execute synchronously
        executor = WorkflowExecutor(db)
        execution = await executor.execute_workflow(
            workflow_id=workflow_id,
            input_data=execution_request.input_data
        )
        return execution


@router.get("/{workflow_id}/executions", response_model=WorkflowExecutionListResponse)
async def get_workflow_executions(
    workflow_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get execution history for a workflow.
    
    - **workflow_id**: UUID of the workflow
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    executions, total = await WorkflowService.get_workflow_executions(
        db=db,
        workflow_id=workflow_id,
        user_id=TEMP_USER_ID,
        skip=skip,
        limit=limit
    )
    
    return WorkflowExecutionListResponse(
        executions=executions,
        total=total
    )
