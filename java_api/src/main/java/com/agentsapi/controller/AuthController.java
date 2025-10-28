package com.agentsapi.controller;

import com.agentsapi.dto.LoginRequest;
import com.agentsapi.dto.LoginResponse;
import com.agentsapi.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller responsible for handling authentication-related endpoints.
 * This controller manages user authentication operations and token generation.
 */
@RestController
@RequestMapping("/login")
public class AuthController {

    @Autowired
    private AuthService authService;

    /**
     * Authenticates a user based on the provided credentials.
     *
     * @param request The login request containing user credentials (username and password)
     * @return ResponseEntity containing the login response with authentication token if successful
     * @throws org.springframework.security.authentication.BadCredentialsException if credentials are invalid
     */
    @PostMapping
    public ResponseEntity<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = authService.login(request);
        return ResponseEntity.ok(response);
    }
}
