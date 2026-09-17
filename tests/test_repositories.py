from datetime import date

from app.repositories import BankingRepository, CustomerRepository


def test_customer_repository_reads_customer_from_sqlite(database):
    customer = CustomerRepository(database).find_by_username("demo.alex")
    assert customer is not None
    assert customer.customer_id == "cust-001"


def test_cross_customer_account_access_is_blocked_in_sql(database):
    repository = BankingRepository(database)
    assert repository.get_account("cust-001", "acc-current-002") is None
    assert repository.get_transactions("cust-001", account_id="acc-current-002") == []


def test_repository_aggregates_customer_scoped_spending(database):
    repository = BankingRepository(database)
    alex = repository.debit_total(
        "cust-001",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
        category="restaurants",
    )
    sam = repository.debit_total(
        "cust-002",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
        category="restaurants",
    )
    assert str(alex) == "69.60"
    assert str(sam) == "25.00"
