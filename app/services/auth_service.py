import hashlib
import hmac

from app.models.auth import AuthenticatedCustomer
from app.repositories import CustomerRepository


class AuthService:
    """Validates demo credentials against customer records in SQLite."""

    def __init__(self, customers: CustomerRepository) -> None:
        self.customers = customers

    def authenticate(self, username: str, password: str) -> AuthenticatedCustomer | None:
        customer = self.customers.find_by_username(username)
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
