"""Digital Certificate Service with Blockchain Integration"""
from typing import Dict, Optional
from datetime import datetime, timezone
import hashlib
import json


class CertificateService:
    """Digital Certificate Service"""
    
    def __init__(self, blockchain_service=None):
        self.blockchain = blockchain_service
        self.certificates = {}
    
    def generate_certificate_hash(self, certificate_data: Dict) -> str:
        """Generate SHA-256 hash of certificate data"""
        cert_string = json.dumps(certificate_data, sort_keys=True)
        return hashlib.sha256(cert_string.encode()).hexdigest()
    
    def issue_certificate(
        self,
        user_id: str,
        user_name: str,
        course_id: str,
        course_title: str,
        completion_date: datetime,
        pilot_site: str
    ) -> Dict:
        """Issue a digital certificate"""
        
        certificate_data = {
            "user_id": user_id,
            "user_name": user_name,
            "course_id": course_id,
            "course_title": course_title,
            "completion_date": completion_date.isoformat(),
            "pilot_site": pilot_site,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "issuer": "Econojin Learning Platform"
        }
        
        # Generate hash
        cert_hash = self.generate_certificate_hash(certificate_data)
        certificate_data["hash"] = cert_hash
        
        # Register on blockchain if available
        blockchain_tx = None
        if self.blockchain:
            try:
                blockchain_tx = self.blockchain.issue_certificate_nft(
                    user_id=user_id,
                    certificate_hash=cert_hash,
                    metadata=certificate_data
                )
                certificate_data["blockchain_tx"] = blockchain_tx
            except Exception as e:
                certificate_data["blockchain_error"] = str(e)
        
        # Generate QR code URL
        qr_url = f"https://econojin.com/verify/{cert_hash}"
        certificate_data["qr_code_url"] = qr_url
        
        # Store certificate
        self.certificates[cert_hash] = certificate_data
        
        return certificate_data
    
    def verify_certificate(self, cert_hash: str) -> Optional[Dict]:
        """Verify a certificate by hash"""
        return self.certificates.get(cert_hash)
    
    def get_user_certificates(self, user_id: str) -> list:
        """Get all certificates for a user"""
        return [c for c in self.certificates.values() if c["user_id"] == user_id]
