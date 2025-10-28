package com.agentsapi.controller;

import com.agentsapi.dto.TaskExecutionRequest;
import com.agentsapi.dto.TaskExecutionResponse;
import com.agentsapi.enums.ExecutionStatus;
import com.agentsapi.service.TaskExecutionService;
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

import java.time.LocalDateTime;
import java.util.Arrays;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = TaskExecutionController.class,
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
class TaskExecutionControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private TaskExecutionService taskExecutionService;

    private TaskExecutionResponse executionResponse;
    private TaskExecutionRequest executionRequest;

    @BeforeEach
    void setUp() {
        executionResponse = TaskExecutionResponse.builder()
                .id(1L)
                .taskId(1L)
                .agentId(1L)
                .status(ExecutionStatus.RUNNING)
                .startedAt(LocalDateTime.now())
                .build();

        executionRequest = new TaskExecutionRequest();
        executionRequest.setTaskId(1L);
        executionRequest.setAgentId(1L);
    }

    @Test
    @WithMockUser
    void startTaskExecution_ShouldReturnCreatedExecution() throws Exception {
        // Given
        when(taskExecutionService.startTaskExecution(any(TaskExecutionRequest.class)))
                .thenReturn(executionResponse);

        // When & Then
        mockMvc.perform(post("/executions/start")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(executionRequest)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.taskId").value(1))
                .andExpect(jsonPath("$.agentId").value(1))
                .andExpect(jsonPath("$.status").value("RUNNING"));
    }

    @Test
    @WithMockUser
    void getRunningTasks_ShouldReturnRunningExecutions() throws Exception {
        // Given
        when(taskExecutionService.getRunningTasks()).thenReturn(Arrays.asList(executionResponse));

        // When & Then
        mockMvc.perform(get("/executions/running"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$[0].id").value(1))
                .andExpect(jsonPath("$[0].status").value("RUNNING"));
    }

    @Test
    @WithMockUser
    void getAllExecutions_ShouldReturnAllExecutions() throws Exception {
        // Given
        when(taskExecutionService.getAllExecutions()).thenReturn(Arrays.asList(executionResponse));

        // When & Then
        mockMvc.perform(get("/executions"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$[0].id").value(1));
    }

    @Test
    @WithMockUser
    void getExecutionById_ShouldReturnExecution() throws Exception {
        // Given
        when(taskExecutionService.getExecutionById(1L)).thenReturn(executionResponse);

        // When & Then
        mockMvc.perform(get("/executions/1"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.status").value("RUNNING"));
    }

    @Test
    void startTaskExecution_WithoutAuthentication_ShouldReturnUnauthorized() throws Exception {
        // When & Then
        mockMvc.perform(post("/executions/start")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(executionRequest)))
                .andExpect(status().isUnauthorized());
    }
}
