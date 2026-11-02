package com.santram.infinity

import android.content.Context
import android.content.Intent
import android.app.AlarmManager
import android.app.PendingIntent
import android.app.TimePickerDialog
import android.os.Build
import android.speech.RecognizerIntent
import android.speech.tts.TextToSpeech
import android.widget.Toast
import java.util.Calendar
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

private const val PREFS_NAME = "santram_infinity_local"
private const val DATA_KEY = "operating_system_data_v2"
private const val SILENT_KEY = "silent_mode_v1"

private data class TaskRecord(val id: String, val text: String, val createdAt: Long, val done: Boolean)
private data class CustomerRecord(val id: String, val name: String, val phone: String, val gstin: String)
private data class InvoiceRecord(val id: String, val customer: String, val description: String, val amount: Double, val createdAt: Long)

private data class OsData(
    val tasks: List<TaskRecord> = emptyList(),
    val customers: List<CustomerRecord> = emptyList(),
    val invoices: List<InvoiceRecord> = emptyList()
)

private enum class Screen(val label: String) {
    HOME("Home"), PERSONAL("Personal"), BUSINESS("Business"), INVOICES("Invoices"), BACKUP("Memory & Backup")
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { SantramOperatingSystem() }
    }
}

@Composable
private fun SantramOperatingSystem() {
    val context = LocalContext.current
    val prefs = remember(context) { context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE) }
    var data by remember { mutableStateOf(readData(prefs.getString(DATA_KEY, null))) }
    var screen by remember { mutableStateOf(Screen.HOME) }
    var silent by remember { mutableStateOf(prefs.getBoolean(SILENT_KEY, true)) }
    var status by remember { mutableStateOf("Local-first mode · This device") }

    val voiceLauncher = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        val spoken = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull()
        if (!spoken.isNullOrBlank()) {
            persist(data.copy(tasks = listOf(TaskRecord(UUID.randomUUID().toString(), spoken, System.currentTimeMillis(), false)) + data.tasks))
            status = "Voice command captured and saved"
        } else if (result.resultCode == android.app.Activity.RESULT_OK) status = "No speech was recognized"
    }
    val notificationPermission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { }
    fun startVoiceCapture() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak your task")
        }
        runCatching { voiceLauncher.launch(intent) }
            .onFailure { status = "Speech service unavailable on this device" }
    }
    fun scheduleAlarm(hour: Int, minute: Int) {
        val alarmTime = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, hour); set(Calendar.MINUTE, minute); set(Calendar.SECOND, 0); set(Calendar.MILLISECOND, 0)
            if (timeInMillis <= System.currentTimeMillis()) add(Calendar.DAY_OF_YEAR, 1)
        }
        val alarmIntent = Intent(context, AlarmReceiver::class.java).putExtra("alarm_label", "SANTRAM reminder")
        val pending = PendingIntent.getBroadcast(context, (hour * 60 + minute), alarmIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val manager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        manager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, alarmTime.timeInMillis, pending)
        status = "Alarm scheduled for " + SimpleDateFormat("hh:mm a", Locale.getDefault()).format(alarmTime.time)
        if (Build.VERSION.SDK_INT >= 33) notificationPermission.launch(android.Manifest.permission.POST_NOTIFICATIONS)
    }

    fun persist(updated: OsData) {
        val saved = prefs.edit().putString(DATA_KEY, encodeData(updated).toString()).commit()
        if (saved) {
            data = updated
            status = "Saved securely on this device"
        } else {
            status = "Save failed · Please retry"
        }
    }

    val exportLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.CreateDocument("application/json")
    ) { uri: Uri? ->
        if (uri != null) {
            runCatching {
                context.contentResolver.openOutputStream(uri)?.use { stream ->
                    stream.write(encodeData(data).toString(2).toByteArray(Charsets.UTF_8))
                } ?: error("Unable to open destination")
            }.onSuccess { status = "Backup exported successfully" }
                .onFailure { status = "Backup export failed: ${it.message}" }
        }
    }

    val importLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri: Uri? ->
        if (uri != null) {
            runCatching {
                val raw = context.contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
                    ?: error("Unable to read selected file")
                decodeData(JSONObject(raw))
            }.onSuccess { imported ->
                persist(imported)
                status = "Backup restored on this device"
            }.onFailure { status = "Restore failed: ${it.message}" }
        }
    }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            Column(
                modifier = Modifier.fillMaxSize().padding(18.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text("SANTRAM INDUSTRIES", style = MaterialTheme.typography.headlineSmall)
                Text("AI OPERATING SYSTEM · INFINITY", style = MaterialTheme.typography.titleMedium)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("SILENT MODE", modifier = Modifier.weight(1f))
                    Switch(checked = silent, onCheckedChange = {
                        silent = it
                        prefs.edit().putBoolean(SILENT_KEY, it).apply()
                    })
                }
                Text(if (silent) "Silent by default · No spoken output" else "Silent mode off · Voice output is not implemented")
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Screen.entries.take(3).forEach { item ->
                        OutlinedButton(onClick = { screen = item }, modifier = Modifier.weight(1f)) {
                            Text(item.label, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Screen.entries.drop(3).forEach { item ->
                        OutlinedButton(onClick = { screen = item }, modifier = Modifier.weight(1f)) {
                            Text(item.label, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
                Text(status, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.secondary)
                when (screen) {
                    Screen.HOME -> HomeScreen(data, onNavigate = { screen = it })
                    Screen.PERSONAL -> PersonalScreen(data, onAdd = { text ->
                        persist(data.copy(tasks = listOf(TaskRecord(UUID.randomUUID().toString(), text, System.currentTimeMillis(), false)) + data.tasks))
                    }, onToggle = { id ->
                        persist(data.copy(tasks = data.tasks.map { if (it.id == id) it.copy(done = !it.done) else it }))
                    }, onVoice = { startVoiceCapture() }, onAlarm = { hour, minute -> scheduleAlarm(hour, minute) })
                    Screen.BUSINESS -> BusinessScreen(data, onAdd = { name, phone, gstin ->
                        persist(data.copy(customers = listOf(CustomerRecord(UUID.randomUUID().toString(), name, phone, gstin)) + data.customers))
                    })
                    Screen.INVOICES -> InvoiceScreen(data, onAdd = { customer, description, amount ->
                        persist(data.copy(invoices = listOf(InvoiceRecord("SI-${System.currentTimeMillis()}", customer, description, amount, System.currentTimeMillis())) + data.invoices))
                    })
                    Screen.BACKUP -> BackupScreen(
                        onExport = { exportLauncher.launch("santram-infinity-backup.json") },
                        onImport = { importLauncher.launch(arrayOf("application/json", "text/json")) }
                    )
                }
            }
        }
    }
}

@Composable
private fun HomeScreen(data: OsData, onNavigate: (Screen) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        item { Text("Central Command Dashboard", style = MaterialTheme.typography.titleLarge) }
        item { Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            MetricCard("Open tasks", data.tasks.count { !it.done }.toString(), Modifier.weight(1f))
            MetricCard("Customers", data.customers.size.toString(), Modifier.weight(1f))
            MetricCard("Invoices", data.invoices.size.toString(), Modifier.weight(1f))
        } }
        item { Text("Operating modules", style = MaterialTheme.typography.titleMedium) }
        item { ModuleButton("Personal command center", "Tasks and reminders stored locally") { onNavigate(Screen.PERSONAL) } }
        item { ModuleButton("SANTRAM Business", "Customer master and contact records") { onNavigate(Screen.BUSINESS) } }
        item { ModuleButton("Invoices & receivables", "Local invoice register · tax engine pending") { onNavigate(Screen.INVOICES) } }
        item { ModuleButton("Memory & Backup", "Export and restore a JSON backup") { onNavigate(Screen.BACKUP) } }
        item { Text("AI provider, cloud sync and GST-compliant invoice issuance are not connected yet. Voice capture and local alarm scheduling are available in Build 5.", style = MaterialTheme.typography.bodySmall) }
    }
}

@Composable
private fun PersonalScreen(data: OsData, onAdd: (String) -> Unit, onToggle: (String) -> Unit, onVoice: () -> Unit, onAlarm: (Int, Int) -> Unit) {
    val context = LocalContext.current
    var command by remember { mutableStateOf("") }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("Personal Command Inbox", style = MaterialTheme.typography.titleLarge)
        OutlinedTextField(value = command, onValueChange = { command = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Enter task, note or reminder") })
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { onAdd(command.trim()); command = "" }, enabled = command.isNotBlank()) { Text("Save task") }
            OutlinedButton(onClick = onVoice) { Text("Speak task") }
        }
        OutlinedButton(onClick = {
            val now = Calendar.getInstance()
            TimePickerDialog(context, { _, hour, minute -> onAlarm(hour, minute) },
                now.get(Calendar.HOUR_OF_DAY), now.get(Calendar.MINUTE), false).show()
        }, modifier = Modifier.fillMaxWidth()) { Text("Set a real Android alarm") }
        Text("Captured tasks · ${data.tasks.size}", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            items(data.tasks, key = { it.id }) { task ->
                Card(Modifier.fillMaxWidth()) {
                    Row(Modifier.padding(12.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Switch(checked = task.done, onCheckedChange = { onToggle(task.id) })
                        Column {
                            Text(task.text)
                            Text(if (task.done) "Completed" else "Open · " + dateLabel(task.createdAt), style = MaterialTheme.typography.bodySmall)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun BusinessScreen(data: OsData, onAdd: (String, String, String) -> Unit) {
    var name by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var gstin by remember { mutableStateOf("") }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("SANTRAM INDUSTRIES · Customers", style = MaterialTheme.typography.titleLarge)
        OutlinedTextField(name, { name = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Customer / company name *") }, singleLine = true)
        OutlinedTextField(phone, { phone = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Phone number") }, singleLine = true)
        OutlinedTextField(gstin, { gstin = it }, modifier = Modifier.fillMaxWidth(), label = { Text("GSTIN (optional)") }, singleLine = true)
        Button(onClick = { onAdd(name.trim(), phone.trim(), gstin.trim()); name = ""; phone = ""; gstin = "" }, enabled = name.isNotBlank()) { Text("Add customer") }
        Text("Customer master · ${data.customers.size}", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            items(data.customers, key = { it.id }) { customer ->
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(12.dp)) {
                        Text(customer.name, style = MaterialTheme.typography.titleMedium)
                        if (customer.phone.isNotBlank()) Text(customer.phone)
                        if (customer.gstin.isNotBlank()) Text("GSTIN: ${customer.gstin}")
                    }
                }
            }
        }
    }
}

@Composable
private fun InvoiceScreen(data: OsData, onAdd: (String, String, Double) -> Unit) {
    var customer by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var amount by remember { mutableStateOf("") }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("Invoice Register · Draft records", style = MaterialTheme.typography.titleLarge)
        OutlinedTextField(customer, { customer = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Customer name *") }, singleLine = true)
        OutlinedTextField(description, { description = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Product / service description *") })
        OutlinedTextField(amount, { amount = it.filter { c -> c.isDigit() || c == '.' } }, modifier = Modifier.fillMaxWidth(), label = { Text("Amount ₹ *") }, singleLine = true)
        Button(onClick = {
            onAdd(customer.trim(), description.trim(), amount.toDouble())
            customer = ""; description = ""; amount = ""
        }, enabled = customer.isNotBlank() && description.isNotBlank() && (amount.toDoubleOrNull() ?: 0.0) > 0.0) { Text("Save invoice draft") }
        Text("Saved records · ${data.invoices.size}", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            items(data.invoices, key = { it.id }) { invoice ->
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(12.dp)) {
                        Text(invoice.id, style = MaterialTheme.typography.titleMedium)
                        Text(invoice.customer)
                        Text(invoice.description)
                        Text("₹ ${String.format(Locale.US, "%.2f", invoice.amount)}")
                        Text(dateLabel(invoice.createdAt), style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
        Text("These are internal draft records, not GST tax invoices. No invoice numbering compliance, tax calculation, PDF issuance or e-invoicing is enabled.", style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
private fun BackupScreen(onExport: () -> Unit, onImport: () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text("Memory & Backup", style = MaterialTheme.typography.titleLarge)
        Text("Your operating records stay on this device unless you explicitly export them.")
        Button(onClick = onExport, modifier = Modifier.fillMaxWidth()) { Text("Export backup JSON") }
        OutlinedButton(onClick = onImport, modifier = Modifier.fillMaxWidth()) { Text("Restore from backup JSON") }
        Text("Choose a secure destination you control. Keep backup files private. Import replaces the current local task, customer and invoice records.", style = MaterialTheme.typography.bodySmall)
        Text("Cloud sync and Google Drive connection are not active.", style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
private fun MetricCard(label: String, value: String, modifier: Modifier = Modifier) {
    Card(modifier) { Column(Modifier.padding(12.dp)) { Text(value, style = MaterialTheme.typography.headlineSmall); Text(label, style = MaterialTheme.typography.bodySmall) } }
}

@Composable
private fun ModuleButton(title: String, subtitle: String, onClick: () -> Unit) {
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(12.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            Text(subtitle, style = MaterialTheme.typography.bodySmall)
            Spacer(Modifier.height(6.dp))
            OutlinedButton(onClick = onClick) { Text("Open module") }
        }
    }
}

private fun dateLabel(time: Long): String = SimpleDateFormat("dd MMM yyyy, hh:mm a", Locale.getDefault()).format(Date(time))

private fun encodeData(data: OsData): JSONObject = JSONObject().apply {
    put("schemaVersion", 2)
    put("product", "SANTRAM INDUSTRIES AI Operating System")
    put("tasks", JSONArray().apply { data.tasks.forEach { put(JSONObject().apply {
        put("id", it.id); put("text", it.text); put("createdAt", it.createdAt); put("done", it.done)
    }) } })
    put("customers", JSONArray().apply { data.customers.forEach { put(JSONObject().apply {
        put("id", it.id); put("name", it.name); put("phone", it.phone); put("gstin", it.gstin)
    }) } })
    put("invoices", JSONArray().apply { data.invoices.forEach { put(JSONObject().apply {
        put("id", it.id); put("customer", it.customer); put("description", it.description); put("amount", it.amount); put("createdAt", it.createdAt)
    }) } })
}

private fun decodeData(root: JSONObject): OsData {
    fun array(name: String) = root.optJSONArray(name) ?: JSONArray()
    val tasks = array("tasks").let { a -> List(a.length()) { i -> a.getJSONObject(i).let {
        TaskRecord(it.optString("id", UUID.randomUUID().toString()), it.optString("text"), it.optLong("createdAt"), it.optBoolean("done"))
    } }.filter { it.text.isNotBlank() } }
    val customers = array("customers").let { a -> List(a.length()) { i -> a.getJSONObject(i).let {
        CustomerRecord(it.optString("id", UUID.randomUUID().toString()), it.optString("name"), it.optString("phone"), it.optString("gstin"))
    } }.filter { it.name.isNotBlank() } }
    val invoices = array("invoices").let { a -> List(a.length()) { i -> a.getJSONObject(i).let {
        InvoiceRecord(it.optString("id", "SI-${System.currentTimeMillis()}"), it.optString("customer"), it.optString("description"), it.optDouble("amount"), it.optLong("createdAt"))
    } }.filter { it.customer.isNotBlank() && it.amount > 0.0 } }
    return OsData(tasks, customers, invoices)
}

private fun readData(raw: String?): OsData = if (raw.isNullOrBlank()) OsData() else runCatching {
    decodeData(JSONObject(raw))
}.getOrDefault(OsData())


class AlarmReceiver : android.content.BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as android.app.NotificationManager
        val channelId = "santram_reminders"
        if (Build.VERSION.SDK_INT >= 26) {
            manager.createNotificationChannel(android.app.NotificationChannel(channelId, "SANTRAM Reminders", android.app.NotificationManager.IMPORTANCE_HIGH))
        }
        val notification = androidx.core.app.NotificationCompat.Builder(context, channelId)
            .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
            .setContentTitle("SANTRAM PERSONAL AI")
            .setContentText(intent.getStringExtra("alarm_label") ?: "Your reminder is due")
            .setPriority(androidx.core.app.NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()
        manager.notify(5001, notification)
    }
}
