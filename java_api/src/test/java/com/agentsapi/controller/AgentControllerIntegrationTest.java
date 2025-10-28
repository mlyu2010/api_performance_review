package com.agentsapi.controller;

import com.agentsapi.dto.AgentRequest;
import com.agentsapi.entity.Agent;
import com.agentsapi.entity.User;
import com.agentsapi.repository.AgentRepository;
import com.agentsapi.repository.UserRepository;
import com.agentsapi.security.JwtUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class AgentControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private AgentRepository agentRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtUtil jwtUtil;

    private String jwtToken;
    private Agent testAgent;

    @BeforeEach
    void setUp() {
        agentRepository.deleteAll();
        userRepository.deleteAll();

        User user = User.builder()
                .username("testuser")
                .password(passwordEncoder.encode("password"))
                .role("ROLE_USER")
                .build();
        userRepository.save(user);

        jwtToken = jwtUtil.generateToken("testuser");

        testAgent = Agent.builder()
                .name("Test Agent")
                .description("Test Description")
                .deleted(false)
                .build();
        testAgent = agentRepository.save(testAgent);
    }

    @Test
    void getAllAgents_ShouldReturnAgentsList() throws Exception {
        mockMvc.perform(get("/agents")
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("Test Agent"));
    }

    @Test
    void getAgentById_WhenExists_ShouldReturnAgent() throws Exception {
        mockMvc.perform(get("/agents/" + testAgent.getId())
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Test Agent"));
    }

    @Test
    void createAgent_ShouldReturnCreatedAgent() throws Exception {
        AgentRequest request = new AgentRequest("New Agent", "New Description");

        mockMvc.perform(post("/agents")
                        .header("Authorization", "Bearer " + jwtToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("New Agent"));
    }

    @Test
    void updateAgent_ShouldReturnUpdatedAgent() throws Exception {
        AgentRequest request = new AgentRequest("Updated Agent", "Updated Description");

        mockMvc.perform(put("/agents/" + testAgent.getId())
                        .header("Authorization", "Bearer " + jwtToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Updated Agent"));
    }

    @Test
    void deleteAgent_ShouldReturnNoContent() throws Exception {
        mockMvc.perform(delete("/agents/" + testAgent.getId())
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isNoContent());
    }

    @Test
    void accessWithoutToken_ShouldReturnUnauthorized() throws Exception {
        mockMvc.perform(get("/agents"))
                .andExpect(status().isForbidden());
    }
}
