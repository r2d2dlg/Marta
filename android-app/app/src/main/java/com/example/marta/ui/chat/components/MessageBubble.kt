package com.example.marta.ui.chat.components

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Reply
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.example.marta.R
import com.example.marta.data.model.*
import com.example.marta.data.model.AppointmentAction
import com.example.marta.data.model.EmailAction
import com.example.marta.ui.components.Avatar
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.absoluteValue
import kotlin.math.roundToInt
import com.example.marta.ui.chat.components.TextMessageBubble
import com.example.marta.ui.chat.components.AppointmentMessageBubble
import com.example.marta.ui.chat.components.EmailDraftMessageBubble
import com.example.marta.ui.chat.components.TypingIndicator
import com.example.marta.ui.chat.components.ReactionChip
import com.example.marta.ui.chat.components.MessageStatusIndicator
import java.time.LocalDateTime

/**
 * Composable that displays a chat message with swipe-to-reply and enhanced styling.
 *
 * @param message The chat message to display
 * @param repliedMessage The message that this message is replying to, if any
 * @param onAppointmentAction Callback when an appointment action is performed
 * @param onEmailAction Callback when an email action is performed
 * @param onReply Callback when the reply action is triggered
 * @param modifier Modifier to be applied to the message bubble
 */
@OptIn(ExperimentalAnimationApi::class)
@Composable
fun MessageBubble(
    message: ChatMessage,
    repliedMessage: ChatMessage? = null,
    onAppointmentAction: (AppointmentAction, String) -> Unit = { _, _ -> },
    onEmailAction: (EmailAction, String) -> Unit = { _, _ -> },
    onReply: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val isUser = message.isFromUser
    val slideOffset = if (isUser) 100 else -100
    val coroutineScope = rememberCoroutineScope()
    val density = LocalDensity.current
    
    // Swipe to reply state
    var offsetX by remember { mutableStateOf(0f) }
    val maxSwipeOffset = 80.dp
    val swipeThreshold = 60.dp
    
    // Animation specs
    val enterTransition = remember {
        fadeIn(animationSpec = tween(300)) + 
        slideInHorizontally(
            initialOffsetX = { slideOffset },
            animationSpec = tween(durationMillis = 400, easing = FastOutSlowInEasing)
        )
    }
    
    val exitTransition = remember {
        fadeOut(animationSpec = tween(300)) + 
        slideOutHorizontally(
            targetOffsetX = { -slideOffset },
            animationSpec = tween(durationMillis = 400, easing = FastOutSlowInEasing)
        )
    }
    
    // Reset offset when message changes
    LaunchedEffect(message.id) {
        offsetX = 0f
    }
    
    // Handle swipe to reply
    val onSwipe: (Float) -> Unit = { delta ->
        if (!isUser) { // Only allow swiping assistant's messages
            val newOffset = with(density) {
                (offsetX + delta).coerceIn(
                    -maxSwipeOffset.toPx(),
                    maxSwipeOffset.toPx()
                )
            }
            offsetX = newOffset
            
            // If swiped past threshold, trigger reply
            if (with(density) { newOffset.absoluteValue >= swipeThreshold.toPx() }) {
                coroutineScope.launch {
                    // Animate to max offset
                    offsetX = with(density) {
                        if (newOffset > 0) maxSwipeOffset.toPx() else -maxSwipeOffset.toPx()
                    }
                    delay(200)
                    onReply()
                    // Reset position
                    offsetX = 0f
                }
            }
        }
    }
    
    AnimatedVisibility(
        visible = true,
        enter = enterTransition,
        exit = exitTransition,
        modifier = modifier
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp, vertical = 4.dp)
        ) {
            // Swipe hint
            if (!isUser) {
                Row(
                    modifier = Modifier
                        .align(Alignment.CenterEnd)
                        .padding(end = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.Reply,
                        contentDescription = "Reply",
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Swipe to reply",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
            
            Column(
                modifier = Modifier
                    .offset(x = offsetX.dp)
                    .pointerInput(Unit) {
                        detectHorizontalDragGestures(
                            onDragEnd = {
                                if (offsetX.absoluteValue < swipeThreshold.toPx()) {
                                    coroutineScope.launch {
                                        animate(initialValue = offsetX, targetValue = 0f) { value, _ ->
                                            offsetX = value
                                        }
                                    }
                                }
                            },
                            onHorizontalDrag = { _, dragAmount ->
                                onSwipe(dragAmount)
                            }
                        )
                    }
                    .graphicsLayer {
                        // Add a slight rotation when swiping
                        val rotation = (offsetX / 20f).coerceIn(-10f, 10f)
                        rotationZ = if (isUser) 0f else rotation
                    }
                    .fillMaxWidth(if (isUser) 0.85f else 0.9f)
                    .padding(horizontal = 8.dp, vertical = 4.dp)
                    .align(if (isUser) Alignment.CenterEnd else Alignment.CenterStart),
                horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
            ) {
                // Message content
                Row(
                    horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start,
                    verticalAlignment = Alignment.Bottom,
                    modifier = Modifier.padding(horizontal = 8.dp)
                ) {
                    if (!isUser) {
                        // Avatar for assistant
                        Avatar(
                            name = message.senderName,
                            imageUrl = message.senderAvatar,
                            modifier = Modifier
                                .size(32.dp)
                                .align(Alignment.Bottom)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                    }
                    
                    // Main message bubble with elevation and shadow
                    Surface(
                        shape = RoundedCornerShape(
                            topStart = 16.dp,
                            topEnd = 16.dp,
                            bottomStart = if (isUser) 16.dp else 4.dp,
                            bottomEnd = if (isUser) 4.dp else 16.dp
                        ),
                        color = if (isUser) 
                            MaterialTheme.colorScheme.primaryContainer 
                        else 
                            MaterialTheme.colorScheme.surfaceVariant,
                        tonalElevation = 2.dp,
                        shadowElevation = 1.dp,
                        modifier = Modifier
                            .clip(
                                RoundedCornerShape(
                                    topStart = 16.dp,
                                    topEnd = 16.dp,
                                    bottomStart = if (isUser) 16.dp else 4.dp,
                                    bottomEnd = if (isUser) 4.dp else 16.dp
                                )
                            )
                            .animateContentSize()
                    ) {
                        when (message.type) {
                            MessageType.TEXT -> TextMessageBubble(message, isUser)
                            MessageType.APPOINTMENT -> AppointmentMessageBubble(
                                message,
                                onAction = onAppointmentAction
                            )
                            MessageType.EMAIL_DRAFT -> EmailDraftMessageBubble(
                                message,
                                onAction = onEmailAction
                            )
                            MessageType.LOADING -> TypingIndicator()
                        }
                    }
                    
                    if (isUser) {
                        Spacer(modifier = Modifier.width(8.dp))
                        // Avatar for user
                        Avatar(
                            name = message.senderName,
                            imageUrl = message.senderAvatar,
                            modifier = Modifier
                                .size(32.dp)
                                .align(Alignment.Bottom),
                            isUser = true
                        )
                    }
                }
                
                // Message status, timestamp, and reactions
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp, vertical = 2.dp),
                    horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
                ) {
                    // Reactions row
                    if (message.reactions.isNotEmpty()) {
                        Row(
                            modifier = Modifier.padding(bottom = 2.dp)
                        ) {
                            message.reactions.forEach { reaction ->
                                ReactionChip(emoji = reaction, onClick = {
                                    // Handle reaction tap
                                })
                                Spacer(modifier = Modifier.width(4.dp))
                            }
                        }
                    }
                    
                    // Status and timestamp row
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        if (isUser) {
                            MessageStatusIndicator(
                                status = message.status,
                                timestamp = LocalDateTime.ofInstant(
                                    java.time.Instant.ofEpochMilli(message.timestamp),
                                    java.time.ZoneId.systemDefault()
                                )
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                        }
                        
                        // Timestamp
                        Text(
                            text = SimpleDateFormat("h:mm a", Locale.getDefault())
                                .format(Date(message.timestamp)),
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.align(Alignment.CenterVertically)
                        )
                    }
                    
                    // Show replied message preview if this is a reply
                    if (message.replyToId != null && repliedMessage != null) {
                        RepliedMessagePreview(
                            message = repliedMessage,
                            isUserMessage = isUser,
                            modifier = Modifier
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                                .fillMaxWidth()
                        )
                    }
                }
            }
        }
    }
    
    // Message actions
    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        // Reply button
        IconButton(
            onClick = onReply,
            modifier = Modifier.size(24.dp)
        ) {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.Reply,
                contentDescription = "Reply",
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        // Add more actions as needed
    }
}
