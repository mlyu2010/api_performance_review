package com.agentsapi.service;

import com.agentsapi.dto.AgentRequest;
import com.agentsapi.dto.AgentResponse;
import com.agentsapi.entity.Agent;
import com.agentsapi.exception.ResourceNotFoundException;
import com.agentsapi.repository.AgentRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AgentServiceTest {

    @Mock
    private AgentRepository agentRepository;

    @InjectMocks
    private AgentService agentService;

    private Agent testAgent;
    private AgentRequest agentRequest;

    @BeforeEach
    void setUp() {
        testAgent = Agent.builder()
                .id(1L)
                .name("Test Agent")
                .description("Test Agent Description")
                .deleted(false)
                .build();

        agentRequest = new AgentRequest();
        agentRequest.setName("Test Agent");
        agentRequest.setDescription("Test Agent Description");
    }

    @Test
    void getAllAgents_ShouldReturnAllAgents() {
        // Given
        Agent agent2 = Agent.builder()
                .id(2L)
                .name("Test Agent 2")
                .description("Test Description 2")
                .deleted(false)
                .build();
        when(agentRepository.findByDeletedFalse()).thenReturn(Arrays.asList(testAgent, agent2));

        // When
        List<AgentResponse> result = agentService.getAllAgents();

        // Then
        assertThat(result).hasSize(2);
        assertThat(result.get(0).getName()).isEqualTo("Test Agent");
        assertThat(result.get(1).getName()).isEqualTo("Test Agent 2");
        verify(agentRepository, times(1)).findByDeletedFalse();
    }

    @Test
    void getAgentById_WhenAgentExists_ShouldReturnAgent() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testAgent));

        // When
        AgentResponse result = agentService.getAgentById(1L);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("Test Agent");
        assertThat(result.getDescription()).isEqualTo("Test Agent Description");
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(1L);
    }

    @Test
    void getAgentById_WhenAgentDoesNotExist_ShouldThrowException() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> agentService.getAgentById(999L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Agent not found with id: 999");
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(999L);
    }

    @Test
    void createAgent_ShouldCreateAndReturnAgent() {
        // Given
        when(agentRepository.save(any(Agent.class))).thenReturn(testAgent);

        // When
        AgentResponse result = agentService.createAgent(agentRequest);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getName()).isEqualTo("Test Agent");
        assertThat(result.getDescription()).isEqualTo("Test Agent Description");
        verify(agentRepository, times(1)).save(any(Agent.class));
    }

    @Test
    void updateAgent_WhenAgentExists_ShouldUpdateAgent() {
        // Given
        AgentRequest updateRequest = new AgentRequest();
        updateRequest.setName("Updated Agent");
        updateRequest.setDescription("Updated Description");

        when(agentRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testAgent));
        when(agentRepository.save(any(Agent.class))).thenReturn(testAgent);

        // When
        AgentResponse result = agentService.updateAgent(1L, updateRequest);

        // Then
        assertThat(result).isNotNull();
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(1L);
        verify(agentRepository, times(1)).save(any(Agent.class));
    }

    @Test
    void updateAgent_WhenAgentDoesNotExist_ShouldThrowException() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> agentService.updateAgent(999L, agentRequest))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Agent not found with id: 999");
        verify(agentRepository, never()).save(any(Agent.class));
    }

    @Test
    void deleteAgent_WhenAgentExists_ShouldDeleteAgent() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testAgent));
        doNothing().when(agentRepository).delete(any(Agent.class));

        // When
        agentService.deleteAgent(1L);

        // Then
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(1L);
        verify(agentRepository, times(1)).delete(testAgent);
    }

    @Test
    void deleteAgent_WhenAgentDoesNotExist_ShouldThrowException() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> agentService.deleteAgent(999L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Agent not found with id: 999");
        verify(agentRepository, never()).delete(any(Agent.class));
    }

    @Test
    void existsById_WhenAgentExists_ShouldReturnTrue() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(testAgent));

        // When
        boolean result = agentService.existsById(1L);

        // Then
        assertThat(result).isTrue();
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(1L);
    }

    @Test
    void existsById_WhenAgentDoesNotExist_ShouldReturnFalse() {
        // Given
        when(agentRepository.findByIdAndDeletedFalse(anyLong())).thenReturn(Optional.empty());

        // When
        boolean result = agentService.existsById(999L);

        // Then
        assertThat(result).isFalse();
        verify(agentRepository, times(1)).findByIdAndDeletedFalse(999L);
    }
}
