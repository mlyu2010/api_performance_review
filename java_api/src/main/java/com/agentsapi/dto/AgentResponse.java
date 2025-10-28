package com.agentsapi.dto;

import com.agentsapi.entity.Agent;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object (DTO) representing an agent response.
 * <p>
 * This class is used to transfer agent data between layers of the application,
 * particularly when responding to API requests. It contains only the essential
 * agent information that needs to be exposed to clients.
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
public class AgentResponse {
    private Long id;
    private String name;
    private String description;

    /**
     * Converts an Agent entity to its DTO representation.
     * <p>
     * This static factory method creates a new AgentResponse instance from
     * an Agent entity, copying only the necessary fields for the response.
     * </p>
     *
     * @param agent the Agent entity to convert
     * @return a new AgentResponse containing the agent's data
     */
    public static AgentResponse fromEntity(Agent agent) {
        return AgentResponse.builder()
                .id(agent.getId())
                .name(agent.getName())
                .description(agent.getDescription())
                .build();
    }
}
