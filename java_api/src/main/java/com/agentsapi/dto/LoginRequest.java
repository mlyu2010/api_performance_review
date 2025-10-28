package com.agentsapi.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object (DTO) for handling login request information.
 * <p>
 * This class encapsulates the credentials required for user authentication.
 * It uses validation annotations to ensure required fields are provided.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginRequest {

    /**
     * The username for authentication.
     * <p>
     * This field cannot be blank and is validated using @NotBlank annotation.
     * </p>
     */
    @NotBlank(message = "Username is required")
    private String username;

    /**
     * The password for authentication.
     * <p>
     * This field cannot be blank and is validated using @NotBlank annotation.
     * </p>
     */
    @NotBlank(message = "Password is required")
    private String password;
}
