from app.models.assistant import AssistantResponse, ExecutionStep
from app.services.banking_service import BankingService


class RecentTransactionsWorkflow:
    def __init__(self, banking: BankingService) -> None:
        self.banking = banking

    def run(self, customer_id: str, limit: int = 5) -> AssistantResponse:
        transactions = self.banking.get_transactions(customer_id, limit=limit)
        lines = []
        for txn in transactions:
            sign = "+" if txn.direction == "credit" else "-"
            lines.append(f"{txn.date:%d %b}: {txn.merchant} {sign}£{txn.amount:,.2f}")

        return AssistantResponse(
            answer="Your most recent transactions are:\n" + "\n".join(lines),
            intent="recent_transactions",
            data={"transactions": [t.model_dump(mode="json") for t in transactions]},
            execution_steps=[
                ExecutionStep(step="route", detail="Selected recent transactions workflow."),
                ExecutionStep(step="scope", detail="Applied the authenticated customer scope."),
                ExecutionStep(step="data", detail=f"Requested the customer's {limit} latest transactions."),
                ExecutionStep(step="format", detail="Formatted transactions in reverse chronological order."),
            ],
        )
