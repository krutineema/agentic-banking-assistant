from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


AccountType = Literal["current", "savings", "credit"]
TransactionDirection = Literal["debit", "credit"]


class Account(BaseModel):
    id: str
    customer_id: str
    name: str
    type: AccountType
    balance: Decimal
    currency: str = "GBP"


class Transaction(BaseModel):
    id: str
    account_id: str
    date: date
    merchant: str
    amount: Decimal
    direction: TransactionDirection
    category: str
    description: str
