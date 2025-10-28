"""
Task Model Module
================

This module defines the Task and TaskAgent models for task management.

The Task model represents work items that can be assigned to and executed by
AI agents. Tasks support many-to-many relationships with agents through the
TaskAgent junction table.

Database Tables
--------------
1. tasks: Main task table
2. task_agents: Junction table for Task-Agent many-to-many relationship

Task Fields:
- id: Primary key (auto-increment integer)
- title: Task title, varchar(255), indexed for fast lookups
- description: Detailed task description (text field)
- status: Task execution status (pending, running, completed, failed)
- created_at: Timestamp (auto-populated on creation)
- updated_at: Timestamp (auto-updated on modification)
- deleted_at: Timestamp for soft deletes (nullable)

TaskAgent Fields:
- id: Primary key
- task_id: Foreign key to tasks table
- agent_id: Foreign key to agents table
- created_at: Timestamp when assignment was created
- Unique constraint: (task_id, agent_id) - prevents duplicate assignments

Relationships
------------
Task has:
- Many-to-many with Agent through TaskAgent
- One-to-many with Execution (task executions)

Access related data:
    # Get all agents assigned to a task
    agents = await task.agents.all()

    # Get all executions of a task
    executions = await task.executions.all()

Status Values
------------
Tasks can have the following status values:
- 'pending': Task created but not yet running
- 'running': Task is currently being executed
- 'completed': Task execution finished successfully
- 'failed': Task execution failed

Usage Examples
-------------
Create a task:
    task = await Task.create(
        title="Process Data",
        description="Process incoming data and generate report"
    )

Assign agents to a task:
    agents = await Agent.filter(id__in=[1, 2, 3]).all()
    await task.agents.add(*agents)

Query tasks by status:
    pending_tasks = await Task.filter(status="pending", deleted_at__isnull=True).all()

Get task with agents:
    task = await Task.get(id=1).prefetch_related("agents")
    agent_names = [agent.name for agent in task.agents]
"""

from tortoise import fields
from tortoise.models import Model


class Task(Model):
    """
    Task model representing a work item that can be executed by agents.

    A task is a discrete unit of work with a title, description, and status.
    Tasks can be assigned to multiple agents through a many-to-many relationship,
    allowing different agents with appropriate capabilities to execute the same task.

    Attributes
    ----------
    id : int
        Primary key, auto-incremented
    title : str
        Task title, max 255 characters, indexed for fast lookups
        Examples: "Process Payment", "Generate Report", "Send Email"
    description : str
        Detailed task description including requirements and expected outcomes
        Text field with no length limit
    status : str
        Current task execution status, max 50 characters
        Valid values: 'pending', 'running', 'completed', 'failed'
        Default: 'pending'
    created_at : datetime
        Timestamp when the task was created, auto-populated
    updated_at : datetime
        Timestamp when the task was last modified, auto-updated
    deleted_at : datetime, optional
        Timestamp when the task was soft-deleted, None if active

    Relationships
    ------------
    agents : ManyToManyRelation[Agent]
        Agents that can execute this task (via TaskAgent junction table)
        Access with: await task.agents.all()

    executions : ReverseRelation[Execution]
        Executions of this task
        Access with: await task.executions.all()

    task_agents : ReverseRelation[TaskAgent]
        Direct access to TaskAgent junction records

    Methods
    -------
    __str__()
        String representation showing task ID and title

    Examples
    --------
    Create a task with agents:
        task = await Task.create(
            title="Data Analysis",
            description="Analyze sales data and generate insights"
        )
        analyst_agent = await Agent.get(name="Data Analyst")
        await task.agents.add(analyst_agent)

    Update task status:
        task.status = "running"
        await task.save()

    Query tasks with specific status:
        completed_tasks = await Task.filter(
            status="completed",
            deleted_at__isnull=True
        ).all()
    """
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, index=True)
    description = fields.TextField()
    status = fields.CharField(max_length=50, default="pending")  # pending, running, completed, failed
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    # Many-to-many relationship with agents through TaskAgent
    agents = fields.ManyToManyField(
        "models.Agent",
        related_name="tasks",
        through="task_agents",
        backward_key="task_id",
        forward_key="agent_id"
    )

    class Meta:
        table = "tasks"

    def __str__(self):
        """
        Return a string representation of the Task.

        Returns
        -------
        str
            String in format "Task(id={id}, title={title})"

        Examples
        --------
        >>> task = Task(id=1, title="Process Data")
        >>> str(task)
        'Task(id=1, title=Process Data)'
        """
        return f"Task(id={self.id}, title={self.title})"


class TaskAgent(Model):
    """
    Junction table model for Task-Agent many-to-many relationship.

    This model represents the assignment of an agent to a task, creating a
    many-to-many relationship between tasks and agents. Each record indicates
    that a specific agent is authorized and capable of executing a specific task.

    The unique constraint on (task, agent) ensures that an agent cannot be
    assigned to the same task multiple times.

    Attributes
    ----------
    id : int
        Primary key, auto-incremented
    task : ForeignKeyRelation[Task]
        Reference to the task being assigned
        Cascade delete: If task is deleted, this record is deleted
    agent : ForeignKeyRelation[Agent]
        Reference to the agent being assigned
        Cascade delete: If agent is deleted, this record is deleted
    created_at : datetime
        Timestamp when the assignment was created, auto-populated

    Relationships
    ------------
    task : ForeignKeyRelation[Task]
        The task in this assignment (via task.task_agents)
    agent : ForeignKeyRelation[Agent]
        The agent in this assignment (via agent.agent_tasks)

    Constraints
    ----------
    unique_together : (task, agent)
        Ensures an agent can only be assigned to a task once

    Examples
    --------
    Direct creation (not recommended - use Task.agents.add() instead):
        task_agent = await TaskAgent.create(task_id=1, agent_id=2)

    Recommended way to assign agents to tasks:
        task = await Task.get(id=1)
        agent = await Agent.get(id=2)
        await task.agents.add(agent)

    Query all tasks for an agent:
        agent = await Agent.get(id=1)
        tasks = await agent.tasks.all()

    Query all agents for a task:
        task = await Task.get(id=1)
        agents = await task.agents.all()

    Notes
    -----
    This is an explicit junction table. Tortoise ORM could create this
    automatically, but an explicit model allows for additional fields
    (like created_at) and better control over the relationship.
    """
    id = fields.IntField(pk=True)
    task = fields.ForeignKeyField("models.Task", related_name="task_agents", on_delete=fields.CASCADE)
    agent = fields.ForeignKeyField("models.Agent", related_name="agent_tasks", on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "task_agents"
        unique_together = (("task", "agent"),)
