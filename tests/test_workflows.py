ALEX = "cust-001"
SAM = "cust-002"


def test_balance_workflow_returns_only_customer_accounts(workflow):
    response = workflow.handle(ALEX, "What are my balances?")
    assert response.intent == "account_balance"
    assert len(response.data["accounts"]) == 3
    assert {a["customer_id"] for a in response.data["accounts"]} == {ALEX}


def test_august_restaurant_spending_is_deterministic_and_customer_scoped(workflow):
    alex = workflow.handle(ALEX, "How much did I spend eating out in August?")
    sam = workflow.handle(SAM, "How much did I spend eating out in August?")
    assert alex.data["total"] == "69.60"
    assert sam.data["total"] == "25.00"


def test_recent_transactions_are_customer_scoped(workflow):
    response = workflow.handle(SAM, "Show recent transactions")
    account_ids = {txn["account_id"] for txn in response.data["transactions"]}
    assert account_ids <= {"acc-current-002", "acc-savings-002"}


def test_transfer_remains_unsupported(workflow):
    assert workflow.handle(ALEX, "Transfer £100 to savings").intent == "unsupported"
