package com.example.marta.data.repository;

import com.example.marta.data.api.ApiService;
import com.example.marta.data.model.ApiResponse;
import com.example.marta.data.model.Appointment;
import com.example.marta.data.model.ChatResponse;
import com.example.marta.data.model.EmailDraft;
import kotlinx.coroutines.Dispatchers;
import kotlinx.coroutines.flow.Flow;
import javax.inject.Inject;
import javax.inject.Singleton;

@javax.inject.Singleton
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000<\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\b\u0007\u0018\u00002\u00020\u0001B\u000f\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J@\u0010\u0005\u001a\u000e\u0012\u0004\u0012\u00020\u0007\u0012\u0004\u0012\u00020\u00010\u00062\u0006\u0010\b\u001a\u00020\u00072\n\b\u0002\u0010\t\u001a\u0004\u0018\u00010\n2\n\b\u0002\u0010\u000b\u001a\u0004\u0018\u00010\f2\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\u0007H\u0002JJ\u0010\u000e\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00110\u00100\u000f2\u0006\u0010\b\u001a\u00020\u00072\n\b\u0002\u0010\u0012\u001a\u0004\u0018\u00010\u00072\n\b\u0002\u0010\t\u001a\u0004\u0018\u00010\n2\n\b\u0002\u0010\u000b\u001a\u0004\u0018\u00010\f2\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\u0007R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0013"}, d2 = {"Lcom/example/marta/data/repository/ChatRepository;", "", "apiService", "Lcom/example/marta/data/api/ApiService;", "(Lcom/example/marta/data/api/ApiService;)V", "createChatRequest", "", "", "message", "appointment", "Lcom/example/marta/data/model/Appointment;", "draft", "Lcom/example/marta/data/model/EmailDraft;", "replyToMessageId", "sendMessage", "Lkotlinx/coroutines/flow/Flow;", "Lcom/example/marta/data/model/ApiResponse;", "Lcom/example/marta/data/model/ChatResponse;", "authToken", "app_debug"})
public final class ChatRepository {
    @org.jetbrains.annotations.NotNull
    private final com.example.marta.data.api.ApiService apiService = null;
    
    @javax.inject.Inject
    public ChatRepository(@org.jetbrains.annotations.NotNull
    com.example.marta.data.api.ApiService apiService) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull
    public final kotlinx.coroutines.flow.Flow<com.example.marta.data.model.ApiResponse<com.example.marta.data.model.ChatResponse>> sendMessage(@org.jetbrains.annotations.NotNull
    java.lang.String message, @org.jetbrains.annotations.Nullable
    java.lang.String authToken, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.Appointment appointment, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.EmailDraft draft, @org.jetbrains.annotations.Nullable
    java.lang.String replyToMessageId) {
        return null;
    }
    
    @kotlin.Suppress(names = {"UNCHECKED_CAST"})
    private final java.util.Map<java.lang.String, java.lang.Object> createChatRequest(java.lang.String message, com.example.marta.data.model.Appointment appointment, com.example.marta.data.model.EmailDraft draft, java.lang.String replyToMessageId) {
        return null;
    }
}