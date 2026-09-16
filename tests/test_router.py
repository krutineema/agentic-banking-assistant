from app.core.router import IntentRouter


def test_routes_balance_request():
    decision = IntentRouter().route("What is my account balance?")
    assert decision.intent == "account_balance"


def test_routes_spending_request():
    decision = IntentRouter().route("How much did I spend on restaurants in August?")
    assert decision.intent == "spending_summary"


def test_routes_transaction_request():
    decision = IntentRouter().route("Show my recent transactions")
    assert decision.intent == "recent_transactions"


def test_rejects_unknown_request():
    decision = IntentRouter().route("Can you transfer money to my friend?")
    assert decision.intent == "unsupported"
