TenantAudit — State Machine Architecture
TenantAudit — State Machine Model
v0.1

Goal
-----
Define lifecycle states and valid transitions for
tenants, runs, and verification processes.

State machines prevent invalid operations and
protect audit integrity.
1. Tenant State Machine
Tenant Lifecycle


            ┌───────────┐
            │  created  │
            └─────┬─────┘
                  │
                  ▼
            ┌───────────┐
            │  active   │
            └─────┬─────┘
                  │
        disable   │
                  ▼
            ┌───────────┐
            │ disabled  │
            └───────────┘
States
State	Meaning
created	tenant record created
active	tenant can operate normally
disabled	tenant cannot perform operations
Allowed Operations
Operation	Allowed State
create run	active
append event	active
seal run	active
verify run	active
Forbidden
disabled tenant
    cannot create runs
    cannot append events

這個其實是 安全保護。

2. Run State Machine（核心）

這是整個系統最重要的一個。

Run Lifecycle


          create_run

            ▼

      ┌───────────┐
      │   open    │
      └─────┬─────┘
            │
            │ append_event
            │
            ▼
      ┌───────────┐
      │   open    │
      └─────┬─────┘
            │
            │ seal_run
            ▼

      ┌───────────┐
      │  sealed   │
      └─────┬─────┘
            │
            │ verify_run
            ▼

      ┌───────────┐
      │ verified  │
      └───────────┘
Run States
State	Meaning
open	run is accepting events
sealed	run closed, chain fixed
verified	verification completed
Allowed Operations
Operation	State
append_event	open
seal_run	open
verify_run	sealed
Forbidden Operations
append_event on sealed run → reject
append_event on verified run → reject

seal_run on sealed run → reject
verify_run on open run → reject
Run State Transition Table
State Transition Table

Current State | Operation      | Next State
--------------------------------------------
none          | create_run     | open
open          | append_event   | open
open          | seal_run       | sealed
sealed        | verify_run     | verified
3. Event Chain State Model

Event 本身沒有狀態機，
但它有 不可變條件。

Event Model

append_event
     │
     ▼
  event created

(no further transitions)

事件一旦寫入：

UPDATE → forbidden
DELETE → forbidden

事件唯一可做的操作：

read
verify
export
4. Verification Result Model

Verify 的結果其實是一個小型狀態模型。

Verification Result


         verify_run

             │
             ▼

        ┌──────────┐
        │  running │
        └────┬─────┘
             │
             │
      ┌──────┴────────┐
      ▼               ▼

 ┌──────────┐    ┌──────────┐
 │   valid  │    │  invalid │
 └──────────┘    └──────────┘
Possible Results
Result	Meaning
valid	chain integrity confirmed
invalid	tampering detected
5. Combined System State Model

把三個狀態一起看會變成：

Tenant
   │
   ▼

Tenant(active)
   │
   ▼

Run(open)
   │
   ├── append_event
   │
   ▼

Run(sealed)
   │
   ▼

Run(verified)

而 tenant disabled 時：

Tenant(disabled)

all operations rejected
6. State Enforcement Layer

狀態機在 Service Layer 強制。

Service Layer

RunService
AuditService
VerifyService

例如：

def append_event(run):

    if run.status != "open":
        raise RunClosedError
def seal_run(run):

    if run.status != "open":
        raise InvalidStateError
def verify_run(run):

    if run.status != "sealed":
        raise InvalidStateError
7. State Machine Invariants

系統必須滿足以下條件：

Invariant 1
sealed run cannot grow.

Invariant 2
event order must be sequential.

Invariant 3
tenant disabled stops new operations.

Invariant 4
verification cannot modify data.