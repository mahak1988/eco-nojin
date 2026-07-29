"""Users router — mounted at /api/v1/users (no extra /users prefix)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from apps.users.dependencies import (
    get_current_active_superuser,
    get_current_user,
    get_user_service,
)
from apps.users.models import User
from apps.users.schemas import LoginRequest, Token, UserCreate, UserResponse, UserUpdate
from apps.users.service import UserService

logger = logging.getLogger(__name__)

# Prefix is applied in main.py as /api/v1/users — do not add /users again
router = APIRouter(tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    try:
        return await user_service.register_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await user_service.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(current_user, user_in)


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.repo.get_multi(limit=limit, offset=skip)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(get_user_service),
):
    success = await user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
