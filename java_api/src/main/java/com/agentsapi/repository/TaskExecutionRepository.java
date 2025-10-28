package com.agentsapi.repository;

import com.agentsapi.entity.TaskExecution;
import com.agentsapi.enums.ExecutionStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository interface for managing TaskExecution entities.
 * Provides methods for querying task executions based on their status and task ID.
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2023-10-27
 */
@Repository
public interface TaskExecutionRepository extends JpaRepository<TaskExecution, Long> {
    /**
     * Finds all task executions with the specified status.
     *
     * @param status the execution status to search for
     * @return list of task executions matching the given status
     */
    List<TaskExecution> findByStatus(ExecutionStatus status);

    /**
     * Finds all task executions for a specific task ID and status.
     *
     * @param taskId the ID of the task
     * @param status the execution status to search for
     * @return list of task executions matching the given task ID and status
     */
    List<TaskExecution> findByTaskIdAndStatus(Long taskId, ExecutionStatus status);
}
