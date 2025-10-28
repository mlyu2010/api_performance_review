"""
Database Models Package
======================

This package contains all Tortoise ORM database models for the Agents & Tasks API.

Models
------
User : tortoise.models.Model
    User account model with authentication support.
    Fields: id, username, email, hashed_password, is_active, created_at, updated_at, deleted_at

Agent : tortoise.models.Model
    AI agent model representing autonomous agents that can execute tasks.
    Fields: id, name, description, created_at, updated_at, deleted_at
    Relationships: Many-to-many with Task through TaskAgent

Task : tortoise.models.Model
    Task model representing work items that can be assigned to agents.
    Fields: id, title, description, status, priority, created_at, updated_at, deleted_at
    Relationships: Many-to-many with Agent through TaskAgent, one-to-many with Execution

TaskAgent : tortoise.models.Model
    Many-to-many relationship model linking Tasks and Agents.
    Fields: id, task_id, agent_id, assigned_at

Execution : tortoise.models.Model
    Task execution model tracking the execution of tasks by agents.
    Fields: id, task_id, agent_id, status, started_at, completed_at, result, error_message
    Relationships: Many-to-one with Task, many-to-one with Agent

Database Configuration
---------------------
Models are registered with Tortoise ORM in app/main.py:
    modules={"models": ["app.models"]}

Database tables are created automatically using:
    await Tortoise.generate_schemas()

Soft Deletes
-----------
User, Agent, and Task models support soft deletion via the deleted_at field.
When a record is soft-deleted, deleted_at is set to the current timestamp
instead of removing the record from the database. This allows for:
- Data recovery if needed
- Audit trail preservation
- Referential integrity maintenance

Usage
-----
Import models individually:
    from app.models import User, Agent, Task, Execution

Create a new record:
    user = await User.create(username="john", email="john@example.com")

Query records:
    users = await User.filter(is_active=True).all()
    user = await User.get(id=1)

Update a record:
    user.email = "newemail@example.com"
    await user.save()

Soft delete:
    from datetime import datetime
    user.deleted_at = datetime.utcnow()
    await user.save()
"""

from app.models.user import User
from app.models.agent import Agent
from app.models.task import Task, TaskAgent
from app.models.execution import Execution

__all__ = ["User", "Agent", "Task", "TaskAgent", "Execution"]
