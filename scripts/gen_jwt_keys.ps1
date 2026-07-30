# Generate HS256 secret and optional RS256 keypair into secrets/
# Usage: .\scripts\gen_jwt_keys.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
New-Item -ItemType Directory -Force -Path secrets | Out-Null

Write-Host "=== SECRET_KEY (paste into .env) ==="
$secret = python -c "import secrets; print(secrets.token_urlsafe(48))"
Write-Host $secret

$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if ($openssl) {
  Write-Host "=== RS256 PEM -> secrets/ ==="
  openssl genrsa -out secrets/jwt_private.pem 2048 2>$null
  openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem 2>$null
  Write-Host "Created secrets/jwt_private.pem and secrets/jwt_public.pem"
  Write-Host "Set in .env:"
  Write-Host "ALGORITHM=RS256"
  Write-Host "JWT_PRIVATE_KEY_PATH=./secrets/jwt_private.pem"
  Write-Host "JWT_PUBLIC_KEY_PATH=./secrets/jwt_public.pem"
} else {
  Write-Host "openssl not found — HS256 secret only. Install OpenSSL or Git Bash for RS256."
}
Write-Host "Done. Never commit secrets/ or .env"
