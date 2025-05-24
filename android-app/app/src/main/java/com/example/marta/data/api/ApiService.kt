package com.example.marta.data.api

import com.example.marta.data.model.ApiResponse
import com.example.marta.data.model.ChatMessage
import com.example.marta.data.model.ChatResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Headers
import retrofit2.http.POST

interface ApiService {
    @Headers("Content-Type: application/json")
    @POST("api/assistant")
    suspend fun sendMessage(
        @Header("Authorization") token: String? = null,
        @Body request: Map<String, Any>
    ): Response<ApiResponse<ChatResponse>>

    // Add more API endpoints as needed
}

/**
 * Request body for sending a chat message
 */
data class ChatRequest(
    val query: String,
    val appointment: Map<String, Any>? = null
)

/**
 * Helper function to create a chat request
 */
fun createChatRequest(
    message: String,
    appointment: Map<String, Any>? = null
): Map<String, Any> {
    return mapOf(
        "query" to message,
        "appointment" to (appointment ?: emptyMap<String, Any>())
    )
}
