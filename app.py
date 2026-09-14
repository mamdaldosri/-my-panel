from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json
import datetime
import random

app = Flask(__name__)
app.secret_key = 'super_secret_key_vless_panel_2026_secure'

# إعدادات المشرف الافتراضية
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin123"

# قاعدة بيانات الحسابات الشاملة بكامل الخصائص والميزات
accounts = [
    {
        "id": 1,
        "username": "STC-VIP-Ultimate",
        "uuid": "d342d11e-d424-4598-b5b5-nnn5nnn5nnn5",
        "worker": "crimson-scene-52b4.mamdaldosri.workers.dev",
        "expiry": "2026-12-31",
        "traffic_limit": "100GB",
        "traffic_used": "14.2GB",
        "status": "active",
        "created_at": "2026-09-14",
        "protocols": ["VLESS+WS+TLS", "VLESS+gRPC"]
    }
]

# واجهة لوحة التحكم الكاملة والمتقدمة مع كافة الميزات الإضافية
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم الشاملة - VLESS Manager Pro</title>
    <style>
        :root {
            --primary: #1e293b;
            --secondary: #0ea5e9;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --bg: #f1f5f9;
        }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: var(--bg); margin: 0; padding: 20px; color: #334155; }
        .container { max-width: 1100px; margin: auto; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 25px; }
        h1, h2 { color: var(--primary); margin: 0; }
        .btn { display: inline-block; background: var(--secondary); color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; transition: 0.2s; }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }
        .btn-danger { background: var(--danger); }
        .btn-success { background: var(--success); }
        .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 14px 12px; border: 1px solid #e2e8f0; text-align: center; font-size: 13px; }
        th { background-color: var(--primary); color: white; }
        tr:nth-child(even) { background-color: #f8fafc; }
        input, select { padding: 10px 14px; margin: 6px 0 15px 0; width: 100%; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; outline: none; }
        input:focus { border-color: var(--secondary); box-shadow: 0 0 0 3px rgba(14,165,233,0.15); }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .badge { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; }
        .badge-active { background: #d1fae5; color: #065f46; }
        .copy-input { font-family: monospace; font-size: 11px; background: #f1f5f9; cursor: pointer; text-align: center; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
        .stat-box { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 20px; border-radius: 12px; text-align: center; border-right: 4px solid var(--secondary); }
        .stat-box h3 { margin: 0 0 8px 0; color: #64748b; font-size: 13px; }
        .stat-box p { margin: 0; font-size: 24px; font-weight: bold; color: var(--primary); }
    </style>
</head>
<body>
    <div class="container">
        {% if session.get('logged_in') %}
            <div class="header">
                <div>
                    <h1>لوحة إدارة VLESS Pro</h1>
                    <p style="color: #64748b; margin: 5px 0 0 0;">إدارة متقدمة للحسابات، توليد الروابط التلقائية، ومراقبة الاستهلاك</p>
                </div>
                <div>
                    <a href="{{ url_for('logout') }}" class="btn btn-danger">تسجيل الخروج</a>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-box">
                    <h3>إجمالي الحسابات</h3>
                    <p>{{ accounts|length }}</p>
                </div>
                <div class="stat-box" style="border-right-color: var(--success);">
                    <h3>الحسابات النشطة</h3>
                    <p>{{ accounts | selectattr('status', 'equalto', 'active') | list | length }}</p>
                </div>
                <div class="stat-box" style="border-right-color: var(--warning);">
                    <h3>إجمالي الاستهلاك</h3>
                    <p>14.2 GB</p>
                </div>
                <div class="stat-box" style="border-right-color: #8b5cf6;">
                    <h3>حالة النظام</h3>
                    <p style="color: var(--success); font-size: 18px; margin-top: 5px;">تشغيل تام</p>
                </div>
            </div>

            <div class="card">
                <h2>إضافة حساب أو خطة جديدة</h2>
                <form method="POST" action="{{ url_for('add_account') }}">
                    <div class="form-grid">
                        <div>
                            <label>اسم المستخدم أو الوصف:</label>
                            <input type="text" name="username" placeholder="مثال: جهاز-آيفون-خاص" required>
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
                    <button type="submit" class="btn btn-success" style="width: 100%; margin-top: 10px;">إضافة الحساب وتوليد الروابط</button>
                </form>
            </div>

            <div class="card">
                <h2>سجل الحسابات والروابط الجاهزة</h2>
                <table>
                    <tr>
                        <th>الرقم</th>
                        <th>اسم المستخدم</th>
                        <th>الاستهلاك</th>
                        <th>رابط الـ VLESS (اضغط للنسخ)</th>
                        <th>الانتهاء</th>
                        <th>الحالة</th>
                        <th>التحكم</th>
                    </tr>
                    {% for acc in accounts %}
                    <tr>
                        <td><b>{{ acc.id }}</b></td>
                        <td>{{ acc.username }}</td>
                        <td><span style="color: #0284c7; font-weight: bold;">{{ acc.traffic_used }}</span> / {{ acc.traffic_limit }}</td>
                        <td>
                            <input type="text" readonly class="copy-input" value="vless://{{ acc.uuid }}@{{ acc.worker }}:443?encryption=none&security=tls&sni={{ acc.worker }}&type=ws&path=%2F#{{ acc.username }}" onclick="this.select(); document.execCommand('copy'); alert('تم نسخ رابط VLESS بنجاح!');" title="اضغط للنسخ السريع">
                        </td>
                        <td>{{ acc.expiry }}</td>
                        <td><span class="badge badge-active">{{ acc.status }}</span></td>
                        <td>
                            <a href="{{ url_for('delete_account', acc_id=acc.id) }}" class="btn btn-danger" style="padding: 6px 12px; font-size: 11px;">حذف</a>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        {% else %}
            <div style="max-width: 420px; margin: 80px auto; background: #fff; padding: 35px; border-radius: 14px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.03);">
                <h2>تسجيل الدخول للمنصة</h2>
                <p style="color: #64748b; font-size: 13px; margin-bottom: 25px;">الرجاء إدخال بيانات المشرف لإدارة لوحة التحكم</p>
                {% if error %}<p style="color: var(--danger); background: #fee2e2; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 15px;">{{ error }}</p>{% endif %}
                <form method="POST">
                    <div style="text-align: right;">
                        <label>اسم المستخدم:</label>
                        <input type="text" name="username" required>
                        <label>كلمة المرور:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn" style="width: 100%; margin-top: 15px; padding: 12px;">تسجيل الدخول</button>
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
        "traffic_limit": "100GB",
        "traffic_used": "0.0GB",
        "status": "active",
        "created_at": str(datetime.date.today()),
        "protocols": ["VLESS+WS+TLS"]
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
