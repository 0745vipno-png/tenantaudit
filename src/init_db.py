import sqlite3
import os

# 1. 取得資料庫絕對路徑
db_path = os.path.join(os.getcwd(), 'tenantaudit.db')

# 2. 如果舊的空資料庫存在，先刪除
if os.path.exists(db_path):
    os.remove(db_path)

# 3. 直接寫入 SQL 語法 (確保萬無一失)
schema_sql = """
CREATE TABLE tenants (
    tenant_id TEXT PRIMARY KEY,
    tenant_name TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('active', 'disabled')),
    created_at TEXT NOT NULL
);

CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('open','sealed')),
    started_at TEXT NOT NULL,
    sealed_at TEXT,
    final_chain_hash TEXT,
    event_count INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

CREATE TABLE audit_events (
    event_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    seq_no INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    prev_hash TEXT,
    event_hash TEXT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (run_id) REFERENCES runs(run_id),
    UNIQUE (run_id, seq_no)
);

CREATE TABLE exported_artifacts (
    artifact_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    run_id TEXT,
    artifact_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);
"""

try:
    conn = sqlite3.connect(db_path)
    # 強制開啟外鍵
    conn.execute("PRAGMA foreign_keys = ON;")
    # 執行所有建表語法
    conn.executescript(schema_sql)
    conn.commit()
    
    # 驗收成果
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    
    print(f"資料庫初始化路徑: {db_path}")
    print(f"驗收成功！已建立的資料表: {tables}")
    
except Exception as e:
    print(f"初始化失敗: {e}")
