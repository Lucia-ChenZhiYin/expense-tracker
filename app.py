#取得所有類別，並以 JSON 格式回傳。
from flask import Flask, jsonify, request
from database import get_connection


# 建立 Flask 應用程式，使用 app 來設定路由、處理請求，以及啟動伺服器。
app = Flask(__name__)

from datetime import datetime
# API：取得所有類別
@app.route("/api/categories", methods=["GET"])
def get_categories():

    # 取得網址中的 type 參數（如果有的話）
    category_type = request.args.get("type")

    conn = get_connection()

    try:
        # 如果有指定類型，就只查詢該類別
        if category_type:
            if category_type not in ("income", "expense"):
                return jsonify({
                    "error": "Invalid category type"
                }), 400

            rows = conn.execute("""
                SELECT id, name, type
                FROM categories
                WHERE type = ?
                ORDER BY id
            """, (category_type,)).fetchall()

        else:
            # 沒有指定類型，就取得全部類別
            rows = conn.execute("""
                SELECT id, name, type
                FROM categories
                ORDER BY id
            """).fetchall()

        # 將 SQLite 查詢結果轉換成 Python Dictionary
        categories = [dict(row) for row in rows]

        # 回傳 JSON
        return jsonify({
            "categories": categories
        })

    finally:
        conn.close()
# API：取得收支紀錄

@app.route("/api/records", methods=["GET"])
def get_records():

    # 取得月份參數
    month = request.args.get("month")

    conn = get_connection()

    try:
        # 基本 SQL 查詢
        sql = """
            SELECT
                records.id,
                records.amount,
                records.type,
                records.category_id,
                categories.name AS category_name,
                records.sub_item,
                records.date,
                records.created_at
            FROM records
            JOIN categories
                ON records.category_id = categories.id
        """

        params = []

        # 如果有指定月份，就增加篩選條件
        if month:
            try:
                datetime.strptime(month, "%Y-%m")

                if len(month) != 7:
                    raise ValueError

            except ValueError:
                return jsonify({
                    "error": "Invalid month format. Use YYYY-MM."
                }), 400

            sql += " WHERE records.date LIKE ?"
            params.append(f"{month}-%")

        # 依日期及 ID 排序
        sql += " ORDER BY records.date DESC, records.id DESC"

        rows = conn.execute(sql, params).fetchall()

        records = [dict(row) for row in rows]

        return jsonify({
            "records": records,
            "total": len(records)
        })

    finally:
        conn.close()

# API：新增收支紀錄
@app.route("/api/records", methods=["POST"])
def create_record():

    # 接收前端傳來的 JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    # 取得各項資料
    amount = data.get("amount")
    record_type = data.get("type")
    category_id = data.get("category_id")
    sub_item = data.get("sub_item", "")
    record_date = data.get("date")

    # 1. 驗證金額
    if (
        not isinstance(amount, int)
        or isinstance(amount, bool)
        or amount <= 0
    ):
        return jsonify({
            "error": "Amount must be a positive integer"
        }), 400

    # 2. 驗證收支類型
    if record_type not in ("expense", "income"):
        return jsonify({
            "error": "Type must be expense or income"
        }), 400

    # 3. 驗證類別 ID
    if (
        not isinstance(category_id, int)
        or isinstance(category_id, bool)
        or category_id <= 0
    ):
        return jsonify({
            "error": "Invalid category_id"
        }), 400

    # 4. 驗證備註
    if not isinstance(sub_item, str):
        return jsonify({
            "error": "sub_item must be a string"
        }), 400

    # 5. 驗證日期
    if not isinstance(record_date, str):
        return jsonify({
            "error": "Invalid date"
        }), 400

    try:
        datetime.strptime(record_date, "%Y-%m-%d")

        if len(record_date) != 10:
            raise ValueError

    except ValueError:
        return jsonify({
            "error": "Date format must be YYYY-MM-DD"
        }), 400

    conn = get_connection()

    try:
        # 確認類別是否存在，以及類別類型是否正確
        category = conn.execute("""
            SELECT id
            FROM categories
            WHERE id = ? AND type = ?
        """, (category_id, record_type)).fetchone()

        if category is None:
            return jsonify({
                "error": "Category does not exist or type does not match"
            }), 400

        # 新增資料
        cursor = conn.execute("""
            INSERT INTO records
            (amount, type, category_id, sub_item, date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            amount,
            record_type,
            category_id,
            sub_item.strip(),
            record_date
        ))

        # 儲存變更
        conn.commit()

        # 取得剛新增的資料
        new_record = conn.execute("""
            SELECT
                records.id,
                records.amount,
                records.type,
                records.category_id,
                categories.name AS category_name,
                records.sub_item,
                records.date,
                records.created_at
            FROM records
            JOIN categories
                ON records.category_id = categories.id
            WHERE records.id = ?
        """, (cursor.lastrowid,)).fetchone()

        return jsonify({
            "message": "Record created successfully",
            "record": dict(new_record)
        }), 201

    finally:
        conn.close()

# API：修改收支紀錄
@app.route("/api/records/<int:record_id>", methods=["PUT"])
def update_record(record_id):

    # 接收前端傳來的 JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    # 取得更新資料
    amount = data.get("amount")
    record_type = data.get("type")
    category_id = data.get("category_id")
    sub_item = data.get("sub_item", "")
    record_date = data.get("date")

    # 1. 驗證金額
    if (
        not isinstance(amount, int)
        or isinstance(amount, bool)
        or amount <= 0
    ):
        return jsonify({
            "error": "Amount must be a positive integer"
        }), 400

    # 2. 驗證收支類型
    if record_type not in ("expense", "income"):
        return jsonify({
            "error": "Type must be expense or income"
        }), 400

    # 3. 驗證類別 ID
    if (
        not isinstance(category_id, int)
        or isinstance(category_id, bool)
        or category_id <= 0
    ):
        return jsonify({
            "error": "Invalid category_id"
        }), 400

    # 4. 驗證備註
    if not isinstance(sub_item, str):
        return jsonify({
            "error": "sub_item must be a string"
        }), 400

    # 5. 驗證日期
    if not isinstance(record_date, str):
        return jsonify({
            "error": "Invalid date"
        }), 400

    try:
        datetime.strptime(record_date, "%Y-%m-%d")

        if len(record_date) != 10:
            raise ValueError

    except ValueError:
        return jsonify({
            "error": "Date format must be YYYY-MM-DD"
        }), 400

    conn = get_connection()

    try:
        # 確認類別存在，且類型相符
        category = conn.execute("""
            SELECT id
            FROM categories
            WHERE id = ? AND type = ?
        """, (category_id, record_type)).fetchone()

        if category is None:
            return jsonify({
                "error": "Category does not exist or type does not match"
            }), 400

        # 更新指定 ID 的紀錄
        cursor = conn.execute("""
            UPDATE records
            SET
                amount = ?,
                type = ?,
                category_id = ?,
                sub_item = ?,
                date = ?
            WHERE id = ?
        """, (
            amount,
            record_type,
            category_id,
            sub_item.strip(),
            record_date,
            record_id
        ))

        # 確認是否真的有更新到資料
        if cursor.rowcount == 0:
            return jsonify({
                "error": "Record not found"
            }), 404

        conn.commit()

        # 取得更新後的資料
        updated_record = conn.execute("""
            SELECT
                records.id,
                records.amount,
                records.type,
                records.category_id,
                categories.name AS category_name,
                records.sub_item,
                records.date,
                records.created_at
            FROM records
            JOIN categories
                ON records.category_id = categories.id
            WHERE records.id = ?
        """, (record_id,)).fetchone()

        return jsonify({
            "message": "Record updated successfully",
            "record": dict(updated_record)
        }), 200

    finally:
        conn.close()

# API：刪除收支紀錄
@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):

    conn = get_connection()

    try:
        # 刪除指定 ID 的紀錄
        cursor = conn.execute("""
            DELETE FROM records
            WHERE id = ?
        """, (record_id,))

        # 確認是否有成功刪除
        if cursor.rowcount == 0:
            return jsonify({
                "error": "Record not found"
            }), 404

        conn.commit()

        return jsonify({
            "message": "Record deleted successfully",
            "deleted_id": record_id
        }), 200

    finally:
        conn.close()

# 啟動 Flask 伺服器
if __name__ == "__main__":
    app.run(debug=True)
