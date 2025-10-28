package com.agentsapi.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Entity representing a user in the system.
 * <p>
 * This class maps to the 'users' table in the database and contains information
 * about system users including their credentials, role, and creation timestamp.
 * </p>
 */
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    /**
     * Unique identifier for the user.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Unique username for the user.
     * This field cannot be null and must be unique across all users.
     */
    @Column(nullable = false, unique = true)
    private String username;

    /**
     * Encrypted password for the user.
     * This field cannot be null and stores the hashed password.
     */
    @Column(nullable = false)
    private String password;

    /**
     * Role assigned to the user.
     * This field cannot be null and determines user permissions.
     */
    @Column(nullable = false)
    private String role;

    /**
     * Timestamp when the user was created.
     * This field is automatically set during creation and cannot be updated.
     */
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /**
     * Callback method executed before persisting the entity.
     * Sets the creation timestamp to the current date and time.
     */
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
