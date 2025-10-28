package com.agentsapi.exception;

import com.agentsapi.dto.ErrorResponse;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Global exception handler for the application.
 * <p>
 * This class provides centralized exception handling across all controllers
 * using Spring's {@link RestControllerAdvice}. It handles various exceptions
 * and converts them into appropriate HTTP responses with detailed error information.
 * </p>
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 2025-10-27
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * Handles ResourceNotFoundException and converts it to an HTTP response.
     * <p>
     * This method handles cases where a requested resource is not found in the system.
     * It returns an HTTP 404 NOT FOUND response with details about the error.
     * </p>
     *
     * @param ex      the ResourceNotFoundException that was thrown
     * @param request the HTTP request that caused the exception
     * @return ResponseEntity containing error details with HTTP 404 status
     */
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFoundException(
            ResourceNotFoundException ex, HttpServletRequest request) {

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.NOT_FOUND.value())
                .error(HttpStatus.NOT_FOUND.getReasonPhrase())
                .message(ex.getMessage())
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    /**
     * Handles InvalidRequestException and converts it to an HTTP response.
     * <p>
     * This method handles cases where the client request is invalid or malformed.
     * It returns an HTTP 400 BAD REQUEST response with details about the error.
     * </p>
     *
     * @param ex      the InvalidRequestException that was thrown
     * @param request the HTTP request that caused the exception
     * @return ResponseEntity containing error details with HTTP 400 status
     */
    @ExceptionHandler(InvalidRequestException.class)
    public ResponseEntity<ErrorResponse> handleInvalidRequestException(
            InvalidRequestException ex, HttpServletRequest request) {

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.BAD_REQUEST.value())
                .error(HttpStatus.BAD_REQUEST.getReasonPhrase())
                .message(ex.getMessage())
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }

    /**
     * Handles validation exceptions and converts them to an HTTP response.
     * <p>
     * This method processes Spring's validation exceptions and creates a detailed
     * error response containing all validation errors. It returns an HTTP 400
     * BAD REQUEST response with a map of field-specific error messages.
     * </p>
     *
     * @param ex      the MethodArgumentNotValidException that was thrown
     * @param request the HTTP request that caused the exception
     * @return ResponseEntity containing a map of validation errors with HTTP 400 status
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationExceptions(
            MethodArgumentNotValidException ex, HttpServletRequest request) {

        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });

        Map<String, Object> response = new HashMap<>();
        response.put("timestamp", LocalDateTime.now());
        response.put("status", HttpStatus.BAD_REQUEST.value());
        response.put("error", "Validation Failed");
        response.put("errors", errors);
        response.put("path", request.getRequestURI());

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handles authentication failures and converts them to an HTTP response.
     * <p>
     * This method handles cases where authentication fails due to invalid credentials.
     * It returns an HTTP 404 NOT FOUND response with a generic error message to
     * avoid revealing specific authentication failure reasons.
     * </p>
     *
     * @param ex      the BadCredentialsException that was thrown
     * @param request the HTTP request that caused the exception
     * @return ResponseEntity containing error details with HTTP 404 status
     */
    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<ErrorResponse> handleBadCredentialsException(
            BadCredentialsException ex, HttpServletRequest request) {

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.NOT_FOUND.value())
                .error(HttpStatus.NOT_FOUND.getReasonPhrase())
                .message("Invalid username or password")
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    /**
     * Handles all uncaught exceptions and converts them to an HTTP response.
     * <p>
     * This method acts as a catch-all handler for any exceptions not handled
     * by more specific exception handlers. It returns an HTTP 500 INTERNAL
     * SERVER ERROR response with generic error details.
     * </p>
     *
     * @param ex      the Exception that was thrown
     * @param request the HTTP request that caused the exception
     * @return ResponseEntity containing error details with HTTP 500 status
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(
            Exception ex, HttpServletRequest request) {

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                .error(HttpStatus.INTERNAL_SERVER_ERROR.getReasonPhrase())
                .message(ex.getMessage())
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
