from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DNSVerificationResult:
    success: bool
    message: str


class DNSVerifier:
    """Simple DNS verifier that ensures the provided token matches expectation."""

    def verify(self, expected_token: str, provided_token: str) -> DNSVerificationResult:
        if provided_token.strip() != expected_token.strip():
            return DNSVerificationResult(success=False, message="DNS record value does not match verification token")
        return DNSVerificationResult(success=True, message="Domain ownership verified")


dns_verifier = DNSVerifier()
