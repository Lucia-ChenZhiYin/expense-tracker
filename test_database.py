#負責測試資料庫是否能正常操作。
from database import get_connection


def test_database():
    conn = get_connection()

    try:
        # 開始測試交易
        conn.execute("BEGIN")

        # 取得飲食與薪水的類別 ID
        expense_category = conn.execute(
            "SELECT id FROM categories WHERE name = ? AND type = ?",
            ("飲食", "expense")
        ).fetchone()

        income_category = conn.execute(
            "SELECT id FROM categories WHERE name = ? AND type = ?",
            ("薪水", "income")
        ).fetchone()

        # 新增一筆支出
        #使用?，Parameterized Query（參數化查詢），可以避免 SQL Injection 等安全問題，也能正確處理資料。
        conn.execute("""
            INSERT INTO records
            (amount, type, category_id, sub_item, date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            120,
            "expense",
            expense_category["id"],
            "測試午餐",
            "2026-11-08"
        ))

        # 新增一筆收入
        conn.execute("""
            INSERT INTO records
            (amount, type, category_id, sub_item, date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            30000,
            "income",
            income_category["id"],
            "測試薪水",
            "2026-11-08"
        ))

        print("新增資料成功！\n")

        # 讀取收支資料，並連接類別表
        rows = conn.execute("""
            SELECT
                records.id,
                records.amount,
                records.type,
                categories.name AS category_name,
                records.sub_item,
                records.date
            FROM records
            JOIN categories
                ON records.category_id = categories.id
            ORDER BY records.id
        """).fetchall()

        print("目前的收支紀錄：")

        for row in rows:
            print(dict(row))

        # 測試結束後回復資料庫，不會一直在正式資料庫裡累積測試資料。
        conn.rollback()

        print("\n測試完成！測試資料已回復，沒有永久儲存。")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    test_database()
