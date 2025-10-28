package com.agentsapi.controller;

import com.agentsapi.dto.AgentRequest;
import com.agentsapi.dto.AgentResponse;
import com.agentsapi.service.AgentService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.FilterType;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Arrays;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = AgentController.class,
        excludeFilters = {
                @ComponentScan.Filter(
                        type = FilterType.REGEX,
                        pattern = "com.agentsapi.filter.*"
                ),
                @ComponentScan.Filter(
                        type = FilterType.REGEX,
                        pattern = "com.agentsapi.security.*"
                ),
                @ComponentScan.Filter(
                        type = FilterType.REGEX,
                        pattern = "com.agentsapi.config.*"
                )
        })
class AgentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private AgentService agentService;

    private AgentResponse agentResponse;
    private AgentRequest agentRequest;

    @BeforeEach
    void setUp() {
        agentResponse = AgentResponse.builder()
                .id(1L)
                .name("Test Agent")
                .description("Test Description")
                .build();

        agentRequest = new AgentRequest();
        agentRequest.setName("Test Agent");
        agentRequest.setDescription("Test Description");
    }

    @Test
    @WithMockUser
    void getAllAgents_ShouldReturnAgentList() throws Exception {
        // Given
        when(agentService.getAllAgents()).thenReturn(Arrays.asList(agentResponse));

        // When & Then
        mockMvc.perform(get("/agents"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$[0].id").value(1))
                .andExpect(jsonPath("$[0].name").value("Test Agent"));
    }

    @Test
    @WithMockUser
    void getAgentById_ShouldReturnAgent() throws Exception {
        // Given
        when(agentService.getAgentById(1L)).thenReturn(agentResponse);

        // When & Then
        mockMvc.perform(get("/agents/1"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.name").value("Test Agent"));
    }

    @Test
    @WithMockUser
    void createAgent_ShouldReturnCreatedAgent() throws Exception {
        // Given
        when(agentService.createAgent(any(AgentRequest.class))).thenReturn(agentResponse);

        // When & Then
        mockMvc.perform(post("/agents")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(agentRequest)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.name").value("Test Agent"));
    }

    @Test
    @WithMockUser
    void updateAgent_ShouldReturnUpdatedAgent() throws Exception {
        // Given
        when(agentService.updateAgent(eq(1L), any(AgentRequest.class))).thenReturn(agentResponse);

        // When & Then
        mockMvc.perform(put("/agents/1")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(agentRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.name").value("Test Agent"));
    }

    @Test
    @WithMockUser
    void deleteAgent_ShouldReturnNoContent() throws Exception {
        // When & Then
        mockMvc.perform(delete("/agents/1")
                        .with(csrf()))
                .andExpect(status().isNoContent());
    }

    @Test
    void getAllAgents_WithoutAuthentication_ShouldReturnUnauthorized() throws Exception {
        // When & Then
        mockMvc.perform(get("/agents"))
                .andExpect(status().isForbidden());
    }
}
