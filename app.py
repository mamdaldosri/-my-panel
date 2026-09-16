from flask import Flask, render_template_string, request
import uuid

app = Flask(__name__)

# رابط Cloudflare Worker الثابت الخاص بك
WORKER_DOMAIN = "crimson-scene-52b4.mamdaldosri.workers.dev"

TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>لوحة إدارة بروكسي VLESS و SSH</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h2 { color: #007bff; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #28a745; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; }
        button:hover { background-color: #218838; }
        .result { margin-top: 20px; background: #e9ecef; padding: 15px; border-radius: 4px; word-break: break-all; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="container">
        <h2>لوحة التحكم الآمنة</h2>
        <form method="POST">
            <div class="form-group">
                <label for="uuid_val">معرف المستخدم (UUID):</label>
                <input type="text" id="uuid_val" name="uuid_val" value="{{ uuid_val }}" required>
            </div>
            <div class="form-group">
                <label for="config_type">نوع الإعداد:</label>
                <select id="config_type" name="config_type">
                    <option value="vless" {% if config_type == 'vless' %}selected{% endif %}>VLESS WebSocket</option>
                    <option value="ssh" {% if config_type == 'ssh' %}selected{% endif %}>SSH Tunnel</option>
                </select>
            </div>
            <button type="submit">توليد الإعدادات</button>
        </form>

        {% if config_string %}
        <div class="result">
            <h3>الإعدادات الجاهزة للنسخ (NPV Tunnel):</h3>
            <pre>{{ config_string }}</pre>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_uuid = str(uuid.uuid4())
    config_string = ""
    config_type = "vless"
    
    if request.method == 'POST':
        user_uuid = request.form.get('uuid_val', generated_uuid)
        config_type = request.form.get('config_type', 'vless')
        
        if config_type == 'vless':
            # توليد رابط الـ VLESS متوافق مع تطبيق NPV Tunnel عبر Cloudflare Worker
            config_string = f"vless://{user_uuid}@{WORKER_DOMAIN}:443?encryption=none&security=tls&sni={WORKER_DOMAIN}&type=ws&path=%2F#Cloudflare-VLESS"
        else:
            # إعدادات الـ SSH المرتبطة بالوكر
            config_string = f"SSH Proxy -> Host: {WORKER_DOMAIN} | Port: 443 | UUID: {user_uuid}"
            
        return render_template_string(TEMPLATE, uuid_val=user_uuid, config_type=config_type, config_string=config_string)
        
    return render_template_string(TEMPLATE, uuid_val=generated_uuid, config_type=config_type, config_string="")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
