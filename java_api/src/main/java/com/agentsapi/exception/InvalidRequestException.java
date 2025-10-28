package com.agentsapi.exception;

/**
 * Exception thrown when a request contains invalid data or violates business rules.
 * <p>
 * This runtime exception is used throughout the application to indicate that
 * a request cannot be processed due to invalid input parameters or state.
 * </p>
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
public class InvalidRequestException extends RuntimeException {
    /**
     * Constructs a new InvalidRequestException with the specified detail message.
     *
     * @param message the detail message explaining the reason for the exception;
     *                this message is saved for later retrieval by the {@link #getMessage()} method
     */
    public InvalidRequestException(String message) {
        super(message);
    }
}
