package com.agentsapi.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.SQLDelete;
import org.hibernate.annotations.Where;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

/**
 * Entity class representing a Task in the system.
 * <p>
 * This class maps to the 'tasks' table in the database and implements soft delete
 * functionality. Tasks can be associated with multiple agents and maintain audit
 * information such as creation, update, and deletion timestamps.
 * </p>
 */
@Entity
@Table(name = "tasks")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@SQLDelete(sql = "UPDATE tasks SET deleted = true, deleted_at = NOW() WHERE id = ?")
public class Task {

    /**
     * Unique identifier for the task
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Title of the task, required field
     */
    @Column(nullable = false)
    private String title;

    /**
     * Detailed description of the task
     */
    @Column(columnDefinition = "TEXT")
    private String description;

    /**
     * Set of agents that can support/execute this task
     */
    @ManyToMany(fetch = FetchType.EAGER, cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(
            name = "task_supported_agents",
            joinColumns = @JoinColumn(name = "task_id"),
            inverseJoinColumns = @JoinColumn(name = "agent_id")
    )
    @lombok.ToString.Exclude
    private Set<Agent> supportedAgents = new HashSet<>();

    /**
     * Flag indicating if the task has been soft deleted
     */
    @Column(nullable = false)
    private Boolean deleted = false;

    /**
     * Timestamp when the task was created
     */
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /**
     * Timestamp when the task was last updated
     */
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    /**
     * Timestamp when the task was soft deleted
     */
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    /**
     * Lifecycle callback method executed before persisting a new task.
     * Sets the creation and update timestamps and ensures the deleted flag is initialized.
     */
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (deleted == null) {
            deleted = false;
        }
    }

    /**
     * Lifecycle callback method executed before updating an existing task.
     * Updates the last modified timestamp.
     */
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
