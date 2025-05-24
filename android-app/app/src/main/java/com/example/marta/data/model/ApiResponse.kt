package com.example.marta.data.model

import com.google.gson.annotations.SerializedName

/**
 * Base response from the API
 */
data class ApiResponse<out T>(
    @SerializedName("success") val success: Boolean,
    @SerializedName("data") val data: T? = null,
    @SerializedName("error") val error: String? = null
)

/**
 * Response for chat messages
 */
data class ChatResponse(
    @SerializedName("response") val response: String,
    @SerializedName("data") val data: ChatData? = null
)

/**
 * Error response from the API
 */
data class ErrorResponse(
    @SerializedName("error") val error: String,
    @SerializedName("message") val message: String? = null,
    @SerializedName("statusCode") val statusCode: Int
)
