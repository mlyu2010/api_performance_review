package com.agentsapi.exception;

/**
 * Exception thrown when a requested resource cannot be found in the system.
 * <p>
 * This runtime exception is used to indicate that a requested resource
 * (such as an Agent, Task, or User) does not exist or cannot be accessed.
 * It extends RuntimeException to be unchecked, allowing for cleaner code
 * in the service layer.
 * </p>
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
public class ResourceNotFoundException extends RuntimeException {
    /**
     * Constructs a new ResourceNotFoundException with the specified detail message.
     *
     * @param message the detail message explaining the reason for the exception
     */
    public ResourceNotFoundException(String message) {
        super(message);
    }
}
