package com.agentsapi.enums;

/**
 * Represents the possible states of a task execution in the system.
 * <p>
 * This enum defines the various states that a task execution can be in during its lifecycle,
 * from initiation to completion or failure.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
public enum ExecutionStatus {
    /**
     * Indicates that the task execution is currently in progress.
     */
    RUNNING,

    /**
     * Indicates that the task execution has successfully completed.
     */
    COMPLETED,

    /**
     * Indicates that the task execution has failed due to an error.
     */
    FAILED,

    /**
     * Indicates that the task execution was cancelled before completion.
     */
    CANCELLED
}
