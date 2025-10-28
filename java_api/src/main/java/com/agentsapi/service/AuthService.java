package com.agentsapi.service;

import com.agentsapi.dto.LoginRequest;
import com.agentsapi.dto.LoginResponse;
import com.agentsapi.entity.User;
import com.agentsapi.repository.UserRepository;
import com.agentsapi.security.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * Service class responsible for handling authentication-related operations.
 * Manages user authentication, token generation, and user creation.
 *
 * @author AgentsAPI Development Team
 * @version 1.0
 * @since 10-27-2025
 */
@Service
public class AuthService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private PasswordEncoder passwordEncoder;

    /**
     * Authenticates a user and generates a JWT token.
     *
     * @param request the login request containing username and password
     * @return LoginResponse containing the generated JWT token and user details
     * @throws RuntimeException if the username or password is invalid
     */
    public LoginResponse login(LoginRequest request) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
            );

            String token = jwtUtil.generateToken(request.getUsername());

            return LoginResponse.builder()
                    .token(token)
                    .type("Bearer")
                    .username(request.getUsername())
                    .build();

        } catch (AuthenticationException e) {
            throw new RuntimeException("Invalid username or password");
        }
    }

    /**
     * Creates a new user with the specified credentials and role.
     *
     * @param username the username for the new user
     * @param password the password for the new user
     * @param role     the role assigned to the new user
     * @return the created User entity
     * @throws RuntimeException if the username already exists
     */
    public User createUser(String username, String password, String role) {
        if (userRepository.existsByUsername(username)) {
            throw new RuntimeException("Username already exists");
        }

        User user = User.builder()
                .username(username)
                .password(passwordEncoder.encode(password))
                .role(role)
                .build();

        return userRepository.save(user);
    }
}
