from app.database import Database
from app.models.auth import StoredCustomer


class CustomerRepository:
    """Persistence adapter for customer authentication records."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def find_by_username(self, username: str) -> StoredCustomer | None:
        sql = """
            SELECT
                customer_id,
                username,
                display_name,
                password_salt,
                password_hash,
                password_iterations
            FROM customers
            WHERE username = ?
        """
        with self.database.connect() as connection:
            row = connection.execute(sql, (username,)).fetchone()

        if row is None:
            return None
        return StoredCustomer.model_validate(dict(row))
