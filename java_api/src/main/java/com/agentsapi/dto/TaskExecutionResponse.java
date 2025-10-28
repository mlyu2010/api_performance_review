package com.agentsapi.dto;

import com.agentsapi.entity.TaskExecution;
import com.agentsapi.enums.ExecutionStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Data Transfer Object (DTO) representing the response for a task execution.
 * <p>
 * This class encapsulates all relevant information about a task execution,
 * including its status, associated task and agent details, execution timestamps,
 * and any results or error messages.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TaskExecutionResponse {
    /**
     * The unique identifier of the task execution.
     */
    private Long id;

    /**
     * The identifier of the task being executed.
     */
    private Long taskId;

    /**
     * The title of the task being executed.
     */
    private String taskTitle;

    /**
     * The identifier of the agent executing the task.
     */
    private Long agentId;

    /**
     * The name of the agent executing the task.
     */
    private String agentName;

    /**
     * The current status of the task execution.
     */
    private ExecutionStatus status;

    /**
     * The timestamp when the task execution started.
     */
    private LocalDateTime startedAt;

    /**
     * The timestamp when the task execution completed.
     */
    private LocalDateTime completedAt;

    /**
     * The result of the task execution, if successful.
     */
    private String result;

    /**
     * The error message if the task execution failed.
     */
    private String errorMessage;

    /**
     * Creates a TaskExecutionResponse instance from a TaskExecution entity.
     * <p>
     * This method maps all relevant fields from the entity to the DTO,
     * including task and agent details.
     * </p>
     *
     * @param execution the TaskExecution entity to convert
     * @return a new TaskExecutionResponse instance containing the entity data
     * @throws IllegalArgumentException if execution is null
     */
    public static TaskExecutionResponse fromEntity(TaskExecution execution) {
        return TaskExecutionResponse.builder()
                .id(execution.getId())
                .taskId(execution.getTask().getId())
                .taskTitle(execution.getTask().getTitle())
                .agentId(execution.getAgent().getId())
                .agentName(execution.getAgent().getName())
                .status(execution.getStatus())
                .startedAt(execution.getStartedAt())
                .completedAt(execution.getCompletedAt())
                .result(execution.getResult())
                .errorMessage(execution.getErrorMessage())
                .build();
    }
}
