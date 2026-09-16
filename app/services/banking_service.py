import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.models.banking import Account, Transaction


class BankingService:
    """Read-only facade over synthetic banking data, scoped by customer.

    Every public data-access method requires ``customer_id``. That makes customer
    isolation a backend invariant rather than a browser/UI convention. When JSON
    is replaced by a relational database, this same boundary will enforce the
    authenticated customer's scope in repository/query calls.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(__file__).resolve().parents[1] / "data"
        self._accounts = self._load_accounts()
        self._transactions = self._load_transactions()

    def _load_accounts(self) -> list[Account]:
        payload = json.loads((self.data_dir / "accounts.json").read_text())
        return [Account.model_validate(item) for item in payload]

    def _load_transactions(self) -> list[Transaction]:
        payload = json.loads((self.data_dir / "transactions.json").read_text())
        return [Transaction.model_validate(item) for item in payload]

    def get_accounts(self, customer_id: str) -> list[Account]:
        return [a for a in self._accounts if a.customer_id == customer_id]

    def get_account(self, customer_id: str, account_id: str) -> Account | None:
        return next(
            (a for a in self._accounts if a.customer_id == customer_id and a.id == account_id),
            None,
        )

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
        owned_account_ids = {a.id for a in self.get_accounts(customer_id)}

        # An explicitly requested account must belong to the authenticated customer.
        if account_id and account_id not in owned_account_ids:
            return []

        transactions = [t for t in self._transactions if t.account_id in owned_account_ids]

        if account_id:
            transactions = [t for t in transactions if t.account_id == account_id]
        if start_date:
            transactions = [t for t in transactions if t.date >= start_date]
        if end_date:
            transactions = [t for t in transactions if t.date <= end_date]
        if category:
            transactions = [t for t in transactions if t.category == category.lower()]

        transactions = sorted(transactions, key=lambda item: item.date, reverse=True)
        return transactions[:limit] if limit else transactions

    def debit_total(
        self,
        customer_id: str,
        *,
        start_date: date,
        end_date: date,
        category: str | None = None,
        account_id: str | None = None,
    ) -> Decimal:
        transactions = self.get_transactions(
            customer_id,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
        )
        return sum(
            (t.amount for t in transactions if t.direction == "debit"),
            start=Decimal("0"),
        )
