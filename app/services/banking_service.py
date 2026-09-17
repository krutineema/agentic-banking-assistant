from datetime import date
from decimal import Decimal

from app.models.banking import Account, Transaction
from app.repositories import BankingRepository


class BankingService:
    """Application/service boundary over banking persistence.

    Workflows and API routes depend on this service exactly as they did in
    Stage 1A. Stage 1B changes the implementation beneath the boundary from
    JSON loading to a repository backed by SQLite.
    """

    def __init__(self, repository: BankingRepository) -> None:
        self.repository = repository

    def get_accounts(self, customer_id: str) -> list[Account]:
        return self.repository.get_accounts(customer_id)

    def get_account(self, customer_id: str, account_id: str) -> Account | None:
        return self.repository.get_account(customer_id, account_id)

    def get_transactions(
        self,
        customer_id: str,
        *,
        account_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        category: str | None = None,
        limit: int | None = None,
    ) -> list[Transaction]:
        return self.repository.get_transactions(
            customer_id,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit,
        )

    def debit_total(
        self,
        customer_id: str,
        *,
        start_date: date,
        end_date: date,
        category: str | None = None,
        account_id: str | None = None,
    ) -> Decimal:
        return self.repository.debit_total(
            customer_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            account_id=account_id,
        )
