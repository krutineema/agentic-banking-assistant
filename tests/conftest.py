from datetime import date

import pytest

from app.database import Database
from app.repositories import BankingRepository, CustomerRepository
from app.services import AuthService, BankingService
from app.workflows import AssistantWorkflow


@pytest.fixture
def database(tmp_path):
    db = Database(tmp_path / "test-banking.db")
    db.initialize()
    return db


@pytest.fixture
def banking(database):
    return BankingService(BankingRepository(database))


@pytest.fixture
def auth(database):
    return AuthService(CustomerRepository(database))


@pytest.fixture
def workflow(banking):
    return AssistantWorkflow(banking, today=date(2026, 9, 15))
