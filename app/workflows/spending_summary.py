from datetime import date

from app.models.assistant import AssistantResponse, ExecutionStep
from app.services.banking_service import BankingService
from app.workflows.date_utils import infer_month_range


KNOWN_CATEGORIES = {
    "groceries": ("grocery", "groceries", "supermarket"),
    "restaurants": ("restaurant", "restaurants", "eating out", "dining", "food out"),
    "transport": ("transport", "fuel", "petrol", "travel"),
    "subscriptions": ("subscription", "subscriptions"),
}


def infer_category(message: str) -> str | None:
    text = message.lower()
    for category, aliases in KNOWN_CATEGORIES.items():
        if any(alias in text for alias in aliases):
            return category
    return None


class SpendingSummaryWorkflow:
    def __init__(self, banking: BankingService, today: date | None = None) -> None:
        self.banking = banking
        self.today = today or date.today()

    def run(self, customer_id: str, message: str) -> AssistantResponse:
        start_date, end_date, period_label = infer_month_range(message, self.today)
        category = infer_category(message)
        total = self.banking.debit_total(
            customer_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
        )
        matching = self.banking.get_transactions(
            customer_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
        )
        debits = [t for t in matching if t.direction == "debit"]

        category_text = f" on {category}" if category else ""
        answer = f"You spent £{total:,.2f}{category_text} in {period_label}."
        if debits:
            answer += f" I found {len(debits)} matching debit transaction(s)."

        return AssistantResponse(
            answer=answer,
            intent="spending_summary",
            data={
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
                "category": category,
                "total": str(total),
                "transactions": [t.model_dump(mode="json") for t in debits],
            },
            execution_steps=[
                ExecutionStep(step="route", detail="Selected spending summary workflow."),
                ExecutionStep(step="scope", detail="Applied the authenticated customer scope."),
                ExecutionStep(
                    step="interpret",
                    detail=f"Resolved period to {period_label} and category to {category or 'all spending'}.",
                ),
                ExecutionStep(step="data", detail="Retrieved the customer's matching debit transactions."),
                ExecutionStep(step="calculate", detail="Summed debit amounts deterministically."),
                ExecutionStep(step="format", detail="Rendered a customer-readable summary."),
            ],
        )
