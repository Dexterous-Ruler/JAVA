from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Certificate:
    domain: str
    issued_at: datetime
    pem: str


class ACMEClient:
    """Minimal ACME automation facade used for issuing mock certificates."""

    def issue_certificate(self, domain: str) -> Certificate:
        issued_at = datetime.utcnow()
        pem = (
            "-----BEGIN CERTIFICATE-----\n"
            f"Mock Certificate for {domain} issued at {issued_at.isoformat()}\n"
            "-----END CERTIFICATE-----"
        )
        return Certificate(domain=domain, issued_at=issued_at, pem=pem)


acme_client = ACMEClient()
