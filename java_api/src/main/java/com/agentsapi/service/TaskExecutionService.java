package com.agentsapi.service;

import com.agentsapi.dto.TaskExecutionRequest;
import com.agentsapi.dto.TaskExecutionResponse;
import com.agentsapi.entity.Agent;
import com.agentsapi.entity.Task;
import com.agentsapi.entity.TaskExecution;
import com.agentsapi.enums.ExecutionStatus;
import com.agentsapi.exception.InvalidRequestException;
import com.agentsapi.exception.ResourceNotFoundException;
import com.agentsapi.repository.AgentRepository;
import com.agentsapi.repository.TaskExecutionRepository;
import com.agentsapi.repository.TaskRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Service class responsible for managing task executions.
 * Handles the lifecycle of task executions including starting, completing, and failing tasks.
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 10-27-2025
 */
@Service
public class TaskExecutionService {

    @Autowired
    private TaskExecutionRepository taskExecutionRepository;

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private AgentRepository agentRepository;

    /**
     * Starts a new task execution with the given request parameters.
     * Validates the task and agent existence and compatibility before starting the execution.
     *
     * @param request the task execution request containing taskId and agentId
     * @return TaskExecutionResponse containing the execution details
     * @throws ResourceNotFoundException if task or agent is not found
     * @throws InvalidRequestException   if agent is not supported for the task
     */
    @Transactional
    public TaskExecutionResponse startTaskExecution(TaskExecutionRequest request) {
        Task task = taskRepository.findByIdAndDeletedFalse(request.getTaskId())
                .orElseThrow(() -> new ResourceNotFoundException("Task not found with id: " + request.getTaskId()));

        Agent agent = agentRepository.findByIdAndDeletedFalse(request.getAgentId())
                .orElseThrow(() -> new ResourceNotFoundException("Agent not found with id: " + request.getAgentId()));

        // Validate that the agent can run this task
        boolean canRun = task.getSupportedAgents().stream()
                .anyMatch(a -> a.getId().equals(agent.getId()));

        if (!canRun) {
            throw new InvalidRequestException("Agent " + agent.getId() + " is not supported for task " + task.getId());
        }

        TaskExecution execution = TaskExecution.builder()
                .task(task)
                .agent(agent)
                .status(ExecutionStatus.RUNNING)
                .startedAt(LocalDateTime.now())
                .build();

        execution = taskExecutionRepository.save(execution);

        // Simulate async task execution (in real scenario, this would be done asynchronously)
        simulateTaskExecution(execution);

        return TaskExecutionResponse.fromEntity(execution);
    }

    /**
     * Retrieves all currently running task executions.
     *
     * @return List of TaskExecutionResponse for all running tasks
     */
    public List<TaskExecutionResponse> getRunningTasks() {
        return taskExecutionRepository.findByStatus(ExecutionStatus.RUNNING).stream()
                .map(TaskExecutionResponse::fromEntity)
                .collect(Collectors.toList());
    }

    /**
     * Retrieves all task executions regardless of their status.
     *
     * @return List of TaskExecutionResponse for all executions
     */
    public List<TaskExecutionResponse> getAllExecutions() {
        return taskExecutionRepository.findAll().stream()
                .map(TaskExecutionResponse::fromEntity)
                .collect(Collectors.toList());
    }

    /**
     * Retrieves a specific task execution by its ID.
     *
     * @param id the ID of the task execution to retrieve
     * @return TaskExecutionResponse containing the execution details
     * @throws ResourceNotFoundException if execution is not found
     */
    public TaskExecutionResponse getExecutionById(Long id) {
        TaskExecution execution = taskExecutionRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Task execution not found with id: " + id));
        return TaskExecutionResponse.fromEntity(execution);
    }

    // Simulate task execution - in production, this would be async

    /**
     * Simulates task execution in a synchronous manner.
     * This is a placeholder method for demonstration purposes.
     *
     * @param execution the task execution to simulate
     */
    private void simulateTaskExecution(TaskExecution execution) {
        // This is a placeholder. In a real application, you would:
        // 1. Execute the task asynchronously (using @Async or message queue)
        // 2. Update the execution status when complete
        // 3. Store the result or error message
    }

    /**
     * Marks a task execution as completed with the given result.
     *
     * @param executionId the ID of the execution to complete
     * @param result      the result of the task execution
     * @return TaskExecutionResponse containing the updated execution details
     * @throws ResourceNotFoundException if execution is not found
     */
    @Transactional
    public TaskExecutionResponse completeExecution(Long executionId, String result) {
        TaskExecution execution = taskExecutionRepository.findById(executionId)
                .orElseThrow(() -> new ResourceNotFoundException("Task execution not found with id: " + executionId));

        execution.setStatus(ExecutionStatus.COMPLETED);
        execution.setCompletedAt(LocalDateTime.now());
        execution.setResult(result);

        execution = taskExecutionRepository.save(execution);
        return TaskExecutionResponse.fromEntity(execution);
    }

    /**
     * Marks a task execution as failed with the given error message.
     *
     * @param executionId  the ID of the execution to fail
     * @param errorMessage the error message describing the failure
     * @return TaskExecutionResponse containing the updated execution details
     * @throws ResourceNotFoundException if execution is not found
     */
    @Transactional
    public TaskExecutionResponse failExecution(Long executionId, String errorMessage) {
        TaskExecution execution = taskExecutionRepository.findById(executionId)
                .orElseThrow(() -> new ResourceNotFoundException("Task execution not found with id: " + executionId));

        execution.setStatus(ExecutionStatus.FAILED);
        execution.setCompletedAt(LocalDateTime.now());
        execution.setErrorMessage(errorMessage);

        execution = taskExecutionRepository.save(execution);
        return TaskExecutionResponse.fromEntity(execution);
    }
}
