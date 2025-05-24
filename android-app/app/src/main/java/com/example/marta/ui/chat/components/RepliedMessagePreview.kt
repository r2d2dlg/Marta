package com.example.marta.ui.chat.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.example.marta.data.model.ChatMessage
import com.example.marta.data.model.MessageType

/**
 * A preview of a replied message shown above the current message.
 *
 * @param message The message being replied to
 * @param isUserMessage Whether the current message is from the user
 * @param onClick Optional click handler for the preview
 * @param modifier Modifier to be applied to the layout
 */
@Composable
fun RepliedMessagePreview(
    message: ChatMessage,
    isUserMessage: Boolean,
    onClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    // Determine the color of the reply indicator based on the message type
    val replyIndicatorColor = when (message.type) {
        MessageType.APPOINTMENT -> MaterialTheme.colorScheme.tertiary
        MessageType.EMAIL_DRAFT -> MaterialTheme.colorScheme.secondary
        else -> MaterialTheme.colorScheme.primary
    }

    // Format the preview text based on message type
    val previewText = when (message.type) {
        MessageType.APPOINTMENT -> "📅 ${message.content.take(40)}${if (message.content.length > 40) "..." else ""}"
        MessageType.EMAIL_DRAFT -> "✉️ ${message.content.take(40)}${if (message.content.length > 40) "..." else ""}"
        else -> message.content.take(80) + if (message.content.length > 80) "..." else ""
    }

    // Determine the sender name
    val senderName = if (message.isFromUser) "You" else message.senderName

    // Determine background and content colors based on the current message's sender
    val backgroundColor = if (isUserMessage) {
        MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)
    } else {
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)
    }

    val contentColor = if (isUserMessage) {
        MaterialTheme.colorScheme.onPrimary
    } else {
        MaterialTheme.colorScheme.onSurfaceVariant
    }

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(backgroundColor)
            .border(
                width = 1.dp,
                color = replyIndicatorColor.copy(alpha = 0.5f),
                shape = RoundedCornerShape(8.dp)
            )
            .then(if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier)
            .padding(8.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            // Reply indicator line
            Box(
                modifier = Modifier
                    .width(3.dp)
                    .height(24.dp)
                    .background(
                        color = replyIndicatorColor,
                        shape = RoundedCornerShape(2.dp)
                    )
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            // Message preview content
            Column(
                modifier = Modifier.weight(1f)
            ) {
                // Sender name
                Text(
                    text = senderName,
                    style = MaterialTheme.typography.labelSmall,
                    color = contentColor,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                
                // Message preview
                Text(
                    text = previewText,
                    style = MaterialTheme.typography.bodySmall,
                    color = contentColor.copy(alpha = 0.8f),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.padding(top = 2.dp)
                )
            }
        }
    }
}
