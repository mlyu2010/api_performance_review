package com.agentsapi.repository;

import com.agentsapi.entity.Agent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for managing Agent entities.
 * Extends JpaRepository to provide standard CRUD operations and custom query methods.
 * All methods in this repository handle soft-delete functionality by filtering deleted agents.
 */
@Repository
public interface AgentRepository extends JpaRepository<Agent, Long> {

    /**
     * Retrieves all non-deleted agents from the database.
     *
     * @return List of all active agents (not marked as deleted)
     */
    @Query("SELECT a FROM Agent a WHERE a.deleted = false")
    List<Agent> findByDeletedFalse();

    /**
     * Finds a non-deleted agent by its ID.
     *
     * @param id the ID of the agent to find
     * @return Optional containing the agent if found and not deleted, empty otherwise
     */
    @Query("SELECT a FROM Agent a WHERE a.id = :id AND a.deleted = false")
    Optional<Agent> findByIdAndDeletedFalse(Long id);

    /**
     * Retrieves all non-deleted agents with IDs from the provided list.
     *
     * @param ids list of agent IDs to search for
     * @return List of active agents (not deleted) whose IDs are in the provided list
     */
    @Query("SELECT a FROM Agent a WHERE a.id IN :ids AND a.deleted = false")
    List<Agent> findAllByIdInAndDeletedFalse(List<Long> ids);
}
