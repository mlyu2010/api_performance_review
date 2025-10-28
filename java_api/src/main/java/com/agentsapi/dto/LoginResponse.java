package com.agentsapi.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object (DTO) representing the response after a successful login.
 * <p>
 * This class encapsulates the authentication token, token type, and username
 * that are returned to the client after successful authentication.
 * Lombok annotations are used to generate boilerplate code.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LoginResponse {
    /**
     * The authentication token issued after successful login.
     * <p>
     * This token should be included in subsequent requests as part of
     * the Authorization header for authenticated access.
     * </p>
     */
    private String token;

    /**
     * The type of authentication token.
     * <p>
     * Default value is "Bearer" as per OAuth 2.0 specification.
     * This indicates how the token should be used in the Authorization header.
     * </p>
     */
    private String type = "Bearer";

    /**
     * The username of the authenticated user.
     * <p>
     * This field contains the identifier of the user who successfully
     * logged in to the system.
     * </p>
     */
    private String username;
}
