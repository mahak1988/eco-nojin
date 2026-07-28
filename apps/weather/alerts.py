"""Smart climate alerts: drought, flood, frost, heat stress."""

from __future__ import annotations

from typing import Any


def evaluate_alerts(series: list[dict[str, Any]]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    if not series:
        return alerts

    for row in series:
        tmin = row.get("temp_min_c")
        tmax = row.get("temp_max_c")
        tmean = row.get("temp_mean_c")
        if tmin is not None and tmin <= 0:
            alerts.append(
                {
                    "type": "frost",
                    "severity": "warning" if tmin > -2 else "critical",
                    "date": row.get("date"),
                    "message": f"Frost risk: min temperature {tmin}°C",
                    "value": tmin,
                }
            )
        peak = tmax if tmax is not None else tmean
        if peak is not None and peak >= 38:
            alerts.append(
                {
                    "type": "heat_stress",
                    "severity": "warning" if peak < 42 else "critical",
                    "date": row.get("date"),
                    "message": f"Heat stress: max/mean temperature {peak}°C",
                    "value": peak,
                }
            )
        p = row.get("precip_mm") or 0
        if p >= 40:
            alerts.append(
                {
                    "type": "flood",
                    "severity": "warning" if p < 60 else "critical",
                    "date": row.get("date"),
                    "message": f"Heavy rainfall {p} mm/day — flood risk",
                    "value": p,
                }
            )

    precip = [float(r.get("precip_mm") or 0) for r in series]
    temps = [float(r.get("temp_mean_c") or r.get("temp_max_c") or 20) for r in series]
    for i in range(len(series)):
        if i >= 2:
            s3 = sum(precip[i - 2 : i + 1])
            if s3 >= 80:
                alerts.append(
                    {
                        "type": "flood",
                        "severity": "critical",
                        "date": series[i].get("date"),
                        "message": f"3-day rainfall sum {s3:.1f} mm",
                        "value": s3,
                    }
                )
        if i >= 13:
            s14 = sum(precip[i - 13 : i + 1])
            t14 = sum(temps[i - 13 : i + 1]) / 14
            if s14 < 5 and t14 > 28:
                alerts.append(
                    {
                        "type": "drought",
                        "severity": "warning" if s14 >= 2 else "critical",
                        "date": series[i].get("date"),
                        "message": f"14-day precip {s14:.1f} mm with mean temp {t14:.1f}°C",
                        "value": s14,
                    }
                )

    seen = set()
    unique = []
    for a in alerts:
        key = (a["type"], a.get("date"), a["message"][:40])
        if key in seen:
            continue
        seen.add(key)
        unique.append(a)
    return unique
