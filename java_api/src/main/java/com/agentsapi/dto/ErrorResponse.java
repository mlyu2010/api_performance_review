package com.agentsapi.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * A data transfer object (DTO) that represents an error response in the API.
 * <p>
 * This class encapsulates error details including timestamp, HTTP status,
 * error description, message, and the request path that caused the error.
 * It is typically used for consistent error handling across the API.
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
public class ErrorResponse {
    /**
     * The timestamp when the error occurred.
     */
    private LocalDateTime timestamp;

    /**
     * The HTTP status code of the error response.
     */
    private int status;

    /**
     * A brief description of the error type.
     */
    private String error;

    /**
     * A detailed message describing the error.
     */
    private String message;

    /**
     * The request path that triggered the error.
     */
    private String path;
}
