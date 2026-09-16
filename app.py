from flask import Flask, render_template_string, request, redirect, url_for
import uuid
import os

app = Flask(__name__)

DEFAULT_WORKER = "crimson-scene-52b4.mamdaldosri.workers.dev"
SAVED_PROFILES = []

TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>⚡ NEXUS-X // Ultimate ISP Matrix</title>
    <style>
        :root {
            --bg-deep: #030712;
            --bg-card: rgba(15, 23, 42, 0.9);
            --border-glow: rgba(56, 189, 248, 0.35);
            --accent-cyan: #38bdf8;
            --accent-green: #34d399;
            --accent-purple: #a855f7;
            --accent-yellow: #facc15;
            --accent-red: #f43f5e;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg-deep);
            color: var(--text-main);
            margin: 0;
            padding: 15px;
            min-height: 100vh;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 20px; color: var(--accent-cyan); margin: 0; }
        .panel-card {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .section-title { font-size: 14px; font-weight: bold; color: var(--accent-cyan); margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .form-group { margin-bottom: 10px; }
        .form-group.full { grid-column: span 2; }
        label { display: block; margin-bottom: 4px; font-size: 11px; color: var(--text-muted); font-weight: bold; }
        input, select, textarea {
            width: 100%; padding: 8px; background: #030712; border: 1px solid rgba(255,255,255,0.15); color: #fff; border-radius: 6px; font-size: 12px;
        }
        textarea { font-family: monospace; height: 50px; color: var(--accent-cyan); }
        .action-btn {
            background: #2563eb; color: white; padding: 10px; border: none; border-radius: 6px; cursor: pointer; width: 100%; font-size: 13px; font-weight: bold; margin-top: 5px;
        }
        .profile-card {
            background: #030712; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px; margin-bottom: 10px;
        }
        .profile-actions { display: flex; gap: 5px; margin-top: 8px; }
        .btn-sm { padding: 5px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; cursor: pointer; border: none; text-decoration: none; text-align: center; }
        .btn-copy { background: rgba(56, 189, 248, 0.2); color: var(--accent-cyan); flex: 1; }
        .btn-download { background: rgba(52, 211, 153, 0.2); color: var(--accent-green); flex: 1; }
        .btn-delete { background: rgba(244, 63, 94, 0.2); color: var(--accent-red); }
        .badge { background: rgba(168, 85, 247, 0.2); color: var(--accent-purple); padding: 2px 6px; border-radius: 4px; font-size: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NEXUS-X // ISP MATRIX</h1>
        </div>

        <div class="panel-card">
            <div class="section-title">+ إصدار ملف بروكسي جديد</div>
            <form method="POST" action="/add">
                <div class="form-grid">
                    <div class="form-group">
                        <label>الشبكة</label>
                        <select name="network">
                            <option value="STC">STC (سوا)</option>
                            <option value="Mobily">Mobily (موبايلي)</option>
                            <option value="Jawwy">Jawwy (جوي)</option>
                            <option value="Zain">Zain (زين)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>باقة البيانات</label>
                        <select name="data_limit">
                            <option value="10 GB">10 قيقا</option>
                            <option value="50 GB">50 قيقا</option>
                            <option value="100 GB">100 قيقا</option>
                            <option value="∞ غير محدود">♾️ غير محدود</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>اسم الملف</label>
                        <input type="text" name="name" value="VIP-01" required>
                    </div>
                    <div class="form-group">
                        <label>UUID</label>
                        <input type="text" name="uuid_val" value="{{ default_uuid }}" required>
                    </div>
                    <div class="form-group full">
                        <label>رابط الوكر (Worker Domain)</label>
                        <input type="text" name="bug_host" value="{{ worker_domain }}" required>
                    </div>
                </div>
                <button type="submit" class="action-btn">🚀 إصدار وحفظ الملف</button>
            </form>
        </div>

        <div class="panel-card">
            <div class="section-title">📁 الملفات النشطة ({{ profiles|length }})</div>
            {% if not profiles %}
            <div style="text-align: center; color: var(--text-muted); font-size: 12px; padding: 10px;">لا توجد ملفات حالياً</div>
            {% endif %}
            {% for p in profiles %}
            <div class="profile-card">
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px;">
                    <div><strong style="color: var(--accent-cyan);">{{ p.name }}</strong> <span class="badge">{{ p.network }}</span> <span style="color: var(--accent-yellow); font-size: 10px;">{{ p.data_limit }}</span></div>
                    <span style="color: var(--accent-green); font-size: 11px;">نشط</span>
                </div>
                <div style="font-family: monospace; font-size: 10px; color: var(--text-muted); word-break: break-all; background: #000; padding: 5px; border-radius: 4px;">
                    {{ p.config }}
                </div>
                <div class="profile-actions">
                    <button class="btn-sm btn-copy" onclick="navigator.clipboard.writeText('{{ p.config }}'); alert('تم النسخ!');">📋 نسخ</button>
                    <a class="btn-sm btn-download" href="/download/{{ p.id }}">💾 تحميل</a>
                    <form action="/delete/{{ p.id }}" method="POST" style="margin:0;"><button type="submit" class="btn-sm btn-delete">🗑️ حذف</button></form>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE, default_uuid=str(uuid.uuid4()), worker_domain=DEFAULT_WORKER, profiles=SAVED_PROFILES)

@app.route('/add', methods=['POST'])
def add_profile():
    network = request.form.get('network', 'STC')
    data_limit = request.form.get('data_limit', '100 GB')
    name = request.form.get('name', 'VIP')
    user_uuid = request.form.get('uuid_val', str(uuid.uuid4()))
    bug_host = request.form.get('bug_host', DEFAULT_WORKER)
    
    config_str = f"vless://{user_uuid}@{bug_host}:443?encryption=none&security=tls&sni={bug_host}&type=ws&path=%2F#{network}-{name}-{data_limit}"
    
    profile_id = str(uuid.uuid4())[:8]
    SAVED_PROFILES.append({
        'id': profile_id, 'name': name, 'network': network, 'data_limit': data_limit, 'config': config_str
    })
    return redirect(url_for('index'))

@app.route('/delete/<profile_id>', methods=['POST'])
def delete_profile(profile_id):
    global SAVED_PROFILES
    SAVED_PROFILES = [p for p in SAVED_PROFILES if p['id'] != profile_id]
    return redirect(url_for('index'))

@app.render if hasattr(app, 'render') else None # Dummy placeholder

@app.route('/download/<profile_id>')
def download_profile(profile_id):
    p = next((item for item in SAVED_PROFILES if item['id'] == profile_id), None)
    if not p: return "الملف غير موجود", 404
    return p['config'], 200, {'Content-Type': 'text/plain; charset=utf-8', 'Content-Disposition': f'attachment; filename={p["name"]}.txt'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
