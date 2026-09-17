from datetime import date
from decimal import Decimal

from app.database import Database
from app.models.banking import Account, Transaction


PENCE = Decimal("100")
PENNY = Decimal("0.01")


def _from_pence(value: int) -> Decimal:
    """Convert exact integer pence to a two-decimal Decimal amount."""
    return (Decimal(value) / PENCE).quantize(PENNY)


class BankingRepository:
    """SQLite data-access layer for customer-scoped banking data.

    Customer ownership is enforced in SQL. A caller cannot fetch another
    customer's account or transaction merely by supplying its identifier.
    """

    def __init__(self, database: Database) -> None:
        self.database = database

    def get_accounts(self, customer_id: str) -> list[Account]:
        sql = """
            SELECT account_id, customer_id, account_name, account_type,
                   balance_pence, currency
            FROM accounts
            WHERE customer_id = ?
            ORDER BY account_id
        """
        with self.database.connect() as connection:
            rows = connection.execute(sql, (customer_id,)).fetchall()
        return [self._account_from_row(row) for row in rows]

    def get_account(self, customer_id: str, account_id: str) -> Account | None:
        sql = """
            SELECT account_id, customer_id, account_name, account_type,
                   balance_pence, currency
            FROM accounts
            WHERE customer_id = ? AND account_id = ?
        """
        with self.database.connect() as connection:
            row = connection.execute(sql, (customer_id, account_id)).fetchone()
        return self._account_from_row(row) if row else None

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
        clauses = ["a.customer_id = ?"]
        parameters: list[object] = [customer_id]

        if account_id:
            clauses.append("t.account_id = ?")
            parameters.append(account_id)
        if start_date:
            clauses.append("t.transaction_date >= ?")
            parameters.append(start_date.isoformat())
        if end_date:
            clauses.append("t.transaction_date <= ?")
            parameters.append(end_date.isoformat())
        if category:
            clauses.append("t.category = ?")
            parameters.append(category.lower())

        sql = f"""
            SELECT
                t.transaction_id,
                t.account_id,
                t.transaction_date,
                t.merchant,
                t.amount_pence,
                t.direction,
                t.category,
                t.description
            FROM transactions t
            JOIN accounts a ON a.account_id = t.account_id
            WHERE {' AND '.join(clauses)}
            ORDER BY t.transaction_date DESC, t.transaction_id DESC
        """

        if limit is not None:
            sql += " LIMIT ?"
            parameters.append(limit)

        with self.database.connect() as connection:
            rows = connection.execute(sql, parameters).fetchall()
        return [self._transaction_from_row(row) for row in rows]

    def debit_total(
        self,
        customer_id: str,
        *,
        start_date: date,
        end_date: date,
        category: str | None = None,
        account_id: str | None = None,
    ) -> Decimal:
        clauses = [
            "a.customer_id = ?",
            "t.direction = 'debit'",
            "t.transaction_date >= ?",
            "t.transaction_date <= ?",
        ]
        parameters: list[object] = [
            customer_id,
            start_date.isoformat(),
            end_date.isoformat(),
        ]

        if category:
            clauses.append("t.category = ?")
            parameters.append(category.lower())
        if account_id:
            clauses.append("t.account_id = ?")
            parameters.append(account_id)

        sql = f"""
            SELECT COALESCE(SUM(t.amount_pence), 0) AS total_pence
            FROM transactions t
            JOIN accounts a ON a.account_id = t.account_id
            WHERE {' AND '.join(clauses)}
        """
        with self.database.connect() as connection:
            row = connection.execute(sql, parameters).fetchone()
        return _from_pence(row["total_pence"])

    @staticmethod
    def _account_from_row(row) -> Account:
        return Account(
            id=row["account_id"],
            customer_id=row["customer_id"],
            name=row["account_name"],
            type=row["account_type"],
            balance=_from_pence(row["balance_pence"]),
            currency=row["currency"],
        )

    @staticmethod
    def _transaction_from_row(row) -> Transaction:
        return Transaction(
            id=row["transaction_id"],
            account_id=row["account_id"],
            date=row["transaction_date"],
            merchant=row["merchant"],
            amount=_from_pence(row["amount_pence"]),
            direction=row["direction"],
            category=row["category"],
            description=row["description"],
        )
