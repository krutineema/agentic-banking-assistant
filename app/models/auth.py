from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class AuthenticatedCustomer(BaseModel):
    customer_id: str
    username: str
    display_name: str


class StoredCustomer(AuthenticatedCustomer):
    password_salt: str
    password_hash: str
    password_iterations: int
