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
    <title>لوحة إدارة بروكسي VLESS الاحترافية</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --border-color: #334155;
        }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            width: 100%;
            max-width: 650px;
            background: var(--card-bg);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
        }
        h2 {
            color: #60a5fa;
            text-align: center;
            margin-bottom: 25px;
            font-size: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #cbd5e1;
        }
        input, select {
            width: 100%;
            padding: 12px;
            box-sizing: border-box;
            background: #0f172a;
            border: 1px solid var(--border-color);
            color: #fff;
            border-radius: 8px;
            font-size: 15px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: var(--primary-color);
        }
        button {
            background-color: var(--primary-color);
            color: white;
            padding: 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            font-weight: bold;
            transition: background 0.2s;
        }
        button:hover {
            background-color: #1d4ed8;
        }
        .result {
            margin-top: 25px;
            background: #0f172a;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            word-break: break-all;
        }
        .result h3 {
            margin-top: 0;
            font-size: 16px;
            color: #38bdf8;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #1e293b;
            padding: 12px;
            border-radius: 6px;
            color: #e2e8f0;
            font-family: monospace;
            font-size: 13px;
        }
        .badge {
            display: inline-block;
            background: #065f46;
            color: #34d399;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>لوحة إدارة بروكسي VLESS</h2>
        <div style="text-align: center;">
            <span class="badge">النظام الثابت: متصل بـ Cloudflare Worker</span>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label for="uuid_val">معرف المستخدم (UUID):</label>
                <input type="text" id="uuid_val" name="uuid_val" value="{{ uuid_val }}" required>
            </div>
            <div class="form-group">
                <label for="config_type">نوع الإعداد / البروتوكول:</label>
                <select id="config_type" name="config_type">
                    <option value="vless" {% if config_type == 'vless' %}selected{% endif %}>VLESS WebSocket (TLS)</option>
                    <option value="ssh" {% if config_type == 'ssh' %}selected{% endif %}>SSH Tunnel Proxy</option>
                </select>
            </div>
            <button type="submit">توليد الإعدادات الثابتة</button>
        </form>

        {% if config_string %}
        <div class="result">
            <h3>الإعدادات الجاهزة للنسخ (متوافقة مع NPV Tunnel والتطبيقات):</h3>
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
            # الرابط الاحترافي الثابت الموجه للـ Worker
            config_string = f"vless://{user_uuid}@{WORKER_DOMAIN}:443?encryption=none&security=tls&sni={WORKER_DOMAIN}&type=ws&path=%2F#Cloudflare-VLESS-Permanent"
        else:
            config_string = f"SSH Tunnel -> Host: {WORKER_DOMAIN} | Port: 443 | UUID: {user_uuid}"
            
        return render_template_string(TEMPLATE, uuid_val=user_uuid, config_type=config_type, config_string=config_string)
        
    return render_template_string(TEMPLATE, uuid_val=generated_uuid, config_type=config_type, config_string="")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
