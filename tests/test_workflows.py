from datetime import date

from app.services.banking_service import BankingService
from app.workflows.assistant_workflow import AssistantWorkflow


ALEX = "cust-001"
SAM = "cust-002"


def workflow() -> AssistantWorkflow:
    return AssistantWorkflow(
        banking=BankingService(),
        today=date(2026, 9, 15),
    )


def test_balance_workflow_returns_only_customer_accounts():
    response = workflow().handle(ALEX, "What are my balances?")
    assert response.intent == "account_balance"
    assert len(response.data["accounts"]) == 3
    assert {a["customer_id"] for a in response.data["accounts"]} == {ALEX}


def test_august_restaurant_spending_is_deterministic_and_customer_scoped():
    alex = workflow().handle(ALEX, "How much did I spend eating out in August?")
    sam = workflow().handle(SAM, "How much did I spend eating out in August?")

    assert alex.intent == "spending_summary"
    assert alex.data["category"] == "restaurants"
    assert alex.data["total"] == "69.60"
    assert sam.data["total"] == "25.00"


def test_recent_transactions_are_customer_scoped():
    response = workflow().handle(SAM, "Show recent transactions")
    account_ids = {txn["account_id"] for txn in response.data["transactions"]}
    assert response.intent == "recent_transactions"
    assert account_ids <= {"acc-current-002", "acc-savings-002"}


def test_transfer_is_not_supported_in_stage_one():
    response = workflow().handle(ALEX, "Transfer £100 to savings")
    assert response.intent == "unsupported"


def test_banking_service_rejects_cross_customer_account_access():
    banking = BankingService()
    assert banking.get_account(ALEX, "acc-current-002") is None
    assert banking.get_transactions(ALEX, account_id="acc-current-002") == []
