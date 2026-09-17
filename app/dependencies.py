"""Application dependency wiring.

Stage 1B keeps object construction separate from business logic so the same
services can be wired to an isolated temporary SQLite database in tests.
"""

from app.database import Database
from app.repositories import BankingRepository, CustomerRepository
from app.services import AuthService, BankingService, SessionService
from app.workflows import AssistantWorkflow


database = Database()
customer_repository = CustomerRepository(database)
banking_repository = BankingRepository(database)

auth_service = AuthService(customer_repository)
banking_service = BankingService(banking_repository)
session_service = SessionService()
assistant_workflow = AssistantWorkflow(banking_service)
