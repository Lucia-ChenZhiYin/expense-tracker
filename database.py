from pathlib import Path
import sqlite3

# 專案根目錄 / instance / expense.db
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "expense.db"


def get_db():
    """建立 SQLite 連線，並讓查詢結果可以用欄位名稱讀取。"""
    INSTANCE_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """建立資料表，並在第一次執行時加入預設類別。"""
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('expense', 'income')),
                UNIQUE (name, type)
            );

            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK (amount > 0),
                type TEXT NOT NULL CHECK (type IN ('expense', 'income')),
                category_id INTEGER NOT NULL,
                sub_item TEXT DEFAULT '',
                date TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );
            """
        )

        default_categories = [
            ("飲食", "expense"),
            ("交通", "expense"),
            ("購物", "expense"),
            ("娛樂", "expense"),
            ("生活用品", "expense"),
            ("醫療", "expense"),
            ("其他支出", "expense"),
            ("薪資", "income"),
            ("獎金", "income"),
            ("其他收入", "income"),
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            default_categories,
        )


if __name__ == "__main__":
    init_db()
    print(f"資料庫初始化完成：{DATABASE_PATH}")
