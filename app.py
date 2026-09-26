from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "歡迎使用個人記帳 API！",
        "status": "success"
    })

if __name__ == '__main__':
    # 開啟除錯模式，修改程式碼後存檔會自動重載
    app.run(debug=True, port=5000)