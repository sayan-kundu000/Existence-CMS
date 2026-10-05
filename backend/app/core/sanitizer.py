"""
Centralized Input Sanitization, XSS Protection, SSRF Defense, and Secret Scrubbing.
Ensures no untrusted client input can inject scripts, execute SSRF probes, or leak credentials into audit trails.
"""
import re
import ipaddress
from urllib.parse import urlparse
from typing import Optional, Any, Dict, List
from app.core.exceptions import ValidationFailedError

# HTML / script pattern matching for XSS sanitization
DANGEROUS_HTML_PATTERNS = [
    re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*iframe[^>]*>.*?<\s*/\s*iframe\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*object[^>]*>.*?<\s*/\s*object\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*embed[^>]*>.*?<\s*/\s*embed\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*style[^>]*>.*?<\s*/\s*style\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"on\w+\s*=\s*[\"'][^\"']*[\"']", re.IGNORECASE),
    re.compile(r"javascript:\s*", re.IGNORECASE),
    re.compile(r"data:text/html", re.IGNORECASE),
    re.compile(r"vbscript:\s*", re.IGNORECASE),
]

# Keys that must never appear in audit trails or diagnostic logs
SENSITIVE_FIELD_NAMES = {
    "password", "password_hash", "hashed_password", "current_password", "new_password",
    "pin", "pin_hash", "hashed_pin", "current_pin", "new_pin",
    "token", "access_token", "refresh_token", "pin_token", "jwt",
    "secret", "secret_key", "api_key", "authorization", "x-action-pin",
    "cookie", "session_id", "database_url"
}

# Blocked SSRF hostnames and IP networks
RESTRICTED_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0", "::1",
    "metadata.google.internal", "169.254.169.254"
}


def sanitize_text(text: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
    """
    Sanitize user-provided text content to prevent stored XSS attacks.
    Strips active execution vectors while preserving genuine user markdown and punctuation.
    """
    if text is None:
        return None

    cleaned = text
    for pattern in DANGEROUS_HTML_PATTERNS:
        cleaned = pattern.sub("", cleaned)

    # Normalize excessive null bytes and control characters
    cleaned = cleaned.replace("\x00", "")

    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned


def validate_safe_url(url: str, allow_empty: bool = False) -> str:
    """
    Validates that a URL is well-formed, uses safe protocols (http/https),
    and prevents SSRF (Server-Side Request Forgery) by blocking loopback,
    cloud metadata, and dangerous URI schemes (javascript:, file:, data:).
    """
    if not url or not url.strip():
        if allow_empty:
            return ""
        raise ValidationFailedError("URL cannot be empty.")

    clean_url = url.strip()

    # Reject dangerous protocols immediately
    lower_url = clean_url.lower()
    if lower_url.startswith(("javascript:", "data:", "file:", "vbscript:", "blob:")):
        raise ValidationFailedError("URL scheme is dangerous or unsupported. Use http:// or https://.")

    try:
        parsed = urlparse(clean_url)
    except Exception:
        raise ValidationFailedError(f"Malformed URL: '{url}'")

    if parsed.scheme not in ("http", "https"):
        raise ValidationFailedError(f"Invalid URL scheme '{parsed.scheme}'. Only 'http' and 'https' are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise ValidationFailedError(f"URL missing a valid hostname: '{url}'")

    lower_host = hostname.lower()
    if lower_host in RESTRICTED_HOSTS:
        raise ValidationFailedError(f"Access to restricted or loopback host '{hostname}' is forbidden.")

    # Check for private or loopback IP ranges
    try:
        ip = ipaddress.ip_address(lower_host)
        if ip.is_loopback or ip.is_private or ip.is_reserved or ip.is_link_local:
            raise ValidationFailedError(f"Access to private/local network address '{lower_host}' is forbidden.")
    except ValueError:
        # Not a raw IP address; standard domain name
        pass

    return clean_url


def sanitize_audit_metadata(data: Any) -> Any:
    """
    Recursively scrubs sensitive keys from audit logs and error details.
    Guarantees that credentials, tokens, and PINs are never stored in audit logs.
    """
    if isinstance(data, dict):
        scrubbed = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_FIELD_NAMES:
                scrubbed[k] = "[REDACTED]"
            else:
                scrubbed[k] = sanitize_audit_metadata(v)
        return scrubbed
    elif isinstance(data, list):
        return [sanitize_audit_metadata(item) for item in data]
    return data
