package com.agentsapi.entity;

import com.agentsapi.enums.ExecutionStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Entity class representing a task execution in the system.
 * <p>
 * A task execution represents a single instance of a task being executed by an agent.
 * It tracks the execution status, timing, results, and any error messages that occur
 * during the execution process.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
@Entity
@Table(name = "task_executions")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TaskExecution {

    /**
     * The unique identifier for this task execution.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * The task being executed.
     * This field establishes a many-to-one relationship with the Task entity.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_id", nullable = false)
    private Task task;

    /**
     * The agent executing the task.
     * This field establishes a many-to-one relationship with the Agent entity.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "agent_id", nullable = false)
    private Agent agent;

    /**
     * The current status of the task execution.
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ExecutionStatus status;

    /**
     * The timestamp when the task execution started.
     */
    @Column(name = "started_at", nullable = false)
    private LocalDateTime startedAt;

    /**
     * The timestamp when the task execution completed.
     * This field is null if the task has not completed.
     */
    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    /**
     * The result of the task execution.
     * This field contains the output or result data from the task execution.
     */
    @Column(columnDefinition = "TEXT")
    private String result;

    /**
     * Any error message that occurred during task execution.
     * This field is populated only if the task execution encountered an error.
     */
    @Column(columnDefinition = "TEXT")
    private String errorMessage;

    /**
     * JPA lifecycle callback method invoked before persisting a new task execution.
     * <p>
     * This method automatically sets the start time to the current time if not specified
     * and initializes the status to RUNNING if not set.
     * </p>
     */
    @PrePersist
    protected void onCreate() {
        if (startedAt == null) {
            startedAt = LocalDateTime.now();
        }
        if (status == null) {
            status = ExecutionStatus.RUNNING;
        }
    }
}
