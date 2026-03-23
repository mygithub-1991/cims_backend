# Android App Integration Guide

This guide explains how to integrate the FastAPI backend with your Android CIMS app.

## Phase 2 Implementation Strategy

### Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌──────────────┐
│   Android App   │ <-----> │  FastAPI     │ <-----> │  PostgreSQL  │
│   (Room DB)     │  HTTP   │  Backend     │  SQL    │  Database    │
└─────────────────┘         └──────────────┘         └──────────────┘
       Local                     Server                   Server
      Storage                    API                     Storage
```

### Sync Strategy

1. **Offline-First**: App works fully offline with local Room database
2. **Network Detection**: Check connectivity before sync
3. **Push Changes**: Send local changes to server when online
4. **Pull Changes**: Get server changes and update local database
5. **Conflict Resolution**: Server timestamp wins (last write wins)

## Step 1: Add Dependencies to Android App

Add to `app/build.gradle.kts`:

```kotlin
dependencies {
    // Existing dependencies...

    // Retrofit for API calls
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")

    // Gson for JSON parsing
    implementation("com.google.code.gson:gson:2.10.1")

    // Kotlin Coroutines (already included, but ensure version)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Work Manager for background sync
    implementation("androidx.work:work-runtime-ktx:2.9.0")

    // Network connectivity
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
}
```

## Step 2: Create API Models

Create `app/src/main/java/com/p4mindset/tutorials/api/models/ApiModels.kt`:

```kotlin
package com.p4mindset.tutorials.api.models

import com.google.gson.annotations.SerializedName

// API Request/Response models
data class TeacherApi(
    val id: Int? = null,
    val name: String,
    val subject: String,
    @SerializedName("contact_number") val contactNumber: String,
    val salary: Double,
    @SerializedName("date_of_joining") val dateOfJoining: Long,
    @SerializedName("is_deleted") val isDeleted: Boolean = false,
    @SerializedName("deleted_at") val deletedAt: Long? = null,
    @SerializedName("created_at") val createdAt: Long,
    @SerializedName("updated_at") val updatedAt: Long,
    @SerializedName("device_id") val deviceId: String? = null
)

data class BatchApi(
    val id: Int? = null,
    val name: String,
    val time: String,
    @SerializedName("teacher_id") val teacherId: Int,
    @SerializedName("is_deleted") val isDeleted: Boolean = false,
    @SerializedName("deleted_at") val deletedAt: Long? = null,
    @SerializedName("created_at") val createdAt: Long,
    @SerializedName("updated_at") val updatedAt: Long,
    @SerializedName("device_id") val deviceId: String? = null
)

data class StudentApi(
    val id: Int? = null,
    @SerializedName("roll_number") val rollNumber: String,
    val name: String,
    @SerializedName("contact_number") val contactNumber: String,
    @SerializedName("total_fees") val totalFees: Double,
    @SerializedName("paid_fees") val paidFees: Double,
    @SerializedName("batch_id") val batchId: Int,
    @SerializedName("payment_mode") val paymentMode: String,
    @SerializedName("installment_type") val installmentType: String?,
    @SerializedName("referred_by") val referredBy: String?,
    @SerializedName("is_deleted") val isDeleted: Boolean = false,
    @SerializedName("deleted_at") val deletedAt: Long? = null,
    @SerializedName("created_at") val createdAt: Long,
    @SerializedName("updated_at") val updatedAt: Long,
    @SerializedName("device_id") val deviceId: String? = null
)

data class FeeRecordApi(
    val id: Int? = null,
    @SerializedName("student_id") val studentId: Int,
    @SerializedName("amount_paid") val amountPaid: Double,
    @SerializedName("payment_method") val paymentMethod: String,
    val date: Long,
    @SerializedName("receipt_id") val receiptId: String,
    val remarks: String?,
    @SerializedName("created_at") val createdAt: Long,
    @SerializedName("device_id") val deviceId: String? = null
)

data class AttendanceApi(
    val id: Int? = null,
    @SerializedName("student_id") val studentId: Int,
    val date: Long,
    @SerializedName("is_present") val isPresent: Boolean,
    @SerializedName("created_at") val createdAt: Long,
    @SerializedName("device_id") val deviceId: String? = null
)

// Sync models
data class SyncRequest(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("last_sync_timestamp") val lastSyncTimestamp: Long
)

data class SyncData(
    val teachers: List<TeacherApi> = emptyList(),
    val batches: List<BatchApi> = emptyList(),
    val students: List<StudentApi> = emptyList(),
    @SerializedName("fee_records") val feeRecords: List<FeeRecordApi> = emptyList(),
    val attendance: List<AttendanceApi> = emptyList()
)

data class SyncResponse(
    val success: Boolean,
    val message: String,
    @SerializedName("server_timestamp") val serverTimestamp: Long,
    val data: SyncData
)

// Bulk push models
data class BulkTeachersRequest(val teachers: List<TeacherApi>)
data class BulkBatchesRequest(val batches: List<BatchApi>)
data class BulkStudentsRequest(val students: List<StudentApi>)
data class BulkFeeRecordsRequest(@SerializedName("fee_records") val feeRecords: List<FeeRecordApi>)
data class BulkAttendanceRequest(val attendance: List<AttendanceApi>)

data class BulkSyncResponse(
    val success: Boolean,
    val created: Int,
    val updated: Int? = null,
    val errors: List<Map<String, String>> = emptyList()
)
```

## Step 3: Create Retrofit API Interface

Create `app/src/main/java/com/p4mindset/tutorials/api/ApiService.kt`:

```kotlin
package com.p4mindset.tutorials.api

import com.p4mindset.tutorials.api.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // Sync endpoints
    @POST("api/sync/pull")
    suspend fun pullSync(@Body request: SyncRequest): Response<SyncResponse>

    @POST("api/sync/push/teachers")
    suspend fun pushTeachers(@Body request: BulkTeachersRequest): Response<BulkSyncResponse>

    @POST("api/sync/push/batches")
    suspend fun pushBatches(@Body request: BulkBatchesRequest): Response<BulkSyncResponse>

    @POST("api/sync/push/students")
    suspend fun pushStudents(@Body request: BulkStudentsRequest): Response<BulkSyncResponse>

    @POST("api/sync/push/fee-records")
    suspend fun pushFeeRecords(@Body request: BulkFeeRecordsRequest): Response<BulkSyncResponse>

    @POST("api/sync/push/attendance")
    suspend fun pushAttendance(@Body request: BulkAttendanceRequest): Response<BulkSyncResponse>

    // Individual CRUD endpoints (optional, for direct operations)
    @GET("api/teachers")
    suspend fun getTeachers(): Response<List<TeacherApi>>

    @GET("api/students")
    suspend fun getStudents(): Response<List<StudentApi>>

    @GET("api/batches")
    suspend fun getBatches(): Response<List<BatchApi>>
}
```

## Step 4: Create Retrofit Client

Create `app/src/main/java/com/p4mindset/tutorials/api/RetrofitClient.kt`:

```kotlin
package com.p4mindset.tutorials.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    // Update this with your actual server URL
    private const val BASE_URL = "http://10.0.2.2:8000/"  // Use this for Android emulator
    // For physical device, use: "http://YOUR_LOCAL_IP:8000/"
    // For production, use: "https://your-domain.com/"

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}
```

## Step 5: Add Network Permission

Add to `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

## Step 6: Create Sync Manager

Create `app/src/main/java/com/p4mindset/tutorials/sync/SyncManager.kt`:

```kotlin
package com.p4mindset.tutorials.sync

import android.content.Context
import android.provider.Settings
import com.p4mindset.tutorials.AppDatabase
import com.p4mindset.tutorials.api.RetrofitClient
import com.p4mindset.tutorials.api.models.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SyncManager(private val context: Context) {

    private val apiService = RetrofitClient.apiService
    private val db = AppDatabase.getDatabase(context)
    private val dao = db.appDao()

    private fun getDeviceId(): String {
        return Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
    }

    suspend fun syncAll(): SyncResult = withContext(Dispatchers.IO) {
        try {
            // 1. Push local changes
            pushLocalChanges()

            // 2. Pull server changes
            pullServerChanges()

            SyncResult.Success("Sync completed successfully")
        } catch (e: Exception) {
            e.printStackTrace()
            SyncResult.Error("Sync failed: ${e.message}")
        }
    }

    private suspend fun pushLocalChanges() {
        val deviceId = getDeviceId()

        // Push teachers
        val teachers = dao.getAllTeachers().map { it.toApiModel(deviceId) }
        if (teachers.isNotEmpty()) {
            apiService.pushTeachers(BulkTeachersRequest(teachers))
        }

        // Push batches
        val batches = dao.getAllBatches().map { it.toApiModel(deviceId) }
        if (batches.isNotEmpty()) {
            apiService.pushBatches(BulkBatchesRequest(batches))
        }

        // Push students
        val students = dao.getAllStudents().map { it.toApiModel(deviceId) }
        if (students.isNotEmpty()) {
            apiService.pushStudents(BulkStudentsRequest(students))
        }

        // Push fee records
        // Push attendance
        // ... similar pattern
    }

    private suspend fun pullServerChanges() {
        val deviceId = getDeviceId()
        val lastSync = getLastSyncTimestamp()

        val response = apiService.pullSync(SyncRequest(deviceId, lastSync))

        if (response.isSuccessful) {
            response.body()?.let { syncResponse ->
                // Update local database with server changes
                syncResponse.data.teachers.forEach { teacher ->
                    // Convert API model to Room entity and upsert
                }

                // Save sync timestamp
                saveLastSyncTimestamp(syncResponse.serverTimestamp)
            }
        }
    }

    private fun getLastSyncTimestamp(): Long {
        val prefs = context.getSharedPreferences("sync_prefs", Context.MODE_PRIVATE)
        return prefs.getLong("last_sync", 0)
    }

    private fun saveLastSyncTimestamp(timestamp: Long) {
        context.getSharedPreferences("sync_prefs", Context.MODE_PRIVATE)
            .edit()
            .putLong("last_sync", timestamp)
            .apply()
    }
}

sealed class SyncResult {
    data class Success(val message: String) : SyncResult()
    data class Error(val message: String) : SyncResult()
}

// Extension functions to convert between Room entities and API models
fun Teacher.toApiModel(deviceId: String) = TeacherApi(
    id = this.id,
    name = this.name,
    subject = this.subject,
    contactNumber = this.contactNumber,
    salary = this.salary,
    dateOfJoining = this.dateOfJoining,
    isDeleted = this.isDeleted,
    deletedAt = this.deletedAt,
    createdAt = this.createdAt,
    updatedAt = this.updatedAt,
    deviceId = deviceId
)

// Similar extension functions for other entities...
```

## Step 7: Network Connectivity Check

Create `app/src/main/java/com/p4mindset/tutorials/utils/NetworkUtils.kt`:

```kotlin
package com.p4mindset.tutorials.utils

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities

object NetworkUtils {
    fun isNetworkAvailable(context: Context): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
               capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
               capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)
    }
}
```

## Step 8: Add Sync Button to Dashboard

Modify `DashboardActivity.kt`:

```kotlin
// Add sync button
findViewById<Button>(R.id.btnSync).setOnClickListener {
    if (NetworkUtils.isNetworkAvailable(this)) {
        lifecycleScope.launch {
            val syncManager = SyncManager(this@DashboardActivity)
            when (val result = syncManager.syncAll()) {
                is SyncResult.Success -> {
                    ToastHelper.success(this@DashboardActivity, result.message)
                }
                is SyncResult.Error -> {
                    ToastHelper.error(this@DashboardActivity, result.message)
                }
            }
        }
    } else {
        ToastHelper.warning(this, "No internet connection")
    }
}
```

## Testing Strategy

### 1. Test Backend First
- Start FastAPI server: `python run.py`
- Test endpoints in Swagger UI: `http://localhost:8000/docs`

### 2. Test Android Connection
- Update `BASE_URL` in RetrofitClient
- Use `10.0.2.2:8000` for emulator
- Use actual IP for physical device
- Test sync button

### 3. Test Offline Mode
- Disable network
- Create/update data
- Enable network
- Trigger sync
- Verify data appears on server

## Next Steps

1. Implement complete sync logic for all entities
2. Add background sync with WorkManager
3. Handle conflict resolution
4. Add sync status UI
5. Implement incremental sync
6. Add retry logic for failed syncs
7. Optimize for battery and data usage

## Configuration

Update base URL in `RetrofitClient.kt` based on environment:
- **Development (Emulator)**: `http://10.0.2.2:8000/`
- **Development (Device)**: `http://YOUR_LOCAL_IP:8000/`
- **Production**: `https://your-domain.com/`
