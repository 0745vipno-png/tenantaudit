03_audit_chain_model.md
Overview

Audit Chain Model 是 TenantAudit 的核心完整性機制。

每一筆審計事件會透過 加密雜湊鏈（Hash Chain） 與前一筆事件連接，使歷史紀錄具備 防篡改特性（Tamper-Evident）。

每個租戶的每個 run 都維護一條獨立的事件鏈。

Tenant
 └─ Run
     └─ Event Chain
Event1 → Event2 → Event3 → ...

若任一歷史事件被修改，整條鏈的驗證將失敗。

Event Chain Structure

每個 run 的 audit 事件按時間順序形成鏈。

Event1
Event2
Event3
...
EventN

每個事件包含：

prev_hash
event_hash

形成鏈式結構：

[Event1] → [Event2] → [Event3] → [Event4]
Event Record Model

Audit Event 在資料庫中的邏輯結構：

Field	Description
event_id	UUID
tenant_id	tenant identifier
run_id	audit run identifier
event_type	event category
payload	JSON payload
created_at	timestamp
prev_hash	previous event hash
event_hash	current event hash
Hash Computation

每個事件的 event_hash 透過 SHA256 計算：

event_hash = SHA256(
    tenant_id
    + run_id
    + event_type
    + payload
    + created_at
    + prev_hash
)

注意事項：

payload 必須 canonical JSON

timestamp 必須 固定格式

字串必須 deterministic serialization

否則驗證會失敗。

Genesis Event

每個 run 的第一個事件稱為 Genesis Event。

prev_hash = "GENESIS"

或

prev_hash = NULL

取決於實作策略。

示例：

Event1
prev_hash = GENESIS
event_hash = H(Event1)

Event2
prev_hash = hash(Event1)
event_hash = H(Event2 + hash(Event1))
Chain Progression

每次新增事件：

prev_hash = last_event.event_hash
event_hash = hash(current_event_data + prev_hash)

形成：

E1 → E2 → E3 → ... → EN
Final Chain Hash

當 run 被 seal 時，系統會記錄：

final_chain_hash

計算方式：

final_chain_hash = last_event.event_hash

Seal 之後：

不允許再新增事件

chain hash 不會再改變

Chain Verification

驗證流程：

verify_run(tenant_id, run_id)

步驟：

讀取 run 所有事件

依序重新計算 hash

驗證 prev_hash

檢查 event_hash

驗證 final_chain_hash

流程圖：

Load Events
     │
Recompute Hash
     │
Check prev_hash
     │
Compare event_hash
     │
Next Event
Verification Failure Cases

驗證會失敗於以下情況：

Case	Description
hash mismatch	event_hash 不一致
prev_hash mismatch	鏈接斷裂
missing event	中間事件缺失
unexpected event order	時序錯誤
final hash mismatch	seal hash 不一致
Security Guarantees

Audit Chain 提供：

tamper-evident history

deterministic verification

append-only evidence record

tenant scoped isolation

任何歷史修改都會破壞 hash chain。

Limitations

TenantAudit 不是區塊鏈系統。

系統不提供：

distributed consensus

trustless verification

external timestamping

public audit anchors

TenantAudit 是 local audit ledger。

Relationship to Hash Engine

core/hash_engine.py 負責：

event hash calculation

chain verification

final chain hash calculation

該模組必須保證：

deterministic hashing

否則 verification 可能出現 false negative。

Implementation Reference

相關模組：

core/hash_engine.py
services/audit_service.py
services/verify_service.py
repositories/event_repository.py
