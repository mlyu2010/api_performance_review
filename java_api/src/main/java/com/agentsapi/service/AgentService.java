package com.agentsapi.service;

import com.agentsapi.dto.AgentRequest;
import com.agentsapi.dto.AgentResponse;
import com.agentsapi.entity.Agent;
import com.agentsapi.exception.ResourceNotFoundException;
import com.agentsapi.repository.AgentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Service class for managing Agent entities.
 * Provides business logic for CRUD operations on agents.
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 10-27-2025
 */
@Service
public class AgentService {

    @Autowired
    private AgentRepository agentRepository;

    /**
     * Retrieves all non-deleted agents from the system.
     *
     * @return List of AgentResponse objects representing all active agents
     */
    public List<AgentResponse> getAllAgents() {
        return agentRepository.findByDeletedFalse().stream()
                .map(AgentResponse::fromEntity)
                .collect(Collectors.toList());
    }

    /**
     * Retrieves a specific agent by their ID.
     *
     * @param id the ID of the agent to retrieve
     * @return AgentResponse object representing the found agent
     * @throws ResourceNotFoundException if no agent is found with the given ID
     */
    public AgentResponse getAgentById(Long id) {
        Agent agent = agentRepository.findByIdAndDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("Agent not found with id: " + id));
        return AgentResponse.fromEntity(agent);
    }

    /**
     * Creates a new agent in the system.
     *
     * @param request the AgentRequest containing the agent details
     * @return AgentResponse object representing the created agent
     */
    @Transactional
    public AgentResponse createAgent(AgentRequest request) {
        Agent agent = Agent.builder()
                .name(request.getName())
                .description(request.getDescription())
                .build();

        agent = agentRepository.save(agent);
        return AgentResponse.fromEntity(agent);
    }

    /**
     * Updates an existing agent's information.
     *
     * @param id      the ID of the agent to update
     * @param request the AgentRequest containing the updated agent details
     * @return AgentResponse object representing the updated agent
     * @throws ResourceNotFoundException if no agent is found with the given ID
     */
    @Transactional
    public AgentResponse updateAgent(Long id, AgentRequest request) {
        Agent agent = agentRepository.findByIdAndDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("Agent not found with id: " + id));

        agent.setName(request.getName());
        agent.setDescription(request.getDescription());

        agent = agentRepository.save(agent);
        return AgentResponse.fromEntity(agent);
    }

    /**
     * Deletes an agent from the system.
     *
     * @param id the ID of the agent to delete
     * @throws ResourceNotFoundException if no agent is found with the given ID
     */
    @Transactional
    public void deleteAgent(Long id) {
        Agent agent = agentRepository.findByIdAndDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("Agent not found with id: " + id));
        agentRepository.delete(agent);
    }

    /**
     * Checks if an agent exists by their ID.
     *
     * @param id the ID of the agent to check
     * @return true if the agent exists and is not deleted, false otherwise
     */
    public boolean existsById(Long id) {
        return agentRepository.findByIdAndDeletedFalse(id).isPresent();
    }
}
