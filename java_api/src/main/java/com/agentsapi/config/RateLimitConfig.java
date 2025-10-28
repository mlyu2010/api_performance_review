package com.agentsapi.config;

import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.Refill;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Configuration class for rate limiting functionality using Bucket4j.
 * Provides configuration for token bucket algorithm implementation to handle rate limiting.
 */
@Configuration
public class RateLimitConfig {

    /**
     * Maximum number of tokens that can be stored in the bucket
     */
    @Value("${ratelimit.capacity}")
    private long capacity;

    /**
     * Number of tokens to be refilled per interval
     */
    @Value("${ratelimit.tokens}")
    private long tokens;

    /**
     * Duration in seconds between token refills
     */
    @Value("${ratelimit.duration}")
    private long duration;

    /**
     * Creates a thread-safe map to store rate limit buckets for different clients.
     * Each client is identified by a unique key in the map.
     *
     * @return A concurrent hash map for storing rate limit buckets
     */
    @Bean
    public Map<String, Bucket> rateLimitBuckets() {
        return new ConcurrentHashMap<>();
    }

    /**
     * Creates a new rate limit bucket with specified capacity and refill rate.
     * The bucket is configured using properties defined in application configuration.
     *
     * @return A new Bucket4j bucket instance with configured rate limiting parameters
     */
    public Bucket createNewBucket() {
        Bandwidth limit = Bandwidth.classic(capacity, Refill.intervally(tokens, Duration.ofSeconds(duration)));
        return Bucket.builder()
                .addLimit(limit)
                .build();
    }
}
