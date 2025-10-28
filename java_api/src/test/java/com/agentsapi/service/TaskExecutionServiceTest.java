package com.agentsapi.service;

import com.agentsapi.dto.TaskExecutionRequest;
import com.agentsapi.dto.TaskExecutionResponse;
import com.agentsapi.entity.Agent;
import com.agentsapi.entity.Task;
import com.agentsapi.entity.TaskExecution;
import com.agentsapi.enums.ExecutionStatus;
import com.agentsapi.exception.InvalidRequestException;
import com.agentsapi.exception.ResourceNotFoundException;
import com.agentsapi.repository.AgentRepository;
import com.agentsapi.repository.TaskExecutionRepository;
import com.agentsapi.repository.TaskRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TaskExecutionServiceTest {

    @Mock
    private TaskExecutionRepository taskExecutionRepository;

    @Mock
    private TaskRepository taskRepository;

    @Mock
    private AgentRepository agentRepository;

    @InjectMocks
    private TaskExecutionService taskExecutionService;

    private TaskExecution testExecution;
    private Task testTask;
    private Agent testAgent;
    private TaskExecutionRequest executionRequest;

    @BeforeEach
    void setUp() {
        testAgent = Agent.builder()
                .id(1L)
                .name("Test Agent")
                .deleted(false)
                .build();

        Set<Agent> agents = new HashSet<>();
        agents.add(testAgent);

        testTask = Task.builder()
                .id(1L)
                .title("Test Task")
                .supportedAgents(agents)
                .deleted(false)
                .build();

        testExecution = TaskExecution.builder()
                .id(1L)
                .task(testTask)
                .agent(testAgent)
                .status(ExecutionStatus.RUNNING)
                .startedAt(LocalDateTime.now())
                .build();

        executionRequest = new TaskExecutionRequest();
        executionRequest.setTaskId(1L);
        executionRequest.setAgentId(1L);
    }

    @Test
    void startTaskExecution_WithValidData_ShouldStartExecution() {
        // Given
        when(taskRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testTask));
        when(agentRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testAgent));
        when(taskExecutionRepository.save(any(TaskExecution.class))).thenReturn(testExecution);

        // When
        TaskExecutionResponse result = taskExecutionService.startTaskExecution(executionRequest);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getStatus()).isEqualTo(ExecutionStatus.RUNNING);
        verify(taskRepository, times(1)).findByIdAndDeletedFalse(1L);
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(1L);
        verify(taskExecutionRepository, times(1)).save(any(TaskExecution.class));
    }

    @Test
    void startTaskExecution_WithInvalidTask_ShouldThrowException() {
        // Given
        when(taskRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> taskExecutionService.startTaskExecution(executionRequest))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Task not found with id: 1");
        verify(taskExecutionRepository, never()).save(any(TaskExecution.class));
    }

    @Test
    void startTaskExecution_WithInvalidAgent_ShouldThrowException() {
        // Given
        when(taskRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testTask));
        when(agentRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> taskExecutionService.startTaskExecution(executionRequest))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Agent not found with id: 1");
        verify(taskExecutionRepository, never()).save(any(TaskExecution.class));
    }

    @Test
    void startTaskExecution_WithUnsupportedAgent_ShouldThrowException() {
        // Given
        Agent unsupportedAgent = Agent.builder()
                .id(2L)
                .name("Unsupported Agent")
                .deleted(false)
                .build();

        executionRequest.setAgentId(2L);

        when(taskRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testTask));
        when(agentRepository.findByIdAndDeletedFalse(2L)).thenReturn(Optional.of(unsupportedAgent));

        // When & Then
        assertThatThrownBy(() -> taskExecutionService.startTaskExecution(executionRequest))
                .isInstanceOf(InvalidRequestException.class)
                .hasMessageContaining("Agent 2 is not supported for task 1");
        verify(taskExecutionRepository, never()).save(any(TaskExecution.class));
    }

    @Test
    void getRunningTasks_ShouldReturnRunningExecutions() {
        // Given
        when(taskExecutionRepository.findByStatus(ExecutionStatus.RUNNING))
                .thenReturn(Arrays.asList(testExecution));

        // When
        List<TaskExecutionResponse> result = taskExecutionService.getRunningTasks();

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getStatus()).isEqualTo(ExecutionStatus.RUNNING);
        verify(taskExecutionRepository, times(1)).findByStatus(ExecutionStatus.RUNNING);
    }

    @Test
    void getAllExecutions_ShouldReturnAllExecutions() {
        // Given
        when(taskExecutionRepository.findAll()).thenReturn(Arrays.asList(testExecution));

        // When
        List<TaskExecutionResponse> result = taskExecutionService.getAllExecutions();

        // Then
        assertThat(result).hasSize(1);
        verify(taskExecutionRepository, times(1)).findAll();
    }

    @Test
    void getExecutionById_WhenExists_ShouldReturnExecution() {
        // Given
        when(taskExecutionRepository.findById(1L)).thenReturn(Optional.of(testExecution));

        // When
        TaskExecutionResponse result = taskExecutionService.getExecutionById(1L);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        verify(taskExecutionRepository, times(1)).findById(1L);
    }

    @Test
    void getExecutionById_WhenNotExists_ShouldThrowException() {
        // Given
        when(taskExecutionRepository.findById(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> taskExecutionService.getExecutionById(999L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Execution not found with id: 999");
    }
}
