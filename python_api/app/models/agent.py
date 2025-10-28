"""
Agent Model Module
=================

This module defines the Agent model for AI agent management.

The Agent model represents autonomous AI agents that can be assigned to tasks
and execute them. Agents can be assigned to multiple tasks through a many-to-many
relationship.

Database Table
-------------
Table name: agents

Fields:
- id: Primary key (auto-increment integer)
- name: Agent name, varchar(255), indexed for fast lookups
- description: Agent description and capabilities (text field)
- created_at: Timestamp (auto-populated on creation)
- updated_at: Timestamp (auto-updated on modification)
- deleted_at: Timestamp for soft deletes (nullable)

Relationships
------------
- Many-to-many with Task through TaskAgent intermediate model
- One-to-many with Execution (executions performed by this agent)

Access related data:
    # Get all tasks assigned to an agent
    tasks = await agent.tasks.all()

    # Get all executions by an agent
    executions = await agent.executions.all()

Soft Delete Support
------------------
Agents support soft deletion via the deleted_at field. When deleted_at is set,
the agent is considered deleted but remains in the database for audit purposes.

Usage Examples
-------------
Create an agent:
    agent = await Agent.create(
        name="Data Analyzer",
        description="Analyzes data and generates reports"
    )

Query agents:
    # All active agents (not soft-deleted)
    agents = await Agent.filter(deleted_at__isnull=True).all()

    # Find by name
    agent = await Agent.filter(name="Data Analyzer").first()

Update an agent:
    agent.description = "Enhanced data analysis capabilities"
    await agent.save()

Soft delete an agent:
    from datetime import datetime
    agent.deleted_at = datetime.utcnow()
    await agent.save()
"""

from tortoise import fields
from tortoise.models import Model


class Agent(Model):
    """
    Agent model representing an AI agent that can execute tasks.

    An agent is an autonomous entity with specific capabilities that can be
    assigned to tasks. Agents maintain a name, description of their capabilities,
    and support soft deletion for data retention.

    Attributes
    ----------
    id : int
        Primary key, auto-incremented
    name : str
        Agent name, max 255 characters, indexed for fast lookups
        Examples: "Data Analyzer", "Report Generator", "Email Processor"
    description : str
        Detailed description of the agent's capabilities and purpose
        Text field with no length limit
    created_at : datetime
        Timestamp when the agent was created, auto-populated
    updated_at : datetime
        Timestamp when the agent was last modified, auto-updated
    deleted_at : datetime, optional
        Timestamp when the agent was soft-deleted, None if active

    Relationships (Reverse)
    ----------------------
    tasks : ManyToManyRelation[Task]
        Tasks assigned to this agent (via TaskAgent intermediate model)
        Access with: await agent.tasks.all()

    executions : ReverseRelation[Execution]
        Executions performed by this agent
        Access with: await agent.executions.all()

    Methods
    -------
    __str__()
        String representation showing agent ID and name

    Examples
    --------
    Create a new agent:
        agent = await Agent.create(
            name="Data Processor",
            description="Processes and validates incoming data streams"
        )

    Get agent with related tasks:
        agent = await Agent.get(id=1)
        tasks = await agent.tasks.filter(status="pending").all()

    Soft delete an agent:
        from datetime import datetime
        agent.deleted_at = datetime.utcnow()
        await agent.save()

    Query active agents:
        active_agents = await Agent.filter(deleted_at__isnull=True).all()
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, index=True)
    description = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    # Relationships
    # The many-to-many relationship is defined in Task model
    # Access tasks through: agent.tasks (reverse relation)

    class Meta:
        table = "agents"

    def __str__(self):
        """
        Return a string representation of the Agent.

        Returns
        -------
        str
            String in format "Agent(id={id}, name={name})"

        Examples
        --------
        >>> agent = Agent(id=1, name="Data Analyzer")
        >>> str(agent)
        'Agent(id=1, name=Data Analyzer)'
        """
        return f"Agent(id={self.id}, name={self.name})"
