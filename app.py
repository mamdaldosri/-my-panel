from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json
import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_me_to_something_very_secure'

# إعدادات المشرف الافتراضية
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin123"

# قاعدة بيانات الحسابات الشاملة
accounts = [
    {
        "id": 1,
        "username": "STC-VIP-01",
        "uuid": "d342d11e-d424-4598-b5b5-nnn5nnn5nnn5",
        "worker": "crimson-scene-52b4.mamdaldosri.workers.dev",
        "expiry": "2026-12-31",
        "traffic_limit": "50GB",
        "status": "active",
        "created_at": "2026-09-14"
    }
]

# واجهة لوحة التحكم الكاملة والمتقدمة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم VLESS المتقدمة</title>
    <style>
        :root {
            --primary-color: #2c3e50;
            --accent-color: #3498db;
            --success-color: #2ecc71;
            --danger-color: #e74c3c;
            --bg-color: #f8f9fa;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg-color); margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1050px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
        .header-flex { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 25px; }
        h1, h2 { color: var(--primary-color); margin: 0; }
        .btn { display: inline-block; background: var(--accent-color); color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; transition: background 0.2s; }
        .btn:hover { opacity: 0.9; }
        .btn-danger { background: var(--danger-color); }
        .btn-success { background: var(--success-color); }
        .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 14px 12px; border: 1px solid #edf2f7; text-align: center; font-size: 14px; }
        th { background-color: var(--primary-color); color: white; }
        tr:nth-child(even) { background-color: #fcfcfc; }
        input, select { padding: 10px 12px; margin: 6px 0 15px 0; width: 100%; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .full-width { grid-column: span 2; }
        .badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; }
        .badge-active { background: #dcfce7; color: #166534; }
        .badge-expired { background: #fee2e2; color: #991b1b; }
        .copy-input { font-family: monospace; font-size: 11px; background: #f1f5f9; cursor: pointer; }
        .stats-box { display: flex; gap: 15px; margin-bottom: 25px; }
        .stat-card { flex: 1; background: #eef2f7; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-card h3 { margin: 0 0 5px 0; color: #555; font-size: 14px; }
        .stat-card p { margin: 0; font-size: 22px; font-weight: bold; color: var(--primary-color); }
    </style>
</head>
<body>
    <div class="container">
        {% if session.get('logged_in') %}
            <div class="header-flex">
                <div>
                    <h1>لوحة تحكم VLESS الذكية</h1>
                    <p style="color: #64748b; margin: 5px 0 0 0;">إدارة متقدمة، توليد روابط فورية، ومراقبة الحسابات</p>
                </div>
                <div>
                    <a href="{{ url_for('logout') }}" class="btn btn-danger">تسجيل الخروج</a>
                </div>
            </div>

            <div class="stats-box">
                <div class="stat-card">
                    <h3>إجمالي الحسابات</h3>
                    <p>{{ accounts|length }}</p>
                </div>
                <div class="stat-card">
                    <h3>الحسابات النشطة</h3>
                    <p>{{ accounts | selectattr('status', 'equalto', 'active') | list | length }}</p>
                </div>
                <div class="stat-card">
                    <h3>حالة الخادم</h3>
                    <p style="color: var(--success-color); font-size: 18px; margin-top: 5px;">متصل وفعّال</p>
                </div>
            </div>

            <div class="card">
                <h2>إضافة حساب أو خطة جديدة</h2>
                <form method="POST" action="{{ url_for('add_account') }}">
                    <div class="form-grid">
                        <div>
                            <label>اسم المستخدم / الوصف:</label>
                            <input type="text" name="username" placeholder="مثال: جهاز-محمد-آيفون" required>
                        </div>
                        <div>
                            <label>معرف الـ UUID:</label>
                            <input type="text" name="uuid" value="d342d11e-d424-4598-b5b5-nnn5nnn5nnn5" required>
                        </div>
                        <div>
                            <label>رابط الـ Worker:</label>
                            <input type="text" name="worker" value="crimson-scene-52b4.mamdaldosri.workers.dev" required>
                        </div>
                        <div>
                            <label>تاريخ الانتهاء:</label>
                            <input type="date" name="expiry" value="2026-12-31" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-success" style="width: 100%; margin-top: 10px;">إضافة وحفظ الحساب</button>
                </form>
            </div>

            <div class="card">
                <h2>سجل الحسابات والروابط الجاهزة</h2>
                <table>
                    <tr>
                        <th>الرقم</th>
                        <th>اسم المستخدم</th>
                        <th>رابط الـ VLESS (اضغط للنسخ)</th>
                        <th>الانتهاء</th>
                        <th>الحالة</th>
                        <th>إجراءات</th>
                    </tr>
                    {% for acc in accounts %}
                    <tr>
                        <td>{{ acc.id }}</td>
                        <td><b>{{ acc.username }}</b></td>
                        <td>
                            <input type="text" readonly class="copy-input" value="vless://{{ acc.uuid }}@{{ acc.worker }}:443?encryption=none&security=tls&sni={{ acc.worker }}&type=ws&path=%2F#{{ acc.username }}" onclick="this.select(); document.execCommand('copy'); alert('تم نسخ الرابط بنجاح!');">
                        </td>
                        <td>{{ acc.expiry }}</td>
                        <td>
                            <span class="badge badge-active">{{ acc.status }}</span>
                        </td>
                        <td>
                            <a href="{{ url_for('delete_account', acc_id=acc.id) }}" class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;">حذف</a>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        {% else %}
            <div style="max-width: 420px; margin: 60px auto; background: #fff; padding: 30px; border-radius: 10px; border: 1px solid #e2e8f0; text-align: center;">
                <h2>تسجيل الدخول للمنصة</h2>
                <p style="color: #64748b; font-size: 13px; margin-bottom: 20px;">الرجاء إدخال بيانات المشرف للمتابعة</p>
                {% if error %}<p style="color: var(--danger-color); background: #fee2e2; padding: 10px; border-radius: 6px; font-size: 13px;">{{ error }}</p>{% endif %}
                <form method="POST">
                    <div style="text-align: right;">
                        <label>اسم المستخدم:</label>
                        <input type="text" name="username" required>
                        <label>كلمة المرور:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn" style="width: 100%; margin-top: 15px;">تسجيل الدخول</button>
                </form>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USER and request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'اسم المستخدم أو كلمة المرور غير صحيحة!'
    return render_template_string(HTML_TEMPLATE, accounts=accounts, error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE, accounts=accounts)

@app.route('/add', methods=['POST'])
def add_account():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    new_id = len(accounts) + 1
    new_acc = {
        "id": new_id,
        "username": request.form.get('username'),
        "uuid": request.form.get('uuid'),
        "worker": request.form.get('worker'),
        "expiry": request.form.get('expiry'),
        "traffic_limit": "غير محدود",
        "status": "active",
        "created_at": str(datetime.date.today())
    }
    accounts.append(new_acc)
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:acc_id>')
def delete_account(acc_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    global accounts
    accounts = [acc for acc in accounts if acc['id'] != acc_id]
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
