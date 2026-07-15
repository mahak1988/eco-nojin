#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for shared_core.database.session
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from apps.shared_core.database.session import get_db, init_db, close_db, AsyncSessionLocal


class TestDatabaseSession:
    """Tests for database session management"""
    
    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test that get_db yields a database session"""
        mock_session = AsyncMock()
        
        with patch("apps.shared_core.database.session.AsyncSessionLocal") as mock_factory:
            mock_factory.return_value.__aenter__.return_value = mock_session
            mock_factory.return_value.__aexit__.return_value = None
            
            async for db in get_db():
                assert db is not None
                break
    
    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """Test that init_db creates database tables"""
        with patch("apps.shared_core.database.session.Base") as mock_base:
            mock_base.metadata.create_all = AsyncMock()
            
            await init_db()
            
            mock_base.metadata.create_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_db_disposes_engine(self):
        """Test that close_db disposes the engine"""
        with patch("apps.shared_core.database.session.engine") as mock_engine:
            mock_engine.dispose = AsyncMock()
            
            await close_db()
            
            mock_engine.dispose.assert_called_once()
