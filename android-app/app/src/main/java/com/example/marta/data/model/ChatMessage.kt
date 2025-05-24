package com.example.marta.data.model

import androidx.compose.runtime.Immutable
import com.google.gson.annotations.SerializedName
import java.util.UUID

/**
 * Represents the status of a chat message
 */
@Immutable
sealed class MessageStatus {
    @Immutable
    data object Sending : MessageStatus()
    
    @Immutable
    data object Sent : MessageStatus()
    
    @Immutable
    data class Error(val message: String) : MessageStatus()
}

/**
 * Represents the type of a message
 */
enum class MessageType {
    TEXT,
    APPOINTMENT,
    EMAIL_DRAFT,
    LOADING
}

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
@Immutable
data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    @SerializedName("role") val role: String, // 'user' or 'assistant'
    @SerializedName("content") val content: String,
    @SerializedName("data") val data: ChatData? = null,
    val timestamp: Long = System.currentTimeMillis(),
    val status: MessageStatus = if (role == "user") MessageStatus.Sending else MessageStatus.Sent,
    val type: MessageType = when {
        data?.appointment != null -> MessageType.APPOINTMENT
        data?.draft != null -> MessageType.EMAIL_DRAFT
        content.isBlank() -> MessageType.LOADING
        else -> MessageType.TEXT
    },
    val replyToId: String? = null,
    val reactions: List<String> = emptyList(),
    val senderName: String = if (role == "user") "You" else "Marta",
    val senderAvatar: String? = if (role == "user") null else "https://example.com/marta-avatar.png",
    val isEdited: Boolean = false,
    val isPinned: Boolean = false
) {
    val isFromUser: Boolean get() = role == "user"
    val isFromAssistant: Boolean get() = role == "assistant"
    
    /**
     * Creates a copy of this message with updated status
     */
    fun updateStatus(newStatus: MessageStatus): ChatMessage {
        return copy(status = newStatus)
    }
    
    /**
     * Creates a copy of this message with updated content
     */
    fun updateContent(newContent: String): ChatMessage {
        return copy(content = newContent, isEdited = true)
    }
    
    /**
     * Creates a copy of this message with a reaction added or removed
     */
    fun toggleReaction(emoji: String): ChatMessage {
        return if (reactions.contains(emoji)) {
            copy(reactions = reactions - emoji)
        } else {
            copy(reactions = reactions + emoji)
        }
    }
}

/**
 * Additional data that can be sent with a chat message
 */
@Immutable
data class ChatData(
    @SerializedName("type") val type: String? = null,
    @SerializedName("appointment") val appointment: Appointment? = null,
    @SerializedName("draft") val draft: EmailDraft? = null,
    @SerializedName("suggestions") val suggestions: List<String> = emptyList()
) {
    companion object {
        val EMPTY = ChatData()
    }
}

/**
 * Represents an appointment in the chat
 */
@Immutable
data class Appointment(
    @SerializedName("id") val id: String = UUID.randomUUID().toString(),
    @SerializedName("title") val title: String? = null,
    @SerializedName("date") val date: String? = null,
    @SerializedName("time") val time: String? = null,
    @SerializedName("currentStep") val currentStep: String? = null,
    @SerializedName("isConfirmed") val isConfirmed: Boolean = false,
    @SerializedName("participants") val participants: List<String> = emptyList()
) {
    val formattedDateTime: String
        get() = listOfNotNull(date, time).joinToString(" at ")
}

/**
 * Represents an email draft in the chat
 */
@Immutable
data class EmailDraft(
    @SerializedName("id") val id: String = UUID.randomUUID().toString(),
    @SerializedName("to") val to: String,
    @SerializedName("subject") val subject: String,
    @SerializedName("body") val body: String,
    @SerializedName("cc") val cc: List<String> = emptyList(),
    @SerializedName("bcc") val bcc: List<String> = emptyList(),
    @SerializedName("isDraft") val isDraft: Boolean = true
) {
    val recipients: List<String>
        get() = listOf(to) + cc + bcc
}
