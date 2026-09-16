# Personal Banking Assistant — Development Design and Phase Plan

> **Purpose of this document**  
> This is the canonical hand-off document for the project. It captures the product vision, architectural decisions, current implementation state, future phases, security boundaries and the reason each capability is being introduced. Attach this file when starting a new chat about a later stage so the project can continue without relying on prior conversation history.
>
> The repository itself always contains the **current implementation**. Completed runnable milestones are preserved using annotated Git tags, while `docs/stages/` records what was built and learned at each milestone. Comparative implementations live under `experiments/` only when there are two real approaches worth comparing; empty speculative experiment folders are not created in advance.

---

## 1. Project vision

Build a fictional but enterprise-style **Personal Banking Assistant** embedded in a banking web/mobile experience.

The project is primarily an **AI architecture learning project**, not an attempt to build a production bank. The visible product should nevertheless feel coherent enough that an interviewer or reviewer can understand how an AI assistant would sit inside a real digital-banking application.

A logged-in customer should eventually be able to:

- view and understand balances and transactions;
- search for specific payments;
- analyse spending over flexible periods and categories;
- ask questions about banking policies, fees and product rules;
- ask broader analytical questions that may require Text-to-SQL;
- perform selected banking actions such as transfers;
- explicitly approve sensitive actions before execution;
- continue multi-turn tasks using controlled conversational state;
- receive useful failure handling when tools or backends fail;
- receive grounded, auditable responses rather than opaque autonomous behaviour.

All users, accounts, transactions, documents and banking services are synthetic.

---

## 2. Core architectural principles

These principles should remain true as the project evolves.

### 2.1 Customer identity exists before AI reasoning

The authenticated customer is established by the application/session layer. The LLM or agent must **never choose, invent or override `customer_id`**.

```text
Browser
  ↓
Login
  ↓
Authenticated server-side session
  ↓
Customer context
  ↓
Assistant / tools / workflows
```

Every banking capability receives customer context from the trusted application boundary.

### 2.2 Customer isolation is a backend invariant

Data isolation must not depend on the UI filtering results correctly.

```text
Authenticated customer
        ↓
Customer-scoped service / repository / query policy
        ↓
Only that customer's banking data
```

Later this same rule applies to tool calls, Text-to-SQL, RAG, transfers, traces and multi-agent hand-offs.

### 2.3 Known operations should use controlled APIs/tools

Normal banking operations should use explicit business capabilities such as:

```text
get_accounts()
get_balance()
search_transactions()
prepare_transfer()
execute_transfer()
```

An LLM should not generate raw SQL for operations already represented by safe application APIs.

### 2.4 Text-to-SQL is for flexible analytical access, not unrestricted database access

For open-ended analytical questions, the assistant may generate SQL, but it does not get a general-purpose database connection.

```text
Natural-language analytical question
        ↓
Text-to-SQL capability
        ↓
SQL validation / policy enforcement
        ↓
Controlled read-only query service
        ↓
Banking database
```

Writes are never performed through Text-to-SQL.

### 2.5 Sensitive writes remain deterministic and approval-gated

For example:

```text
"Move £250 to savings"
        ↓
Agent decides which business capability is needed
        ↓
prepare_transfer(...)
        ↓
Business validation + risk checks
        ↓
Human approval
        ↓
execute_transfer(...)
```

The LLM can request a business action. It cannot directly mutate account balances.

### 2.6 Introduce complexity only when it solves a demonstrated problem

The project deliberately starts with deterministic workflows, then introduces an agent, planning, frameworks and possibly multiple agents only after their value can be compared against a simpler baseline.

### 2.7 Evaluation and observability are architectural features

We should be able to see and test:

- which workflow/tool was selected;
- which arguments were passed;
- what data source was used;
- whether approval was required;
- whether customer scope was preserved;
- whether a request succeeded or failed safely;
- latency and model/tool usage where relevant.

Do not expose private model chain-of-thought. Store safe execution metadata and explicit decisions instead.

---

## 3. Target logical architecture

The final project may evolve, but the intended capability boundaries are approximately:

```text
                         ┌─────────────────────────┐
                         │ Banking Web / Mobile UX │
                         │ Login + Assistant       │
                         └────────────┬────────────┘
                                      │
                         Authenticated customer
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Assistant API / Session │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Orchestration / Agent   │
                         │ routing · state · plan  │
                         └────────────┬────────────┘
                                      │
              ┌───────────────────────┼────────────────────────┐
              │                       │                        │
              ▼                       ▼                        ▼
    ┌──────────────────┐   ┌─────────────────────┐   ┌──────────────────┐
    │ Banking tools    │   │ Insights capability │   │ Knowledge / RAG  │
    │ known operations │   │ Text-to-SQL          │   │ policies / FAQs  │
    └────────┬─────────┘   └──────────┬──────────┘   └──────────────────┘
             │                        │
             ▼                        ▼
    ┌──────────────────┐   ┌─────────────────────┐
    │ Banking service  │   │ SQL policy + query  │
    │ business rules   │   │ read-only execution │
    └────────┬─────────┘   └──────────┬──────────┘
             │                        │
             └────────────┬───────────┘
                          ▼
                   ┌──────────────┐
                   │ Banking DB   │
                   └──────────────┘
```

Later we will test whether the orchestration layer should remain one agent with capability families or be decomposed into specialist agents.

---

## 4. Current implementation status

### Current stage: **Stage 1A — Deterministic workflow baseline with customer session**

This is the first milestone intended to be preserved as a Git snapshot before Stage 1B begins. The historical write-up for this milestone lives at `docs/stages/stage1.md`. Recommended tag: `stage-1a`.

Implemented now:

- FastAPI backend;
- banking-style web UI;
- login screen with two known synthetic users;
- salted PBKDF2 password hashes;
- opaque server-side session token in an HttpOnly cookie;
- no signup workflow;
- customer identity derived from the authenticated session;
- customer-specific synthetic accounts and transactions;
- backend-enforced account ownership and transaction isolation;
- deterministic keyword intent router;
- account-balance workflow;
- recent-transactions workflow;
- spending-summary workflow;
- execution-trace panel;
- automated tests including cross-customer isolation.

Current demo credentials:

```text
demo.alex / Banking123!
demo.sam  / Banking456!
```

Current persistence:

```text
customers.json
accounts.json
transactions.json
```

JSON is temporary bootstrap persistence. It is **not** the intended end state.

Current high-level flow:

```text
Login
  ↓
Server-side customer session
  ↓
Message
  ↓
Deterministic router
  ↓
Fixed workflow
  ↓
Customer-scoped BankingService
  ↓
JSON data
  ↓
Deterministic response
```

### Stage 1A design decisions

1. Authentication exists from the beginning so later AI capabilities inherit the correct identity boundary.
2. The browser never sends `customer_id` as the authority for data access.
3. `BankingService` requires `customer_id` for every data operation.
4. Transactions are scoped by the accounts owned by that customer.
5. The assistant is not yet an agent; no LLM is involved.
6. Transfers are deliberately unsupported.

### Stage 1A limitations

The authentication implementation is educational rather than production-ready:

- sessions are in memory and vanish when the application restarts;
- no MFA;
- no lockout/rate-limiting policy;
- no password-reset flow;
- no external identity provider;
- local HTTP means the demo cookie is not marked `Secure`;
- persistence is still JSON.

These are acceptable for the current learning objective because the important architectural boundary — authenticated customer context before banking access — already exists.

---

# 5. Development phases

## Stage 1B — Replace JSON with a local relational banking database

### Primary learning question

**Can we introduce realistic relational persistence without changing the workflow/assistant layers?**

### Why this phase exists

The finished project needs relational data for:

- realistic banking relationships;
- joins and aggregations;
- future Text-to-SQL experiments;
- query-policy/customer-scope enforcement;
- future transfer transactions;
- a clearer separation between domain services and persistence.

### Build

Use **SQLite** as the local development database.

Initial logical schema:

```text
customers
---------
customer_id PK
username
password_hash
password_salt
password_iterations
display_name

accounts
--------
account_id PK
customer_id FK -> customers
account_type
account_name
balance
currency

transactions
------------
transaction_id PK
account_id FK -> accounts
transaction_date
merchant
amount
direction
category
description
```

Later tables will include beneficiaries, transfers and possibly audit events.

### Architecture change

```text
Before
BankingService → JSON

After
BankingService → Repository → SQLite
```

The deterministic workflows should change little or not at all.

### Customer isolation

Repository methods must remain customer scoped, for example conceptually:

```text
get_accounts(customer_id)
get_transactions(customer_id, ...)
```

SQL should join through account ownership instead of trusting a caller-provided account ID.

### Deliverables

- database schema/init script;
- seed data for both demo customers;
- repository/data-access layer;
- migration of authentication/customer lookup to the database;
- migration of account/transaction reads to the database;
- tests proving both demo users still receive different data;
- tests proving one user cannot retrieve another user's account/transactions;
- README/run instructions updated.

### Completion criteria

- JSON is no longer used as runtime banking persistence;
- UI and deterministic workflows behave as before;
- all tests pass;
- customer isolation remains enforced in backend data access.

---

## Stage 2 — Tool calling and the first real agent

### Primary learning question

**What changes when an LLM chooses which banking capability to invoke instead of a deterministic router choosing a workflow?**

### Build

Expose read-only application capabilities as agent tools, initially something similar to:

```text
get_accounts()
get_balance(account_id)
get_transactions(filters...)
search_transactions(...)
calculate_spending(...)
```

The authenticated `customer_id` must **not** be a model-controlled argument. It is injected by the trusted tool execution layer.

### Architecture

```text
Customer message
      ↓
LLM agent
      ↓
Tool choice + arguments
      ↓
Trusted tool executor
      + authenticated customer context
      ↓
BankingService
      ↓
Database
```

### Compare against Stage 1

Keep the deterministic implementation so we can compare:

- flexibility of phrasing;
- tool-selection correctness;
- argument correctness;
- failure modes;
- latency;
- token usage/cost;
- cases where deterministic logic is still preferable.

This becomes the **first formal experiment in this repository**. Once both implementations exist, create something like:

```text
experiments/
└── workflow-vs-agent/
    ├── README.md
    ├── scenarios/
    └── results/
```

The experiment folder should contain the comparison scenarios, results and findings rather than a full duplicate copy of the application. The complete Stage 1 implementation remains available through its Git tag.

### Deliverables

- LLM provider abstraction/configuration;
- tool schemas;
- tool executor with customer-context injection;
- agent execution trace;
- `experiments/workflow-vs-agent/` comparison once both paths are runnable;
- comparison examples/tests between deterministic and agent routing;
- documented findings.

### Completion criteria

The model can handle the Stage 1 read-only requests through tools without receiving arbitrary direct database access.

---

## Stage 3 — Conversational state and memory boundaries

### Primary learning question

**What information needs to survive between turns, and where should that state live?**

### Scenarios

```text
User: How much did I spend eating out in August?
Assistant: £69.60.
User: What about July?
```

and later:

```text
User: Move £200 into savings.
Assistant: Which account should I move it from?
User: My current account.
```

### Separate these concepts

- authenticated customer/session state;
- conversation history;
- current task/workflow state;
- durable user memory/preferences.

Do not call all previous messages "memory".

### Security rule

Conversation state can refer to the authenticated customer, but it must never replace or override the authenticated session identity.

### Deliverables

- conversation/session model;
- multi-turn request support;
- explicit task-state object;
- context-window strategy;
- tests for follow-up questions and session separation.

---

## Stage 4 — Planning for genuinely multi-step requests

### Primary learning question

**Which requests benefit from planning, and which should remain a single tool call or deterministic workflow?**

### Example

> Look at the last three months and help me understand why I am saving less.

Possible execution plan:

```text
Retrieve transactions
      ↓
Aggregate by month/category
      ↓
Compare periods
      ↓
Identify material changes
      ↓
Generate findings
```

### Design rule

Planning should be conditional. Do not use an expensive planner for simple requests such as "What is my balance?"

### Deliverables

- complexity/planning decision boundary;
- multi-step plan representation;
- sequential tool execution;
- intermediate-result handling;
- failure handling if a planned step fails;
- execution trace showing plan vs actual execution.

---

## Stage 5 — Human-in-the-loop transfers and controlled write actions

### Primary learning question

**Where should agent autonomy stop in a banking application?**

### Database additions

Add concepts such as:

```text
beneficiaries
transfers
```

### Business capability split

```text
prepare_transfer(...)
execute_transfer(...)
```

`prepare_transfer` may:

- resolve source/destination;
- check ownership;
- check beneficiary validity;
- check available balance;
- calculate/display the resulting state;
- create an approval-ready transfer proposal.

`execute_transfer` is callable only after a valid customer approval checkpoint.

### UX

Render an approval card, for example:

```text
Transfer £250.00
Everyday Current Account → Easy Access Savings

[Confirm transfer]  [Cancel]
```

### Security rule

No SQL-generating capability may perform money movement. Writes go through business services and transaction boundaries only.

### Deliverables

- transfer domain models/tables;
- prepare/execute APIs;
- approval token/state;
- confirmation UI;
- idempotent execution protection;
- audit event;
- tests proving the agent cannot execute without approval.

---

## Stage 6 — Guardrails, permissions and failure handling

### Primary learning question

**What happens when inputs, tools or model decisions are wrong?**

### Failure scenarios

- insufficient funds;
- unknown account;
- invalid beneficiary;
- malformed tool arguments;
- tool timeout;
- duplicate transfer/retry;
- ambiguous amount/account;
- unsupported request;
- prompt injection;
- instruction to bypass customer approval;
- attempted access to another customer's data.

### Controls

- typed input/tool schemas;
- business validation;
- permission checks;
- customer-scope enforcement;
- retry policies;
- timeouts;
- idempotency for writes;
- safe failure responses;
- approval-state validation;
- least-privilege capability exposure.

### Deliverables

- formal guardrail/policy layer where useful;
- negative test suite;
- fault-injection examples;
- documented failure taxonomy.

---

## Stage 7 — Banking knowledge with RAG

### Primary learning question

**When should the assistant retrieve unstructured/semi-structured knowledge rather than query customer banking data?**

### Knowledge corpus

Synthetic documents such as:

- account FAQs;
- charges and fees;
- card usage abroad;
- transfer rules;
- fraud/security guidance;
- product terms.

### Example

> Will I be charged for withdrawing cash abroad?

```text
Question
  ↓
Knowledge retrieval
  ↓
Relevant policy passages
  ↓
Grounded answer + source
```

### Cross-source scenario

> I was charged £7.50 on this withdrawal. Is that consistent with the foreign cash fee?

```text
Transaction tool ──────┐
                       ├─→ Assistant → grounded answer
Policy RAG ────────────┘
```

### Relationship to the separate RAG learning repository

The detailed experiments for chunking, metadata filtering, top-k, hybrid retrieval, reranking and retrieval evaluation belong in `rag-architecture-playground`.

This banking project consumes the chosen RAG capability as part of an enterprise application.

### Deliverables

- synthetic banking knowledge corpus;
- retrieval integration;
- citations/source display;
- routing between banking data vs knowledge retrieval;
- cross-source answer example;
- groundedness/retrieval tests.

---

## Stage 8 — Controlled Text-to-SQL analytics

### Primary learning question

**How can an LLM answer flexible analytical questions over banking data without receiving unrestricted database access?**

### Intended use

Use Text-to-SQL for open-ended read-only analytics where creating a bespoke API for every question is impractical.

Example:

> Which spending categories increased most over the last three months compared with the previous three?

Do **not** use Text-to-SQL for normal banking commands already represented by controlled APIs.

### Architecture

```text
Analytical question
       ↓
Schema/context provider
       ↓
Text-to-SQL generation
       ↓
SQL parser + validator
       ↓
Policy checks
       ↓
Customer-scope enforcement
       ↓
Read-only query executor
       ↓
SQLite database
       ↓
Structured result
       ↓
Answer generation
```

### Required controls

At minimum:

1. SELECT/read-only statements only;
2. allow-listed tables/columns;
3. block DDL/DML (`INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.);
4. authenticated customer scope enforced outside the LLM;
5. row/result limits;
6. query timeout/complexity controls where practical;
7. parameterisation where applicable;
8. execution audit/tracing;
9. read-only SQLite connection mode for the query executor.

### Important customer-isolation rule

The LLM must not be trusted to remember:

```sql
WHERE customer_id = 'cust-001'
```

The trusted query policy/execution layer must guarantee that a valid query cannot return another customer's rows.

### Comparison experiment

Compare:

```text
Known business API/tool
vs
Text-to-SQL
```

for several request types and document when each approach is appropriate.

### Deliverables

- schema-context exposure strategy;
- SQL-generation component;
- SQL validation/policy layer;
- read-only executor;
- customer-scope tests;
- malicious SQL tests;
- analytical example set;
- architecture findings.

---

## Stage 9 — MCP integration

### Primary learning question

**What do we gain or lose by exposing capabilities through MCP rather than direct Python/API integration?**

### Candidate MCP capabilities

Potentially expose selected read-only banking and knowledge capabilities through a local MCP server.

```text
Agent
  ↓
MCP client
  ↓
Banking MCP server
  ↓
Controlled capabilities
  ↓
Services/query layer
```

Do not expose unrestricted database access merely because MCP can transport a tool call.

### Compare

- discoverability;
- coupling;
- capability descriptions;
- permissions;
- interoperability;
- operational complexity;
- traceability;
- security surface.

### Deliverables

- local MCP server;
- selected tools exposed via MCP;
- direct-vs-MCP implementation comparison;
- documented trade-offs.

---

## Stage 10 — LangGraph reimplementation / orchestration comparison

### Primary learning question

**When does an orchestration framework provide enough value to justify its abstraction and complexity?**

Do this only after the mechanics of routing, tools, state, planning and approval are understood in our own implementation.

Potential graph:

```text
START
  ↓
Interpret request
  ↓
Route
 ┌───────────────┬───────────────────┬─────────────────┐
 ↓               ↓                   ↓                 ↓
Answer       Banking tool         Knowledge         Analytics
                                      │                 │
                                     RAG            Text-to-SQL
                                      │                 │
 └───────────────────────┬────────────┴─────────────────┘
                         ↓
                  Sensitive action?
                         │
                    yes  ↓
                     Approval
                         ↓
                      Respond
```

### Compare with hand-written orchestration

- clarity;
- state handling;
- checkpoints;
- retries;
- observability;
- testability;
- framework coupling;
- complexity for simple paths.

### Deliverables

- equivalent LangGraph flow for selected scenarios;
- side-by-side comparison;
- decision on whether the final application benefits from LangGraph.

---

## Stage 11 — Formal evaluation and observability

### Primary learning question

**How do we demonstrate that the assistant is correct, safe and useful rather than merely impressive in a demo?**

Evaluation should exist informally throughout the project; this stage makes it systematic.

### Evaluation scenario set

Include:

- balance lookup;
- transaction search;
- spending analysis;
- conversational follow-up;
- multi-step analysis;
- RAG question;
- cross-source RAG + transaction question;
- Text-to-SQL analytical question;
- transfer requiring approval;
- approval-bypass attempt;
- insufficient funds;
- tool failure;
- ambiguous request;
- cross-customer access attempt;
- malicious SQL request.

### Metrics/signals

- routing/tool-selection correctness;
- tool-argument correctness;
- query correctness;
- task completion;
- customer-isolation compliance;
- approval-policy compliance;
- groundedness/citation quality;
- failure recovery;
- latency;
- model/tool token usage and approximate cost.

### Observability model

Capture safe execution events such as:

```text
request
  → route/model decision
  → tool/query request
  → validated arguments/policy decision
  → tool/query result metadata
  → approval checkpoint
  → final result
```

Do not store or display private model chain-of-thought.

### Deliverables

- evaluation dataset;
- repeatable evaluation runner;
- result summaries/charts where useful;
- structured traces;
- regression checks across architecture versions.

---

## Stage 12 — Single-agent vs multi-agent experiment

### Primary learning question

**Does decomposing the assistant into specialist agents materially improve the system?**

Do not assume multi-agent is better.

### Candidate multi-agent experiment

```text
                         Supervisor
                              │
          ┌───────────────────┼──────────────────────┐
          │                   │                      │
          ▼                   ▼                      ▼
 Banking Operations       Insights Agent        Knowledge Agent
       capability          Text-to-SQL                RAG
          │                   │                      │
          ▼                   ▼                      ▼
 Banking tools/API      Query service          Retrieval service
          │                   │
          └──────────────┬────┘
                         ▼
                     Banking DB
```

Possible responsibilities:

### Banking Operations capability/agent

- balances;
- transaction lookup through known APIs;
- transfer preparation/execution through guarded business services.

### Insights capability/agent

- flexible analytical questions;
- controlled Text-to-SQL;
- structured financial analysis.

### Knowledge capability/agent

- policy/product questions;
- RAG and source-grounded answers.

### Compare with a single-agent design

Measure:

- task success;
- routing errors;
- latency;
- token/cost overhead;
- duplicated context;
- debugging complexity;
- permission isolation;
- conceptual clarity;
- whether specialist boundaries improve maintainability.

### Valid final outcome

It is entirely acceptable — and architecturally valuable — to conclude that one agent with well-designed capability boundaries is better for this application.

The purpose of the stage is to make an evidence-based architecture decision, not to force a multi-agent implementation into the final design.

---

# 6. Cross-cutting security and governance model

These requirements accumulate rather than belong to only one phase.

## Identity

- customer identity comes from trusted authentication/session context;
- customer identity is never selected by the LLM;
- every capability receives the minimum identity/context it requires.

## Data access

- customer-specific account/transaction data is scoped server-side;
- agent tools expose controlled capabilities, not raw datastore access;
- Text-to-SQL is read-only and policy controlled;
- writes use business services only.

## Actions

- sensitive operations require explicit approval;
- approval is bound to the prepared action, not just a generic "yes";
- repeated execution is protected through idempotency controls.

## Auditability

Capture enough information to reconstruct:

- who initiated the request;
- which capability ran;
- what safe parameters were used;
- which policy/approval decision occurred;
- whether the operation succeeded.

Avoid storing unnecessary secrets or private model reasoning.

---

# 7. Repository evolution

Current structure at the Stage 1A milestone:

```text
agentic-banking-assistant/
├── app/
│   ├── api/
│   ├── core/
│   ├── data/
│   ├── models/
│   ├── services/
│   ├── static/
│   ├── workflows/
│   └── main.py
├── docs/
│   ├── adr/
│   └── stages/
│       └── stage1.md
├── tests/
├── DEVELOPMENT_PHASES.md
├── README.md
└── requirements.txt
```

Expected later concepts may introduce directories such as:

```text
app/
├── agents/
├── tools/
├── repositories/
├── database/
├── rag/
├── text_to_sql/
├── policies/
├── evaluation/
└── observability/

mcp/
experiments/
architecture/
```

Do not create all of these folders upfront. Add them when the corresponding capability is implemented so repository structure reflects real code rather than a speculative architecture diagram.

## 7.1 Preserving milestones: main branch, stage documents and Git tags

This repository is intentionally an evolving learning project, but it should still read like one coherent application rather than a collection of copied codebases.

Use the following convention:

```text
main branch
    → current / most advanced implementation

Git tags
    → exact runnable snapshot of completed milestones

docs/stages/
    → historical record of what was built, why it changed and what was learned

experiments/
    → focused side-by-side comparisons only when multiple real approaches exist
```

Recommended milestone tags:

| Milestone | Snapshot tag | Historical document |
|---|---|---|
| Stage 1A — deterministic workflows + customer session | `stage-1a` | `docs/stages/stage1.md` |
| Stage 1B — SQLite + repository boundary | `stage-1b` | `docs/stages/stage1b.md` |
| Stage 2 — LLM tool calling / first agent | `stage-2` | `docs/stages/stage2.md` |
| Later stages | `stage-N` | `docs/stages/stageN.md` |

A stage document describes the milestone; the Git tag preserves the code exactly as it existed when that milestone completed. Do not copy the whole application into `stage1/`, `stage2/`, etc.

## 7.2 Experiment strategy

Experiments begin only when the project contains two meaningful architectural approaches that can be evaluated against each other. Do not create empty experiment folders merely because they appear on the roadmap.

Planned comparison points:

| Stage | Experiment | Purpose |
|---|---|---|
| Stage 2 | `workflow-vs-agent` | Compare deterministic routing/workflows with LLM tool selection |
| Stage 8 | `api-vs-text-to-sql` | Compare controlled business tools with flexible read-only analytical SQL |
| Stage 9 | `direct-tools-vs-mcp` | Compare direct integration with MCP-exposed capabilities |
| Stage 10 | `raw-vs-langgraph` | Compare hand-written orchestration with LangGraph |
| Stage 12 | `single-vs-multi-agent` | Compare one agent with specialist multi-agent decomposition |

Experiment folders should primarily contain evaluation scenarios, small comparison harnesses, results and findings. Historical full-application versions are preserved by Git tags instead.

---

# 8. Architecture decision records

Important decisions should be captured in `docs/adr/` as they are made.

Already present:

- `0001-start-with-deterministic-workflows.md`
- `0002-customer-session-from-stage-1.md`

Likely future ADRs:

- SQLite/repository boundary;
- agent tool security/customer-context injection;
- transfer approval model;
- Text-to-SQL query-policy architecture;
- direct tools vs MCP;
- raw orchestration vs LangGraph;
- single-agent vs multi-agent final decision.

---

# 9. Recommended implementation order from current state

The immediate sequence is:

```text
Stage 1A  Customer-scoped deterministic baseline        ✅ complete
    ↓
Stage 1B  SQLite + repository/data-access boundary      ← next
    ↓
Stage 2   LLM tool calling / first agent
    ↓
Stage 3   Conversational state
    ↓
Stage 4   Conditional multi-step planning
    ↓
Stage 5   HITL transfers / controlled writes
    ↓
Stage 6   Guardrails + failure handling
    ↓
Stage 7   RAG banking knowledge
    ↓
Stage 8   Controlled Text-to-SQL analytics
    ↓
Stage 9   MCP integration experiment
    ↓
Stage 10  LangGraph comparison
    ↓
Stage 11  Formal evaluation + observability
    ↓
Stage 12  Single-agent vs multi-agent experiment
```

Evaluation, tests, security boundaries and execution tracing should continue to evolve throughout rather than wait until Stage 11.

---

# 10. Context to preserve when starting a new stage/chat

The following decisions should be treated as project invariants unless deliberately revisited through an ADR:

1. This is a **banking UX + AI architecture** project, not a collection of disconnected agent demos.
2. The customer logs in before using the assistant.
3. All banking data is customer specific.
4. The authenticated session, not the model or UI request body, determines customer identity.
5. Stage 1 deliberately begins deterministic so later agent behaviour has a baseline for comparison.
6. JSON is temporary; SQLite is the next persistence layer.
7. Known banking operations use controlled APIs/tools.
8. Text-to-SQL is a separate read-only analytics capability behind validation, policy and customer-scope enforcement.
9. Money movement never occurs through Text-to-SQL.
10. Sensitive writes require business validation and explicit human approval.
11. RAG experiments live mainly in the separate RAG playground; this project integrates the resulting retrieval capability.
12. MCP and LangGraph are introduced as comparison experiments, not assumed requirements.
13. Multi-agent architecture is tested late and must justify itself against a simpler single-agent design.
14. Execution traces expose safe architectural steps, not hidden model reasoning.
15. The repository should remain understandable enough to support learning and architecture discussion, not become framework-heavy for its own sake.
16. The `main` branch holds the current implementation; completed milestones are preserved through Git tags rather than copied stage-by-stage source trees.
17. `docs/stages/` records the architectural journey; `experiments/` is created only when there are multiple implemented approaches to compare.

---

## Current hand-off statement

**Implemented:** Stage 1A — authenticated customer session + customer-scoped deterministic banking workflows and UX.  
**Verified:** automated tests cover authentication, separate customer data, assistant customer scope and blocked cross-customer account access.  
**Milestone preservation:** document the completed milestone in `docs/stages/stage1.md`, commit the repository, and create annotated tag `stage-1a`.  
**Next implementation:** Stage 1B — replace JSON persistence with SQLite and introduce the repository/data-access layer while preserving the existing UI, workflow and customer-isolation behaviour.
