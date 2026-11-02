package com.santram.infinity

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Button
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.AssistChip
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { InfinityHome() }
    }
}

@Composable
private fun InfinityHome() {
    var command by remember { mutableStateOf("") }
    var tasks by remember { mutableStateOf(listOf<String>()) }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            Column(
                modifier = Modifier.fillMaxSize().padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text("SANTRAM PERSONAL AI", style = MaterialTheme.typography.headlineSmall)
                Text("INFINITY · Android 15 foundation", style = MaterialTheme.typography.titleMedium)
                AssistChip(onClick = {}, label = { Text("SILENT MODE · ON") })

                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Command Inbox", style = MaterialTheme.typography.titleLarge)
                        Text("Text-first workspace. Voice capture is not enabled in this build.")
                        OutlinedTextField(
                            value = command,
                            onValueChange = { command = it },
                            modifier = Modifier.fillMaxWidth(),
                            label = { Text("Enter a task or business instruction") }
                        )
                        Button(
                            onClick = {
                                val clean = command.trim()
                                if (clean.isNotEmpty()) {
                                    tasks = listOf(clean) + tasks
                                    command = ""
                                }
                            },
                            enabled = command.isNotBlank()
                        ) { Text("Add to inbox") }
                    }
                }

                Text("Workspace Modules", style = MaterialTheme.typography.titleLarge)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    ModuleCard("Personal", "Tasks & notes", Modifier.weight(1f))
                    ModuleCard("Business", "Customers & invoices", Modifier.weight(1f))
                }
                ModuleCard("Memory & Backup", "Local-first · approval required", Modifier.fillMaxWidth())

                Text("Captured Tasks", style = MaterialTheme.typography.titleLarge)
                if (tasks.isEmpty()) {
                    Text("No tasks captured yet.")
                } else {
                    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(tasks) { item ->
                            Card(Modifier.fillMaxWidth()) {
                                Text(item, Modifier.padding(12.dp))
                            }
                        }
                    }
                }
                Spacer(Modifier.height(4.dp))
                Text(
                    "Privacy: no microphone, notification, location, or accessibility access is requested in this foundation build.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun ModuleCard(title: String, subtitle: String, modifier: Modifier = Modifier) {
    Card(modifier = modifier) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            Text(subtitle, style = MaterialTheme.typography.bodySmall)
        }
    }
}
