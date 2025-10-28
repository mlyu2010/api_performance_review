package com.agentsapi.controller;

import com.agentsapi.dto.AgentRequest;
import com.agentsapi.dto.AgentResponse;
import com.agentsapi.service.AgentService;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for managing Agent resources.
 * Provides endpoints for CRUD operations on agents.
 * All endpoints require Bearer token authentication.
 */
@RestController
@RequestMapping("/agents")
public class AgentController {

    @Autowired
    private AgentService agentService;

    /**
     * Retrieves all agents from the system.
     *
     * @return ResponseEntity containing a list of all agents
     */
    @GetMapping
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<List<AgentResponse>> getAllAgents() {
        List<AgentResponse> agents = agentService.getAllAgents();
        return ResponseEntity.ok(agents);
    }

    /**
     * Retrieves a specific agent by their ID.
     *
     * @param id the ID of the agent to retrieve
     * @return ResponseEntity containing the requested agent
     */
    @GetMapping("/{id}")
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<AgentResponse> getAgentById(@PathVariable Long id) {
        AgentResponse agent = agentService.getAgentById(id);
        return ResponseEntity.ok(agent);
    }

    /**
     * Creates a new agent.
     *
     * @param request the agent details in the request body
     * @return ResponseEntity containing the created agent
     */
    @PostMapping
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<AgentResponse> createAgent(@Valid @RequestBody AgentRequest request) {
        AgentResponse agent = agentService.createAgent(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(agent);
    }

    /**
     * Updates an existing agent.
     *
     * @param id      the ID of the agent to update
     * @param request the updated agent details
     * @return ResponseEntity containing the updated agent
     */
    @PutMapping("/{id}")
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<AgentResponse> updateAgent(@PathVariable Long id, @Valid @RequestBody AgentRequest request) {
        AgentResponse agent = agentService.updateAgent(id, request);
        return ResponseEntity.ok(agent);
    }

    /**
     * Deletes an agent by their ID.
     *
     * @param id the ID of the agent to delete
     * @return ResponseEntity with no content
     */
    @DeleteMapping("/{id}")
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<Void> deleteAgent(@PathVariable Long id) {
        agentService.deleteAgent(id);
        return ResponseEntity.noContent().build();
    }
}
