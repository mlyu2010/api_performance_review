"""
Pydantic Schemas Package
========================

This package contains all Pydantic models for request/response validation.

Schemas are organized by domain:
- auth: Authentication schemas (login, tokens)
- agent: Agent CRUD schemas
- task: Task CRUD schemas
- execution: Execution schemas

Schema Categories
----------------
Each domain typically has three types of schemas:

1. Create schemas (*Create):
   - Used for POST requests creating new records
   - Contains only fields required/allowed for creation
   - Example: AgentCreate, TaskCreate

2. Update schemas (*Update):
   - Used for PUT/PATCH requests updating existing records
   - All fields are optional (partial updates)
   - Example: AgentUpdate, TaskUpdate

3. Response schemas (*Response):
   - Used for API responses (GET, POST, PUT)
   - Includes all fields that should be exposed
   - Includes generated fields (id, timestamps)
   - Example: AgentResponse, TaskResponse

Pydantic Features
----------------
All schemas use Pydantic v2 features:
- Automatic validation of field types
- Field constraints (min_items, max_length, etc.)
- Email validation via EmailStr
- Datetime parsing and serialization
- from_attributes mode for ORM model compatibility

Usage in Routers
---------------
Schemas are used as type hints for request/response validation:

    @router.post("/agents", response_model=AgentResponse)
    async def create_agent(agent_data: AgentCreate):
        # agent_data is validated AgentCreate instance
        agent = await AgentService.create_agent(agent_data)
        # agent is converted to AgentResponse for response
        return agent

Benefits
--------
- Automatic request validation (422 on invalid data)
- Automatic response serialization to JSON
- API documentation generation (OpenAPI/Swagger)
- Type safety and IDE autocomplete
- Clear contract between API and clients

Exported Schemas
---------------
Authentication:
- Token: JWT token response
- LoginRequest: Login credentials

Agents:
- AgentCreate: Create agent request
- AgentUpdate: Update agent request  
- AgentResponse: Agent details response

Tasks:
- TaskCreate: Create task request
- TaskUpdate: Update task request
- TaskResponse: Task details response

Executions:
- ExecutionCreate: Start execution request
- ExecutionResponse: Execution details response
"""

from app.schemas.auth import Token, LoginRequest
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.execution import ExecutionCreate, ExecutionResponse

__all__ = [
    "Token",
    "LoginRequest",
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "ExecutionCreate",
    "ExecutionResponse",
]
