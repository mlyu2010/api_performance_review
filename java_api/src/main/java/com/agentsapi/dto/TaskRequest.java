package com.agentsapi.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Set;

/**
 * Data Transfer Object (DTO) representing a request to create or update a task.
 * <p>
 * This class encapsulates the necessary information for task operations, including
 * the task's title, description, and the IDs of agents that can support this task.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class TaskRequest {

    /**
     * The title of the task.
     * <p>
     * This field cannot be blank as it serves as a primary identifier for users
     * to recognize the task.
     * </p>
     */
    @NotBlank(message = "Title is required")
    private String title;

    /**
     * The detailed description of the task.
     * <p>
     * This field provides additional information about the task's requirements,
     * objectives, and any specific instructions. It is optional.
     * </p>
     */
    private String description;

    /**
     * The set of agent IDs that can execute this task.
     * <p>
     * This field must contain at least one agent ID to indicate which agents
     * are capable of performing the task.
     * </p>
     */
    @NotEmpty(message = "At least one supported agent ID is required")
    private Set<Long> supportedAgentIds;
}
