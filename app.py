from datetime import date, datetime, timedelta
from flask import Flask, jsonify, render_template, request, make_response
import csv
import io

from database import init_db, get_db

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# 確保資料庫與預設類別存在
init_db()


def get_month():
    """取得並驗證查詢月份；未提供或格式錯誤時使用本月。"""
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    try:
        datetime.strptime(month, "%Y-%m")
        return month
    except ValueError:
        return date.today().strftime("%Y-%m")


def validate_record(data):
    """共用新增／編輯紀錄的欄位驗證。"""
    try:
        amount = round(float(data.get("amount")), 2)
        category_id = int(data.get("category_id"))
        record_date = data.get("date")
        datetime.strptime(record_date, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None, "請確認金額、類別與日期格式。"

    record_type = data.get("type")
    note = str(data.get("sub_item", "")).strip()

    if not 0 < amount <= 100_000_000:
        return None, "金額必須大於 0，且不可超過 100,000,000。"
    if record_type not in ("expense", "income"):
        return None, "收支類型不正確。"
    if len(note) > 100:
        return None, "備註最多 100 個字。"

    return {
        "amount": amount,
        "category_id": category_id,
        "date": record_date,
        "type": record_type,
        "sub_item": note,
    }, None


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/categories")
def api_get_categories():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, type FROM categories ORDER BY type, name"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/categories")
def api_add_category():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    category_type = data.get("type")

    if not name or len(name) > 30:
        return jsonify(error="類別名稱需為 1 至 30 個字。"), 400
    if category_type not in ("expense", "income"):
        return jsonify(error="請選擇正確的類別類型。"), 400

    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO categories (name, type) VALUES (?, ?)",
                (name, category_type),
            )
            category_id = cursor.lastrowid
    except Exception as exc:
        # SQLite UNIQUE constraint：同類型不能有重複類別名稱
        if "UNIQUE" in str(exc).upper():
            return jsonify(error="這個類別已經存在。"), 409
        raise

    return jsonify(id=category_id, name=name, type=category_type), 201


@app.get("/api/records")
def api_get_records():
    month = get_month()
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT r.id, r.amount, r.type, r.category_id, c.name AS category,
                   r.sub_item, r.date
            FROM records r
            JOIN categories c ON c.id = r.category_id
            WHERE substr(r.date, 1, 7) = ?
            ORDER BY r.date DESC, r.id DESC
            """,
            (month,),
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/records")
def api_create_record():
    payload, error = validate_record(request.get_json(silent=True) or {})
    if error:
        return jsonify(error=error), 400

    with get_db() as conn:
        category = conn.execute(
            "SELECT id FROM categories WHERE id = ? AND type = ?",
            (payload["category_id"], payload["type"]),
        ).fetchone()
        if not category:
            return jsonify(error="類別不存在，或類別類型與收支類型不符。"), 400

        cursor = conn.execute(
            """
            INSERT INTO records (amount, type, category_id, sub_item, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload["amount"], payload["type"], payload["category_id"],
                payload["sub_item"], payload["date"],
            ),
        )
        new_id = cursor.lastrowid

    return jsonify(id=new_id, message="新增成功"), 201


@app.put("/api/records/<int:record_id>")
def api_update_record(record_id):
    payload, error = validate_record(request.get_json(silent=True) or {})
    if error:
        return jsonify(error=error), 400

    with get_db() as conn:
        category = conn.execute(
            "SELECT id FROM categories WHERE id = ? AND type = ?",
            (payload["category_id"], payload["type"]),
        ).fetchone()
        if not category:
            return jsonify(error="類別不存在，或類別類型與收支類型不符。"), 400

        cursor = conn.execute(
            """
            UPDATE records
            SET amount = ?, type = ?, category_id = ?, sub_item = ?, date = ?
            WHERE id = ?
            """,
            (
                payload["amount"], payload["type"], payload["category_id"],
                payload["sub_item"], payload["date"], record_id,
            ),
        )
        if cursor.rowcount == 0:
            return jsonify(error="找不到這筆紀錄。"), 404

    return jsonify(message="更新成功")


@app.delete("/api/records/<int:record_id>")
def api_delete_record(record_id):
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
        if cursor.rowcount == 0:
            return jsonify(error="找不到這筆紀錄。"), 404
    return jsonify(message="刪除成功")


@app.get("/api/analytics/monthly")
def api_monthly_analytics():
    month = get_month()
    with get_db() as conn:
        totals = conn.execute(
            """
            SELECT type, COALESCE(SUM(amount), 0) AS total
            FROM records
            WHERE substr(date, 1, 7) = ?
            GROUP BY type
            """,
            (month,),
        ).fetchall()

        category_rows = conn.execute(
            """
            SELECT c.name, SUM(r.amount) AS total
            FROM records r
            JOIN categories c ON c.id = r.category_id
            WHERE r.type = 'expense' AND substr(r.date, 1, 7) = ?
            GROUP BY c.id, c.name
            ORDER BY total DESC
            """,
            (month,),
        ).fetchall()

    result = {"income": 0, "expense": 0}
    for row in totals:
        result[row["type"]] = round(row["total"], 2)

    result["balance"] = round(result["income"] - result["expense"], 2)
    result["by_category"] = [
        {"name": row["name"], "total": round(row["total"], 2)}
        for row in category_rows
    ]
    return jsonify(result)


@app.get("/api/analytics/monthly-comparison")
def api_monthly_comparison():
    month = get_month()
    current_date = datetime.strptime(month + "-01", "%Y-%m-%d")
    previous_month = (current_date - timedelta(days=1)).strftime("%Y-%m")

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.name,
              SUM(CASE WHEN substr(r.date, 1, 7) = ? THEN r.amount ELSE 0 END) AS current_total,
              SUM(CASE WHEN substr(r.date, 1, 7) = ? THEN r.amount ELSE 0 END) AS previous_total
            FROM records r
            JOIN categories c ON c.id = r.category_id
            WHERE r.type = 'expense'
              AND substr(r.date, 1, 7) IN (?, ?)
            GROUP BY c.id, c.name
            ORDER BY current_total DESC, previous_total DESC
            """,
            (month, previous_month, month, previous_month),
        ).fetchall()

    return jsonify([
        {
            "category": row["name"],
            "current": round(row["current_total"] or 0, 2),
            "previous": round(row["previous_total"] or 0, 2),
            "difference": round(
                (row["current_total"] or 0) - (row["previous_total"] or 0), 2
            ),
        }
        for row in rows
    ])


@app.get("/api/export/csv")
def api_export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["日期", "收支類型", "類別", "金額", "備註"])

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT r.date, r.type, c.name, r.amount, r.sub_item
            FROM records r
            JOIN categories c ON c.id = r.category_id
            ORDER BY r.date DESC, r.id DESC
            """
        ).fetchall()

    for row in rows:
        writer.writerow([
            row["date"],
            "支出" if row["type"] == "expense" else "收入",
            row["name"],
            row["amount"],
            row["sub_item"],
        ])

    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        "attachment; filename=expense_records.csv"
    )
    return response


if __name__ == "__main__":
    app.run(debug=True)
