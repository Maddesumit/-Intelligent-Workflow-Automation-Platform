"""Pydantic schemas for workflows."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema."""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., description="Type of task (http_request, email, database, transform, conditional)")
    configuration: Dict[str, Any] = Field(default_factory=dict)
    order_index: int = Field(default=0, ge=0)


class TaskCreate(TaskBase):
    """Task creation schema."""
    pass


class TaskUpdate(BaseModel):
    """Task update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    order_index: Optional[int] = Field(None, ge=0)


class TaskResponse(TaskBase):
    """Task response schema."""
    id: UUID
    workflow_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowBase(BaseModel):
    """Base workflow schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_active: bool = True


class WorkflowCreate(WorkflowBase):
    """Workflow creation schema."""
    tasks: List[TaskCreate] = Field(default_factory=list)


class WorkflowUpdate(BaseModel):
    """Workflow update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    """Workflow response schema."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class WorkflowListResponse(BaseModel):
    """Workflow list response schema."""
    workflows: List[WorkflowResponse]
    total: int
    page: int
    page_size: int


# Execution Schemas
class WorkflowExecutionRequest(BaseModel):
    """Workflow execution request schema."""
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Input data for workflow")


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response schema."""
    id: UUID
    workflow_id: UUID
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowExecutionListResponse(BaseModel):
    """Workflow execution list response schema."""
    executions: List[WorkflowExecutionResponse]
    total: int
