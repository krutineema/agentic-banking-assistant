from app.models.assistant import AssistantResponse, ExecutionStep
from app.services.banking_service import BankingService


class AccountBalanceWorkflow:
    def __init__(self, banking: BankingService) -> None:
        self.banking = banking

    def run(self, customer_id: str) -> AssistantResponse:
        accounts = self.banking.get_accounts(customer_id)
        lines = [f"{a.name}: £{a.balance:,.2f}" for a in accounts]

        return AssistantResponse(
            answer="Here are your account balances:\n" + "\n".join(lines),
            intent="account_balance",
            data={"accounts": [a.model_dump(mode="json") for a in accounts]},
            execution_steps=[
                ExecutionStep(step="route", detail="Selected account balance workflow."),
                ExecutionStep(step="scope", detail="Applied the authenticated customer scope."),
                ExecutionStep(step="data", detail="Loaded the customer's accounts from the banking service."),
                ExecutionStep(step="format", detail="Formatted account balances for the customer."),
            ],
        )
