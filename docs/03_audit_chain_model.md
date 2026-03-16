1. Purpose

TenantAudit 的 Audit Chain Model 用於確保 審計紀錄不可竄改（Tamper-Evident）。
每一筆 Audit Record 會透過 Hash Chain 方式連接前一筆紀錄，形成可驗證的審計鏈。

設計目標：

保證審計資料完整性（Integrity）

提供可驗證的歷史紀錄（Verifiable History）

防止任意刪除或修改 audit log

2. Audit Record Structure

每一筆 audit record 具備以下欄位：

Field	Type	Description
id	UUID	唯一識別碼
tenant_id	string	租戶識別
action	string	操作類型
actor	string	執行者
timestamp	datetime	事件發生時間
payload	json	相關資料
prev_hash	string	前一筆 record hash
record_hash	string	本筆 record hash
3. Hash Chain Model

Audit Chain 採用類似 區塊鏈的鏈式結構：

Record1
  hash = H(data1)

Record2
  prev_hash = hash1
  hash = H(data2 + hash1)

Record3
  prev_hash = hash2
  hash = H(data3 + hash2)

鏈式結構如下：

[Record1] -> [Record2] -> [Record3] -> [Record4]

若中間任一 record 被修改：

該 record 的 hash 會改變

後續所有 record 的 prev_hash 失效

系統可立即偵測異常

4. Hash Calculation

Record Hash 計算方式：

record_hash = SHA256(
    tenant_id +
    action +
    actor +
    timestamp +
    payload +
    prev_hash
)

建議：

使用 SHA256

Payload 需固定序列化（canonical JSON）

5. Chain Verification

系統可定期執行 Chain Verification：

流程：

讀取第一筆 audit record

重新計算 hash

驗證 record_hash 是否一致

檢查下一筆 record 的 prev_hash

持續驗證至最後一筆

若發生以下情況即判定為 Integrity Violation：

hash mismatch

prev_hash mismatch

record missing

6. Tamper Detection Strategy

當 audit chain 發現異常：

系統應：

記錄安全事件

發送警示

鎖定 audit chain 狀態

啟動調查流程

7. Design Considerations
Append Only

Audit log 必須為 append-only：

不允許修改

不允許刪除

Immutable Storage

建議：

Write-once storage

或 Object Storage + versioning

Multi-Tenant Isolation

Audit chain 應該 tenant scoped：

Tenant A Chain
A1 -> A2 -> A3

Tenant B Chain
B1 -> B2 -> B3
8. Future Extensions

可能擴展：

Merkle Tree verification

External notarization

Remote audit anchoring

Signed audit record
