
# Agents & Tasks REST API

Java 17 and Python 3.12 based projects built to implement requirements stated in the 
Trase_Backend_Take-home_Test.pdf

## Dependencies
- Docker
- Docker Compose

A comprehensive implementation in Java and Python for managing Agents and Tasks with 
JWT authentication, PostgreSQL database, soft deletion, rate limiting, 
task execution capabilities and performance testing based on 'k6_load_test' module.

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

See corresponding projecs for Java and Python.


## API Documentation and source code documentation

The API includes interactive Swagger UI documentation for easy testing 
and exploration. Source code documentation is built during projects build time.
See corresponding projecs for Java and Python.

## To do

1. Update Java to the latest JDK 25
2. Update Spring Boot to the latest 4.0
3. Update Python to the latest 3.14
4. Add Go project implementation.
5. Add Rust project implementation.
