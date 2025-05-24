package com.example.marta.ui.chat.components;

import androidx.compose.foundation.layout.*;
import androidx.compose.material.icons.Icons;
import androidx.compose.runtime.Composable;
import androidx.compose.ui.Alignment;
import androidx.compose.ui.Modifier;
import androidx.compose.ui.text.style.TextOverflow;
import com.example.marta.R;
import com.example.marta.data.model.MessageStatus;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;

@kotlin.Metadata(mv = {1, 9, 0}, k = 2, xi = 48, d1 = {"\u0000 \n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0000\u001a0\u0010\u0000\u001a\u00020\u00012\b\b\u0002\u0010\u0002\u001a\u00020\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u00052\b\b\u0002\u0010\u0006\u001a\u00020\u00072\b\b\u0002\u0010\b\u001a\u00020\tH\u0007\u00a8\u0006\n"}, d2 = {"MessageStatusIndicator", "", "status", "Lcom/example/marta/data/model/MessageStatus;", "timestamp", "Ljava/time/LocalDateTime;", "showTime", "", "modifier", "Landroidx/compose/ui/Modifier;", "app_debug"})
public final class MessageStatusIndicatorKt {
    
    @androidx.compose.runtime.Composable
    public static final void MessageStatusIndicator(@org.jetbrains.annotations.NotNull
    com.example.marta.data.model.MessageStatus status, @org.jetbrains.annotations.NotNull
    java.time.LocalDateTime timestamp, boolean showTime, @org.jetbrains.annotations.NotNull
    androidx.compose.ui.Modifier modifier) {
    }
}