import csv
import io
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.shared_core.database.session import get_db_session
from apps.simulation.runs.models import SimulationRun

router = APIRouter(prefix="/api/v1/simulation", tags=["📊 Reports"])

@router.get("/reports/{run_id}/csv", summary="Export run as CSV")
async def export_run_csv(run_id: UUID, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(SimulationRun).where(SimulationRun.id == str(run_id)))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["simulator_id", "simulator_name", "created_at", "metric_key", "metric_value", "parameter_key", "parameter_value"])
    
    metrics = run.metrics or {}
    params = run.parameters or {}
    for mk, mv in metrics.items():
        writer.writerow([run.simulator_id, run.simulator_name, str(run.created_at), mk, mv, "", ""])
    for pk, pv in params.items():
        writer.writerow([run.simulator_id, run.simulator_name, str(run.created_at), "", "", pk, pv])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={run.simulator_id}_{run_id}.csv"}
    )

@router.get("/reports/{run_id}/html", summary="Get structured HTML report for PDF printing")
async def export_run_html(run_id: UUID, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(SimulationRun).where(SimulationRun.id == str(run_id)))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    
    metrics_html = "".join([f'<div class="metric"><strong>{k}:</strong> {v}</div>' for k, v in (run.metrics or {}).items()])
    params_html = "".join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in (run.parameters or {}).items()])

    html_content = """<!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <title>گزارش شبیه‌سازی """ + str(run.simulator_name) + """</title>
        <style>
            @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
            body { font-family: 'Vazirmatn', Tahoma, sans-serif; padding: 40px; line-height: 1.8; color: #1e293b; direction: rtl; }
            h1 { color: #0f766e; border-bottom: 3px solid #0f766e; padding-bottom: 10px; margin-bottom: 30px; }
            h3 { color: #334155; margin-top: 30px; }
            .metric { display: inline-block; background: #f0fdfa; border: 1px solid #99f6e4; padding: 12px 20px; border-radius: 8px; margin: 5px; min-width: 120px; text-align: center; }
            .metric strong { display: block; color: #0f766e; font-size: 1.2em; margin-bottom: 5px; }
            ul { list-style-type: none; padding: 0; }
            li { background: #f8fafc; margin: 5px 0; padding: 10px; border-radius: 6px; border-right: 4px solid #0f766e; }
            .btn-print { margin-top: 30px; padding: 12px 24px; background: #0f766e; color: white; border: none; border-radius: 8px; cursor: pointer; font-family: 'Vazirmatn'; font-size: 16px; }
            .btn-print:hover { background: #0d9488; }
            @media print { .no-print { display: none; } body { padding: 0; } }
        </style>
    </head>
    <body>
        <h1>گزارش جامع شبیه‌سازی: """ + str(run.simulator_name) + """</h1>
        <p>تاریخ اجرا: """ + str(run.created_at) + """</p>
        <h3>📊 متریک‌های کلیدی</h3>
        <div>""" + metrics_html + """</div>
        <h3>⚙️ پارامترهای ورودی</h3>
        <ul>""" + params_html + """</ul>
        <button class="btn-print no-print" onclick="window.print()">🖨️ چاپ یا ذخیره به‌عنوان PDF</button>
    </body>
    </html>"""
    
    return HTMLResponse(content=html_content)
