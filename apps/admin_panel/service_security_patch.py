# ==============================================================================
# PATCH FILE: Security Fix for Self-Deletion Vulnerability
# TARGET FILE: apps\admin_panel\service.py
# INSTRUCTION: Replace the existing 'delete_user' method with this implementation.
# ==============================================================================

from fastapi import HTTPException, status

# ... سایر ایمپورتهای موجود در فایل شما ...


class AdminUserService:
    # ... سایر متدها ...

    async def delete_user(
        self,
        db: AsyncSession,
        target_user_id: int,
        current_user_id: int,  # اطمینان حاصل کنید این پارامتر از Dependency (مثلا get_current_active_superuser) تزریق میشود
    ) -> bool:
        """
        حذف کاربر با محافظت قطعی در برابر حذف حساب سوپریوزر فعلی.
        """
        # ۱. بررسی امنیتی حیاتی (Critical Security Check)
        if target_user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superusers cannot deactivate or delete their own accounts via the admin panel.",
            )

        # ۲. دریافت کاربر هدف
        user = await self.user_repo.get_by_id(db, id=target_user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # ۳. عملیات حذف (Soft delete یا Hard delete بسته به معماری شما)
        await self.user_repo.delete(db, obj=user)

        # ۴. ثبت در لاگ ممیزی (Audit Log)
        await self.audit_log_repo.create(
            db=db,
            event_type="USER_DELETED",
            actor_id=current_user_id,
            target_id=target_user_id,
            details={"username": user.username},
        )

        return True
