"""Pydantic schemas for tasks."""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl


# Task Configuration Schemas for different task types

class HttpRequestTaskConfig(BaseModel):
    """HTTP Request task configuration."""
    url: str = Field(..., description="URL to send request to")
    method: str = Field(default="GET", description="HTTP method (GET, POST, PUT, DELETE, PATCH)")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    retry_count: int = Field(default=3, ge=0, le=10)


class EmailTaskConfig(BaseModel):
    """Email task configuration."""
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body (supports templates)")
    cc: Optional[str] = None
    bcc: Optional[str] = None
    html: bool = Field(default=False, description="Whether body is HTML")


class DatabaseTaskConfig(BaseModel):
    """Database task configuration."""
    operation: str = Field(..., description="Operation type (select, insert, update, delete)")
    query: Optional[str] = Field(None, description="SQL query (for select)")
    table: Optional[str] = Field(None, description="Table name")
    data: Optional[Dict[str, Any]] = Field(None, description="Data for insert/update")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions for update/delete")


class TransformTaskConfig(BaseModel):
    """Data transformation task configuration."""
    operation: str = Field(..., description="Transformation operation (map, filter, reduce, extract)")
    source_field: Optional[str] = Field(None, description="Source data field")
    target_field: Optional[str] = Field(None, description="Target data field")
    transform_expression: Optional[str] = Field(None, description="Transformation expression")
    script: Optional[str] = Field(None, description="Python script for transformation")


class ConditionalTaskConfig(BaseModel):
    """Conditional logic task configuration."""
    condition: str = Field(..., description="Condition expression to evaluate")
    true_tasks: list[str] = Field(default_factory=list, description="Task IDs to execute if true")
    false_tasks: list[str] = Field(default_factory=list, description="Task IDs to execute if false")
