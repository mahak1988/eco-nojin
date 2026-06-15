"""Quick test to verify bcrypt works correctly"""

import sys
import os

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

import bcrypt


def test_bcrypt():
    """Test bcrypt directly"""
    print("=" * 60)
    print("Bcrypt Direct Test")
    print("=" * 60)
    print()
    
    try:
        print(f"Bcrypt version: {bcrypt.__version__}")
        print()
        
        # Test password
        password = os.environ.get("TEST_PASSWORD", "secure_default_password")
        
        # Hash password
        print(f"[1/3] Hashing password: {password}")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_str = hashed.decode('utf-8')
        print(f"        Hash: {hashed_str[:50]}...")
        print()
        
        # Verify correct password
        print("[2/3] Verifying correct password")
        is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed)
        print(f"        Result: {is_valid}")
        assert is_valid, "Password verification failed!"
        print()
        
        # Verify wrong password
        print("[3/3] Verifying wrong password")
        wrong = bcrypt.checkpw(b"wrongpassword", hashed)
        print(f"        Result: {wrong}")
        assert not wrong, "Wrong password should not verify!"
        print()
        
        print("=" * 60)
        print("SUCCESS: All bcrypt tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERROR: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_bcrypt()
    sys.exit(0 if success else 1)
