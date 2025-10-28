package com.agentsapi.service;

import com.agentsapi.dto.TaskRequest;
import com.agentsapi.dto.TaskResponse;
import com.agentsapi.entity.Agent;
import com.agentsapi.entity.Task;
import com.agentsapi.exception.InvalidRequestException;
import com.agentsapi.exception.ResourceNotFoundException;
import com.agentsapi.repository.AgentRepository;
import com.agentsapi.repository.TaskRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Service class responsible for managing task-related operations.
 * Provides methods for CRUD operations on tasks and their associations with agents.
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 10-27-2025
 */
@Service
@Slf4j
@Transactional(readOnly = true)
public class TaskService {

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private AgentRepository agentRepository;

    /**
     * Retrieves all non-deleted tasks from the database.
     * Includes debug logging for task and agent relationships.
     *
     * @return List of TaskResponse objects representing all active tasks
     */
    public List<TaskResponse> getAllTasks() {
        List<Task> tasks = taskRepository.findByDeletedFalse();

        List<TaskResponse> responses = tasks.stream()
                .map(task -> {
                    TaskResponse response = TaskResponse.fromEntity(task);
                    log.info("\nTaskResponse ID: {} AgentIds:{} ", response.getId(),response.getSupportedAgentIds());
                    return response;
                })
                .collect(Collectors.toList());

        log.info("=== getAllTasks END ===");
        return responses;
    }

    /**
     * Retrieves a specific task by its ID.
     *
     * @param id the ID of the task to retrieve
     * @return TaskResponse object representing the found task
     * @throws ResourceNotFoundException if task is not found or is deleted
     */
    public TaskResponse getTaskById(Long id) {
        Task task = taskRepository.findByIdAndDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("Task not found with id: " + id));
        return TaskResponse.fromEntity(task);
    }

    /**
     * Creates a new task with the provided information.
     *
     * @param request TaskRequest object containing task details and supported agent IDs
     * @return TaskResponse object representing the created task
     * @throws InvalidRequestException if any of the specified agents are not found
     */
    @Transactional
    public TaskResponse createTask(TaskRequest request) {
        Set<Agent> supportedAgents = validateAndGetAgents(request.getSupportedAgentIds());

        Task task = Task.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .supportedAgents(supportedAgents)
                .build();

        task = taskRepository.save(task);
        return TaskResponse.fromEntity(task);
    }

    /**
     * Updates an existing task with new information.
     *
     * @param id      the ID of the task to update
     * @param request TaskRequest object containing updated task details
     * @return TaskResponse object representing the updated task
     * @throws ResourceNotFoundException if task is not found or is deleted
     * @throws InvalidRequestException   if any of the specified agents are not found
     */
    @Transactional
    public TaskResponse updateTask(Long id, TaskRequest request) {
        Task task = taskRepository.findByIdAndDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("Task not found with id: " + id));

        Set<Agent> supportedAgents = validateAndGetAgents(request.getSupportedAgentIds());

        task.setTitle(request.getTitle());
        task.setDescription(request.getDescription());
        task.setSupportedAgents(supportedAgents);

        task = taskRepository.save(task);
        return TaskResponse.fromEntity(task);
    }

    /**
     * Deletes a task by its ID.
     *
     * @param id the ID of the task to delete
     * @throws ResourceNotFoundException if task is not found or is already deleted
     */
    @Transactional
    public void deleteTask(Long id) {
        Task task = taskRepository.findByIdAndDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("Task not found with id: " + id));
        taskRepository.delete(task);
    }

    /**
     * Validates and retrieves a set of agents based on provided IDs.
     *
     * @param agentIds Set of agent IDs to validate and retrieve
     * @return Set of Agent entities corresponding to the provided IDs
     * @throws InvalidRequestException if any agent is not found or is deleted
     */
    private Set<Agent> validateAndGetAgents(Set<Long> agentIds) {
        Set<Agent> agents = new HashSet<>();
        for (Long agentId : agentIds) {
            Agent agent = agentRepository.findByIdAndDeletedFalse(agentId)
                    .orElseThrow(() -> new InvalidRequestException("Agent not found with id: " + agentId));
            agents.add(agent);
        }
        return agents;
    }
}
