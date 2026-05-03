$ErrorActionPreference = 'Stop'
$tok = (& "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" account get-access-token --resource "https://copilot-test1.crm5.dynamics.com" --query accessToken -o tsv)
$base = "https://copilot-test1.crm5.dynamics.com/api/data/v9.2"
$h = @{ Authorization="Bearer $tok"; Accept="application/json"; "OData-MaxVersion"="4.0"; "OData-Version"="4.0" }
$appId = "514a86bd-9540-f111-bec7-000d3a8223b7"
$uniqueId = (Invoke-RestMethod -Uri "$base/appmodules?`$filter=appmoduleid eq $appId&`$select=appmoduleidunique" -Headers $h).value[0].appmoduleidunique
$c = Invoke-RestMethod -Uri "$base/appmodulecomponents?`$filter=_appmoduleidunique_value eq $uniqueId&`$select=componenttype,objectid" -Headers $h
$grouped = $c.value | Group-Object componenttype
"=== Components on MDA $appId (unique=$uniqueId) ==="
$grouped | ForEach-Object { "  componenttype $($_.Name) -> count $($_.Count)" }
"  TOTAL: $($c.value.Count)"
""
"=== Component-type 20 (Security Roles) detail ==="
$c.value | Where-Object componenttype -eq 20 | ForEach-Object { "  role $($_.objectid)" }
""
"=== Component-type 1 (Entities) detail (5 expected, dedup objectid) ==="
$c.value | Where-Object componenttype -eq 1 | Select-Object -ExpandProperty objectid | Sort-Object -Unique | ForEach-Object { "  entity-meta $_" }
""
"=== App publish state ==="
Invoke-RestMethod -Uri "$base/appmodules($appId)?`$select=name,uniquename,publishedon,statecode,statuscode" -Headers $h | ConvertTo-Json -Depth 3
