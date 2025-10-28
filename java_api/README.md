
# Agents & Tasks REST API

## Dependencies
- Docker
- Docker Compose

A comprehensive Spring Boot REST API for managing Agents and Tasks with 
JWT authentication, PostgreSQL database, soft deletion, rate limiting, 
task execution capabilities and performance testing via 'k6_load_test' module.

## Features

-  JWT Authentication : Secure login with token-based authentication
-  Agent Management : Full CRUD operations for agents
-  Task Management : Full CRUD operations for tasks with multi-agent support
-  Task Execution : Start and track task executions with specific agents
-  Soft Deletion : Agents and tasks are soft-deleted, not permanently removed
-  Rate Limiting : API rate limiting to prevent abuse (100 requests per minute per client)
-  PostgreSQL Database : Production-ready database integration
-  Swagger UI/OpenAPI : Interactive API documentation and testing interface
-  Comprehensive Testing : Unit and integration tests included
-  Error Handling : Consistent error responses across all endpoints
-  Performance testing via 'k6_load_test' module.

## Technology Stack

- Java 17
- Spring Boot 3.2.0
- Spring Security with JWT
- Spring Data JPA
- PostgreSQL 18
- Bucket4j (Rate Limiting)
- Swagger/OpenAPI 3 (springdoc-openapi)
- Lombok
- JUnit 5 & Mockito
- Maven

>  Note : All endpoints are documented and testable via Swagger UI at 
> http://localhost:8080/swagger-ui.html

## API Documentation

The API includes interactive Swagger UI documentation for easy testing 
and exploration.
Java code documentation is generated via 'mvn clean install' command.
HTML is available at 'target/site/apidocs/index.html'


### Accessing Swagger UI

Once the application is running, access Swagger UI at:
-  Swagger UI : http://localhost:8080/swagger-ui.html
-  OpenAPI JSON : http://localhost:8080/api-docs

### Using Swagger UI with JWT Authentication

1.  Login to get JWT token :
   - Navigate to the `auth-controller` section
   - Expand the `POST /api/auth/login` endpoint
   - Click "Try it out"
   - Enter credentials in the request body:
     json
     {
       "username": "admin",
       "password": "admin123"
     }
     
   - Click "Execute"
   - Copy the `token` value from the response

2.  Authorize in Swagger UI :
   - Click the "Authorize" button (lock icon) at the top right of the Swagger UI page
   - In the "Value" field, enter: `Bearer <your-token>` (replace `<your-token>` with the token you copied)
   - Click "Authorize" and then "Close"

3.  Test Protected Endpoints :
   - Now you can test any endpoint in the API
   - All requests will automatically include your JWT token in the Authorization header
   - Try creating agents, tasks, and executing tasks using the interactive interface

### Available API Groups

-  Authentication : Login endpoint (`/login`)
-  Agents : CRUD operations for agents (`/agents`)
-  Tasks : CRUD operations for tasks (`/tasks`)
-  Executions : Task execution management (`/executions`)

## Prerequisites

- JDK 17 or higher
- Maven 3.6+
- PostgreSQL 18 (or Docker)

## Database Setup and test users creation
Test users "admin/admin123" and "user/user123" are created in the database
during application startup automatically. See DatabaseInitializer.java.

## PostgreSQL is installed via Docker, see docker-compose.yml

## Running the Application

docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f app
