import secrets

from app.models.auth import AuthenticatedCustomer


class SessionService:
    """Tiny in-memory server-side session store for Stage 1.

    Session tokens are opaque random values placed in an HttpOnly cookie. The
    authenticated customer identity remains server-side. Sessions intentionally
    disappear when the local app restarts; durable/session-provider integration is
    outside Stage 1.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, AuthenticatedCustomer] = {}

    def create(self, customer: AuthenticatedCustomer) -> str:
        token = secrets.token_urlsafe(32)
        self._sessions[token] = customer
        return token

    def get(self, token: str | None) -> AuthenticatedCustomer | None:
        if not token:
            return None
        return self._sessions.get(token)

    def delete(self, token: str | None) -> None:
        if token:
            self._sessions.pop(token, None)
