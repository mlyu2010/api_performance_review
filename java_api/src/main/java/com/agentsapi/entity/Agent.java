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
 * Entity class representing an Agent in the system.
 * <p>
 * This class manages agent data including their basic information and task associations.
 * It implements soft delete functionality through the @SQLDelete annotation and
 * includes automatic timestamp management for creation and updates.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
@Entity
@Table(name = "agents")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@SQLDelete(sql = "UPDATE agents SET deleted = true, deleted_at = NOW() WHERE id = ?")
public class Agent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false)
    private Boolean deleted = false;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    @ManyToMany(mappedBy = "supportedAgents")
    @lombok.ToString.Exclude
    @lombok.EqualsAndHashCode.Exclude
    private Set<Task> tasks = new HashSet<>();

    /**
     * Lifecycle callback method executed before persisting a new Agent entity.
     * <p>
     * Initializes creation and update timestamps to the current time and
     * ensures the deleted flag is set to false if not already set.
     * </p>
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
     * Lifecycle callback method executed before updating an existing Agent entity.
     * <p>
     * Updates the updatedAt timestamp to the current time whenever the entity is modified.
     * </p>
     */
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
