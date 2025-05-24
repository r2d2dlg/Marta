package com.example.marta.ui.chat.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.marta.R
import com.example.marta.data.model.ChatMessage
import com.example.marta.data.model.MessageType

/**
 * A preview of the message being replied to.
 *
 * @param message The message being replied to
 * @param onDismiss Callback when the reply is dismissed
 * @param modifier Modifier to be applied to the layout
 */
@Composable
fun ReplyPreview(
    message: ChatMessage,
    onDismiss: () -> Unit,
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
        MessageType.APPOINTMENT -> "Appointment: ${message.content.take(40)}${if (message.content.length > 40) "..." else ""}"
        MessageType.EMAIL_DRAFT -> "Email draft: ${message.content.take(40)}${if (message.content.length > 40) "..." else ""}"
        else -> message.content.take(80) + if (message.content.length > 80) "..." else ""
    }

    // Determine the sender name
    val senderName = if (message.isFromUser) "You" else message.senderName

    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f),
        shadowElevation = 1.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp)
        ) {
            // Header with sender info and close button
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
                
                // Sender name
                Text(
                    text = "Replying to $senderName",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )
                
                // Close button
                IconButton(
                    onClick = onDismiss,
                    modifier = Modifier.size(24.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Close,
                        contentDescription = "Dismiss reply",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
            
            // Message preview
            Text(
                text = previewText,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(start = 11.dp) // Align with the text above (3dp line + 8dp spacing)
            )
        }
    }
}
