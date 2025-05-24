package com.example.marta.ui.chat

import androidx.compose.runtime.Immutable
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.marta.data.model.ApiResponse
import com.example.marta.data.model.ChatData
import com.example.marta.data.model.ChatMessage
import com.example.marta.data.model.MessageStatus
import com.example.marta.data.model.MessageType
import com.example.marta.data.repository.ChatRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

@Immutable
data class ChatUiState(
    val messages: List<ChatMessage> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val currentReplyToId: String? = null
) {
    val lastUserMessage: ChatMessage?
        get() = messages.lastOrNull { it.role == "user" }

    val lastAssistantMessage: ChatMessage?
        get() = messages.lastOrNull { it.role == "assistant" }

    val hasOngoingRequest: Boolean
        get() = messages.any { it.role == "user" && it.status is MessageStatus.Sending }
}

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    fun setReplyingTo(messageId: String?) {
        _uiState.update { it.copy(currentReplyToId = messageId) }
    }
    
    /**
     * Sends a message from the user.
     *
     * @param content The text content of the message.
     */
    fun sendMessage(content: String) {
        if (content.isBlank() && _uiState.value.currentReplyToId == null) {
            if (content.isBlank()) return
        }

        val replyToId = _uiState.value.currentReplyToId

        val userMessage = ChatMessage(
            role = "user",
            content = content,
            replyToId = replyToId
        )

        _uiState.update { currentState ->
            currentState.copy(
                messages = currentState.messages + userMessage,
                isLoading = true,
                error = null,
                currentReplyToId = null
            )
        }

        viewModelScope.launch {
            try {
                chatRepository.sendMessage(
                    message = content,
                    authToken = null,
                    appointment = null,
                    draft = null,
                    replyToMessageId = replyToId
                ).collect { apiResponse: com.example.marta.data.model.ApiResponse<com.example.marta.data.model.ChatResponse> ->
                    if (apiResponse.success && apiResponse.data != null) {
                        val chatResponseData: com.example.marta.data.model.ChatResponse = apiResponse.data
                        updateMessageStatus(userMessage.id, MessageStatus.Sent)

                        val assistantMessage = ChatMessage(
                            role = "assistant",
                            content = chatResponseData.response,
                            data = chatResponseData.data,
                            type = when {
                                chatResponseData.data?.appointment != null -> MessageType.APPOINTMENT
                                chatResponseData.data?.draft != null -> MessageType.EMAIL_DRAFT
                                else -> MessageType.TEXT
                            },
                            replyToId = null
                        )
                        _uiState.update { currentState ->
                            currentState.copy(
                                messages = currentState.messages + assistantMessage,
                                isLoading = false
                            )
                        }
                    } else {
                        val errorMessage = apiResponse.error ?: "API request failed without specific error."
                        updateMessageStatus(userMessage.id, MessageStatus.Error(errorMessage))
                        _uiState.update { currentState ->
                            currentState.copy(isLoading = false, error = errorMessage)
                        }
                    }
                }
            } catch (e: Exception) {
                val errorMessage = when (e) {
                    is IOException -> "Network error: ${e.message}"
                    is HttpException -> "HTTP error: ${e.code()} - ${e.message()}"
                    else -> e.message ?: "An unknown error occurred while sending the message."
                }
                updateMessageStatus(userMessage.id, MessageStatus.Error(errorMessage))
                _uiState.update { currentState ->
                    currentState.copy(error = errorMessage, isLoading = false)
                }
            }
        }
    }

    /**
     * Updates the status of a message
     */
    private fun updateMessageStatus(messageId: String, status: MessageStatus) {
        _uiState.update { currentState ->
            currentState.copy(
                messages = currentState.messages.map { message ->
                    if (message.id == messageId) {
                        message.copy(status = status)
                    } else {
                        message
                    }
                }
            )
        }
    }

    /**
     * Clears any error message
     */
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
    
    /**
     * Adds a loading message to indicate the assistant is typing
     */
    fun showTypingIndicator() {
        val loadingMessage = ChatMessage(
            id = "typing_indicator",
            role = "assistant",
            content = "",
            type = MessageType.LOADING 
        )
        if (_uiState.value.messages.none { it.id == "typing_indicator" && it.type == MessageType.LOADING }) {
            _uiState.update { currentState ->
                currentState.copy(
                    messages = currentState.messages + loadingMessage
                )
            }
        }
    }
    
    /**
     * Removes the typing indicator
     */
    fun hideTypingIndicator() {
        _uiState.update { currentState ->
            currentState.copy(
                messages = currentState.messages.filterNot { it.id == "typing_indicator" && it.type == MessageType.LOADING }
            )
        }
    }
}
