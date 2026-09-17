def test_schema_and_seed_create_expected_records(database):
    with database.connect() as connection:
        customers = connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        accounts = connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        transactions = connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]

    assert customers == 2
    assert accounts == 5
    assert transactions == 17


def test_database_initialization_is_idempotent(database):
    database.initialize()
    with database.connect() as connection:
        assert connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 2
