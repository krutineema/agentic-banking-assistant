# Stage 1B review against the real GitHub repository

The connected GitHub repository was inspected before regenerating this update.

## Confirmed current Stage 1A state

- `BankingService` currently reads `accounts.json` and `transactions.json` directly.
- `AuthService` currently reads `customers.json` directly.
- `routes.py` constructs `BankingService`, `AuthService`, `SessionService` and `AssistantWorkflow` as module globals.
- customer scoping is already enforced in the Stage 1A service boundary.
- current tests include authenticated session isolation and cross-customer access checks.
- the repository also contains `requirements-dev.txt` and `scripts/print_trace_path.py` for VizTracer-based local tracing.

## Stage 1B change

```text
Stage 1A
BankingService → JSON
AuthService    → customers.json

Stage 1B
BankingService → BankingRepository  → SQLite
AuthService    → CustomerRepository → SQLite
```

Application dependency construction moves to `app/dependencies.py`.

## Additional correction made during real-repo validation

The first Stage 1B draft converted integer pence using Decimal division, which produced values such as `Decimal("69.6")`. Stage 1A exposes the same value as `"69.60"` in assistant response metadata. The repository conversion now quantizes to `Decimal("0.01")`, preserving the Stage 1A API/data representation rather than changing it accidentally.

## Tests

The regenerated package passes **19 tests**.
