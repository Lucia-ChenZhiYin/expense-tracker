import sqlite3 #Python內建的輕量級資料庫工具

DB_NAME = "expense_tracker.db"#.db 是 SQLite 資料庫的副檔名

def get_db_connection():#用來打開與資料庫的通道
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row#把查詢結果改成了類似字典的格式，可以直接用欄位名稱來拿資料
    return conn

def init_db():
    """初始化資料庫：建立資料表並寫入預設類別"""
    conn = get_db_connection()
    cursor = conn.cursor()#游標（Cursor）

    # 1. 建立 categories (類別表)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('expense', 'income'))
        )
    ''')

    # 2. 建立 records (明細表)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
            category_id INTEGER NOT NULL,
            sub_item TEXT,
            date TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # 3. 預設初始類別（如果表格是空的才寫入）
    cursor.execute('SELECT COUNT(*) FROM categories')
    if cursor.fetchone()[0] == 0:
        default_categories = [
            ('飲食', 'expense'),
            ('交通', 'expense'),
            ('娛樂', 'expense'),
            ('其他', 'expense'),
            ('薪水', 'income'),
            ('副業/獎金', 'income')
        ]
        cursor.executemany('INSERT INTO categories (name, type) VALUES (?, ?)', default_categories)

    conn.commit()
    conn.close()
    print("✅ 資料庫初始化完成！")

if __name__ == '__main__':
    init_db()