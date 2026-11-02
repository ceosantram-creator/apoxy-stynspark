package com.santram.infinity

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

internal object AiBackend {
    suspend fun send(baseUrl: String, token: String, history: List<Pair<String, String>>): String =
        withContext(Dispatchers.IO) {
            require(baseUrl.startsWith("https://")) { "Use an HTTPS backend URL." }
            require(token.isNotBlank()) { "Enter your SANTRAM app access token." }
            val messages = JSONArray()
            history.takeLast(20).forEach { (role, content) ->
                messages.put(JSONObject().put("role", role).put("content", content))
            }
            val connection = (URL(baseUrl.trimEnd('/') + "/v1/chat").openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = 15000
                readTimeout = 50000
                doOutput = true
                setRequestProperty("Content-Type", "application/json")
                setRequestProperty("Authorization", "Bearer $token")
            }
            try {
                connection.outputStream.use {
                    it.write(JSONObject().put("messages", messages).toString().toByteArray(Charsets.UTF_8))
                }
                val code = connection.responseCode
                val stream = if (code in 200..299) connection.inputStream else connection.errorStream
                val body = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
                val json = runCatching { JSONObject(body) }.getOrNull()
                if (code !in 200..299) throw IllegalStateException(
                    when (code) {
                        401 -> "Backend access token rejected."
                        429 -> "Backend rate limit reached. Please wait."
                        503 -> "OpenAI API is not configured on your server yet."
                        else -> json?.optString("error")?.takeIf { it.isNotBlank() } ?: "Backend request failed ($code)."
                    }
                )
                json?.optString("reply")?.takeIf { it.isNotBlank() } ?: "The AI returned an empty response."
            } finally {
                connection.disconnect()
            }
        }
}
