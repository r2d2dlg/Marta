package com.example.marta.data.model;

import androidx.compose.runtime.Immutable;
import com.google.gson.annotations.SerializedName;
import java.util.UUID;

/**
 * Represents the type of a message
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0006\b\u0086\u0081\u0002\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002j\u0002\b\u0003j\u0002\b\u0004j\u0002\b\u0005j\u0002\b\u0006\u00a8\u0006\u0007"}, d2 = {"Lcom/example/marta/data/model/MessageType;", "", "(Ljava/lang/String;I)V", "TEXT", "APPOINTMENT", "EMAIL_DRAFT", "LOADING", "app_debug"})
public enum MessageType {
    /*public static final*/ TEXT /* = new TEXT() */,
    /*public static final*/ APPOINTMENT /* = new APPOINTMENT() */,
    /*public static final*/ EMAIL_DRAFT /* = new EMAIL_DRAFT() */,
    /*public static final*/ LOADING /* = new LOADING() */;
    
    MessageType() {
    }
    
    @org.jetbrains.annotations.NotNull
    public static kotlin.enums.EnumEntries<com.example.marta.data.model.MessageType> getEntries() {
        return null;
    }
}