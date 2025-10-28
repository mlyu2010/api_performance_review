package com.agentsapi.dto;

import com.agentsapi.entity.Agent;
import com.agentsapi.entity.Task;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Set;
import java.util.stream.Collectors;

/**
 * Data Transfer Object (DTO) representing a task response in the system.
 * <p>
 * This class is used to transfer task data between layers of the application,
 * particularly when sending task information to clients. It includes essential
 * task information and associated agent IDs.
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
public class TaskResponse {
    /**
     * The unique identifier of the task.
     */
    private Long id;

    /**
     * The title of the task.
     */
    private String title;

    /**
     * The detailed description of the task.
     */
    private String description;

    /**
     * Set of IDs representing the agents that support this task.
     */
    private Set<Long> supportedAgentIds;

    /**
     * Converts a Task entity to its DTO representation.
     * <p>
     * This method transforms a {@link Task} entity into a {@link TaskResponse} DTO,
     * extracting relevant information and handling null cases for supported agents.
     * </p>
     *
     * @param task the task entity to convert; must not be null
     * @return a new {@link TaskResponse} instance containing the task data
     * @throws IllegalArgumentException if task is null
     */
    public static TaskResponse fromEntity(Task task) {
        Set<Long> agentIds = task.getSupportedAgents() != null 
                ? task.getSupportedAgents().stream()
                        .filter(agent -> agent != null && agent.getId() != null)
                        .map(Agent::getId)
                        .collect(Collectors.toSet())
                : Set.of();

        return TaskResponse.builder()
                .id(task.getId())
                .title(task.getTitle())
                .description(task.getDescription())
                .supportedAgentIds(agentIds)
                .build();
    }
}
