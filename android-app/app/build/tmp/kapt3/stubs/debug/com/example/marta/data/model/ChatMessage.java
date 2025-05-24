package com.example.marta.data.model;

import androidx.compose.runtime.Immutable;
import com.google.gson.annotations.SerializedName;
import java.util.UUID;

/**
 * Represents a message in the chat conversation.
 *
 * @property id Unique identifier for the message
 * @property role The role of the message sender ('user' or 'assistant')
 * @property content The text content of the message
 * @property data Additional structured data associated with the message (appointments, email drafts, etc.)
 * @property timestamp When the message was created (in milliseconds since epoch)
 * @property status The current status of the message (sending, sent, error)
 * @property type The type of message (text, appointment, email draft, etc.)
 * @property replyToId The ID of the message this is replying to, if any
 * @property reactions List of reaction emojis added to the message
 * @property senderName Display name of the sender
 * @property senderAvatar URL to the sender's avatar image
 * @property isEdited Whether the message has been edited
 * @property isPinned Whether the message is pinned in the chat
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000D\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\t\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\'\n\u0002\u0010\b\n\u0002\b\b\b\u0087\b\u0018\u00002\u00020\u0001B\u008f\u0001\u0012\b\b\u0002\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0003\u0012\u0006\u0010\u0005\u001a\u00020\u0003\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0007\u0012\b\b\u0002\u0010\b\u001a\u00020\t\u0012\b\b\u0002\u0010\n\u001a\u00020\u000b\u0012\b\b\u0002\u0010\f\u001a\u00020\r\u0012\n\b\u0002\u0010\u000e\u001a\u0004\u0018\u00010\u0003\u0012\u000e\b\u0002\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\u00030\u0010\u0012\b\b\u0002\u0010\u0011\u001a\u00020\u0003\u0012\n\b\u0002\u0010\u0012\u001a\u0004\u0018\u00010\u0003\u0012\b\b\u0002\u0010\u0013\u001a\u00020\u0014\u0012\b\b\u0002\u0010\u0015\u001a\u00020\u0014\u00a2\u0006\u0002\u0010\u0016J\t\u0010+\u001a\u00020\u0003H\u00c6\u0003J\t\u0010,\u001a\u00020\u0003H\u00c6\u0003J\u000b\u0010-\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003J\t\u0010.\u001a\u00020\u0014H\u00c6\u0003J\t\u0010/\u001a\u00020\u0014H\u00c6\u0003J\t\u00100\u001a\u00020\u0003H\u00c6\u0003J\t\u00101\u001a\u00020\u0003H\u00c6\u0003J\u000b\u00102\u001a\u0004\u0018\u00010\u0007H\u00c6\u0003J\t\u00103\u001a\u00020\tH\u00c6\u0003J\t\u00104\u001a\u00020\u000bH\u00c6\u0003J\t\u00105\u001a\u00020\rH\u00c6\u0003J\u000b\u00106\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003J\u000f\u00107\u001a\b\u0012\u0004\u0012\u00020\u00030\u0010H\u00c6\u0003J\u0097\u0001\u00108\u001a\u00020\u00002\b\b\u0002\u0010\u0002\u001a\u00020\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u00032\b\b\u0002\u0010\u0005\u001a\u00020\u00032\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u00072\b\b\u0002\u0010\b\u001a\u00020\t2\b\b\u0002\u0010\n\u001a\u00020\u000b2\b\b\u0002\u0010\f\u001a\u00020\r2\n\b\u0002\u0010\u000e\u001a\u0004\u0018\u00010\u00032\u000e\b\u0002\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\u00030\u00102\b\b\u0002\u0010\u0011\u001a\u00020\u00032\n\b\u0002\u0010\u0012\u001a\u0004\u0018\u00010\u00032\b\b\u0002\u0010\u0013\u001a\u00020\u00142\b\b\u0002\u0010\u0015\u001a\u00020\u0014H\u00c6\u0001J\u0013\u00109\u001a\u00020\u00142\b\u0010:\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010;\u001a\u00020<H\u00d6\u0001J\t\u0010=\u001a\u00020\u0003H\u00d6\u0001J\u000e\u0010>\u001a\u00020\u00002\u0006\u0010?\u001a\u00020\u0003J\u000e\u0010@\u001a\u00020\u00002\u0006\u0010A\u001a\u00020\u0003J\u000e\u0010B\u001a\u00020\u00002\u0006\u0010C\u001a\u00020\u000bR\u0016\u0010\u0005\u001a\u00020\u00038\u0006X\u0087\u0004\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0017\u0010\u0018R\u0018\u0010\u0006\u001a\u0004\u0018\u00010\u00078\u0006X\u0087\u0004\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0019\u0010\u001aR\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001b\u0010\u0018R\u0011\u0010\u0013\u001a\u00020\u0014\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0013\u0010\u001cR\u0011\u0010\u001d\u001a\u00020\u00148F\u00a2\u0006\u0006\u001a\u0004\b\u001d\u0010\u001cR\u0011\u0010\u001e\u001a\u00020\u00148F\u00a2\u0006\u0006\u001a\u0004\b\u001e\u0010\u001cR\u0011\u0010\u0015\u001a\u00020\u0014\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0015\u0010\u001cR\u0017\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\u00030\u0010\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001f\u0010 R\u0013\u0010\u000e\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b!\u0010\u0018R\u0016\u0010\u0004\u001a\u00020\u00038\u0006X\u0087\u0004\u00a2\u0006\b\n\u0000\u001a\u0004\b\"\u0010\u0018R\u0013\u0010\u0012\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b#\u0010\u0018R\u0011\u0010\u0011\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b$\u0010\u0018R\u0011\u0010\n\u001a\u00020\u000b\u00a2\u0006\b\n\u0000\u001a\u0004\b%\u0010&R\u0011\u0010\b\u001a\u00020\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\'\u0010(R\u0011\u0010\f\u001a\u00020\r\u00a2\u0006\b\n\u0000\u001a\u0004\b)\u0010*\u00a8\u0006D"}, d2 = {"Lcom/example/marta/data/model/ChatMessage;", "", "id", "", "role", "content", "data", "Lcom/example/marta/data/model/ChatData;", "timestamp", "", "status", "Lcom/example/marta/data/model/MessageStatus;", "type", "Lcom/example/marta/data/model/MessageType;", "replyToId", "reactions", "", "senderName", "senderAvatar", "isEdited", "", "isPinned", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lcom/example/marta/data/model/ChatData;JLcom/example/marta/data/model/MessageStatus;Lcom/example/marta/data/model/MessageType;Ljava/lang/String;Ljava/util/List;Ljava/lang/String;Ljava/lang/String;ZZ)V", "getContent", "()Ljava/lang/String;", "getData", "()Lcom/example/marta/data/model/ChatData;", "getId", "()Z", "isFromAssistant", "isFromUser", "getReactions", "()Ljava/util/List;", "getReplyToId", "getRole", "getSenderAvatar", "getSenderName", "getStatus", "()Lcom/example/marta/data/model/MessageStatus;", "getTimestamp", "()J", "getType", "()Lcom/example/marta/data/model/MessageType;", "component1", "component10", "component11", "component12", "component13", "component2", "component3", "component4", "component5", "component6", "component7", "component8", "component9", "copy", "equals", "other", "hashCode", "", "toString", "toggleReaction", "emoji", "updateContent", "newContent", "updateStatus", "newStatus", "app_debug"})
@androidx.compose.runtime.Immutable
public final class ChatMessage {
    @org.jetbrains.annotations.NotNull
    private final java.lang.String id = null;
    @com.google.gson.annotations.SerializedName(value = "role")
    @org.jetbrains.annotations.NotNull
    private final java.lang.String role = null;
    @com.google.gson.annotations.SerializedName(value = "content")
    @org.jetbrains.annotations.NotNull
    private final java.lang.String content = null;
    @com.google.gson.annotations.SerializedName(value = "data")
    @org.jetbrains.annotations.Nullable
    private final com.example.marta.data.model.ChatData data = null;
    private final long timestamp = 0L;
    @org.jetbrains.annotations.NotNull
    private final com.example.marta.data.model.MessageStatus status = null;
    @org.jetbrains.annotations.NotNull
    private final com.example.marta.data.model.MessageType type = null;
    @org.jetbrains.annotations.Nullable
    private final java.lang.String replyToId = null;
    @org.jetbrains.annotations.NotNull
    private final java.util.List<java.lang.String> reactions = null;
    @org.jetbrains.annotations.NotNull
    private final java.lang.String senderName = null;
    @org.jetbrains.annotations.Nullable
    private final java.lang.String senderAvatar = null;
    private final boolean isEdited = false;
    private final boolean isPinned = false;
    
    public ChatMessage(@org.jetbrains.annotations.NotNull
    java.lang.String id, @org.jetbrains.annotations.NotNull
    java.lang.String role, @org.jetbrains.annotations.NotNull
    java.lang.String content, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.ChatData data, long timestamp, @org.jetbrains.annotations.NotNull
    com.example.marta.data.model.MessageStatus status, @org.jetbrains.annotations.NotNull
    com.example.marta.data.model.MessageType type, @org.jetbrains.annotations.Nullable
    java.lang.String replyToId, @org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> reactions, @org.jetbrains.annotations.NotNull
    java.lang.String senderName, @org.jetbrains.annotations.Nullable
    java.lang.String senderAvatar, boolean isEdited, boolean isPinned) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String getId() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String getRole() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String getContent() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final com.example.marta.data.model.ChatData getData() {
        return null;
    }
    
    public final long getTimestamp() {
        return 0L;
    }
    
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.MessageStatus getStatus() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.MessageType getType() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getReplyToId() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.util.List<java.lang.String> getReactions() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String getSenderName() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getSenderAvatar() {
        return null;
    }
    
    public final boolean isEdited() {
        return false;
    }
    
    public final boolean isPinned() {
        return false;
    }
    
    public final boolean isFromUser() {
        return false;
    }
    
    public final boolean isFromAssistant() {
        return false;
    }
    
    /**
     * Creates a copy of this message with updated status
     */
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.ChatMessage updateStatus(@org.jetbrains.annotations.NotNull
    com.example.marta.data.model.MessageStatus newStatus) {
        return null;
    }
    
    /**
     * Creates a copy of this message with updated content
     */
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.ChatMessage updateContent(@org.jetbrains.annotations.NotNull
    java.lang.String newContent) {
        return null;
    }
    
    /**
     * Creates a copy of this message with a reaction added or removed
     */
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.ChatMessage toggleReaction(@org.jetbrains.annotations.NotNull
    java.lang.String emoji) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String component1() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String component10() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String component11() {
        return null;
    }
    
    public final boolean component12() {
        return false;
    }
    
    public final boolean component13() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String component2() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String component3() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final com.example.marta.data.model.ChatData component4() {
        return null;
    }
    
    public final long component5() {
        return 0L;
    }
    
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.MessageStatus component6() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.MessageType component7() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String component8() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.util.List<java.lang.String> component9() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final com.example.marta.data.model.ChatMessage copy(@org.jetbrains.annotations.NotNull
    java.lang.String id, @org.jetbrains.annotations.NotNull
    java.lang.String role, @org.jetbrains.annotations.NotNull
    java.lang.String content, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.ChatData data, long timestamp, @org.jetbrains.annotations.NotNull
    com.example.marta.data.model.MessageStatus status, @org.jetbrains.annotations.NotNull
    com.example.marta.data.model.MessageType type, @org.jetbrains.annotations.Nullable
    java.lang.String replyToId, @org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> reactions, @org.jetbrains.annotations.NotNull
    java.lang.String senderName, @org.jetbrains.annotations.Nullable
    java.lang.String senderAvatar, boolean isEdited, boolean isPinned) {
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
}