package com.agentsapi.service;

import com.agentsapi.dto.TaskRequest;
import com.agentsapi.dto.TaskResponse;
import com.agentsapi.entity.Agent;
import com.agentsapi.entity.Task;
import com.agentsapi.exception.InvalidRequestException;
import com.agentsapi.exception.ResourceNotFoundException;
import com.agentsapi.repository.AgentRepository;
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
class TaskServiceTest {

    @Mock
    private TaskRepository taskRepository;

    @Mock
    private AgentRepository agentRepository;

    @InjectMocks
    private TaskService taskService;

    private Task testTask;
    private Agent testAgent;
    private TaskRequest taskRequest;

    @BeforeEach
    void setUp() {
        testAgent = Agent.builder()
                .id(1L)
                .name("Test Agent")
                .description("Test Description")
                .deleted(false)
                .build();

        Set<Agent> agents = new HashSet<>();
        agents.add(testAgent);

        testTask = Task.builder()
                .id(1L)
                .title("Test Task")
                .description("Test Task Description")
                .supportedAgents(agents)
                .deleted(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        taskRequest = new TaskRequest();
        taskRequest.setTitle("Test Task");
        taskRequest.setDescription("Test Task Description");
        taskRequest.setSupportedAgentIds(Set.of(1L));
    }

    @Test
    void getAllTasks_ShouldReturnAllTasks() {
        // Given
        when(taskRepository.findByDeletedFalse()).thenReturn(Arrays.asList(testTask));

        // When
        List<TaskResponse> result = taskService.getAllTasks();

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getTitle()).isEqualTo("Test Task");
        assertThat(result.get(0).getSupportedAgentIds()).contains(1L);
        verify(taskRepository, times(1)).findByDeletedFalse();
    }

    @Test
    void getTaskById_WhenTaskExists_ShouldReturnTask() {
        // Given
        when(taskRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testTask));

        // When
        TaskResponse result = taskService.getTaskById(1L);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getTitle()).isEqualTo("Test Task");
        assertThat(result.getSupportedAgentIds()).contains(1L);
        verify(taskRepository, times(1)).findByIdAndDeletedFalse(1L);
    }

    @Test
    void getTaskById_WhenTaskDoesNotExist_ShouldThrowException() {
        // Given
        when(taskRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> taskService.getTaskById(999L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Task not found with id: 999");
    }

    @Test
    void createTask_WithValidAgents_ShouldCreateTask() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testAgent));
        when(taskRepository.save(any(Task.class))).thenReturn(testTask);

        // When
        TaskResponse result = taskService.createTask(taskRequest);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getTitle()).isEqualTo("Test Task");
        assertThat(result.getSupportedAgentIds()).contains(1L);
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(1L);
        verify(taskRepository, times(1)).save(any(Task.class));
    }

    @Test
    void createTask_WithInvalidAgent_ShouldThrowException() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> taskService.createTask(taskRequest))
                .isInstanceOf(InvalidRequestException.class)
                .hasMessageContaining("Agent not found with id: 1");
        verify(taskRepository, never()).save(any(Task.class));
    }

    @Test
    void updateTask_WhenTaskExists_ShouldUpdateTask() {
        // Given
        TaskRequest updateRequest = new TaskRequest();
        updateRequest.setTitle("Updated Task");
        updateRequest.setDescription("Updated Description");
        updateRequest.setSupportedAgentIds(Set.of(1L));

        when(taskRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testTask));
        when(agentRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testAgent));
        when(taskRepository.save(any(Task.class))).thenReturn(testTask);

        // When
        TaskResponse result = taskService.updateTask(1L, updateRequest);

        // Then
        assertThat(result).isNotNull();
        verify(taskRepository, times(1)).findByIdAndDeletedFalse(1L);
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(1L);
        verify(taskRepository, times(1)).save(any(Task.class));
    }

    @Test
    void updateTask_WhenTaskDoesNotExist_ShouldThrowException() {
        // Given
        when(taskRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> taskService.updateTask(999L, taskRequest))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Task not found with id: 999");
        verify(taskRepository, never()).save(any(Task.class));
    }

    @Test
    void deleteTask_WhenTaskExists_ShouldDeleteTask() {
        // Given
        when(taskRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testTask));
        doNothing().when(taskRepository).delete(any(Task.class));

        // When
        taskService.deleteTask(1L);

        // Then
        verify(taskRepository, times(1)).findByIdAndDeletedFalse(1L);
        verify(taskRepository, times(1)).delete(testTask);
    }

    @Test
    void deleteTask_WhenTaskDoesNotExist_ShouldThrowException() {
        // Given
        when(taskRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> taskService.deleteTask(999L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Task not found with id: 999");
        verify(taskRepository, never()).delete(any(Task.class));
    }
}
