package com.example.marta.data.model;

import androidx.compose.runtime.Immutable;
import com.google.gson.annotations.SerializedName;
import java.util.UUID;

/**
 * Additional data that can be sent with a chat message
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00004\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\b\u000f\n\u0002\u0010\u000b\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0003\b\u0087\b\u0018\u0000 \u001e2\u00020\u0001:\u0001\u001eB9\u0012\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0007\u0012\u000e\b\u0002\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00030\t\u00a2\u0006\u0002\u0010\nJ\u000b\u0010\u0013\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003J\u000b\u0010\u0014\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003J\u000b\u0010\u0015\u001a\u0004\u0018\u00010\u0007H\u00c6\u0003J\u000f\u0010\u0016\u001a\b\u0012\u0004\u0012\u00020\u00030\tH\u00c6\u0003J=\u0010\u0017\u001a\u00020\u00002\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u00032\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u00052\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u00072\u000e\b\u0002\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00030\tH\u00c6\u0001J\u0013\u0010\u0018\u001a\u00020\u00192\b\u0010\u001a\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\u001b\u001a\u00020\u001cH\u00d6\u0001J\t\u0010\u001d\u001a\u00020\u0003H\u00d6\u0001R\u0018\u0010\u0004\u001a\u0004\u0018\u00010\u00058\u0006X\u0087\u0004\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000b\u0010\fR\u0018\u0010\u0006\u001a\u0004\u0018\u00010\u00078\u0006X\u0087\u0004\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\u000eR\u001c\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00030\t8\u0006X\u0087\u0004\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000f\u0010\u0010R\u0018\u0010\u0002\u001a\u0004\u0018\u00010\u00038\u0006X\u0087\u0004\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0011\u0010\u0012\u00a8\u0006\u001f"}, d2 = {"Lcom/example/marta/data/model/ChatData;", "", "type", "", "appointment", "Lcom/example/marta/data/model/Appointment;", "draft", "Lcom/example/marta/data/model/EmailDraft;", "suggestions", "", "(Ljava/lang/String;Lcom/example/marta/data/model/Appointment;Lcom/example/marta/data/model/EmailDraft;Ljava/util/List;)V", "getAppointment", "()Lcom/example/marta/data/model/Appointment;", "getDraft", "()Lcom/example/marta/data/model/EmailDraft;", "getSuggestions", "()Ljava/util/List;", "getType", "()Ljava/lang/String;", "component1", "component2", "component3", "component4", "copy", "equals", "", "other", "hashCode", "", "toString", "Companion", "app_debug"})
@androidx.compose.runtime.Immutable
public final class ChatData {
    @com.google.gson.annotations.SerializedName(value = "type")
    @org.jetbrains.annotations.Nullable
    private final java.lang.String type = null;
    @com.google.gson.annotations.SerializedName(value = "appointment")
    @org.jetbrains.annotations.Nullable
    private final com.example.marta.data.model.Appointment appointment = null;
    @com.google.gson.annotations.SerializedName(value = "draft")
    @org.jetbrains.annotations.Nullable
    private final com.example.marta.data.model.EmailDraft draft = null;
    @com.google.gson.annotations.SerializedName(value = "suggestions")
    @org.jetbrains.annotations.NotNull
    private final java.util.List<java.lang.String> suggestions = null;
    @org.jetbrains.annotations.NotNull
    private static final com.example.marta.data.model.ChatData EMPTY = null;
    @org.jetbrains.annotations.NotNull
    public static final com.example.marta.data.model.ChatData.Companion Companion = null;
    
    public ChatData(@org.jetbrains.annotations.Nullable
    java.lang.String type, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.Appointment appointment, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.EmailDraft draft, @org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> suggestions) {
        super();
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getType() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final com.example.marta.data.model.Appointment getAppointment() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final com.example.marta.data.model.EmailDraft getDraft() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.util.List<java.lang.String> getSuggestions() {
        return null;
    }
    
    public ChatData() {
        super();
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String component1() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final com.example.marta.data.model.Appointment component2() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final com.example.marta.data.model.EmailDraft component3() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.util.List<java.lang.String> component4() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.ChatData copy(@org.jetbrains.annotations.Nullable
    java.lang.String type, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.Appointment appointment, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.EmailDraft draft, @org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> suggestions) {
        return null;
    }
    
    @java.lang.Override
    public boolean equals(@org.jetbrains.annotations.Nullable
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override
    @org.jetbrains.annotations.NotNull
    public java.lang.String toString() {
        return null;
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0086\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002R\u0011\u0010\u0003\u001a\u00020\u0004\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0005\u0010\u0006\u00a8\u0006\u0007"}, d2 = {"Lcom/example/marta/data/model/ChatData$Companion;", "", "()V", "EMPTY", "Lcom/example/marta/data/model/ChatData;", "getEMPTY", "()Lcom/example/marta/data/model/ChatData;", "app_debug"})
    public static final class Companion {
        
        private Companion() {
            super();
        }
        
        @org.jetbrains.annotations.NotNull
        public final com.example.marta.data.model.ChatData getEMPTY() {
            return null;
        }
    }
}