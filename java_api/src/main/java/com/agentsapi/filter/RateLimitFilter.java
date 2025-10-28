package com.agentsapi.filter;

import com.agentsapi.config.RateLimitConfig;
import io.github.bucket4j.Bucket;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Map;

/**
 * A filter component that implements rate limiting functionality for HTTP requests.
 * Uses Bucket4j for token bucket implementation to control request rates.
 * Each client (identified by IP and username combination) has its own rate limit bucket.
 */
@Component
public class RateLimitFilter extends OncePerRequestFilter {

    @Autowired
    private Map<String, Bucket> rateLimitBuckets;

    @Autowired
    private RateLimitConfig rateLimitConfig;

    /**
     * Processes each HTTP request through rate limiting logic.
     * If the request is within rate limits, it's allowed to proceed;
     * otherwise, it returns a 429 (Too Many Requests) response.
     *
     * @param request     the HTTP servlet request
     * @param response    the HTTP servlet response
     * @param filterChain the filter chain for request processing
     * @throws ServletException if a servlet error occurs
     * @throws IOException      if an I/O error occurs
     */
    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String clientId = getClientId(request);
        Bucket bucket = rateLimitBuckets.computeIfAbsent(clientId, k -> rateLimitConfig.createNewBucket());

        if (bucket.tryConsume(1)) {
            filterChain.doFilter(request, response);
        } else {
            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.getWriter().write("{\"error\": \"Too many requests. Please try again later.\"}");
            response.setContentType("application/json");
        }
    }

    /**
     * Generates a unique identifier for the client making the request.
     * The identifier is a combination of the client's IP address and username.
     *
     * @param request the HTTP servlet request
     * @return a string representing the unique client identifier
     */
    private String getClientId(HttpServletRequest request) {
        String clientIp = request.getRemoteAddr();
        String username = request.getUserPrincipal() != null ? request.getUserPrincipal().getName() : "anonymous";
        return clientIp + "_" + username;
    }
}
