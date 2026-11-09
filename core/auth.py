import hashlib


def hash_password(password):
    """Return the SHA-256 hex digest of *password*."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password, stored_hash):
    """Return True if the SHA-256 hash of *password* matches *stored_hash*."""
    return hash_password(password) == stored_hash
