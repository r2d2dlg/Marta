package com.example.marta.ui.chat.components;

import androidx.compose.foundation.layout.Arrangement;
import androidx.compose.foundation.text.KeyboardOptions;
import androidx.compose.material.icons.Icons;
import androidx.compose.material3.ExperimentalMaterial3Api;
import androidx.compose.material3.OutlinedTextFieldDefaults;
import androidx.compose.runtime.Composable;
import androidx.compose.ui.Alignment;
import androidx.compose.ui.ExperimentalComposeUiApi;
import androidx.compose.ui.Modifier;
import androidx.compose.ui.focus.FocusRequester;
import androidx.compose.ui.text.input.ImeAction;
import com.example.marta.data.model.ChatMessage;

@kotlin.Metadata(mv = {1, 9, 0}, k = 2, xi = 48, d1 = {"\u0000.\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0002\u001a`\u0010\u0000\u001a\u00020\u00012\u0012\u0010\u0002\u001a\u000e\u0012\u0004\u0012\u00020\u0004\u0012\u0004\u0012\u00020\u00010\u00032\n\b\u0002\u0010\u0005\u001a\u0004\u0018\u00010\u00062\u000e\b\u0002\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00010\b2\b\b\u0002\u0010\t\u001a\u00020\n2\b\b\u0002\u0010\u000b\u001a\u00020\u00042\b\b\u0002\u0010\f\u001a\u00020\r2\b\b\u0002\u0010\u000e\u001a\u00020\rH\u0007\u00a8\u0006\u000f"}, d2 = {"ChatInput", "", "onMessageSent", "Lkotlin/Function1;", "", "replyToMessage", "Lcom/example/marta/data/model/ChatMessage;", "onDismissReply", "Lkotlin/Function0;", "modifier", "Landroidx/compose/ui/Modifier;", "placeholderText", "maxLines", "", "minLines", "app_debug"})
public final class ChatInputKt {
    
    /**
     * A customizable input field for sending chat messages with support for replying to messages.
     *
     * @param onMessageSent Callback when the user sends a message
     * @param replyToMessage Optional message that the user is replying to
     * @param onDismissReply Callback when the user dismisses the reply
     * @param modifier Modifier to be applied to the layout
     */
    @kotlin.OptIn(markerClass = {androidx.compose.material3.ExperimentalMaterial3Api.class, androidx.compose.ui.ExperimentalComposeUiApi.class})
    @androidx.compose.runtime.Composable
    public static final void ChatInput(@org.jetbrains.annotations.NotNull
    kotlin.jvm.functions.Function1<? super java.lang.String, kotlin.Unit> onMessageSent, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.ChatMessage replyToMessage, @org.jetbrains.annotations.NotNull
    kotlin.jvm.functions.Function0<kotlin.Unit> onDismissReply, @org.jetbrains.annotations.NotNull
    androidx.compose.ui.Modifier modifier, @org.jetbrains.annotations.NotNull
    java.lang.String placeholderText, int maxLines, int minLines) {
    }
}