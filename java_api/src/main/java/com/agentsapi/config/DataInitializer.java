package com.agentsapi.config;

import com.agentsapi.entity.User;
import com.agentsapi.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Component responsible for initializing default user data in the application.
 * Creates default admin and regular user accounts if they don't exist.
 */
@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    /**
     * Executes the data initialization process when the application starts.
     * Creates default admin user with ROLE_ADMIN and regular user with ROLE_USER if they don't exist.
     *
     * @param args command line arguments passed to the application
     * @throws Exception if any error occurs during initialization
     */
    @Override
    public void run(String... args) throws Exception {
        if (!userRepository.existsByUsername("admin")) {
            User admin = User.builder()
                    .username("admin")
                    .password(passwordEncoder.encode("admin123"))
                    .role("ROLE_ADMIN")
                    .build();
            userRepository.save(admin);
            System.out.println("Default admin user created: username=admin, password=admin123");
        }

        if (!userRepository.existsByUsername("user")) {
            User user = User.builder()
                    .username("user")
                    .password(passwordEncoder.encode("user123"))
                    .role("ROLE_USER")
                    .build();
            userRepository.save(user);
            System.out.println("Default user created: username=user, password=user123");
        }
    }
}
