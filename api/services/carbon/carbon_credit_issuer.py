"""Carbon Credit Issuer"""
from datetime import datetime, timezone
import hashlib, uuid, json

class CarbonCreditIssuer:
    CARBON_PRICE_USD = 12.5
    def issue_credits(self, mrv_report):
        pilot_site = mrv_report["pilot_site"]
        total_tCO2e = mrv_report["carbon"]["total_sequestration_tCO2"]
        credit_id = f"CREDIT-{pilot_site.upper()}-{uuid.uuid4().hex[:8].upper()}"
        tx_data = {"credit_id": credit_id, "pilot_site": pilot_site, "volume_tCO2e": total_tCO2e}
        tx_hash = "0x" + hashlib.sha256(json.dumps(tx_data, sort_keys=True).encode()).hexdigest()[:64]
        return {"credit_id": credit_id, "pilot_site": pilot_site, "volume_tCO2e": round(total_tCO2e, 2), "credit_value_usd": round(total_tCO2e * self.CARBON_PRICE_USD, 2), "blockchain_tx_hash": tx_hash, "status": "issued"}