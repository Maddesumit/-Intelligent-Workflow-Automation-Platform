"""Base task executor and implementations."""
from abc import ABC, abstractmethod
from typing import Any, Dict
import httpx
import asyncio
from app.core.logging import logger


class BaseTaskExecutor(ABC):
    """Base class for task executors."""
    
    @abstractmethod
    async def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the task.
        
        Args:
            config: Task configuration
            context: Execution context with data from previous tasks
            
        Returns:
            Task execution result
        """
        pass


class HttpRequestExecutor(BaseTaskExecutor):
    """Executor for HTTP request tasks."""
    
    async def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request."""
        url = config.get("url")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body")
        timeout = config.get("timeout", 30)
        
        logger.info(f"Executing HTTP {method} request to {url}")
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if body else None
                )
                
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text,
                    "success": 200 <= response.status_code < 300
                }
        except Exception as e:
            logger.error(f"HTTP request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class EmailExecutor(BaseTaskExecutor):
    """Executor for email tasks."""
    
    async def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email sending (placeholder for now)."""
        to = config.get("to")
        subject = config.get("subject")
        body = config.get("body")
        
        logger.info(f"Sending email to {to} with subject: {subject}")
        
        # TODO: Integrate with actual email service (SendGrid, Mailgun, etc.) in Phase 5
        # For now, just simulate email sending
        await asyncio.sleep(0.5)  # Simulate sending
        
        return {
            "success": True,
            "to": to,
            "subject": subject,
            "message": "Email sent successfully (simulated)"
        }


class DatabaseExecutor(BaseTaskExecutor):
    """Executor for database tasks."""
    
    async def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database operation (placeholder for now)."""
        operation = config.get("operation")
        table = config.get("table")
        
        logger.info(f"Executing database {operation} on table {table}")
        
        # TODO: Implement actual database operations
        # For now, just simulate
        await asyncio.sleep(0.3)
        
        return {
            "success": True,
            "operation": operation,
            "table": table,
            "message": "Database operation completed (simulated)"
        }


class TransformExecutor(BaseTaskExecutor):
    """Executor for data transformation tasks."""
    
    async def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data transformation."""
        operation = config.get("operation")
        source_field = config.get("source_field")
        target_field = config.get("target_field")
        
        logger.info(f"Executing transformation: {operation}")
        
        try:
            # Get source data from context
            source_data = context.get(source_field, {})
            
            # Simple transformations
            if operation == "uppercase" and isinstance(source_data, str):
                result = source_data.upper()
            elif operation == "lowercase" and isinstance(source_data, str):
                result = source_data.lower()
            elif operation == "extract" and isinstance(source_data, dict):
                extract_key = config.get("extract_key")
                result = source_data.get(extract_key) if extract_key else source_data
            else:
                result = source_data
            
            return {
                "success": True,
                target_field or "result": result
            }
        except Exception as e:
            logger.error(f"Transformation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class ConditionalExecutor(BaseTaskExecutor):
    """Executor for conditional logic tasks."""
    
    async def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conditional logic."""
        condition = config.get("condition")
        
        logger.info(f"Evaluating condition: {condition}")
        
        try:
            # Simple condition evaluation
            # TODO: Implement more sophisticated expression parser in Phase 3
            result = eval(condition, {"__builtins__": {}}, context)
            
            return {
                "success": True,
                "condition_met": bool(result),
                "true_tasks": config.get("true_tasks", []) if result else [],
                "false_tasks": config.get("false_tasks", []) if not result else []
            }
        except Exception as e:
            logger.error(f"Condition evaluation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Task executor registry
TASK_EXECUTORS = {
    "http_request": HttpRequestExecutor(),
    "email": EmailExecutor(),
    "database": DatabaseExecutor(),
    "transform": TransformExecutor(),
    "conditional": ConditionalExecutor(),
}


def get_task_executor(task_type: str) -> BaseTaskExecutor:
    """
    Get task executor for a given task type.
    
    Args:
        task_type: Type of task
        
    Returns:
        Task executor instance
        
    Raises:
        ValueError: If task type is not supported
    """
    executor = TASK_EXECUTORS.get(task_type)
    if not executor:
        raise ValueError(f"Unsupported task type: {task_type}")
    return executor
