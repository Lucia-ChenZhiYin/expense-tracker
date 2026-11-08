#負責正式的資料庫架構及連線。
import sqlite3
from pathlib import Path


# 1. 設定資料庫位置
BASE_DIR = Path(__file__).resolve().parent
#__file__：目前 Python 檔案的位置，resolve()：取得完整路徑，parent：取得上一層資料夾，/：使用 pathlib 組合路徑。
DB_PATH = BASE_DIR / "instance" / "expense.db"


# 2. 建立資料庫連線
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    # 讓查詢結果可以使用欄位名稱取得資料
    conn.row_factory = sqlite3.Row

    # 啟用外鍵約束
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# 3. 初始化資料庫
def init_db():
    conn = get_connection()

    try:
        # 建立 categories 類別表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL
                    CHECK (type IN ('expense', 'income')),
                UNIQUE (name, type),
                UNIQUE (id, type)
            )
        """)

        # 建立 records 收支明細表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL CHECK (amount > 0),
                type TEXT NOT NULL
                    CHECK (type IN ('expense', 'income')),
                category_id INTEGER NOT NULL,
                sub_item TEXT,
                date TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (category_id, type)
                    REFERENCES categories (id, type)
            )
        """)

        # 4. 建立預設類別
        default_categories = [
            ("飲食", "expense"),
            ("交通", "expense"),
            ("購物", "expense"),
            ("娛樂", "expense"),
            ("生活", "expense"),
            ("薪水", "income"),
            ("獎金", "income"),
            ("其他收入", "income")
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO categories (name, type)
            VALUES (?, ?)
        """, default_categories)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
    print(f"Database location: {DB_PATH}")
