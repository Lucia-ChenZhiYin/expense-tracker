# Expense Tracker｜個人記帳與財務統計

Python Flask + SQLite + HTML/CSS/JavaScript + Chart.js 個人記帳練習專案。

## 功能
- 新增、查詢、編輯、刪除收入與支出（CRUD）
- 內建類別與自訂類別
- 依月份查看收支紀錄
- 月收入、月支出、月結餘統計
- Chart.js 支出類別圓餅圖
- 本月與上月各類別支出比較
- 匯出全部紀錄為 UTF-8 CSV

## 專案結構
```text
expense-tracker/
├── app.py
├── database.py
├── test_database.py
├── requirements.txt
├── instance/
│   └── expense.db
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Windows / VS Code 執行
在 VS Code 開啟專案資料夾，使用 PowerShell 終端機：

```powershell
# 如果已經有 venv，可以跳過建立步驟
python -m venv venv

# 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 安裝套件
pip install -r requirements.txt

# 啟動
python app.py
```

瀏覽器開啟 `http://127.0.0.1:5000`。

停止伺服器按 `Ctrl + C`；離開虛擬環境輸入 `deactivate`。

## 資料庫
資料庫固定使用 `instance/expense.db`。第一次執行會自動建立資料表及預設類別。資料庫檔案已加入 `.gitignore`，不會被 Git 提交。若已有自己的資料庫，請先備份再替換程式。

## 執行資料庫測試
```powershell
python -m unittest test_database.py
```

## API
| Method | Endpoint | 說明 |
|---|---|---|
| GET | `/api/categories` | 取得類別 |
| POST | `/api/categories` | 新增類別 |
| GET | `/api/records?month=YYYY-MM` | 查詢月份紀錄 |
| POST | `/api/records` | 新增紀錄 |
| PUT | `/api/records/<id>` | 編輯紀錄 |
| DELETE | `/api/records/<id>` | 刪除紀錄 |
| GET | `/api/analytics/monthly?month=YYYY-MM` | 月統計 |
| GET | `/api/analytics/monthly-comparison?month=YYYY-MM` | 月份比較 |
| GET | `/api/export/csv` | 匯出 CSV |

這是單人本機練習專案，未包含登入、雲端同步或正式部署所需的安全功能。
