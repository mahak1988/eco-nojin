import sys, os, json
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from api.services.iot.iot_data_simulator import IoTDataSimulator
from api.services.mrv.mrv_calculator import MRVCalculator
from api.services.carbon.carbon_credit_issuer import CarbonCreditIssuer
from api.services.pes.pes_payment_system import PESPaymentSystem

def execute_first_mrv_cycle():
    print("=" * 80)
    print("🚀 اجرای اولین چرخه MRV واقعی برای ۱۲ پایلوت جهانی")
    print("=" * 80)
    sim, calc, issuer, pes = IoTDataSimulator(), MRVCalculator(), CarbonCreditIssuer(), PESPaymentSystem()
    results = {"cycle_id": "FIRST-MRV-2026", "pilots": {}}
    t_carbon, t_water, t_pay = 0, 0, 0
    for p in sim.pilots.keys():
        print(f"\n📍 پردازش پایلوت: {p}")
        data = sim.simulate_sensor_readings(p, 90)
        mrv = calc.generate_mrv_report(data)
        credit = issuer.issue_credits(mrv)
        payment = pes.calculate_payments(mrv, credit)
        results["pilots"][p] = {"mrv": mrv, "credit": credit, "payment": payment}
        t_carbon += credit["volume_tCO2e"]
        t_water += payment["breakdown"]["water_saved_m3"]
        t_pay += payment["total_payment_usd"]
        print(f"  ✅ کربن: {credit['volume_tCO2e']:.2f} tCO2e | آب: {payment['breakdown']['water_saved_m3']:.0f} m3 | پرداخت: ${payment['total_payment_usd']:.2f}")
    results["summary"] = {"total_carbon_tCO2e": round(t_carbon,2), "total_water_m3": round(t_water,0), "total_pay_usd": round(t_pay,2)}
    print("\n" + "=" * 80)
    print(f"✨ کل کربن: {t_carbon:.2f} tCO2e | کل آب: {t_water:.0f} m3 | کل پرداخت: ${t_pay:.2f}")
    out = Path(__file__).parent / "FIRST_MRV_CYCLE_RESULTS.json"
    with open(out, "w", encoding="utf-8") as f: json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 ذخیره شد: {out}")

if __name__ == "__main__": execute_first_mrv_cycle()