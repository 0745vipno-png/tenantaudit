TenantAudit 使用手冊（Windows PowerShell）
0. 啟動前準備

每次開啟終端機後，先進入專案根目錄，並設定 PYTHONPATH：

cd C:\Users\王治程\OneDrive\桌面\tenantaudit
$env:PYTHONPATH = ".\src"
1. 租戶管理（Tenant）
功能	指令範例
建立新租戶	python -m tenantaudit.cli.main tenant create "客戶名稱"
列出所有租戶	python -m tenantaudit.cli.main tenant list

提醒： 建立後請手動記下輸出的 tenant_id (UUID)。

2. 稽核批次管理（Run）
功能	指令範例
開啟新 Run	python -m tenantaudit.cli.main run create <tenant_id>
列出租戶的 Runs	python -m tenantaudit.cli.main run list <tenant_id>
封印 Run	python -m tenantaudit.cli.main run seal <tenant_id> <run_id>

注意： 一旦執行 seal，該 Run 就不可再新增事件。

3. 事件紀錄（Event）

基本語法：

python -m tenantaudit.cli.main event append <tenant_id> <run_id> <event_type> <json_payload>

PowerShell 範例：

python -m tenantaudit.cli.main event append <T_ID> <R_ID> LOGIN "{""user"":""admin""}"

注意： payload 必須是合法 JSON，PowerShell 內雙引號需要跳脫。

4. 完整性驗證（Verify）
功能	指令範例
驗證 Run 完整性	python -m tenantaudit.cli.main verify run <tenant_id> <run_id>

驗證成功時，系統會回傳類似：

{'status': 'valid', 'run_id': '...', 'event_count': 1, 'final_hash': '...'}

這表示：

事件鏈順序正確

每筆事件雜湊一致

final_chain_hash 一致

event_count 一致

若出現 VerificationError，表示鏈完整性檢查失敗，可能有資料遭修改、鏈結中斷或封印資訊不一致。

5. 實戰演練
Step 1：建立租戶
python -m tenantaudit.cli.main tenant create "Test"

記下輸出的 tenant_id。

Step 2：建立 Run
python -m tenantaudit.cli.main run create <tenant_id>

記下輸出的 run_id。

Step 3：新增事件
python -m tenantaudit.cli.main event append <tenant_id> <run_id> ACTION "{""data"":""hello""}"
Step 4：封印 Run
python -m tenantaudit.cli.main run seal <tenant_id> <run_id>
Step 5：驗證完整性
python -m tenantaudit.cli.main verify run <tenant_id> <run_id>