from flask import Flask, render_template_string, request, redirect, url_for, Response, session
import uuid
import json
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# كلمة المرور الخاصة بك كأدمن لإدارة اللوحة والبيع
ADMIN_PASSWORD = "nexus123"
DEFAULT_WORKER = "crimson-scene-52b4.mamdaldosri.workers.dev"
DB_NAME = "nexus_store.db"

# إعداد قاعدة البيانات الحقيقية (SQLite) لضمان عدم ضياع البيانات
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            name TEXT,
            network TEXT,
            data_limit TEXT,
            uuid_val TEXT,
            bug_host TEXT,
            vless_link TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>⚡ NEXUS-X // Commercial Admin Matrix</title>
    <style>
        :root {
            --bg-deep: #030712;
            --bg-card: rgba(15, 23, 42, 0.95);
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
        .container { max-width: 850px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); padding: 10px 15px; border-radius: 10px; border: 1px solid var(--border-glow); }
        .header h1 { font-size: 16px; color: var(--accent-cyan); margin: 0; }
        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px; }
        .stat-box { background: var(--bg-card); border: 1px solid var(--border-glow); padding: 10px; border-radius: 8px; text-align: center; }
        .stat-box span { display: block; font-size: 18px; font-weight: bold; color: var(--accent-cyan); }
        .stat-box label { font-size: 10px; color: var(--text-muted); }
        .panel-card {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .section-title { font-size: 13px; font-weight: bold; color: var(--accent-cyan); margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .form-group { margin-bottom: 10px; }
        .form-group.full { grid-column: span 2; }
        label { display: block; margin-bottom: 4px; font-size: 11px; color: var(--text-muted); font-weight: bold; }
        input, select {
            width: 100%; padding: 8px; background: #030712; border: 1px solid rgba(255,255,255,0.15); color: #fff; border-radius: 6px; font-size: 12px;
        }
        .action-btn {
            background: #2563eb; color: white; padding: 10px; border: none; border-radius: 6px; cursor: pointer; width: 100%; font-size: 13px; font-weight: bold; margin-top: 5px;
        }
        .btn-logout { background: var(--accent-red); color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px; text-decoration: none; }
        .profile-card {
            background: #030712; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px; margin-bottom: 10px;
        }
        .profile-actions { display: flex; gap: 5px; margin-top: 8px; flex-wrap: wrap; }
        .btn-sm { padding: 5px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; cursor: pointer; border: none; text-decoration: none; text-align: center; }
        .btn-copy { background: rgba(56, 189, 248, 0.2); color: var(--accent-cyan); flex: 1; }
        .btn-download { background: rgba(52, 211, 153, 0.2); color: var(--accent-green); flex: 1; }
        .btn-edit { background: rgba(250, 204, 21, 0.2); color: var(--accent-yellow); flex: 1; }
        .btn-delete { background: rgba(244, 63, 94, 0.2); color: var(--accent-red); }
        .badge { background: rgba(168, 85, 247, 0.2); color: var(--accent-purple); padding: 2px 6px; border-radius: 4px; font-size: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ NEXUS-X // نظام إدارة المبيعات التجارية</h1>
            <a href="/logout" class="btn-logout">تسجيل خروج</a>
        </div>

        <div class="stats-grid">
            <div class="stat-box">
                <span>{{ profiles|length }}</span>
                <label>إجمالي الملفات الصادرة</label>
            </div>
            <div class="stat-box">
                <span>نشط</span>
                <label>حالة الاتصال والسيرفر</label>
            </div>
            <div class="stat-box">
                <span>SQLite</span>
                <label>نوع قاعدة البيانات</label>
            </div>
        </div>

        <div class="panel-card">
            <div class="section-title">+ إصدار ملف بروكسي جديد للعميل</div>
            <form method="POST" action="/add">
                <div class="form-grid">
                    <div class="form-group">
                        <label>الشبكة المستهدفة</label>
                        <select name="network">
                            <option value="STC">STC (سوا)</option>
                            <option value="Mobily">Mobily (موبايلي)</option>
                            <option value="Zain">Zain (زين)</option>
                            <option value="Asia">آسيا / أسياسيل (Asia)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>باقة البيانات</label>
                        <select name="data_limit">
                            <option value="10 GB">10 قيقا</option>
                            <option value="50 GB">50 قيقا</option>
                            <option value="100 GB">100 قيقا</option>
                            <option value="Unlimited">♾️ غير محدود</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>اسم العميل / الملف</label>
                        <input type="text" name="name" placeholder="مثال: متعب-VIP" required>
                    </div>
                    <div class="form-group">
                        <label>UUID العميل</label>
                        <input type="text" name="uuid_val" value="{{ default_uuid }}" required>
                    </div>
                    <div class="form-group full">
                        <label>رابط الوكر (Worker Domain)</label>
                        <input type="text" name="bug_host" value="{{ default_worker }}" required>
                    </div>
                </div>
                <button type="submit" class="action-btn">🚀 إصدار وحفظ الملف بقاعدة البيانات</button>
            </form>
        </div>

        <div class="panel-card">
            <div class="section-title">📁 ملفات العملاء المسجلة والمحفوظة ({{ profiles|length }})</div>
            {% if not profiles %}
            <div style="text-align: center; color: var(--text-muted); font-size: 12px; padding: 10px;">لا توجد ملفات حالياً</div>
            {% endif %}
            {% for p in profiles %}
            <div class="profile-card">
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px;">
                    <div><strong style="color: var(--accent-cyan);">{{ p[1] }}</strong> <span class="badge">{{ p[2] }}</span> <span style="color: var(--accent-yellow); font-size: 10px;">{{ p[3] }}</span></div>
                    <span style="color: var(--accent-green); font-size: 11px;">محفوظ بقاعدة البيانات</span>
                </div>
                <div style="font-family: monospace; font-size: 10px; color: var(--text-muted); word-break: break-all; background: #000; padding: 6px; border-radius: 4px; max-height: 50px; overflow-y: auto;">
                    {{ p[6] }}
                </div>
                <div class="profile-actions">
                    <button class="btn-sm btn-copy" onclick="navigator.clipboard.writeText(`{{ p[6] }}`); alert('تم نسخ رابط العميل بنجاح!');">📋 نسخ</button>
                    <a class="btn-sm btn-edit" href="/edit/{{ p[0] }}">✏️ تعديل</a>
                    <a class="btn-sm btn-download" href="/download/{{ p[0] }}">💾 تحميل</a>
                    <form action="/delete/{{ p[0] }}" method="POST" style="margin:0;"><button type="submit" class="btn-sm btn-delete">🗑️</button></form>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

EDIT_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>تعديل ملف العميل // NEXUS-X</title>
    <style>
        body { font-family: system-ui; background: #030712; color: #fff; padding: 20px; }
        .box { max-width: 500px; margin: 0 auto; background: rgba(15, 23, 42, 0.95); padding: 20px; border-radius: 10px; border: 1px solid #38bdf8; }
        input, select { width: 100%; padding: 8px; margin-bottom: 10px; background: #000; border: 1px solid #333; color: #fff; border-radius: 5px; }
        button { background: #2563eb; color: #fff; padding: 10px; width: 100%; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h3>✏️ تعديل بيانات الملف للعميل</h3>
        <form method="POST">
            <label>اسم العميل / الملف</label>
            <input type="text" name="name" value="{{ profile[1] }}" required>
            <label>الشبكة</label>
            <select name="network">
                <option value="STC" {% if profile[2] == 'STC' %}selected{% endif %}>STC</option>
                <option value="Mobily" {% if profile[2] == 'Mobily' %}selected{% endif %}>Mobily</option>
                <option value="Zain" {% if profile[2] == 'Zain' %}selected{% endif %}>Zain</option>
                <option value="Asia" {% if profile[2] == 'Asia' %}selected{% endif %}>Asia</option>
            </select>
            <label>باقة البيانات</label>
            <select name="data_limit">
                <option value="10 GB" {% if profile[3] == '10 GB' %}selected{% endif %}>10 قيقا</option>
                <option value="50 GB" {% if profile[3] == '50 GB' %}selected{% endif %}>50 قيقا</option>
                <option value="100 GB" {% if profile[3] == '100 GB' %}selected{% endif %}>100 قيقا</option>
                <option value="Unlimited" {% if profile[3] == 'Unlimited' %}selected{% endif %}>غير محدود</option>
            </select>
            <label>UUID</label>
            <input type="text" name="uuid_val" value="{{ profile[4] }}" required>
            <label>رابط الوكر (Worker)</label>
            <input type="text" name="bug_host" value="{{ profile[5] }}" required>
            <button type="submit">💾 حفظ التعديلات</button>
        </form>
    </div>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>تسجيل دخول الأدمن // NEXUS-X</title>
    <style>
        body { font-family: system-ui; background: #030712; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: rgba(15, 23, 42, 0.95); padding: 25px; border-radius: 12px; border: 1px solid #38bdf8; width: 320px; text-align: center; }
        input { width: 100%; padding: 10px; margin: 15px 0; background: #000; border: 1px solid #333; color: #fff; border-radius: 6px; }
        button { background: #2563eb; color: #fff; padding: 10px; width: 100%; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .error { color: #f43f5e; font-size: 11px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h3>🔐 لوحة تحكم الأدمن</h3>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="أدخل كلمة مرور الأدمن" required>
            <button type="submit">دخول النظام</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = "كلمة المرور غير صحيحة!"
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles")
    profiles = cursor.fetchall()
    conn.close()
    
    return render_template_string(TEMPLATE, default_uuid=str(uuid.uuid4()), default_worker=DEFAULT_WORKER, profiles=profiles)

@app.route('/add', methods=['POST'])
def add_profile():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    network = request.form.get('network', 'STC')
    data_limit = request.form.get('data_limit', '100 GB')
    name = request.form.get('name', 'Client')
    user_uuid = request.form.get('uuid_val', str(uuid.uuid4()))
    bug_host = request.form.get('bug_host', DEFAULT_WORKER).strip()
    
    if "://" in bug_host:
        bug_host = bug_host.split("://")[1].split("/")[0]

    vless_link = f"vless://{user_uuid}@{bug_host}:443?encryption=none&security=tls&sni={bug_host}&type=ws&path=%2F#{network}-{name}-{data_limit}"
    
    profile_id = str(uuid.uuid4())[:8]
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO profiles VALUES (?, ?, ?, ?, ?, ?, ?)", 
                   (profile_id, name, network, data_limit, user_uuid, bug_host, vless_link))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/edit/<profile_id>', methods=['GET', 'POST'])
def edit_profile(profile_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        network = request.form.get('network')
        data_limit = request.form.get('data_limit')
        user_uuid = request.form.get('uuid_val')
        bug_host = request.form.get('bug_host').strip()
        
        if "://" in bug_host:
            bug_host = bug_host.split("://")[1].split("/")[0]
            
        vless_link = f"vless://{user_uuid}@{bug_host}:443?encryption=none&security=tls&sni={bug_host}&type=ws&path=%2F#{network}-{name}-{data_limit}"
        
        cursor.execute("UPDATE profiles SET name=?, network=?, data_limit=?, uuid_val=?, bug_host=?, vless_link=? WHERE id=?",
                       (name, network, data_limit, user_uuid, bug_host, vless_link, profile_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
        
    cursor.execute("SELECT * FROM profiles WHERE id=?", (profile_id,))
    profile = cursor.fetchone()
    conn.close()
    
    if not profile:
        return "الملف غير موجود", 404
        
    return render_template_string(EDIT_TEMPLATE, profile=profile)

@app.route('/delete/<profile_id>', methods=['POST'])
def delete_profile(profile_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiles WHERE id=?", (profile_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/download/<profile_id>')
def download_profile(profile_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE id=?", (profile_id,))
    p = cursor.fetchone()
    conn.close()
    
    if not p: return "الملف غير موجود", 404
    return Response(
        p[6],
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment;filename={p[1]}_{p[2]}.txt"}
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
