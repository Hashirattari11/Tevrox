$base='http://localhost:3001'
foreach ($p in @('/','/landing','/login','/signup','/dashboard','/products','/admin/products')) {
  try { $r = Invoke-WebRequest -Uri "$base$p" -UseBasicParsing -TimeoutSec 25; Write-Host "$p : $($r.StatusCode)" } catch { Write-Host "$p : ERROR $($_.Exception.Response.StatusCode)" }
}
