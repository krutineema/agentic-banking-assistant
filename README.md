# Personal Banking Assistant

An evolving **AI application architecture learning project** that starts with a conventional, deterministic banking application and incrementally introduces agentic capabilities only when they solve a demonstrated problem.

The end goal is a fictional but enterprise-style personal banking assistant embedded in a banking web/mobile experience. The project will eventually cover LLM tool calling, conversational state, planning, human approval, guardrails, RAG, controlled Text-to-SQL, MCP, LangGraph, evaluation/observability, and a single-agent vs multi-agent architecture comparison.

> **Current milestone:** Stage 1A — customer-scoped deterministic workflows  
> **Recommended snapshot tag:** `stage-1a`  
> **Next:** Stage 1B — SQLite + repository/data-access boundary

## Why the project starts without an agent

The first architectural question is not “Which agent framework should we use?” It is:

> **Does this task need an agent at all?**

Stage 1 deliberately uses explicit control flow and deterministic workflows. This gives the project a baseline that later agentic implementations can be compared against.

```text
Login
  ↓
Authenticated customer session
  ↓
Customer request
  ↓
Deterministic intent router
  ↓
Selected workflow
  ↓
Customer-scoped BankingService
  ↓
Synthetic banking data
  ↓
Deterministic response
```

There is **no LLM in Stage 1A**.

## Current Stage 1A capabilities

The application currently includes:

- a small banking-style web UX;
- login with known synthetic customers;
- server-side customer sessions referenced by an HttpOnly cookie;
- customer-specific accounts and transactions;
- backend-enforced customer isolation;
- account-balance workflow;
- recent-transactions workflow;
- spending-summary workflow;
- deterministic intent routing;
- an execution-trace panel showing safe workflow steps;
- automated tests including cross-customer isolation.

### Demo users

```text
demo.alex / Banking123!
demo.sam  / Banking456!
```

There is deliberately no signup workflow.

## Repository strategy

This is a learning repository, but it is kept as **one evolving application**, not a set of copied stage folders.

```text
main branch
    → current / most advanced implementation

Git tags
    → exact runnable snapshot of completed milestones

docs/stages/
    → what was built, why it changed and what was learned

experiments/
    → focused comparisons when two real architectural approaches exist
```

For example:

| Milestone | Architecture change | Snapshot |
|---|---|---|
| Stage 1A | Deterministic workflows + authenticated customer session | `stage-1a` |
| Stage 1B | SQLite + repository/data-access layer | `stage-1b` |
| Stage 2 | LLM tool calling / first agent | `stage-2` |
| Stage 3 | Conversational state | `stage-3` |
| Later stages | See `DEVELOPMENT_PHASES.md` | `stage-N` |

The detailed plan lives in [`DEVELOPMENT_PHASES.md`](DEVELOPMENT_PHASES.md). The completed Stage 1A milestone is documented in [`docs/stages/stage1.md`](docs/stages/stage1.md).

## When experiments begin

We do **not** create empty experiment folders in advance. An experiment is added only when two implemented approaches can be meaningfully compared.

Planned comparison points include:

| Stage | Experiment | Comparison |
|---|---|---|
| Stage 2 | `workflow-vs-agent` | deterministic workflow routing vs LLM tool selection |
| Stage 8 | `api-vs-text-to-sql` | known business tools vs controlled Text-to-SQL analytics |
| Stage 9 | `direct-tools-vs-mcp` | direct tool integration vs MCP |
| Stage 10 | `raw-vs-langgraph` | hand-written orchestration vs LangGraph |
| Stage 12 | `single-vs-multi-agent` | one capable agent vs specialist agents |

These experiment folders should contain focused scenarios, comparison harnesses, results and findings — **not full copies of historical application code**. Historical code is preserved by Git tags.

## Stage 1A structure

```text
agentic-banking-assistant/
├── app/
│   ├── api/                 # FastAPI routes / controller boundary
│   ├── core/                # deterministic intent router
│   ├── data/                # temporary synthetic JSON persistence
│   ├── models/              # Pydantic domain/API schemas
│   ├── services/            # auth, session and banking service boundaries
│   ├── static/              # banking-style UX
│   ├── workflows/           # deterministic banking workflows
│   └── main.py              # application bootstrap / composition root
├── docs/
│   ├── adr/                 # architecture decision records
│   └── stages/
│       └── stage1.md        # completed Stage 1A learning record
├── tests/
├── DEVELOPMENT_PHASES.md
├── README.md
└── requirements.txt
```

## Key Stage 1A boundaries

### Customer identity is established before banking access

The browser does not submit `customer_id` as an authority signal. Login creates a server-side session and protected API requests derive the authenticated customer from that session.

```text
Session cookie
     ↓
require_customer
     ↓
AuthenticatedCustomer
     ↓ customer_id
workflow / banking service
```

This rule will remain important when LLM tools, Text-to-SQL, RAG and multiple agents are introduced.

### The assistant is another consumer of banking capabilities

The normal dashboard and the assistant both use the banking service rather than the assistant becoming the banking backend itself.

```text
Traditional banking UX ─────┐
                            ├── BankingService → persistence
Assistant workflows ────────┘
```

### Persistence is intentionally temporary

Stage 1A reads synthetic data from JSON files only to keep the first learning problem focused on workflow design and customer isolation.

Stage 1B replaces:

```text
BankingService → JSON
```

with:

```text
BankingService → Repository → SQLite
```

The layers above the service boundary should change very little.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- Banking UX: `http://127.0.0.1:8000`
- FastAPI docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

Run tests:

```bash
pytest -q
```

## Try these Stage 1A requests

After logging in:

```text
What are my balances?
Show my recent transactions
How much did I spend in August?
How much did I spend eating out in August?
How much did I spend on groceries last month?
```

A request such as:

```text
Transfer £100 to savings
```

is deliberately unsupported at this stage. Controlled write actions and explicit human approval are introduced later.

## Suggested code-reading order

If you are studying the implementation, follow this path:

1. `app/models/`
2. `app/data/`
3. `app/services/auth_service.py`
4. `app/services/session_service.py`
5. `app/services/banking_service.py`
6. `app/core/router.py`
7. `app/workflows/assistant_workflow.py`
8. individual workflows such as `spending_summary.py`
9. `app/api/routes.py`
10. `app/static/app.js`
11. `tests/`

The most important Stage 1 learning distinction is:

```text
router.py
natural language → intent

assistant_workflow.py
intent → selected deterministic workflow
```

Later stages will deliberately challenge and evolve these boundaries.

## Architecture documentation

- [`DEVELOPMENT_PHASES.md`](DEVELOPMENT_PHASES.md) — forward-looking canonical architecture and development plan
- [`docs/stages/stage1.md`](docs/stages/stage1.md) — historical Stage 1A implementation and learning record
- `docs/adr/` — individual architecture decisions

## Next milestone

**Stage 1B: relational persistence.**

The next change introduces SQLite and a repository/data-access layer while preserving the existing UX, authentication, deterministic workflow behaviour and customer-isolation rules.
