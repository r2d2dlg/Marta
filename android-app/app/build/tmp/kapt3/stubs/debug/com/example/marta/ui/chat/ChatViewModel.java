package com.example.marta.ui.chat;

import androidx.compose.runtime.Immutable;
import androidx.lifecycle.ViewModel;
import com.example.marta.data.model.ApiResponse;
import com.example.marta.data.model.ChatData;
import com.example.marta.data.model.ChatMessage;
import com.example.marta.data.model.MessageStatus;
import com.example.marta.data.model.MessageType;
import com.example.marta.data.repository.ChatRepository;
import dagger.hilt.android.lifecycle.HiltViewModel;
import kotlinx.coroutines.flow.StateFlow;
import retrofit2.HttpException;
import java.io.IOException;
import javax.inject.Inject;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000:\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0002\b\u0003\n\u0002\u0010\u000e\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00020\u0001B\u000f\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u0006\u0010\f\u001a\u00020\rJ\u0006\u0010\u000e\u001a\u00020\rJ\u000e\u0010\u000f\u001a\u00020\r2\u0006\u0010\u0010\u001a\u00020\u0011J\u0010\u0010\u0012\u001a\u00020\r2\b\u0010\u0013\u001a\u0004\u0018\u00010\u0011J\u0006\u0010\u0014\u001a\u00020\rJ\u0018\u0010\u0015\u001a\u00020\r2\u0006\u0010\u0013\u001a\u00020\u00112\u0006\u0010\u0016\u001a\u00020\u0017H\u0002R\u0014\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u0006X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\n\u0010\u000b\u00a8\u0006\u0018"}, d2 = {"Lcom/example/marta/ui/chat/ChatViewModel;", "Landroidx/lifecycle/ViewModel;", "chatRepository", "Lcom/example/marta/data/repository/ChatRepository;", "(Lcom/example/marta/data/repository/ChatRepository;)V", "_uiState", "Lkotlinx/coroutines/flow/MutableStateFlow;", "Lcom/example/marta/ui/chat/ChatUiState;", "uiState", "Lkotlinx/coroutines/flow/StateFlow;", "getUiState", "()Lkotlinx/coroutines/flow/StateFlow;", "clearError", "", "hideTypingIndicator", "sendMessage", "content", "", "setReplyingTo", "messageId", "showTypingIndicator", "updateMessageStatus", "status", "Lcom/example/marta/data/model/MessageStatus;", "app_debug"})
@dagger.hilt.android.lifecycle.HiltViewModel
public final class ChatViewModel extends androidx.lifecycle.ViewModel {
    @org.jetbrains.annotations.NotNull
    private final com.example.marta.data.repository.ChatRepository chatRepository = null;
    @org.jetbrains.annotations.NotNull
    private final kotlinx.coroutines.flow.MutableStateFlow<com.example.marta.ui.chat.ChatUiState> _uiState = null;
    @org.jetbrains.annotations.NotNull
    private final kotlinx.coroutines.flow.StateFlow<com.example.marta.ui.chat.ChatUiState> uiState = null;
    
    @javax.inject.Inject
    public ChatViewModel(@org.jetbrains.annotations.NotNull
    com.example.marta.data.repository.ChatRepository chatRepository) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull
    public final kotlinx.coroutines.flow.StateFlow<com.example.marta.ui.chat.ChatUiState> getUiState() {
        return null;
    }
    
    public final void setReplyingTo(@org.jetbrains.annotations.Nullable
    java.lang.String messageId) {
    }
    
    /**
     * Sends a message from the user.
     *
     * @param content The text content of the message.
     */
    public final void sendMessage(@org.jetbrains.annotations.NotNull
    java.lang.String content) {
    }
    
    /**
     * Updates the status of a message
     */
    private final void updateMessageStatus(java.lang.String messageId, com.example.marta.data.model.MessageStatus status) {
    }
    
    /**
     * Clears any error message
     */
    public final void clearError() {
    }
    
    /**
     * Adds a loading message to indicate the assistant is typing
     */
    public final void showTypingIndicator() {
    }
    
    /**
     * Removes the typing indicator
     */
    public final void hideTypingIndicator() {
    }
}