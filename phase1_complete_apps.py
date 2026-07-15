#!/usr/bin/env python3
"""
Eco Nojin — Phase 1: Complete apps/ Directory Structure
=========================================================
Scaffolds missing standard files for every sub-app in apps/:
  - Backend apps (FastAPI/Python): router, models, schemas, service, repository,
    dependencies, __init__, tests, README
  - Frontend apps (React/TypeScript): pages, components, hooks, lib, types,
    api client, __tests__, README

Features:
  • Auto-detects app type (backend / frontend / shared / unknown)
  • Idempotent — never overwrites existing files
  • Dry-run mode by default (use --apply to write)
  • Per-app enable/disable via --only / --skip flags
  • Generates a phase1_report.json summary at the end
  • Bilingual comments (Persian + English) in templates

Usage:
    python3 phase1_complete_apps.py                       # dry-run, scan apps/
    python3 phase1_complete_apps.py --apply               # actually create files
    python3 phase1_complete_apps.py --only users,web      # only specific apps
    python3 phase1_complete_apps.py --skip simulation     # skip specific apps
    python3 phase1_complete_apps.py --root /path/to/repo  # custom repo root

Exit codes:
    0 = success (or dry-run completed)
    1 = apps/ directory not found
    2 = error during execution
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════
# APP TYPE DETECTION
# ═══════════════════════════════════════════════════════════════════════

# Files that strongly indicate a Python/FastAPI backend app
BACKEND_MARKERS = {
    "router.py", "models.py", "schemas.py", "service.py",
    "repository.py", "dependencies.py", "main.py", "app.py",
    "auth_router.py", "requirements.txt", "pyproject.toml",
}

# Files that strongly indicate a TypeScript/React frontend app
FRONTEND_MARKERS = {
    "package.json", "vite.config.ts", "vite.config.js",
    "tsconfig.json", "next.config.js", "next.config.mjs",
    "webpack.config.js", "tailwind.config.js", "tailwind.config.ts",
    "index.html",
}

# Sub-apps that are clearly "shared" libraries (not standalone services)
SHARED_PREFIXES = {"shared_", "lib_"}


def detect_app_type(app_dir: Path) -> str:
    """Detect the type of an app based on its file markers.

    Returns one of: 'backend', 'frontend', 'shared_backend', 'shared_frontend',
    'unknown'.
    """
    name = app_dir.name
    files_present = {f.name for f in app_dir.iterdir() if f.is_file()}

    # Strong frontend signals
    if files_present & FRONTEND_MARKERS:
        if name.startswith("shared_") or name in {"library"}:
            return "shared_frontend"
        return "frontend"

    # Strong backend signals
    if files_present & BACKEND_MARKERS:
        if name.startswith("shared_"):
            return "shared_backend"
        return "backend"

    # Check one level deep (some apps have files in subdirectories)
    try:
        sub_files = set()
        for child in app_dir.iterdir():
            if child.is_file():
                sub_files.add(child.name)
            elif child.is_dir():
                for grandchild in child.iterdir():
                    if grandchild.is_file():
                        sub_files.add(grandchild.name)
        if sub_files & FRONTEND_MARKERS:
            return "frontend" if not name.startswith("shared_") else "shared_frontend"
        if sub_files & BACKEND_MARKERS:
            return "backend" if not name.startswith("shared_") else "shared_backend"
    except (PermissionError, OSError):
        pass

    # Heuristic: apps with tests/ directory (even without __init__.py at root)
    # are likely Python backend modules. This covers `simulation/` which has
    # tests/__init__.py but no top-level __init__.py
    if (app_dir / "tests").is_dir():
        # Check if any test file is Python
        tests_dir = app_dir / "tests"
        try:
            has_python = any(
                f.suffix == ".py"
                for f in tests_dir.iterdir() if f.is_file()
            )
            if has_python or (tests_dir / "__init__.py").exists():
                if name.startswith("shared_"):
                    return "shared_backend"
                return "backend"
        except (PermissionError, OSError):
            pass

    # Heuristic: apps with only __init__.py and a subdirectory of the same name
    # (e.g., shared_knowledge/knowledge/) — typical of Python packages
    if (app_dir / "__init__.py").exists():
        subdirs = [d for d in app_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        if len(subdirs) >= 1:
            if name.startswith("shared_"):
                return "shared_backend"
            return "backend"

    # Heuristic: apps with any subdirectory containing Python files
    # (covers `simulation/` with 9 domain subdirs like agriculture/, hydrology/)
    try:
        for child in app_dir.iterdir():
            if child.is_dir() and not child.name.startswith(".") and child.name != "tests":
                # Check if this subdir has any .py files
                try:
                    has_py = any(
                        f.suffix == ".py"
                        for f in child.iterdir() if f.is_file()
                    )
                    if has_py:
                        if name.startswith("shared_"):
                            return "shared_backend"
                        return "backend"
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        pass

    # Heuristic: apps named "simulation", "api", "shared" or starting with
    # "shared_" are very likely Python backend modules in a FastAPI monorepo
    likely_backend_names = {"simulation", "api", "shared", "services", "modules"}
    if name in likely_backend_names or name.startswith("shared_"):
        # Even without markers, treat as backend (the templates will create
        # the standard structure; user can rename/remove if wrong)
        if name.startswith("shared_"):
            return "shared_backend"
        return "backend"

    return "unknown"


# ═══════════════════════════════════════════════════════════════════════
# BACKEND TEMPLATES (FastAPI / Python)
# ═══════════════════════════════════════════════════════════════════════

def backend_init_py(app_name: str) -> str:
    """__init__.py for a backend module."""
    return f'''"""
{app_name} module | ماژول {app_name}
====================================
Part of the Eco Nojin platform. Provides {app_name} functionality.
Auto-scaffolded by phase1_complete_apps.py on {datetime.now().strftime("%Y-%m-%d")}.
"""

__version__ = "0.1.0"
'''


def backend_models_py(app_name: str) -> str:
    """SQLAlchemy models for the app."""
    class_name = "".join(p.capitalize() for p in app_name.split("_"))
    table_name = app_name.lower()
    return f'''"""
{app_name} models | مدل‌های {app_name}
=====================================
SQLAlchemy ORM models for the {app_name} module.

NOTE: This is a starter template. Adjust fields and relationships
      to match your actual domain model.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

# Adjust this import to match your project's database session setup
try:
    from apps.shared_core.database.base import Base
except ImportError:
    # Fallback: define a minimal Base if shared_core is not yet set up
    from sqlalchemy.orm import DeclarativeBase
    class Base(DeclarativeBase):
        pass


class {class_name}(Base):
    """Primary {app_name} entity."""

    __tablename__ = "{table_name}"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<{class_name}(id={{self.id}}, name={{self.name!r}})>"

    def to_dict(self) -> dict:
        """Serialize to dictionary (for API responses)."""
        return {{
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }}
'''


def backend_schemas_py(app_name: str) -> str:
    """Pydantic schemas for the app."""
    class_name = "".join(p.capitalize() for p in app_name.split("_"))
    return f'''"""
{app_name} schemas | شِما‌های {app_name}
=====================================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class {class_name}Base(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, description="Description")


class {class_name}Create({class_name}Base):
    """Schema for creating a new {app_name}."""

    pass


class {class_name}Update(BaseModel):
    """Schema for updating an existing {app_name} (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class {class_name}Response({class_name}Base):
    """Schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class {class_name}ListResponse(BaseModel):
    """Paginated list response."""

    items: list[{class_name}Response]
    total: int
    skip: int = 0
    limit: int = 100
'''


def backend_repository_py(app_name: str) -> str:
    """Data access layer."""
    class_name = "".join(p.capitalize() for p in app_name.split("_"))
    return f'''"""
{app_name} repository | لایه دسترسی داده {app_name}
==================================================
Data access layer — all database queries live here.
Services call repositories; repositories never call services.
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.{app_name}.models import {class_name}
from apps.{app_name}.schemas import {class_name}Create, {class_name}Update


class {class_name}Repository:
    """Repository for {class_name} entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[{class_name}]:
        """Fetch a single record by ID."""
        result = await self.session.execute(
            select({class_name}).where({class_name}.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[{class_name}], int]:
        """Fetch a paginated list of records + total count."""
        result = await self.session.execute(
            select({class_name})
            .order_by({class_name}.id.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(result.scalars().all())

        count_result = await self.session.execute(
            select(func.count()).select_from({class_name})
        )
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: {class_name}Create) -> {class_name}:
        """Insert a new record."""
        obj = {class_name}(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, data: {class_name}Update) -> Optional[{class_name}]:
        """Update an existing record. Returns None if not found."""
        obj = await self.get_by_id(id)
        if not obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        """Delete a record. Returns True if deleted, False if not found."""
        obj = await self.get_by_id(id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True
'''


def backend_service_py(app_name: str) -> str:
    """Business logic layer."""
    class_name = "".join(p.capitalize() for p in app_name.split("_"))
    return f'''"""
{app_name} service | لایه کسب‌وکار {app_name}
=============================================
Business logic layer — orchestrates repositories and enforces rules.
Controllers (routers) call services; services call repositories.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.{app_name}.models import {class_name}
from apps.{app_name}.repository import {class_name}Repository
from apps.{app_name}.schemas import {class_name}Create, {class_name}Update


class {class_name}Service:
    """Service for {app_name} operations."""

    def __init__(self, session: AsyncSession):
        self.repo = {class_name}Repository(session)

    async def get(self, id: int) -> Optional[{class_name}]:
        """Get a single record. Raises NotFoundError if missing."""
        obj = await self.repo.get_by_id(id)
        if not obj:
            # Replace with your project's standard exception
            raise ValueError(f"{class_name} with id={{id}} not found")
        return obj

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[{class_name}], int]:
        """List records with pagination."""
        # Cap limit to prevent abuse
        limit = min(limit, 1000)
        return await self.repo.list(skip=skip, limit=limit)

    async def create(self, data: {class_name}Create) -> {class_name}:
        """Create a new record."""
        # Add business rule validation here (e.g., uniqueness check)
        return await self.repo.create(data)

    async def update(self, id: int, data: {class_name}Update) -> {class_name}:
        """Update an existing record."""
        return await self.get(id)  # raises if not found
        # The line below actually performs the update
        obj = await self.repo.update(id, data)
        if not obj:
            raise ValueError(f"{class_name} with id={{id}} not found")
        return obj

    async def delete(self, id: int) -> None:
        """Delete a record. Raises if not found."""
        obj = await self.get(id)
        await self.repo.delete(id)
'''


def backend_router_py(app_name: str) -> str:
    """FastAPI router."""
    class_name = "".join(p.capitalize() for p in app_name.split("_"))
    return f'''"""
{app_name} router | روتر {app_name}
=================================
FastAPI router exposing {app_name} endpoints.

Endpoints:
    GET    /{app_name}          List with pagination
    GET    /{app_name}/{{id}}    Get by ID
    POST   /{app_name}          Create
    PATCH  /{app_name}/{{id}}    Update
    DELETE /{app_name}/{{id}}    Delete
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Adjust this import to match your project's database session dependency
try:
    from apps.shared_core.database.session import get_db_session
except ImportError:
    # Fallback stub — replace with real implementation
    from typing import AsyncGenerator
    async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
        raise NotImplementedError("Wire up get_db_session in apps.shared_core.database.session")

from apps.{app_name}.schemas import (
    {class_name}Create,
    {class_name}Update,
    {class_name}Response,
    {class_name}ListResponse,
)
from apps.{app_name}.service import {class_name}Service

router = APIRouter(prefix="/{app_name}", tags=["{app_name}"])


@router.get("", response_model={class_name}ListResponse)
async def list_{app_name}(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List {app_name} records with pagination."""
    service = {class_name}Service(session)
    items, total = await service.list(skip=skip, limit=limit)
    return {class_name}ListResponse(
        items=[{class_name}Response.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{{item_id}}", response_model={class_name}Response)
async def get_{app_name}(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single {app_name} by ID."""
    service = {class_name}Service(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {class_name}Response.model_validate(item)


@router.post("", response_model={class_name}Response, status_code=status.HTTP_201_CREATED)
async def create_{app_name}(
    payload: {class_name}Create,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new {app_name}."""
    service = {class_name}Service(session)
    item = await service.create(payload)
    await session.commit()
    return {class_name}Response.model_validate(item)


@router.patch("/{{item_id}}", response_model={class_name}Response)
async def update_{app_name}(
    item_id: int,
    payload: {class_name}Update,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing {app_name}."""
    service = {class_name}Service(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return {class_name}Response.model_validate(item)


@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{app_name}(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a {app_name} by ID."""
    service = {class_name}Service(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return None
'''


def backend_dependencies_py(app_name: str) -> str:
    """FastAPI dependencies."""
    return f'''"""
{app_name} dependencies | وابستگی‌های {app_name}
===============================================
FastAPI dependency injections for the {app_name} module.

NOTE: Adjust to match your project's auth/permission system.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status


# Example: a stub for the current user dependency.
# Replace with your real auth dependency (e.g., from apps.users.dependencies).
async def get_current_user() -> dict:
    """Return the current authenticated user."""
    # TODO: integrate with apps.users.auth_router / JWT validation
    return {{"id": 1, "email": "anonymous@example.com", "role": "user"}}


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(*roles: str):
    """Dependency factory: require the user to have one of the given roles."""
    async def _check(user: CurrentUser) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {{', '.join(roles)}}",
            )
        return user
    return _check
'''


def backend_test_init_py() -> str:
    return '"""Tests for this module."""\n'


def backend_test_main_py(app_name: str) -> str:
    """Test file for the app."""
    class_name = "".join(p.capitalize() for p in app_name.split("_"))
    return f'''"""
Tests for {app_name} module | تست‌های {app_name}
===============================================
Run with: pytest apps/{app_name}/tests/test_{app_name}.py -v
"""

import pytest

# TODO: replace these stubs with real tests once models and services are wired
#       to a test database session.


def test_module_imports():
    """Verify that the {app_name} module can be imported."""
    # This will fail until models.py / service.py are importable
    # try:
    #     from apps.{app_name} import models, schemas, service, repository
    # except ImportError as e:
    #     pytest.fail(f"Failed to import {app_name} module: {{e}}")
    pass


def test_{app_name}_create_schema():
    """Test the {class_name}Create schema validates input."""
    # from apps.{app_name}.schemas import {class_name}Create
    # obj = {class_name}Create(name="test", description="desc")
    # assert obj.name == "test"
    pass


def test_{app_name}_response_schema():
    """Test the {class_name}Response schema serializes correctly."""
    # from apps.{app_name}.schemas import {class_name}Response
    pass


@pytest.mark.asyncio
async def test_{app_name}_service_create():
    """Test creating a record via the service."""
    # from apps.{app_name}.service import {class_name}Service
    # service = {class_name}Service(session=test_session)
    # obj = await service.create({class_name}Create(name="test"))
    # assert obj.id is not None
    pass


@pytest.mark.asyncio
async def test_{app_name}_service_list():
    """Test listing records via the service."""
    pass
'''


def backend_readme_md(app_name: str) -> str:
    """README for the app."""
    return f'''# {app_name} | ماژول {app_name}

Part of the **Eco Nojin** platform.

## Overview

This module provides {app_name} functionality for the Econojin platform.
It follows the standard layered architecture:

```
{app_name}/
├── __init__.py        # Module init
├── router.py          # FastAPI router (HTTP endpoints)
├── schemas.py         # Pydantic validation models
├── service.py         # Business logic
├── repository.py      # Database access (SQLAlchemy)
├── models.py          # ORM models
├── dependencies.py    # FastAPI dependencies (auth, etc.)
└── tests/             # Pytest tests
```

## Endpoints

| Method | Path                  | Description          |
|--------|-----------------------|----------------------|
| GET    | `/{app_name}`         | List with pagination |
| GET    | `/{app_name}/{{id}}`  | Get by ID            |
| POST   | `/{app_name}`         | Create               |
| PATCH  | `/{app_name}/{{id}}`  | Update               |
| DELETE | `/{app_name}/{{id}}`  | Delete               |

## Development

```bash
# Run tests
pytest apps/{app_name}/tests/ -v

# Run the dev server (from repo root)
uvicorn apps.main:app --reload
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual domain model.
'''


# ═══════════════════════════════════════════════════════════════════════
# FRONTEND TEMPLATES (React / TypeScript)
# ═══════════════════════════════════════════════════════════════════════

def frontend_index_tsx(class_name: str, app_name: str) -> str:
    """Main entry page for the frontend app."""
    return f'''/**
 * {app_name} — main entry page | صفحه اصلی {app_name}
 *
 * Auto-scaffolded by phase1_complete_apps.py
 */

import React from "react";

export default function {class_name}Page() {{
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          {class_name}
        </h1>
        <p className="text-lg text-gray-600">
          Welcome to the {app_name} page. Replace this with your actual content.
        </p>
      </div>
    </div>
  );
}}
'''


def frontend_types_ts(class_name: str, app_name: str) -> str:
    """TypeScript types for the app."""
    return f'''/**
 * {app_name} types | انواع TypeScript برای {app_name}
 *
 * Auto-scaffolded by phase1_complete_apps.py
 */

export interface {class_name} {{
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}}

export interface {class_name}Create {{
  name: string;
  description?: string;
}}

export interface {class_name}Update {{
  name?: string;
  description?: string;
  is_active?: boolean;
}}

export interface {class_name}ListResponse {{
  items: {class_name}[];
  total: number;
  skip: number;
  limit: number;
}}

export type {class_name}Status = "active" | "inactive" | "pending";
'''


def frontend_api_ts(class_name: str, app_name: str) -> str:
    """API client for the app.
    
    Args:
        class_name: PascalCase identifier (e.g., "HydrologyFrontend")
        app_name: URL path component (e.g., "hydrology-frontend" or "web")
    """
    return f'''/**
 * {app_name} API client | کلاینت API {app_name}
 *
 * Auto-scaffolded by phase1_complete_apps.py
 * Adjust the BASE_URL and import axios from your preferred location.
 */

import axios, {{ AxiosInstance }} from "axios";

import type {{
  {class_name},
  {class_name}Create,
  {class_name}Update,
  {class_name}ListResponse,
}} from "../types";

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL || "/api/v1";

const client: AxiosInstance = axios.create({{
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {{ "Content-Type": "application/json" }},
}});

export const {app_name.replace("-", "_")}Api = {{
  async list(params?: {{ skip?: number; limit?: number }}): Promise<{class_name}ListResponse> {{
    const {{ data }} = await client.get(`/{app_name}`, {{ params }});
    return data;
  }},

  async get(id: number): Promise<{class_name}> {{
    const {{ data }} = await client.get(`/{app_name}/${{id}}`);
    return data;
  }},

  async create(payload: {class_name}Create): Promise<{class_name}> {{
    const {{ data }} = await client.post(`/{app_name}`, payload);
    return data;
  }},

  async update(id: number, payload: {class_name}Update): Promise<{class_name}> {{
    const {{ data }} = await client.patch(`/{app_name}/${{id}}`, payload);
    return data;
  }},

  async delete(id: number): Promise<void> {{
    await client.delete(`/{app_name}/${{id}}`);
  }},
}};
'''


def frontend_hooks_ts(class_name: str, app_name: str) -> str:
    """React Query hooks for the app."""
    # Convert app_name to a valid JS identifier for the API object name
    api_obj = app_name.replace("-", "_") + "Api"
    return f'''/**
 * {app_name} hooks | هوک‌های React Query برای {app_name}
 *
 * Auto-scaffolded by phase1_complete_apps.py
 * Requires @tanstack/react-query to be installed in the workspace.
 */

import {{
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
}} from "@tanstack/react-query";

import {{ {api_obj} }} from "../api";
import type {{ {class_name}, {class_name}Create, {class_name}Update }} from "../types";

const QUERY_KEY = "{app_name}";

export function useList{class_name}s(params?: {{ skip?: number; limit?: number }}) {{
  return useQuery({{
    queryKey: [QUERY_KEY, "list", params],
    queryFn: () => {api_obj}.list(params),
  }});
}}

export function use{class_name}(id: number, options?: Partial<UseQueryOptions<{class_name}>>) {{
  return useQuery({{
    queryKey: [QUERY_KEY, "detail", id],
    queryFn: () => {api_obj}.get(id),
    enabled: !!id,
    ...options,
  }});
}}

export function useCreate{class_name}() {{
  const qc = useQueryClient();
  return useMutation({{
    mutationFn: (payload: {class_name}Create) => {api_obj}.create(payload),
    onSuccess: () => {{
      qc.invalidateQueries({{ queryKey: [QUERY_KEY] }});
    }},
  }});
}}

export function useUpdate{class_name}() {{
  const qc = useQueryClient();
  return useMutation({{
    mutationFn: ({{ id, payload }}: {{ id: number; payload: {class_name}Update }}) =>
      {api_obj}.update(id, payload),
    onSuccess: () => {{
      qc.invalidateQueries({{ queryKey: [QUERY_KEY] }});
    }},
  }});
}}

export function useDelete{class_name}() {{
  const qc = useQueryClient();
  return useMutation({{
    mutationFn: (id: number) => {api_obj}.delete(id),
    onSuccess: () => {{
      qc.invalidateQueries({{ queryKey: [QUERY_KEY] }});
    }},
  }});
}}
'''


def frontend_component_tsx(class_name: str, app_name: str) -> str:
    """Reusable component for the app."""
    return f'''/**
 * {class_name}Card component | کامپوننت کارت {class_name}
 *
 * Auto-scaffolded by phase1_complete_apps.py
 */

import React from "react";

import type {{ {class_name} }} from "../types";

interface {class_name}CardProps {{
  item: {class_name};
  onClick?: (item: {class_name}) => void;
}}

export function {class_name}Card({{ item, onClick }}: {class_name}CardProps) {{
  return (
    <div
      className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={{() => onClick?.(item)}}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-gray-900">{{item.name}}</h3>
        <span
          className={{`
            px-2 py-1 text-xs rounded-full
            ${{item.is_active
              ? "bg-green-100 text-green-800"
              : "bg-gray-100 text-gray-600"}}
          `}}
        >
          {{item.is_active ? "Active" : "Inactive"}}
        </span>
      </div>
      {{item.description && (
        <p className="text-sm text-gray-600">{{item.description}}</p>
      )}}
      <div className="mt-2 text-xs text-gray-400">
        ID: #{{item.id}} • Updated: {{new Date(item.updated_at).toLocaleDateString()}}
      </div>
    </div>
  );
}}

export default {class_name}Card;
'''


def frontend_lib_utils_ts() -> str:
    """Utility functions."""
    return '''/**
 * Shared utilities | توابع مشترک
 *
 * Auto-scaffolded by phase1_complete_apps.py
 */

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(date: string | Date): string {
  return new Date(date).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function classNames(...classes: (string | undefined | false | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function debounce<T extends (...args: any[]) => void>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
'''


def frontend_test_tsx(class_name: str, app_name: str) -> str:
    """Vitest test file."""
    return f'''/**
 * Tests for {app_name} | تست‌های {app_name}
 *
 * Auto-scaffolded by phase1_complete_apps.py
 * Requires vitest + @testing-library/react to be installed.
 */

import {{ describe, it, expect }} from "vitest";

import type {{ {class_name} }} from "../types";

describe("{class_name}", () => {{
  it("has the expected shape", () => {{
    const item: {class_name} = {{
      id: 1,
      name: "Test",
      description: "A test item",
      is_active: true,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    }};
    expect(item.id).toBe(1);
    expect(item.name).toBe("Test");
  }});

  it("can be inactive", () => {{
    const item: {class_name} = {{
      id: 2,
      name: "Inactive",
      is_active: false,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    }};
    expect(item.is_active).toBe(false);
  }});
}});
'''


def frontend_readme_md(app_name: str) -> str:
    """README for the frontend app."""
    return f'''# {app_name} | اپلیکیشن {app_name}

Part of the **Eco Nojin** platform.

## Overview

This is the {app_name} frontend application, built with:
- React 18
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query (React Query)

## Structure

```
{app_name}/
├── src/
│   ├── pages/           # Route-level components
│   ├── components/      # Reusable UI components
│   ├── hooks/           # React Query hooks
│   ├── api/             # API client
│   ├── types/           # TypeScript types
│   └── lib/             # Utility functions
└── __tests__/           # Vitest tests
```

## Development

```bash
# Install dependencies (from repo root)
pnpm install

# Run dev server
pnpm --filter {app_name} dev

# Build for production
pnpm --filter {app_name} build

# Run tests
pnpm --filter {app_name} test
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual UI requirements.
'''


# ═══════════════════════════════════════════════════════════════════════
# COMPLETION PLANS
# ═══════════════════════════════════════════════════════════════════════

def backend_completion_plan(app_name: str) -> list[tuple[str, str]]:
    """Return list of (relative_path, content) tuples for a backend app."""
    return [
        ("__init__.py", backend_init_py(app_name)),
        ("models.py", backend_models_py(app_name)),
        ("schemas.py", backend_schemas_py(app_name)),
        ("repository.py", backend_repository_py(app_name)),
        ("service.py", backend_service_py(app_name)),
        ("router.py", backend_router_py(app_name)),
        ("dependencies.py", backend_dependencies_py(app_name)),
        ("tests/__init__.py", backend_test_init_py()),
        (f"tests/test_{app_name}.py", backend_test_main_py(app_name)),
        ("README.md", backend_readme_md(app_name)),
    ]


def frontend_completion_plan(class_name: str, app_name: str) -> list[tuple[str, str]]:
    """Return list of (relative_path, content) tuples for a frontend app.

    Args:
        class_name: PascalCase class name (e.g., "HydrologyFrontend", "Cms", "Web")
        app_name:   original app name (e.g., "hydrology-frontend", "cms", "web")
                    used for URL paths and human-readable labels
    """
    return [
        ("src/pages/index.tsx", frontend_index_tsx(class_name, app_name)),
        ("src/types/index.ts", frontend_types_ts(class_name, app_name)),
        ("src/api/index.ts", frontend_api_ts(class_name, app_name)),
        ("src/hooks/index.ts", frontend_hooks_ts(class_name, app_name)),
        ("src/components/Card.tsx", frontend_component_tsx(class_name, app_name)),
        ("src/lib/utils.ts", frontend_lib_utils_ts()),
        ("__tests__/index.test.tsx", frontend_test_tsx(class_name, app_name)),
        ("README.md", frontend_readme_md(app_name)),
    ]


# ═══════════════════════════════════════════════════════════════════════
# CORE EXECUTION
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class AppReport:
    name: str
    type: str
    files_existing: int = 0
    files_planned: int = 0
    files_created: list = field(default_factory=list)
    files_skipped: list = field(default_factory=list)
    errors: list = field(default_factory=list)


def complete_app(
    app_dir: Path,
    app_name: str,
    app_type: str,
    apply: bool = False,
) -> AppReport:
    """Scaffold missing files for a single app."""
    report = AppReport(name=app_name, type=app_type)

    # For frontend apps, derive a valid class name from the package name.
    # Rules:
    #   - "web" → "Web"
    #   - "@econojin/cms" → "Cms"
    #   - "hydrology-frontend" → "HydrologyFrontend" (hyphens → PascalCase)
    #   - "my_cool_app" → "MyCoolApp" (underscores → PascalCase)
    # We also produce a snake_case "module name" for backend imports.
    display_name = app_name
    if app_type in ("frontend", "shared_frontend"):
        pj_path = app_dir / "package.json"
        if pj_path.exists():
            try:
                pj = json.loads(pj_path.read_text(encoding="utf-8-sig"))
                pkg_name = pj.get("name", "")
                if pkg_name:
                    # Strip scope: "@econojin/web" → "web"
                    if pkg_name.startswith("@"):
                        parts = pkg_name.split("/", 1)
                        if len(parts) == 2:
                            display_name = parts[1]
                        else:
                            display_name = pkg_name
                    else:
                        display_name = pkg_name
            except (json.JSONDecodeError, OSError):
                pass

    # Sanitize the display name into a valid TS/JS identifier (PascalCase)
    # "hydrology-frontend" → "HydrologyFrontend"
    # "my_cool_app" → "MyCoolApp"
    # "web" → "Web"
    def to_pascal_case(s: str) -> str:
        # Split on hyphens, underscores, spaces, and camelCase boundaries
        parts = re.split(r'[-_\s]+', s)
        result = ""
        for part in parts:
            if part:
                # Capitalize first letter, keep rest as-is
                result += part[0].upper() + part[1:]
        # If result is empty (all separators), fall back to original
        return result if result else s.capitalize()

    safe_class_name = to_pascal_case(display_name)

    # Choose the completion plan based on app type
    # For frontend templates, pass BOTH the safe class name and the original
    # name so templates can use whichever is appropriate.
    if app_type in ("backend", "shared_backend"):
        plan = backend_completion_plan(app_name)
    elif app_type in ("frontend", "shared_frontend"):
        plan = frontend_completion_plan(safe_class_name, app_name)
    else:
        report.errors.append(f"Unknown app type: {app_type}")
        return report

    report.files_planned = len(plan)

    # Count existing files in the app dir (top-level only, for status display)
    try:
        report.files_existing = sum(1 for f in app_dir.rglob("*") if f.is_file())
    except (PermissionError, OSError):
        pass

    for rel_path, content in plan:
        target = app_dir / rel_path
        try:
            if target.exists():
                report.files_skipped.append(rel_path)
                continue
            if apply:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            report.files_created.append(rel_path)
        except (PermissionError, OSError) as e:
            report.errors.append(f"{rel_path}: {e}")

    return report


def main():
    parser = argparse.ArgumentParser(
        prog="phase1_complete_apps",
        description="Eco Nojin Phase 1: Complete apps/ directory structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--root", type=str, default=".",
        help="Path to the repo root (default: current directory)",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually create files (default: dry-run, just preview)",
    )
    parser.add_argument(
        "--only", type=str, default=None,
        help="Comma-separated list of app names to process (default: all)",
    )
    parser.add_argument(
        "--skip", type=str, default=None,
        help="Comma-separated list of app names to skip",
    )
    parser.add_argument(
        "--report", type=str, default="phase1_report.json",
        help="Path to write JSON summary (default: ./phase1_report.json)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output (list every file created/skipped)",
    )
    parser.add_argument(
        "--force-type", type=str, default=None,
        help=("Override auto-detection. Comma-separated list of "
              "app_name:type pairs. Valid types: backend, frontend, "
              "shared_backend, shared_frontend. "
              "Example: --force-type api:backend,shared:backend,"
              "shared_sim:shared_backend"),
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    apps_dir = root / "apps"
    if not apps_dir.exists():
        print(f"Error: apps/ directory not found at: {apps_dir}", file=sys.stderr)
        sys.exit(1)

    # Build include/exclude sets
    only_set = {s.strip() for s in args.only.split(",")} if args.only else None
    skip_set = {s.strip() for s in args.skip.split(",")} if args.skip else set()

    # Build force-type override map (app_name → type)
    force_types: dict[str, str] = {}
    if args.force_type:
        valid_types = {"backend", "frontend", "shared_backend", "shared_frontend"}
        for entry in args.force_type.split(","):
            entry = entry.strip()
            if not entry:
                continue
            if ":" not in entry:
                print(f"Error: --force-type entry '{entry}' is missing ':type'. "
                      f"Expected 'app_name:type'", file=sys.stderr)
                sys.exit(2)
            app_name, app_type = entry.split(":", 1)
            app_name = app_name.strip()
            app_type = app_type.strip()
            if app_type not in valid_types:
                print(f"Error: invalid type '{app_type}' for app '{app_name}'. "
                      f"Valid: {', '.join(sorted(valid_types))}", file=sys.stderr)
                sys.exit(2)
            force_types[app_name] = app_type

    # Discover apps
    app_dirs = sorted(
        [d for d in apps_dir.iterdir()
         if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("__")]
    )

    if not app_dirs:
        print(f"No subdirectories found in {apps_dir}", file=sys.stderr)
        sys.exit(1)

    mode_label = "APPLY (writing files)" if args.apply else "DRY-RUN (no files written — pass --apply to execute)"
    print("=" * 70)
    print(f"  Eco Nojin Phase 1 — Complete apps/ Structure")
    print(f"  Mode: {mode_label}")
    print(f"  Root: {root}")
    print(f"  Apps found: {len(app_dirs)}")
    print("=" * 70)
    print()

    all_reports: list[AppReport] = []
    for app_dir in app_dirs:
        name = app_dir.name

        # Filter by --only / --skip
        if only_set and name not in only_set:
            continue
        if name in skip_set:
            continue

        app_type = force_types.get(name) or detect_app_type(app_dir)
        if name in force_types:
            print(f"  [{app_type:>15}] {name}/  (forced via --force-type)")
        else:
            print(f"  [{app_type:>15}] {name}/")

        if app_type == "unknown":
            print(f"      → skipping (unknown type, no markers found)")
            continue

        report = complete_app(app_dir, name, app_type, apply=args.apply)
        all_reports.append(report)

        if report.errors:
            for e in report.errors:
                print(f"      ! ERROR: {e}")

        if args.verbose:
            for f in report.files_created:
                action = "CREATED" if args.apply else "WO CREATE"
                print(f"      + {action}: {f}")
            for f in report.files_skipped:
                print(f"      · skip (exists): {f}")
        else:
            n_created = len(report.files_created)
            n_skipped = len(report.files_skipped)
            n_planned = report.files_planned
            action_word = "created" if args.apply else "to create"
            print(f"      → {n_created} files {action_word}, {n_skipped} skipped (of {n_planned} planned)")

    # Summary
    total_created = sum(len(r.files_created) for r in all_reports)
    total_skipped = sum(len(r.files_skipped) for r in all_reports)
    total_errors = sum(len(r.errors) for r in all_reports)

    print()
    print("=" * 70)
    print(f"  SUMMARY")
    print("=" * 70)
    print(f"  Apps processed : {len(all_reports)}")
    print(f"  Files {'created' if args.apply else 'to create'}: {total_created}")
    print(f"  Files skipped  : {total_skipped} (already exist)")
    print(f"  Errors         : {total_errors}")
    if not args.apply and total_created > 0:
        print()
        print("  ⚠  This was a DRY-RUN. To actually create the files, run:")
        print(f"     python3 {Path(sys.argv[0]).name} --apply")
    print()

    # Write JSON report
    report_path = root / args.report
    report_data = {
        "tool": "phase1_complete_apps.py",
        "mode": "apply" if args.apply else "dry-run",
        "executed_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "apps_processed": len(all_reports),
        "total_files_created_or_planned": total_created,
        "total_files_skipped": total_skipped,
        "total_errors": total_errors,
        "apps": [asdict(r) for r in all_reports],
    }
    try:
        report_path.write_text(
            json.dumps(report_data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        print(f"  Report written to: {report_path}")
    except (PermissionError, OSError) as e:
        print(f"  Warning: could not write report: {e}", file=sys.stderr)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
