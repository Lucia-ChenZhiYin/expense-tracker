# Expense Tracker 開發筆記

## 專案架構
- `app.py`：Flask 應用程式、API 路由、資料驗證。
- `database.py`：SQLite 連線、資料表建立、預設類別。
- `instance/expense.db`：本機記帳資料庫。
- `templates/index.html`：網頁結構。
- `static/css/style.css`：網頁樣式與 RWD。
- `static/js/app.js`：前端互動、呼叫 API、圖表與明細顯示。
- `test_database.py`：資料庫初始化的簡單測試。

## 為什麼使用 venv
隔離不同 Python 專案的套件，避免版本互相影響。
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
deactivate
```

## 為什麼使用 Flask
Flask 負責接收前端 HTTP 請求、執行 Python 程式與 SQL，再將資料以 JSON 回傳給前端。

## 為什麼使用 requirements.txt
記錄專案需要的 Python 套件，讓其他環境可以使用 `pip install -r requirements.txt` 安裝。

## 為什麼使用 .gitignore
排除虛擬環境、Python 快取及個人資料庫，避免不必要或私人的檔案被提交到 Git。

## 建議理解程式的順序
1. 先閱讀 `database.py`，理解資料表和外鍵。
2. 看 `app.py` 的 `api_create_record()`，追蹤新增資料流程。
3. 看 `index.html`，理解表單與畫面結構。
4. 看 `app.js` 的表單 submit 事件，理解前端如何呼叫 API。
5. 看 `api_monthly_analytics()`，理解 SQL 如何計算每月統計。
6. 自己新增一個小功能，例如依類別篩選紀錄。
