from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.models.assistant import AssistantRequest, AssistantResponse
from app.models.auth import AuthenticatedCustomer, LoginRequest
from app.services.auth_service import AuthService
from app.services.banking_service import BankingService
from app.services.session_service import SessionService
from app.workflows.assistant_workflow import AssistantWorkflow


router = APIRouter(prefix="/api")
banking = BankingService()
auth = AuthService()
sessions = SessionService()
assistant = AssistantWorkflow(banking=banking)

SESSION_COOKIE = "northstar_session"


def require_customer(
    northstar_session: str | None = Cookie(default=None),
) -> AuthenticatedCustomer:
    customer = sessions.get(northstar_session)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return customer


@router.post("/auth/login", response_model=AuthenticatedCustomer)
def login(request: LoginRequest, response: Response) -> AuthenticatedCustomer:
    customer = auth.authenticate(request.username, request.password)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    session_token = sessions.create(customer)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False,  # Local HTTP demo. Production would require HTTPS + Secure cookies.
        max_age=60 * 60,
    )
    return customer


@router.get("/auth/session", response_model=AuthenticatedCustomer)
def get_session(customer: AuthenticatedCustomer = Depends(require_customer)) -> AuthenticatedCustomer:
    return customer


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    northstar_session: str | None = Cookie(default=None),
) -> None:
    sessions.delete(northstar_session)
    response.delete_cookie(SESSION_COOKIE)


@router.get("/accounts")
def list_accounts(customer: AuthenticatedCustomer = Depends(require_customer)):
    return [
        account.model_dump(mode="json")
        for account in banking.get_accounts(customer.customer_id)
    ]


@router.get("/transactions")
def list_transactions(
    limit: int = 8,
    customer: AuthenticatedCustomer = Depends(require_customer),
):
    transactions = banking.get_transactions(
        customer.customer_id,
        limit=min(max(limit, 1), 50),
    )
    return [transaction.model_dump(mode="json") for transaction in transactions]


@router.post("/assistant/message", response_model=AssistantResponse)
def assistant_message(
    request: AssistantRequest,
    customer: AuthenticatedCustomer = Depends(require_customer),
) -> AssistantResponse:
    return assistant.handle(customer.customer_id, request.message)
