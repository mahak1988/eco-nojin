"""PES Payment System"""
from datetime import datetime, timezone
import hashlib, uuid, json

class PESPaymentSystem:
    CARBON_PAYMENT_USD, WATER_PAYMENT_USD, SOIL_PAYMENT_USD = 10.0, 0.75, 75.0
    def calculate_payments(self, mrv_report, credit):
        pilot = mrv_report["pilot_site"]
        c_pay = mrv_report["carbon"]["total_sequestration_tCO2"] * self.CARBON_PAYMENT_USD
        w_pay = mrv_report["water"]["water_saved_m3"] * self.WATER_PAYMENT_USD
        s_pay = 100 * self.SOIL_PAYMENT_USD * (90/365)
        total = c_pay + w_pay + s_pay
        pay_id = f"PES-{pilot.upper()}-{uuid.uuid4().hex[:8].upper()}"
        tx_hash = "0x" + hashlib.sha256(json.dumps({"id": pay_id, "total": total}).encode()).hexdigest()[:64]
        return {"payment_id": pay_id, "pilot_site": pilot, "breakdown": {"carbon_payment_usd": round(c_pay,2), "water_saved_m3": mrv_report["water"]["water_saved_m3"], "water_payment_usd": round(w_pay,2), "soil_payment_usd": round(s_pay,2)}, "total_payment_usd": round(total, 2), "blockchain_tx_hash": tx_hash, "status": "paid"}