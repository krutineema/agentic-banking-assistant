from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    intent: str
    reason: str


class IntentRouter:
    """A transparent, deterministic router.

    This is intentionally NOT an LLM router and NOT an agent. It exists so we
    can inspect where deterministic rules work, where they become brittle, and
    what changes when we later let a model choose tools dynamically.
    """

    def route(self, message: str) -> RouteDecision:
        text = message.lower().strip()

        if any(word in text for word in ("balance", "how much money", "accounts")):
            return RouteDecision(
                intent="account_balance",
                reason="Matched account/balance vocabulary.",
            )

        if any(word in text for word in ("spent", "spend", "spending")):
            return RouteDecision(
                intent="spending_summary",
                reason="Matched spending-analysis vocabulary.",
            )

        if any(word in text for word in ("transaction", "transactions", "payment", "payments")):
            return RouteDecision(
                intent="recent_transactions",
                reason="Matched transaction/payment vocabulary.",
            )

        return RouteDecision(
            intent="unsupported",
            reason="No Stage 1 deterministic route matched the request.",
        )
