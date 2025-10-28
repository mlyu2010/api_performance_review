package com.agentsapi.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object (DTO) representing the request to create or update an agent.
 * Used for handling incoming API requests related to agent management.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgentRequest {

    /**
     * The name of the agent. This field is required and cannot be blank.
     */
    @NotBlank(message = "Name is required")
    private String name;

    /**
     * Optional description of the agent providing additional details about its purpose or functionality.
     */
    private String description;
}
