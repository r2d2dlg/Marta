package com.example.marta.ui.chat.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DoneAll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.example.marta.R
import com.example.marta.data.model.MessageStatus
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

@Composable
fun MessageStatusIndicator(
    status: com.example.marta.data.model.MessageStatus = com.example.marta.data.model.MessageStatus.Sent,
    timestamp: LocalDateTime = LocalDateTime.now(),
    showTime: Boolean = true,
    modifier: Modifier = Modifier
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.End,
        modifier = modifier
    ) {
        if (showTime) {
            val timeText = when {
                ChronoUnit.MINUTES.between(timestamp, LocalDateTime.now()) < 1 -> "Just now"
                ChronoUnit.HOURS.between(timestamp, LocalDateTime.now()) < 24 -> 
                    timestamp.format(DateTimeFormatter.ofPattern("h:mm a"))
                else -> timestamp.format(DateTimeFormatter.ofPattern("MMM d"))
            }
            
            Text(
                text = timeText,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.outline,
                maxLines = 1,
                overflow = TextOverflow.Visible,
                modifier = Modifier.padding(end = 4.dp)
            )
        }

        when (status) {
            is com.example.marta.data.model.MessageStatus.Sending -> {
                Icon(
                    painter = painterResource(id = R.drawable.ic_clock), // You'll need to add this drawable
                    contentDescription = "Sending",
                    tint = MaterialTheme.colorScheme.outline,
                    modifier = Modifier.size(14.dp)
                )
            }
            is com.example.marta.data.model.MessageStatus.Sent -> {
                Icon(
                    imageVector = Icons.Default.DoneAll,
                    contentDescription = "Sent",
                    tint = MaterialTheme.colorScheme.outline,
                    modifier = Modifier.size(14.dp)
                )
            }
            is com.example.marta.data.model.MessageStatus.Error -> {
                Icon(
                    painter = painterResource(id = R.drawable.ic_error), // You'll need to add this drawable
                    contentDescription = "Failed: ${status.message}",
                    tint = MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(14.dp)
                )
            }
        }
    }
}
