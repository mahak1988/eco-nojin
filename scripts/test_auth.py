#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test authentication module"""

import pytest
from backend.api.auth import (
    login_user,
    get_current_user,
    verify_token,
    logout_user,
    AuthError,
    TokenManager
)


class TestAuth:
    """Test authentication functions"""
    
    def test_import_auth_module(self):
        """Test that auth module can be imported"""
        assert login_user is not None
        assert get_current_user is not None
        assert verify_token is not None
        assert logout_user is not None
    
    def test_has_auth_functions(self):
        """Test that auth module has required functions"""
        assert callable(login_user)
        assert callable(get_current_user)
        assert callable(verify_token)
        assert callable(logout_user)
    
    def test_login_user_success(self):
        """Test successful login"""
        result = login_user("testuser", "testpass")
        
        assert "token" in result
        assert "user_id" in result
        assert "username" in result
        assert result["username"] == "testuser"
        assert "expires_in" in result
    
    def test_login_user_empty_credentials(self):
        """Test login with empty credentials"""
        with pytest.raises(AuthError):
            login_user("", "password")
        
        with pytest.raises(AuthError):
            login_user("username", "")
    
    def test_get_current_user_valid_token(self):
        """Test getting user with valid token"""
        login_result = login_user("testuser", "testpass")
        token = login_result["token"]
        
        user = get_current_user(token)
        
        assert user is not None
        assert "user_id" in user
        assert user["authenticated"] is True
    
    def test_get_current_user_invalid_token(self):
        """Test getting user with invalid token"""
        user = get_current_user("invalid_token")
        assert user is None
    
    def test_verify_token_valid(self):
        """Test verifying valid token"""
        login_result = login_user("testuser", "testpass")
        token = login_result["token"]
        
        assert verify_token(token) is True
    
    def test_verify_token_invalid(self):
        """Test verifying invalid token"""
        assert verify_token("invalid_token") is False
    
    def test_logout_user(self):
        """Test logout user"""
        login_result = login_user("testuser", "testpass")
        token = login_result["token"]
        
        # Verify token is valid
        assert verify_token(token) is True
        
        # Logout
        result = logout_user(token)
        assert result is True
        
        # Verify token is now invalid
        assert verify_token(token) is False
    
    def test_token_manager(self):
        """Test TokenManager class"""
        manager = TokenManager("test_secret")
        
        # Generate token
        token = manager.generate_token("user123")
        assert token is not None
        
        # Verify token
        user_id = manager.verify_token(token)
        assert user_id == "user123"
        
        # Revoke token
        result = manager.revoke_token(token)
        assert result is True
        
        # Verify revoked token
        user_id = manager.verify_token(token)
        assert user_id is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])