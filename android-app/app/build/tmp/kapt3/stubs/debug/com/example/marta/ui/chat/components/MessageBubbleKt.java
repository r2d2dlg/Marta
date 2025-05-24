package com.example.marta.ui.chat.components;

import androidx.compose.animation.*;
import androidx.compose.animation.core.*;
import androidx.compose.foundation.layout.*;
import androidx.compose.material.icons.Icons;
import androidx.compose.material.icons.filled.*;
import androidx.compose.material3.*;
import androidx.compose.runtime.*;
import androidx.compose.ui.Alignment;
import androidx.compose.ui.Modifier;
import androidx.compose.ui.layout.ContentScale;
import androidx.compose.ui.text.style.TextAlign;
import androidx.compose.ui.text.style.TextOverflow;
import androidx.compose.ui.unit.Dp;
import coil.request.ImageRequest;
import com.example.marta.R;
import com.example.marta.data.model.*;
import com.example.marta.data.model.AppointmentAction;
import com.example.marta.data.model.EmailAction;
import java.text.SimpleDateFormat;
import java.util.*;
import java.time.LocalDateTime;

@kotlin.Metadata(mv = {1, 9, 0}, k = 2, xi = 48, d1 = {"\u00000\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\u001an\u0010\u0000\u001a\u00020\u00012\u0006\u0010\u0002\u001a\u00020\u00032\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u00032\u001a\b\u0002\u0010\u0005\u001a\u0014\u0012\u0004\u0012\u00020\u0007\u0012\u0004\u0012\u00020\b\u0012\u0004\u0012\u00020\u00010\u00062\u001a\b\u0002\u0010\t\u001a\u0014\u0012\u0004\u0012\u00020\n\u0012\u0004\u0012\u00020\b\u0012\u0004\u0012\u00020\u00010\u00062\u000e\b\u0002\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\u00010\f2\b\b\u0002\u0010\r\u001a\u00020\u000eH\u0007\u00a8\u0006\u000f"}, d2 = {"MessageBubble", "", "message", "Lcom/example/marta/data/model/ChatMessage;", "repliedMessage", "onAppointmentAction", "Lkotlin/Function2;", "Lcom/example/marta/data/model/AppointmentAction;", "", "onEmailAction", "Lcom/example/marta/data/model/EmailAction;", "onReply", "Lkotlin/Function0;", "modifier", "Landroidx/compose/ui/Modifier;", "app_debug"})
public final class MessageBubbleKt {
    
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
    @kotlin.OptIn(markerClass = {androidx.compose.animation.ExperimentalAnimationApi.class})
    @androidx.compose.runtime.Composable
    public static final void MessageBubble(@org.jetbrains.annotations.NotNull
    com.example.marta.data.model.ChatMessage message, @org.jetbrains.annotations.Nullable
    com.example.marta.data.model.ChatMessage repliedMessage, @org.jetbrains.annotations.NotNull
    kotlin.jvm.functions.Function2<? super com.example.marta.data.model.AppointmentAction, ? super java.lang.String, kotlin.Unit> onAppointmentAction, @org.jetbrains.annotations.NotNull
    kotlin.jvm.functions.Function2<? super com.example.marta.data.model.EmailAction, ? super java.lang.String, kotlin.Unit> onEmailAction, @org.jetbrains.annotations.NotNull
    kotlin.jvm.functions.Function0<kotlin.Unit> onReply, @org.jetbrains.annotations.NotNull
    androidx.compose.ui.Modifier modifier) {
    }
}