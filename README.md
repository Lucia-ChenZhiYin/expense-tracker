# expense-tracker
# 📊 個人記帳與財務統計網頁應用 (Personal Expense Tracker)

這是一個基於 Python (Flask) 與原生 Web 技術開發的簡單記帳與財務分析系統。支援收支紀錄、自訂類別、動態圖表視覺化、月度花費比對及 CSV 資料匯出功能。

---

## 🎯 專案功能清單 (Features)

### 1. 基礎收支管理 (CRUD)
- [ ] **新增收支**：可選擇支出/收入、金額、日期、類別及細項備註。
- [ ] **自訂類別**：可新增個人化的消費/收入類別，並自動更新至下拉選單。
- [ ] **每日明細**：依日期分組顯示明細，支援點擊展開/收合、編輯與刪除。
- [ ] **月度統計卡片**：顯示當月總收入、總支出與當期結餘。

### 2. 進階分析與工具 (Analytics & Export)
- [ ] **圓餅圖視覺化**：呈現當月各類別支出佔比，圓餅圖中央動態顯示結餘金額。
- [ ] **月度增減比較**：比較本月與上月的各類別支出，標示花費增加或減少的金額。
- [ ] **CSV 資料匯出**：一鍵將所有收支明細匯出為 CSV 檔，方便後續財務管理。

---

## 🛠 技術棧 (Tech Stack)

- **前端 (Frontend)**: HTML5, CSS3, JavaScript (ES6+), Chart.js
- **後端 (Backend)**: Python 3.10+, Flask
- **資料庫 (Database)**: SQLite
- **開發工具 (Tools)**: VS Code, Git, GitHub

---

## 🗄 資料庫設計 (Database Schema)

### `categories` (類別表)
| 欄位名稱 | 型態 | 說明 |
| :--- | :--- | :--- |
| `id` | INTEGER | 主鍵 (Primary Key) |
| `name` | TEXT | 類別名稱 (如：飲食, 交通) |
| `type` | TEXT | 類型 (`expense` 或 `income`) |

### `records` (明細表)
| 欄位名稱 | 型態 | 說明 |
| :--- | :--- | :--- |
| `id` | INTEGER | 主鍵 (Primary Key) |
| `amount` | REAL | 金額 |
| `type` | TEXT | 類型 (`expense` 或 `income`) |
| `category_id` | INTEGER | 外鍵 (Foreign Key) |
| `sub_item` | TEXT | 細項名稱/備註 |
| `date` | TEXT | 日期 (`YYYY-MM-DD`) |
| `created_at` | DATETIME | 建立時間 |

---

## 🔌 API 介面設計規劃 (API Endpoints)

| HTTP 方法 | 路徑 | 說明 |
| :--- | :--- | :--- |
| `GET` | `/api/records?month=YYYY-MM` | 取得指定月份的所有記帳明細 |
| `POST` | `/api/records` | 新增一筆記帳紀錄 |
| `DELETE` | `/api/records/<id>` | 刪除指定記帳紀錄 |
| `GET` | `/api/categories` | 取得所有類別選單 |
| `POST` | `/api/categories` | 新增自訂類別 |
| `GET` | `/api/analytics/monthly-comparison` | 取得本月與上月的類別支出比較資料 |
| `GET` | `/api/export/csv` | 下載全量明細 CSV 檔案 |

---

## 🚀 開發時程與階段規劃

- [x] **Phase 0**: 撰寫 README 專案計畫書與規格設計
- [ ] **Phase 1**: 建立 Python (Flask) 開發環境與 SQLite 資料庫連線
- [ ] **Phase 2**: 完成基礎 HTML/CSS 介面骨架與基礎 CRUD API
- [ ] **Phase 3**: 串接 Chart.js 實現當月支出圓餅圖
- [ ] **Phase 4**: 實作前後月花費比較演算法與介面顯示
- [ ] **Phase 5**: 完成 CSV 檔案下載功能與 UI 增強