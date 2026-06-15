@echo off
echo ========================================
echo EcoNojin API - Authentication Test
echo ========================================
echo.

echo [1/4] Testing Register...
curl -s -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"farmer@test.com\", \"password\": \"password123\", \"full_name\": \"Test Farmer\", \"role\": \"farmer\"}"
echo.
echo.

echo [2/4] Testing Login...
curl -s -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@econojin.com\", \"password\": \"admin123456\"}"
echo.
echo.

echo [3/4] Testing Get Current User (need token)...
echo Copy the access_token from above and run:
echo curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/auth/me
echo.

echo [4/4] Testing List Users (admin only)...
echo curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/users/
echo.

echo ========================================
echo Test complete!
echo ========================================
