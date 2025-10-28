package com.agentsapi.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object (DTO) for creating a new task execution request.
 * <p>
 * This class represents the request payload for initiating a new task execution,
 * containing the necessary identifiers for both the task to be executed and the
 * agent that will perform the execution.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class TaskExecutionRequest {

    /**
     * The unique identifier of the task to be executed.
     * <p>
     * This field must not be null as it identifies the specific task
     * that needs to be executed by the agent.
     * </p>
     */
    @NotNull(message = "Task ID is required")
    private Long taskId;

    /**
     * The unique identifier of the agent that will execute the task.
     * <p>
     * This field must not be null as it identifies the specific agent
     * that will be responsible for executing the task.
     * </p>
     */
    @NotNull(message = "Agent ID is required")
    private Long agentId;
}
