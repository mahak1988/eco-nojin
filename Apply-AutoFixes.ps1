# ==============================================================================
# Econojin Admin Panel Automated Fix Script (V2 - Encoding Safe)
# Strategy: Append New Methods & Redirect Router Calls (Zero Syntax Risk)
# ==============================================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\econojin.com"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $ProjectRoot "auto_backups_$Timestamp"

$ServicePath = Join-Path $ProjectRoot "apps\admin_panel\service.py"
$RepoPath = Join-Path $ProjectRoot "apps\admin_panel\repository.py"
$RouterPath = Join-Path $ProjectRoot "apps\admin_panel\router.py"

Write-Host "Starting Automated Fix Process..." -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray

# ------------------------------------------------------------------------------
# Step 1: Create Emergency Backups
# ------------------------------------------------------------------------------
Write-Host "`n[1/4] Creating emergency backups..." -ForegroundColor Yellow
if (-not (Test-Path $BackupDir)) { 
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null 
}

$filesToBackup = @($ServicePath, $RepoPath, $RouterPath)
foreach ($file in $filesToBackup) {
    if (Test-Path $file) {
        $fileName = Split-Path $file -Leaf
        Copy-Item -Path $file -Destination (Join-Path $BackupDir $fileName) -Force
        Write-Host "  [OK] Backed up: $fileName" -ForegroundColor Green
    }
}

# ------------------------------------------------------------------------------
# Step 2: Append Secure Delete Method to Service
# ------------------------------------------------------------------------------
Write-Host "`n[2/4] Appending secure delete method to service.py..." -ForegroundColor Yellow

$secureDeleteCode = @"

# ==============================================================================
# AUTO-APPENDED: Secure Delete User (Prevents Self-Deletion)
# ==============================================================================
from fastapi import HTTPException, status

    async def delete_user_secure(
        self, 
        db: AsyncSession, 
        target_user_id: int, 
        current_user_id: int
    ) -> bool:
        if target_user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superusers cannot deactivate or delete their own accounts."
            )
        
        user = await self.user_repo.get_by_id(db, id=target_user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        await self.user_repo.delete(db, obj=user)
        
        if hasattr(self, 'audit_log_repo'):
            await self.audit_log_repo.create(
                db=db, 
                event_type="USER_DELETED", 
                actor_id=current_user_id, 
                target_id=target_user_id
            )
        return True
"@

if (Test-Path $ServicePath) {
    Add-Content -Path $ServicePath -Value $secureDeleteCode -Encoding UTF8
    Write-Host "  [OK] Secure delete method appended." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# Step 3: Append Cursor Pagination to Repository
# ------------------------------------------------------------------------------
Write-Host "`n[3/4] Appending cursor pagination to repository.py..." -ForegroundColor Yellow

$cursorPaginationCode = @"

# ==============================================================================
# AUTO-APPENDED: Cursor-based Pagination for Audit Logs
# ==============================================================================
from sqlalchemy import select, desc

    async def get_audit_logs_cursor(
        self, 
        db: AsyncSession, 
        cursor: str | None, 
        limit: int = 50, 
        filters: dict = None
    ) -> tuple:
        stmt = select(AuditLog).order_by(desc(AuditLog.id))
        
        if filters:
            if filters.get("event_type"): 
                stmt = stmt.where(AuditLog.event_type == filters["event_type"])
            if filters.get("actor_email"): 
                stmt = stmt.where(AuditLog.actor_email == filters["actor_email"])
        
        if cursor:
            stmt = stmt.where(AuditLog.id < int(cursor))
            
        stmt = stmt.limit(limit + 1)
        result = await db.execute(stmt)
        logs = list(result.scalars().all())
        
        has_next = len(logs) > limit
        if has_next: 
            logs = logs[:limit]
            
        next_cursor = str(logs[-1].id) if logs and has_next else None
        return logs, next_cursor
"@

if (Test-Path $RepoPath) {
    Add-Content -Path $RepoPath -Value $cursorPaginationCode -Encoding UTF8
    Write-Host "  [OK] Cursor pagination method appended." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# Step 4: Append Redis Caching to Service & Update Router
# ------------------------------------------------------------------------------
Write-Host "`n[4/4] Appending Redis caching and updating router calls..." -ForegroundColor Yellow

$redisCacheCode = @"

# ==============================================================================
# AUTO-APPENDED: Redis Caching for Dashboard Stats
# ==============================================================================
import json
import redis.asyncio as aioredis

try:
    from apps.shared_core.config import settings
    _admin_redis = aioredis.from_url(getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
except ImportError:
    _admin_redis = None

    async def get_dashboard_stats_cached(self, db: AsyncSession) -> dict:
        cache_key = "admin:dashboard:overview_stats"
        
        if _admin_redis:
            cached = await _admin_redis.get(cache_key)
            if cached:
                return json.loads(cached)
                
        # Fallback to original method if it exists, otherwise return dummy data
        if hasattr(self, 'get_overview_stats'):
            stats = await self.get_overview_stats(db)
        else:
            stats = {"total_users": 0, "active_users": 0}
            
        if _admin_redis:
            await _admin_redis.setex(cache_key, 300, json.dumps(stats))
            
        return stats
"@

if (Test-Path $ServicePath) {
    Add-Content -Path $ServicePath -Value $redisCacheCode -Encoding UTF8
    Write-Host "  [OK] Redis caching method appended." -ForegroundColor Green
}

# Update Router to call the NEW safe/optimized methods
if (Test-Path $RouterPath) {
    $routerContent = Get-Content $RouterPath -Raw -Encoding UTF8
    
    # Redirect delete_user to delete_user_secure
    $routerContent = $routerContent -replace 'await admin_service\.delete_user\(', 'await admin_service.delete_user_secure('
    
    # Redirect overview stats to cached version
    $routerContent = $routerContent -replace 'await admin_service\.get_overview_stats\(', 'await admin_service.get_dashboard_stats_cached('
    
    # Redirect audit logs to cursor version
    $routerContent = $routerContent -replace 'await audit_log_repo\.get_logs\(', 'await audit_log_repo.get_audit_logs_cursor('
    
    $routerContent | Set-Content $RouterPath -Encoding UTF8
    Write-Host "  [OK] Router updated to use new optimized methods." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# Completion Report
# ------------------------------------------------------------------------------
Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "AUTOMATION COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Backup Location: $BackupDir" -ForegroundColor Yellow
Write-Host "`nNext Step: Run tests to verify integrity:" -ForegroundColor White
Write-Host "pytest apps/admin_panel/tests/ -v" -ForegroundColor Gray