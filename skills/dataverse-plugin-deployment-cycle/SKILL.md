---
name: dataverse-plugin-deployment-cycle
description: |
  Complete Dataverse plugin deployment cycle: compile, upload DLL, register
  types, register steps, register pre-images, cache flush, verify via trace
  logs. Covers exact Web API calls, error codes, and the mandatory ordering
  that prevents runtime failures.
trigger_keywords:
  - plugin registration
  - plugin deployment
  - pre-image
  - sdkmessageprocessingstep
  - pluginassembly
  - plugin trace
  - cache flush
  - register plugin
allowed_tools:
  - Read
---

# Dataverse Plugin Deployment Cycle

Complete deployment pipeline for C# plugins in Dataverse. Follow this exact order —
skipping or reordering steps causes runtime KeyNotFoundException, stale cache, or
missing pre-images.

---

## Deployment Order (MANDATORY)

```
1. Compile DLL (dotnet build --configuration Release)
2. Upload assembly (POST pluginassemblies or PATCH content)
3. Register plugin types (POST plugintypes)
4. Register steps (POST sdkmessageprocessingsteps)
5. Register pre-images (POST sdkmessageprocessingstepimages)
6. Cache flush (deactivate → 2s → reactivate each step)
7. Verify via plugintracelogs
```

---

## Step 1: Compile

```powershell
dotnet build --configuration Release
$dllPath = "bin/Release/net462/<AssemblyName>.dll"  # or net472 for newer SDK
```

**Strong-name signing** (required for sandbox isolation):
```powershell
# Generate key if not present
$rsa = [System.Security.Cryptography.RSACryptoServiceProvider]::new(1024)
[System.IO.File]::WriteAllBytes("key.snk", $rsa.ExportCspBlob($true))
```

Add to `.csproj`:
```xml
<SignAssembly>true</SignAssembly>
<AssemblyOriginatorKeyFile>key.snk</AssemblyOriginatorKeyFile>
```

---

## Step 2: Upload Assembly

```powershell
$dllBytes = [System.IO.File]::ReadAllBytes($dllPath)
$base64 = [Convert]::ToBase64String($dllBytes)

# Check if exists
$uri = "$orgUrl/api/data/v9.2/pluginassemblies?`$filter=name eq '$asmName'&`$select=pluginassemblyid"
$existing = (Invoke-RestMethod -Uri $uri -Headers $headers).value

if ($existing.Count -gt 0) {
    # UPDATE — ONLY send content field
    # CRITICAL: Do NOT include ishidden, version, or other metadata in PATCH body
    # Sending ishidden causes: "PrimitiveValue node found where StartArray expected"
    $body = @{ content = $base64 } | ConvertTo-Json
    Invoke-RestMethod -Method PATCH `
        -Uri "$orgUrl/api/data/v9.2/pluginassemblies($($existing[0].pluginassemblyid))" `
        -Headers $headers -Body $body -ContentType "application/json"
} else {
    # CREATE
    $body = @{
        name = $asmName
        content = $base64
        isolationmode = 2   # 2 = Sandbox (required for online)
        sourcetype = 0      # 0 = Database
    } | ConvertTo-Json
    $resp = Invoke-RestMethod -Method POST `
        -Uri "$orgUrl/api/data/v9.2/pluginassemblies" `
        -Headers (@{ Authorization = "Bearer $token"; "Content-Type" = "application/json"; "Prefer" = "return=representation" }) `
        -Body $body -ContentType "application/json"
    $asmId = $resp.pluginassemblyid
}
```

**Error codes:**
- `0x8004416c` = unsigned assembly (missing strong-name key)
- `0x80048537` = assembly too large (>16MB limit)

---

## Step 3: Register Plugin Types

One POST per class that implements `IPlugin`:

```powershell
$body = @{
    typename = "MyNamespace.MyPlugin"
    friendlyname = "My Plugin"
    name = "MyNamespace.MyPlugin"
    "pluginassemblyid@odata.bind" = "/pluginassemblies($asmId)"
} | ConvertTo-Json

$typeResp = Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/plugintypes" `
    -Headers (@{ Authorization = "Bearer $token"; "Content-Type" = "application/json"; "Prefer" = "return=representation" }) `
    -Body $body -ContentType "application/json"
$typeId = $typeResp.plugintypeid
```

---

## Step 4: Register Steps

**MUST bind BOTH sdkmessageid AND sdkmessagefilterid.** Omitting sdkmessagefilterid
causes error `0x80040200`.

```powershell
# Get message ID
$msgUri = "$orgUrl/api/data/v9.2/sdkmessages?`$filter=name eq 'Update'&`$select=sdkmessageid"
$msgId = (Invoke-RestMethod -Uri $msgUri -Headers $headers).value[0].sdkmessageid

# Get message filter ID (binds message to specific entity)
$filterUri = "$orgUrl/api/data/v9.2/sdkmessagefilters?`$filter=sdkmessageid/sdkmessageid eq '$msgId' and primaryobjecttypecode eq '<prefix>_<table>'&`$select=sdkmessagefilterid"
$filterId = (Invoke-RestMethod -Uri $filterUri -Headers $headers).value[0].sdkmessagefilterid

$stepBody = @{
    name = "MyPlugin: Update of <prefix>_<table>"
    mode = 0                  # 0 = Synchronous, 1 = Asynchronous
    rank = 1
    stage = 20               # 10 = PreValidation, 20 = PreOperation, 40 = PostOperation
    supporteddeployment = 0  # 0 = ServerOnly
    filteringattributes = "<prefix>_status,<prefix>_approverid"  # ALWAYS set for Update
    "sdkmessageid@odata.bind" = "/sdkmessages($msgId)"
    "sdkmessagefilterid@odata.bind" = "/sdkmessagefilters($filterId)"
    "eventhandler_plugintype@odata.bind" = "/plugintypes($typeId)"
} | ConvertTo-Json

$stepResp = Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/sdkmessageprocessingsteps" `
    -Headers (@{ Authorization = "Bearer $token"; "Content-Type" = "application/json"; "Prefer" = "return=representation" }) `
    -Body $stepBody -ContentType "application/json"
$stepId = $stepResp.sdkmessageprocessingstepid
```

**CRITICAL: Always set `filteringattributes` on Update steps.** Omitting it causes the
plugin to fire on EVERY field update — massive performance degradation.

---

## Step 5: Register Pre-Images

**Always register pre-images, even if the step already existed.** Skipping this
causes `KeyNotFoundException` when the plugin reads `context.PreEntityImages["PreImage"]`.

```powershell
# Delete existing pre-image first (avoids duplicate key error)
$imgUri = "$orgUrl/api/data/v9.2/sdkmessageprocessingstepimages?`$filter=sdkmessageprocessingstepid/sdkmessageprocessingstepid eq '$stepId' and imagetype eq 0"
$existingImgs = (Invoke-RestMethod -Uri $imgUri -Headers $headers).value
foreach ($img in $existingImgs) {
    Invoke-RestMethod -Method DELETE `
        -Uri "$orgUrl/api/data/v9.2/sdkmessageprocessingstepimages($($img.sdkmessageprocessingstepimageid))" `
        -Headers $headers
}

# Register new pre-image
$imgBody = @{
    name = "PreImage"
    entityalias = "PreImage"
    imagetype = 0                    # 0 = PreImage, 1 = PostImage, 2 = Both
    messagepropertyname = "Target"   # MANDATORY — omitting causes 0x80040203
    attributes = "<prefix>_status,<prefix>_requestorid,<prefix>_approverid"
    "sdkmessageprocessingstepid@odata.bind" = "/sdkmessageprocessingsteps($stepId)"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/sdkmessageprocessingstepimages" `
    -Headers $headers -Body $imgBody -ContentType "application/json"
```

**Error `0x80040203`** = missing `messagepropertyname`. Must be `"Target"` for
Create/Update messages, `"Id"` for Delete.

---

## Step 6: Cache Flush

Dataverse sandbox caches plugin registrations. After adding/modifying pre-images,
the cache must be invalidated:

```powershell
# Deactivate step
$deactivate = @{ statecode = 1; statuscode = 2 } | ConvertTo-Json
Invoke-RestMethod -Method PATCH `
    -Uri "$orgUrl/api/data/v9.2/sdkmessageprocessingsteps($stepId)" `
    -Headers $headers -Body $deactivate -ContentType "application/json"

# Wait for cache to clear
Start-Sleep -Seconds 2

# Reactivate step
$activate = @{ statecode = 0; statuscode = 1 } | ConvertTo-Json
Invoke-RestMethod -Method PATCH `
    -Uri "$orgUrl/api/data/v9.2/sdkmessageprocessingsteps($stepId)" `
    -Headers $headers -Body $activate -ContentType "application/json"
```

**Without this step**, the plugin continues running with the OLD pre-image configuration
(or no pre-image) until the sandbox worker recycles naturally (~minutes to hours).

---

## Step 7: Verify via Trace Logs

```powershell
# CRITICAL: endpoint is plugintracelogs (PLURAL)
# Using singular "plugintracelog" returns 0x80060888 "resource not found"
$traceUri = "$orgUrl/api/data/v9.2/plugintracelogs?`$top=5&`$orderby=createdon desc&`$select=typename,messagename,exceptiondetails,createdon"
$traces = (Invoke-RestMethod -Uri $traceUri -Headers $headers).value

foreach ($t in $traces) {
    Write-Host "$($t.createdon) | $($t.typename) | $($t.messagename) | $($t.exceptiondetails)"
}
```

**Diagnostic: If plugin doesn't fire at all:**
1. Check step is active: `statecode eq 0`
2. Check filteringattributes includes the column being updated
3. Check sdkmessagefilterid points to the correct entity
4. Check assembly content hash matches the latest DLL

---

## Error Code Reference

| Code | Meaning | Fix |
|---|---|---|
| 0x8004416c | Unsigned assembly | Add strong-name key to project |
| 0x80040200 | Missing sdkmessageid or sdkmessagefilterid binding | Bind both on step creation |
| 0x80040203 | Missing messagepropertyname on image | Set to "Target" for Create/Update |
| 0x80048537 | Assembly exceeds size limit | Reduce dependencies, ILMerge |
| 0x80060888 | Resource not found | Check entity set name (plural form) |
| KeyNotFoundException | Pre-image not registered or cached stale | Re-register pre-image + cache flush |

---

## Reset Test Data Pattern

When resetting test records that a plugin guards (e.g., status transitions):

```powershell
# 1. Deactivate the plugin step
Invoke-RestMethod -Method PATCH -Uri "$orgUrl/api/data/v9.2/sdkmessageprocessingsteps($stepId)" `
    -Headers $headers -Body '{"statecode":1,"statuscode":2}' -ContentType "application/json"

# 2. Reset the records
Invoke-RestMethod -Method PATCH -Uri "$orgUrl/api/data/v9.2/<prefix>_<table>($recordId)" `
    -Headers $headers -Body '{"<prefix>_status": 0}' -ContentType "application/json"

# 3. Reactivate the plugin step
Invoke-RestMethod -Method PATCH -Uri "$orgUrl/api/data/v9.2/sdkmessageprocessingsteps($stepId)" `
    -Headers $headers -Body '{"statecode":0,"statuscode":1}' -ContentType "application/json"
```

This avoids the plugin blocking the reset (e.g., "cannot change status from Rejected to Pending").
