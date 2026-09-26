筆記:
1.為什麼用venv(虛擬環境)
原因:為了環境隔離，避免不同專案間的套件版本互相影響
使用指令：
建立環境：*python -m venv venv*(-m代表Module、venv代表Virtual Environment縮寫、第二個nenv代表虛擬環境資料夾名稱)
啟動環境 ：*.\venv\Scripts\Activate.ps1*
    (1).\：代表當前目錄（Current Directory）。告訴系統從你目前所在的資料夾開始找起。
    (2)venv\：進入你剛剛建立的 venv 虛擬環境資料夾。
    (3)Scripts\：進入存放 Windows 執行檔與腳本的核心資料夾。
    (4)Activate.ps1：執行這個專門給 PowerShell 使用的腳本檔案，正式切換進入虛擬環境。
關閉環境：*deactivate*
2.為甚麼用Flask(後段架構)
原因:可以將前端的HTML/CSS/JS與資料庫(SQLite)連結
3.為何建立requirements.txt
原因:記錄當前開發環境中安裝的所有 Python 套件與其版本
使用指令:*pip freeze > requirements.txt*
freeze:會列出目前Python 環境裡面所有已安裝套件的名稱與確切版本號
功能:方便其他人一鍵還原開發環境
指令:*pip install -r requirements.txt*(-r代表Requirements讀取這個檔案裡面的內容)
4.為什麼用.gitignore
原因:告訴 Git 忽略掉不需要版控的暫存檔(虛擬環境資料夾venv/、Python快取資料夾__pycache__/、Python 編譯快取檔案*.pyc、資料庫檔案*.db)