# ADR 0002 — Establish customer session and data isolation in Stage 1

## Status

Accepted.

## Context

The banking assistant will eventually use LLM tools, Text-to-SQL, RAG and possibly multiple agents. Every one of those capabilities must operate inside the identity and authorisation boundary of the authenticated banking customer.

If customer scoping were added only when agents are introduced, early code and tests could accidentally assume globally accessible banking data. That would create the wrong architecture to build on.

## Decision

Stage 1 includes authentication and a customer session even though the assistant itself is still deterministic.

- The demo has known synthetic users; there is no signup workflow.
- Passwords are stored as salted PBKDF2 hashes rather than plaintext.
- Successful login creates an opaque random server-side session token.
- The browser receives only that token in an HttpOnly cookie.
- Protected API endpoints derive `customer_id` from the authenticated session.
- `customer_id` is passed explicitly into every banking-service and assistant-workflow data request.
- The service determines account ownership and only returns transactions for accounts owned by that customer.
- The UI never supplies `customer_id` as an authority signal.

## Current limitations

This is a local learning implementation, not production authentication:

- sessions are held in memory and disappear when the app restarts;
- there is no MFA, lockout, password reset, CSRF framework, external IdP or session revocation store;
- the cookie is not marked `Secure` because the demo normally runs over local HTTP.

These limitations are deliberate. Later architecture can replace the authentication/session implementation without changing the rule that all banking access is derived from authenticated customer context.

## Why this matters later

The same identity boundary must flow into:

- LLM tool calls;
- RAG access where documents are customer/segment specific;
- Text-to-SQL query execution and row-level/customer-scope enforcement;
- transfer preparation and approval;
- audit logs and observability;
- any multi-agent hand-offs.

The agent must never be trusted to invent or select the customer identity.
