package com.agentsapi.controller;

import com.agentsapi.dto.TaskExecutionRequest;
import com.agentsapi.dto.TaskExecutionResponse;
import com.agentsapi.service.TaskExecutionService;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller responsible for managing task execution operations.
 * Provides endpoints for starting tasks, retrieving running tasks,
 * and querying task execution status.
 */
@RestController
@RequestMapping("/executions")
public class TaskExecutionController {

    @Autowired
    private TaskExecutionService taskExecutionService;

    /**
     * Initiates a new task execution based on the provided request.
     *
     * @param request The task execution request containing necessary parameters
     * @return ResponseEntity containing the TaskExecutionResponse with HTTP status CREATED
     */
    @PostMapping("/start")
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<TaskExecutionResponse> startTaskExecution(@Valid @RequestBody TaskExecutionRequest request) {
        TaskExecutionResponse execution = taskExecutionService.startTaskExecution(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(execution);
    }

    /**
     * Retrieves a list of currently running task executions.
     *
     * @return ResponseEntity containing a list of TaskExecutionResponse for running tasks
     */
    @GetMapping("/running")
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<List<TaskExecutionResponse>> getRunningTasks() {
        List<TaskExecutionResponse> runningTasks = taskExecutionService.getRunningTasks();
        return ResponseEntity.ok(runningTasks);
    }

    /**
     * Retrieves a list of all task executions in the system.
     *
     * @return ResponseEntity containing a list of all TaskExecutionResponse objects
     */
    @GetMapping
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<List<TaskExecutionResponse>> getAllExecutions() {
        List<TaskExecutionResponse> executions = taskExecutionService.getAllExecutions();
        return ResponseEntity.ok(executions);
    }

    /**
     * Retrieves a specific task execution by its ID.
     *
     * @param id The ID of the task execution to retrieve
     * @return ResponseEntity containing the TaskExecutionResponse for the specified ID
     */
    @GetMapping("/{id}")
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<TaskExecutionResponse> getExecutionById(@PathVariable Long id) {
        TaskExecutionResponse execution = taskExecutionService.getExecutionById(id);
        return ResponseEntity.ok(execution);
    }
}
