# Test script for SoundTracker API using curl

# Base URL for the API
$baseUrl = "http://localhost:8000/api/v1"

# Function to make API requests
function Invoke-ApiRequest {
    param (
        [string]$Method,
        [string]$Endpoint,
        [string]$Body = $null
    )
    
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $uri = "$baseUrl$Endpoint"
    
    Write-Host "`n$Method $uri" -ForegroundColor Cyan
    
    if ($Body) {
        Write-Host "Request Body:" -ForegroundColor Yellow
        $Body | ConvertFrom-Json | ConvertTo-Json -Depth 5 | Write-Host -ForegroundColor Yellow
        
        $response = Invoke-WebRequest -Method $Method -Uri $uri -Headers $headers -Body $Body -UseBasicParsing
    } else {
        $response = Invoke-WebRequest -Method $Method -Uri $uri -Headers $headers -UseBasicParsing
    }
    
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    
    if ($response.Content) {
        Write-Host "Response:" -ForegroundColor Green
        $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 5 | Write-Host -ForegroundColor Green
    }
    
    return $response
}

# Test data
$testEvent = @{
    audio_file_path = "/test/audio/sample.wav"
    sound_type = "speech"
    confidence = 0.95
    noise_level_db = 42.5
    duration_seconds = 10.5
    sample_rate = 44100
    channels = 2
    event_metadata = @{
        speaker_id = "spk_123"
        language = "en-US"
        transcription = "This is a test transcription"
    }
} | ConvertTo-Json -Depth 5

# Test creating an event
Write-Host "\n=== Testing Create Event ===" -ForegroundColor Magenta
$createResponse = Invoke-ApiRequest -Method "POST" -Endpoint "/sounds" -Body $testEvent

# Extract the event ID if creation was successful
$eventId = $null
if ($createResponse.StatusCode -eq 201) {
    $eventData = $createResponse.Content | ConvertFrom-Json
    $eventId = $eventData.id
    Write-Host "Created event with ID: $eventId" -ForegroundColor Green
}

# Test listing events
Write-Host "\n=== Testing List Events ===" -ForegroundColor Magenta
Invoke-ApiRequest -Method "GET" -Endpoint "/sounds"

# Test getting a specific event
if ($eventId) {
    Write-Host "\n=== Testing Get Event ===" -ForegroundColor Magenta
    Invoke-ApiRequest -Method "GET" -Endpoint "/sounds/$eventId"
    
    # Test deleting the event
    Write-Host "\n=== Testing Delete Event ===" -ForegroundColor Magenta
    Invoke-ApiRequest -Method "DELETE" -Endpoint "/sounds/$eventId"
    
    # Verify deletion
    Write-Host "\n=== Verifying Deletion ===" -ForegroundColor Magenta
    try {
        $response = Invoke-WebRequest -Method "GET" -Uri "$baseUrl/sounds/$eventId" -ErrorAction Stop -UseBasicParsing
        Write-Host "Warning: Event was not deleted successfully" -ForegroundColor Red
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "Event was successfully deleted (404 Not Found)" -ForegroundColor Green
        } else {
            Write-Host "Error verifying deletion: $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Skipping get and delete tests - no event ID available" -ForegroundColor Yellow
}

Write-Host "\n=== Testing Complete ===" -ForegroundColor Magenta
