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
    <title>لوحة إدارة الهوستات والسيرفرات</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --border-color: #334155;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --badge-bg: #065f46;
            --badge-text: #34d399;
        }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 15px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        h2 {
            color: #60a5fa;
            text-align: center;
            font-size: 20px;
            margin-bottom: 15px;
        }
        .badge {
            display: block;
            text-align: center;
            background: var(--badge-bg);
            color: var(--badge-text);
            padding: 6px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-ضيف: 12px;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .card-title {
            font-size: 16px;
            font-weight: bold;
            color: #38bdf8;
            margin-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }
        .form-group {
            margin-bottom: 12px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-size: 13px;
            color: #cbd5e1;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            box-sizing: border-box;
            background: #0f172a;
            border: 1px solid var(--border-color);
            color: #fff;
            border-radius: 6px;
            font-size: 14px;
        }
        textarea {
            font-family: monospace;
            font-size: 12px;
            height: 70px;
            resize: vertical;
        }
        .row {
            display: flex;
            gap: 10px;
        }
        .col {
            flex: 1;
        }
        button {
            background-color: var(--primary);
            color: white;
            padding: 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            font-size: 15px;
            font-weight: bold;
            transition: background 0.2s;
            margin-top: 10px;
        }
        button:hover {
            background-color: var(--primary-hover);
        }
        .result-box {
            background: #0f172a;
            border: 1px solid var(--border-color);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #1e293b;
            padding: 10px;
            border-radius: 6px;
            color: #38bdf8;
            font-size: 12px;
            margin: 5px 0 0 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>لوحة إدارة الهوستات والسيرفرات</h2>
        <span class="badge">متصل بنظام Cloudflare Worker الثابت</span>

        <form method="POST">
            <!-- قسم VLESS -->
            <div class="card">
                <div class="card-title">+ إضافة سيرفر VLESS جديد</div>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>الشبكة / الباقة</label>
                            <input type="text" name="net_type" value="سوا STC">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>اسم السيرفر</label>
                            <input type="text" name="server_name" value="VIP-1">
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label>هوست السيرفر (Bug / Host)</label>
                    <input type="text" name="bug_host" value="{{ worker_domain }}">
                </div>
                <div class="form-group">
                    <label>معرف المستخدم (UUID)</label>
                    <input type="text" name="uuid_val" value="{{ uuid_val }}">
                </div>
                <div class="form-group">
                    <label>HTTP Payload</label>
                    <textarea name="http_payload">GET / HTTP/1.1[crlf]Host: {{ worker_domain }}[crlf]Upgrade: websocket[crlf][crlf]</textarea>
                </div>
                <div class="form-group">
                    <label>WSS Payload</label>
                    <textarea name="wss_payload">GET wss://{{ worker_domain }} HTTP/1.1[crlf]Host: {{ worker_domain }}[crlf]Upgrade: websocket[crlf]Connection: Upgrade[crlf][crlf]</textarea>
                </div>
                <button type="submit" name="action_type" value="vless">حفظ سيرفر VLESS</button>
            </div>

            <!-- قسم SSH -->
            <div class="card">
                <div class="card-title">+ إضافة سيرفر SSH WebSocket (اختياري)</div>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>الشبكة</label>
                            <input type="text" name="ssh_net" value="سوا STC">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>اسم السيرفر</label>
                            <input type="text" name="ssh_name" value="SSH-Server-1">
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>Host / IP</label>
                            <input type="text" name="ssh_host" value="{{ worker_domain }}">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>Port</label>
                            <input type="text" name="ssh_port" value="443">
                        </div>
                    </div>
                </div>
                <button type="submit" name="action_type" value="ssh">حفظ سيرفر SSH</button>
            </div>
        </form>

        {% if generated_config %}
        <div class="card">
            <div class="card-title" style="color: #34d399;">تم التوليد بنجاح</div>
            <div class="result-box">
                <label style="color: #38bdf8; font-weight: bold;">الإعداد الناتج للاستخدام:</label>
                <pre>{{ generated_config }}</pre>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    default_uuid = str(uuid.uuid4())
    generated_config = ""
    
    if request.method == 'POST':
        action_type = request.form.get('action_type')
        user_uuid = request.form.get('uuid_val', default_uuid)
        bug_host = request.form.get('bug_host', WORKER_DOMAIN)
        
        if action_type == 'vless':
            # بناء رابط VLESS المتقدم المتوافق مع التطبيق مع دمج الهوست الثابت
            generated_config = f"vless://{user_uuid}@{bug_host}:443?encryption=none&security=tls&sni={bug_host}&type=ws&path=%2F#Cloudflare-VLESS-Pro"
        elif action_type == 'ssh':
            ssh_host = request.form.get('ssh_host', WORKER_DOMAIN)
            ssh_port = request.form.get('ssh_port', '443')
            generated_config = f"SSH Tunnel -> Host: {ssh_host} | Port: {ssh_port} | UUID/User: {user_uuid}"
            
        return render_template_string(TEMPLATE, uuid_val=user_uuid, worker_domain=WORKER_DOMAIN, generated_config=generated_config)
        
    return render_template_string(TEMPLATE, uuid_val=default_uuid, worker_domain=WORKER_DOMAIN, generated_config="")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
