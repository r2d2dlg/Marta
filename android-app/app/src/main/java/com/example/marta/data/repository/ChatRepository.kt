package com.example.marta.data.repository

import com.example.marta.data.api.ApiService
import com.example.marta.data.model.ApiResponse
import com.example.marta.data.model.Appointment
import com.example.marta.data.model.ChatResponse
import com.example.marta.data.model.EmailDraft
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ChatRepository @Inject constructor(
    private val apiService: ApiService
) {
    fun sendMessage(
        message: String,
        authToken: String? = null,
        appointment: Appointment? = null,
        draft: EmailDraft? = null,
        replyToMessageId: String? = null
    ): Flow<ApiResponse<ChatResponse>> = flow {
        try {
            val response = apiService.sendMessage(
                token = authToken,
                request = createChatRequest(message, appointment, draft, replyToMessageId)
            )
            if (response.isSuccessful && response.body() != null) {
                emit(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Unknown HTTP error"
                emit(ApiResponse(success = false, data = null, error = "HTTP ${response.code()}: $errorBody"))
            }
        } catch (e: Exception) {
            emit(ApiResponse(success = false, data = null, error = e.message ?: "Network or unexpected error"))
        }
    }.flowOn(Dispatchers.IO)

    @Suppress("UNCHECKED_CAST")
    private fun createChatRequest(
        message: String,
        appointment: Appointment? = null,
        draft: EmailDraft? = null,
        replyToMessageId: String? = null
    ): Map<String, Any> {
        val requestMap = mutableMapOf<String, Any?>(
            "query" to message
        )
        appointment?.let { requestMap["appointment"] = it }
        draft?.let { requestMap["draft"] = it }
        replyToMessageId?.let { requestMap["replyToMessageId"] = it }
        
        return requestMap.filterValues { it != null } as Map<String, Any>
    }
}
