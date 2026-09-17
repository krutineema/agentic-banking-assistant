def test_authenticate_known_demo_customer(auth):
    customer = auth.authenticate("demo.alex", "Banking123!")
    assert customer is not None
    assert customer.customer_id == "cust-001"


def test_reject_invalid_password(auth):
    assert auth.authenticate("demo.alex", "wrong") is None
