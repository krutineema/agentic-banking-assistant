import hashlib
import hmac
import json
from pathlib import Path

from app.models.auth import AuthenticatedCustomer, StoredCustomer


class AuthService:
    """Validates demo credentials stored as salted password hashes.

    This is intentionally small and local for the learning project. It models the
    authentication boundary without pretending to be a production identity system.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(__file__).resolve().parents[1] / "data"
        self._customers = self._load_customers()

    def _load_customers(self) -> list[StoredCustomer]:
        payload = json.loads((self.data_dir / "customers.json").read_text())
        return [StoredCustomer.model_validate(item) for item in payload]

    def authenticate(self, username: str, password: str) -> AuthenticatedCustomer | None:
        customer = next((c for c in self._customers if c.username == username), None)
        if customer is None:
            return None

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(customer.password_salt),
            customer.password_iterations,
        ).hex()

        if not hmac.compare_digest(candidate, customer.password_hash):
            return None

        return AuthenticatedCustomer(
            customer_id=customer.customer_id,
            username=customer.username,
            display_name=customer.display_name,
        )
