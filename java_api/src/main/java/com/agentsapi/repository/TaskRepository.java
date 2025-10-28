package com.agentsapi.repository;

import com.agentsapi.entity.Task;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for managing Task entities.
 * Extends JpaRepository to provide standard CRUD operations and custom query methods.
 * All methods in this repository handle soft-delete functionality by filtering deleted tasks.
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 10-27-2025
 */
@Repository
public interface TaskRepository extends JpaRepository<Task, Long> {

    /**
     * Retrieves all non-deleted tasks from the database.
     * This method performs a left join fetch with supported agents to avoid N+1 queries.
     *
     * @return List of all active tasks (not marked as deleted)
     */
    @Query("SELECT DISTINCT t FROM Task t LEFT JOIN FETCH t.supportedAgents a WHERE t.deleted = false AND (a IS NULL OR a.deleted = false)")
    List<Task> findByDeletedFalse();

    /**
     * Finds a non-deleted task by its ID.
     * This method performs a left join fetch with supported agents to avoid N+1 queries.
     *
     * @param id the ID of the task to find
     * @return Optional containing the task if found and not deleted, empty otherwise
     */
    @Query("SELECT DISTINCT t FROM Task t LEFT JOIN FETCH t.supportedAgents a WHERE t.id = :id AND t.deleted = false AND (a IS NULL OR a.deleted = false)")
    Optional<Task> findByIdAndDeletedFalse(@Param("id") Long id);
}
