"""Carbon Credit Issuance and Verification Service

این ماژول فرآیند صدور، راستی‌آزمایی و ثبت اعتبارات کربن را مدیریت می‌کند.
"""
from typing import Dict, Optional
from datetime import datetime
import uuid


class CarbonCreditService:
    """سرویس صدور و مدیریت اعتبارات کربن"""
    
    def __init__(self, blockchain_service=None):
        self.blockchain = blockchain_service
        self.issued_credits = {}
    
    def issue_carbon_credit(
        self,
        project_id: str,
        volume_tCO2e: float,
        verification_date: datetime,
        price_per_ton: float = 25.0,
        currency: str = 'USD'
    ) -> Dict:
        """
        صدور اعتبار کربن جدید
        """
        credit_id = str(uuid.uuid4())
        
        credit = {
            'credit_id': credit_id,
            'project_id': project_id,
            'volume_tCO2e': volume_tCO2e,
            'verification_date': verification_date.isoformat(),
            'price_per_ton': price_per_ton,
            'currency': currency,
            'total_value': round(volume_tCO2e * price_per_ton, 2),
            'status': 'VERIFIED',
            'issued_at': datetime.utcnow().isoformat(),
            'blockchain_tx_hash': None
        }
        
        self.issued_credits[credit_id] = credit
        
        # ثبت در بلاکچین (در صورت وجود)
        if self.blockchain:
            try:
                tx_hash = self.blockchain.issue_gaia_certificate(
                    project_id=project_id,
                    volume_tco2e=int(volume_tCO2e),
                    verification_timestamp=int(verification_date.timestamp()),
                    private_key=os.getenv('BLOCKCHAIN_PRIVATE_KEY', '')
                )
                credit['blockchain_tx_hash'] = tx_hash
                credit['status'] = 'BLOCKCHAIN_VERIFIED'
            except Exception as e:
                credit['status'] = 'VERIFIED_PENDING_BLOCKCHAIN'
        
        return credit
    
    def verify_credit(self, credit_id: str, verifier_id: str) -> bool:
        """راستی‌آزمایی اعتبار کربن"""
        if credit_id in self.issued_credits:
            self.issued_credits[credit_id]['verified_by'] = verifier_id
            self.issued_credits[credit_id]['verified_at'] = datetime.utcnow().isoformat()
            return True
        return False
    
    def retire_credit(self, credit_id: str, reason: str) -> bool:
        """بازنشستگی اعتبار کربن (استفاده نهایی)"""
        if credit_id in self.issued_credits:
            self.issued_credits[credit_id]['status'] = 'RETIRED'
            self.issued_credits[credit_id]['retired_at'] = datetime.utcnow().isoformat()
            self.issued_credits[credit_id]['retirement_reason'] = reason
            return True
        return False
    
    def get_project_credits(self, project_id: str) -> list:
        """دریافت تمام اعتبارات یک پروژه"""
        return [
            credit for credit in self.issued_credits.values()
            if credit['project_id'] == project_id
        ]
    
    def get_total_issued_volume(self, project_id: Optional[str] = None) -> float:
        """محاسبه حجم کل اعتبارات صادرشده"""
        if project_id:
            credits = self.get_project_credits(project_id)
        else:
            credits = list(self.issued_credits.values())
        
        return sum(c['volume_tCO2e'] for c in credits if c['status'] != 'RETIRED')
