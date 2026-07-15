# Temporal for Eco Nojin

## ۱. راه‌اندازی سرور Temporal (Temporalite)
برای توسعه محلی بدون Docker، از Temporalite استفاده کنید:

۱. `temporalite.exe` را از لینک زیر دانلود کنید:
   https://github.com/DataDog/temporalite/releases/latest/download/temporalite_windows_amd64.exe

۲. فایل را به `C:\Windows\System32` یا هر مسیری که در PATH است منتقل کنید (اختیاری).

۳. یک ترمینال جدید باز کرده و اجرا کنید:
   temporalite start --namespace default

۴. سرور روی `localhost:7233` گوش می‌دهد.

## ۲. اجرای Worker
در ترمینال پروژه، worker را اجرا کنید:
   python -m app.temporal.worker

## ۳. ارسال یک Workflow
از داخل کد یا از طریق API بک‌اند می‌توانید workflow را شروع کنید:
   client.start_workflow(SimulationWorkflow.run, args=['watershed-1', 'SWAT'], task_queue='eco-nojin-simulation-queue')
