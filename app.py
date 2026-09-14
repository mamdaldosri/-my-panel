import os
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
  return """
    <html dir="rtl">
    <head><title>لوحة التحكم</title></head>
    <body style="font-family:sans-serif; text-align:center; padding:50px; background:#f4f4f9;">
        <h1 style="color:#4b2e83;">لوحة التحكم - شغال 100%</h1>
        <div style="background:white; padding:20px; border-radius:10px; display:inline-block; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
            <h3>حالة المشتركين</h3>
            <p>المستخدمين المتصلين: <b style="color:green;">1</b></p>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
