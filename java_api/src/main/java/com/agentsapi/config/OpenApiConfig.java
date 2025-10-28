package com.agentsapi.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeIn;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Contact;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.info.License;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import io.swagger.v3.oas.annotations.servers.Server;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration class for OpenAPI/Swagger documentation of the Agents & Tasks REST API.
 * This class configures the OpenAPI documentation with API information, server details,
 * and security schemes for JWT authentication.
 *
 * @version 1.0.0
 * @since 2025-10-27
 */
@Configuration
@OpenAPIDefinition(
        info = @Info(
                title = "Agents & Tasks REST API",
                version = "1.0.0",
                description = "A comprehensive REST API for managing Agents and Tasks with JWT authentication, " +
                        "PostgreSQL database, soft deletion, rate limiting, and task execution capabilities.",
                contact = @Contact(
                        name = "API Support",
                        email = "support@agentsapi.com"
                ),
                license = @License(
                        name = "Apache 2.0",
                        url = "https://www.apache.org/licenses/LICENSE-2.0.html"
                )
        ),
        servers = {
                @Server(
                        url = "http://localhost:8080",
                        description = "Local Development Server"
                )
        }
)
@SecurityScheme(
        name = "bearerAuth",
        description = "JWT Bearer Token Authentication",
        scheme = "bearer",
        type = SecuritySchemeType.HTTP,
        bearerFormat = "JWT",
        in = SecuritySchemeIn.HEADER
)
public class OpenApiConfig {
}
