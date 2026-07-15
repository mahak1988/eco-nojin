# Julia Scientific Service
## راه‌اندازی
1. از داخل پوشه `automation/julia_server`، بسته‌ها را نصب کنید:
   julia -e 'import Pkg; Pkg.activate("."); Pkg.instantiate()'
2. سرور را اجرا کنید:
   julia --project=. server.jl
3. سرور روی `http://localhost:8080` آماده دریافت درخواست است.

## تست
curl -X POST http://localhost:8080/compute -H "Content-Type: application/json" -d '{"watershed_id":"test"}'
