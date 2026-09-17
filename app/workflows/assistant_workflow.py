from datetime import date

from app.core.router import IntentRouter
from app.models.assistant import AssistantResponse, ExecutionStep
from app.services.banking_service import BankingService
from app.workflows.account_balance import AccountBalanceWorkflow
from app.workflows.recent_transactions import RecentTransactionsWorkflow
from app.workflows.spending_summary import SpendingSummaryWorkflow


class AssistantWorkflow:
    """Stage 1 orchestrator: fixed routes, fixed workflows, no model autonomy."""

    def __init__(
        self,
        banking: BankingService,
        router: IntentRouter | None = None,
        today: date | None = None,
    ) -> None:
        self.banking = banking
        self.router = router or IntentRouter()
        self.today = today

    def handle(self, customer_id: str, message: str) -> AssistantResponse:
        decision = self.router.route(message)

        if decision.intent == "account_balance":
            response = AccountBalanceWorkflow(self.banking).run(customer_id)
        elif decision.intent == "recent_transactions":
            response = RecentTransactionsWorkflow(self.banking).run(customer_id)
        elif decision.intent == "spending_summary":
            response = SpendingSummaryWorkflow(self.banking, today=self.today).run(customer_id, message)
        else:
            response = AssistantResponse(
                answer=(
                    "I can't handle that request in Stage 1 yet. Try asking for account balances, "
                    "recent transactions, or a spending summary."
                ),
                intent="unsupported",
                execution_steps=[
                    ExecutionStep(step="route", detail="No supported deterministic workflow matched."),
                ],
            )

        response.execution_steps.insert(
            0,
            ExecutionStep(step="router", detail=decision.reason),
        )
        return response
