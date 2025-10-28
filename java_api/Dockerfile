#
# Builder stage
#

FROM maven:3-amazoncorretto-17-alpine as builder

RUN mkdir -p /usr/src/java_api
WORKDIR /usr/src/java_api

# Copy Maven configuration first for better layer caching
COPY pom.xml /usr/src/java_api/
RUN mvn dependency:go-offline -B

# Copy source code
COPY src /usr/src/java_api/src

# Build the application
RUN mvn clean package -DskipTests -B

#
# Runtime stage
#

FROM eclipse-temurin:17-jre-alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Create non-root user for security
RUN addgroup -S spring && adduser -S spring -G spring

# Set working directory
WORKDIR /app

# Copy the built artifact from builder stage
COPY --from=builder /usr/src/java_api/target/agents-tasks-api-*.jar app.jar

# Change ownership to spring user
RUN chown spring:spring app.jar

USER spring:spring

# Expose application port
EXPOSE 8080

# Production-optimized JVM settings
ENV JAVA_OPTS="\
    -server \
    -XX:+UseContainerSupport \
    -XX:MaxRAMPercentage=75.0 \
    -XX:InitialRAMPercentage=50.0 \
    -XX:+UseG1GC \
    -XX:MaxGCPauseMillis=200 \
    -XX:+ParallelRefProcEnabled \
    -XX:+UnlockExperimentalVMOptions \
    -XX:+UseStringDeduplication \
    -XX:+OptimizeStringConcat \
    -XX:+UseCompressedOops \
    -Djava.security.egd=file:/dev/./urandom \
    -Dspring.profiles.active=prod"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# Run the Spring Boot application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
