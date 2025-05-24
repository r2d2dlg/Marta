package com.example.marta.ui.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.marta.R
import com.example.marta.data.model.ChatMessage
import com.example.marta.data.model.MessageStatus
import com.example.marta.data.model.MessageType
import com.example.marta.ui.chat.components.MessageBubble
import com.example.marta.ui.chat.components.ChatInput
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private const val TYPING_INDICATOR_DELAY = 1000L

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    onNavigateBack: () -> Unit = {},
    viewModel: ChatViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberLazyListState()
    var messageToReplyToPreview by remember { mutableStateOf<ChatMessage?>(null) }
    
    LaunchedEffect(uiState.messages.size, messageToReplyToPreview) {
        if (uiState.messages.isNotEmpty()) {
            listState.animateScrollToItem(uiState.messages.size - 1)
        }
    }
    
    // Handle errors
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            // Show error to user (could be replaced with a Snackbar)
            println("Error: $error")
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = stringResource(R.string.app_name),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        },
        content = { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                // Messages list
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .background(MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    if (uiState.messages.isEmpty()) {
                        // Show empty state
                        Box(
                            modifier = Modifier.fillMaxSize(),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = "Start chatting with Marta!",
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(vertical = 8.dp, horizontal = 8.dp),
                            state = listState,
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            items(uiState.messages, key = { it.id }) { message ->
                                val repliedMessage = message.replyToId?.let { replyId ->
                                    uiState.messages.find { it.id == replyId }
                                }
                                MessageBubble(
                                    message = message,
                                    repliedMessage = repliedMessage,
                                    onAppointmentAction = { _, _ ->
                                        // TODO: Handle appointment actions
                                    },
                                    onEmailAction = { _, _ ->
                                        // TODO: Handle email actions
                                    },
                                    onReply = {
                                        messageToReplyToPreview = message
                                        viewModel.setReplyingTo(message.id)
                                    }
                                )
                            }
                        }
                    }
                }

                // Loading indicator for user message sending
                if (uiState.isLoading) {
                    LinearProgressIndicator(
                        modifier = Modifier.fillMaxWidth()
                    )
                }

                // Input field
                ChatInput(
                    onMessageSent = { messageContent ->
                        viewModel.sendMessage(content = messageContent)
                        messageToReplyToPreview = null
                        viewModel.setReplyingTo(null)
                    },
                    replyToMessage = messageToReplyToPreview,
                    onDismissReply = {
                        messageToReplyToPreview = null
                        viewModel.setReplyingTo(null)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .navigationBarsPadding()
                        .imePadding()
                        .padding(8.dp)
                )
            }
        }
    )
}
