from flask import Flask, render_template_string, request, redirect, url_for, Response, session
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_me_very_secure'

DB_FILE = "database.json"
CRED_FILE = "credentials.json"

# تحميل بيانات الاعتماد الافتراضية
def load_credentials():
    if os.path.exists(CRED_FILE):
        with open(CRED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"username": "admin", "password": "admin123"}

def save_credentials(creds):
    with open(CRED_FILE, "w", encoding="utf-8") as f:
        json.dump(creds, f, ensure_ascii=False, indent=4)

# تحميل الحسابات من الملف الدائم
def load_accounts():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    # الحساب الافتراضي في حال عدم وجود ملف
    default_accounts = [
        {
            "id": 1,
            "username": "Germany-Zain-VIP",
            "country": "🇩🇪 ألمانيا (Frankfurt)",
            "server_ip": "104.18.8.7",
            "host": "speedtest.zain.com",
            "uuid": "12345678-abcd-1234-abcd-123456789abc",
            "carrier": "⚡ زين Zain",
            "sub_type": "غير محدود (مفتوح)",
            "status": "نشط",
            "config": "vless://12345678-abcd-1234-abcd-123456789abc@104.18.8.7:443?type=ws&security=tls&host=speedtest.zain.com#Germany-Zain-VIP"
        }
    ]
    save_accounts(default_accounts)
    return default_accounts

def save_accounts(accounts):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=4)

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - لوحة VLESS الاحترافية</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; padding: 15px; }
        .login-card { background: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; width: 100%; max-width: 380px; text-align: right; }
        .login-card h2 { color: #38bdf8; margin-bottom: 8px; font-size: 20px; }
        .login-card p { color: #94a3b8; font-size: 13px; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 5px; }
        .form-control { width: 100%; padding: 12px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; font-size: 14px; }
        .btn-primary { background: #06b6d4; color: #fff; border: none; padding: 12px; border-radius: 8px; font-size: 15px; font-weight: bold; width: 100%; cursor: pointer; }
        .error { color: #ef4444; font-size: 12px; margin-bottom: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>تسجيل الدخول للوحة</h2>
        <p>أدخل بيانات الحساب للوصول إلى إدارة السيرفرات</p>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <div class="form-group">
                <label>اسم المستخدم:</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="form-group">
                <label>كلمة المرور:</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn-primary">دخول</button>
        </form>
    </div>
</body>
</html>
'''

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة سيطرة VLESS المتكاملة</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 15px; }
        .container { max-width: 600px; margin: auto; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header h1 { font-size: 20px; font-weight: bold; color: #38bdf8; margin-bottom: 3px; }
        .header p { color: #94a3b8; font-size: 12px; }
        .logout-btn { background: #ef444420; color: #ef4444; border: 1px solid #ef444440; padding: 6px 12px; border-radius: 8px; font-size: 12px; text-decoration: none; font-weight: bold; }
        
        .top-actions { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 15px; }
        .btn-secondary { background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 8px 4px; border-radius: 8px; font-size: 11px; cursor: pointer; text-align: center; text-decoration: none; font-weight: bold; }
        
        .sub-box { background: #1e293b; border: 1px solid #334155; padding: 12px; border-radius: 10px; margin-bottom: 15px; text-align: right; }
        .sub-box label { font-size: 12px; color: #38bdf8; display: block; margin-bottom: 5px; font-weight: bold; }
        .sub-input { width: 100%; padding: 8px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; font-size: 12px; margin-bottom: 8px; }
        
        .form-card, .settings-card { background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        .form-group { margin-bottom: 10px; text-align: right; }
        .form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
        .form-control, .form-select { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; font-size: 14px; }
        
        .row-group { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        
        .btn-primary { background: #06b6d4; color: #fff; border: none; padding: 14px; border-radius: 10px; font-size: 16px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 5px; }
        .btn-primary:hover { background: #0891b2; }
        
        .btn-uuid { background: #334155; color: #38bdf8; border: 1px solid #475569; padding: 6px 10px; border-radius: 6px; font-size: 11px; cursor: pointer; float: left; font-weight: bold; }

        .account-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 12px; text-align: right; }
        .account-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .account-title { font-weight: bold; font-size: 15px; color: #38bdf8; }
        .badge-carrier { background: #3b82f620; color: #3b82f6; border: 1px solid #3b82f640; padding: 3px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; margin-right: 5px; }
        .badge-country { background: #8b5cf620; color: #a78bfa; border: 1px solid #8b5cf640; padding: 3px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; margin-right: 5px; }
        .badge-status-active { background: #10b98120; color: #10b981; border: 1px solid #10b98140; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .badge-status-inactive { background: #ef444420; color: #ef4444; border: 1px solid #ef444440; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        
        .info-grid { font-size: 12px; color: #94a3b8; line-height: 1.8; }
        .info-grid span { color: #f1f5f9; }
        
        .actions-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 6px; margin-top: 10px; }
        .action-btn { padding: 8px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px; text-align: center; border: 1px solid #475569; text-decoration: none; }
        .btn-copy { background: #334155; color: #38bdf8; }
        .btn-toggle { background: #3b82f620; color: #3b82f6; border-color: #3b82f640; }
        .btn-edit { background: #f59e0b20; color: #f59e0b; border-color: #f59e0b40; }
        .btn-delete { background: #ef444420; color: #ef4444; border-color: #ef444440; }
    </style>
    
    <script>
        function updateNetworkData(prefix = '') {
            var carrierSelect = document.getElementById(prefix + "carrierSelect");
            var ipInput = document.getElementById(prefix + "ipInput");
            var hostInput = document.getElementById(prefix + "hostInput");
            var selectedCarrier = carrierSelect.value;
            
            if (selectedCarrier.includes("سوا")) {
                ipInput.value = "172.65.90.47";
                hostInput.value = "m.youtube.com";
            } else if (selectedCarrier.includes("جوي")) {
                ipInput.value = "104.16.120.28";
                hostInput.value = "jawwy.sa";
            } else if (selectedCarrier.includes("موبايلي")) {
                ipInput.value = "104.18.38.8";
                hostInput.value = "portal.mobily.com.sa";
            } else if (selectedCarrier.includes("زين")) {
                ipInput.value = "104.18.8.7";
                hostInput.value = "speedtest.zain.com";
            } else if (selectedCarrier.includes("فيرجين")) {
                ipInput.value = "104.18.40.1";
                hostInput.value = "virginmobile.sa";
            }
        }

        function generateUUID(prefix = '') {
            var d = new Date().getTime();
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = (d + Math.random()*16)%16 | 0;
                d = Math.floor(d/16);
                return (c=='x' ? r : (r&0x3|0x8)).toString(16);
            });
            document.getElementById(prefix + "uuidInput").value = uuid;
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>لوحة سيطرة VLESS</h1>
                <p>إجمالي السيرفرات: <span style="color:#38bdf8; font-weight:bold;">{{ accounts|length }}</span></p>
            </div>
            <a href="/logout" class="logout-btn">🚪 خروج</a>
        </div>

        <div class="top-actions">
            <a href="/export/csv" class="btn-secondary">📥 CSV</a>
            <a href="/export/json" class="btn-secondary">📄 JSON</a>
            <a href="/export/txt" class="btn-secondary">📝 ملف TXT</a>
            <a href="#settings" class="btn-secondary" style="background:#334155; color:#38bdf8;">⚙️ إعدادات</a>
        </div>

        <div class="sub-box">
            <label>🔗 رابط الاشتراك (مباشر للتطبيقات):</label>
            <input type="text" class="sub-input" readonly value="{{ request.url_root }}sub" id="subLink">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <button class="action-btn btn-copy" style="background:#0891b2; color:#fff;" onclick="navigator.clipboard.writeText(document.getElementById('subLink').value); alert('تم نسخ رابط الاشتراك!');">
                    📋 نسخ الرابط الشامل
                </button>
                <button class="action-btn btn-copy" onclick="navigator.clipboard.writeText(`{{ all_configs }}`); alert('تم نسخ كافة الروابط دفعة واحدة!');">
                    📂 نسخ كافة الروابط
                </button>
            </div>
        </div>

        <!-- نموذج إضافة حساب جديد -->
        <form action="/add" method="POST" class="form-card">
            <h3 style="margin-bottom: 12px; font-size: 15px; color: #38bdf8;">+ إضافة سيرفر خارجي جديد</h3>
            
            <div class="row-group">
                <div class="form-group">
                    <label>الدولة:</label>
                    <select name="country" class="form-select">
                        <option value="🇩🇪 ألمانيا (Frankfurt)">🇩🇪 ألمانيا (Frankfurt)</option>
                        <option value="🇫🇷 فرنسا (Paris)">🇫🇷 فرنسا (Paris)</option>
                        <option value="🇳🇱 هولندا (Amsterdam)">🇳🇱 هولندا (Amsterdam)</option>
                        <option value="🇺🇸 أمريكا (New York)">🇺🇸 أمريكا (New York)</option>
                        <option value="🇸🇬 سنغافورة (Singapore)">🇸🇬 سنغافورة (Singapore)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>الشبكة (الهوست):</label>
                    <select name="carrier" id="carrierSelect" class="form-select" onchange="updateNetworkData('')">
                        <option value="⚡ زين Zain">⚡ زين Zain</option>
                        <option value="🇸🇦 سوا STC">🇸🇦 سوا STC</option>
                        <option value="🇸🇦 جوي Jawwy">🇸🇦 جوي Jawwy</option>
                        <option value="📱 موبايلي Mobily">📱 موبايلي Mobily</option>
                        <option value="🟣 فيرجن Virgin">🟣 فيرجن Virgin</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label>اسم الحساب:</label>
                <input type="text" name="username" class="form-control" placeholder="مثال: Germany-VIP-1" required>
            </div>
            
            <div class="form-group">
                <label>عنوان السيرفر (IP أو CDN):</label>
                <input type="text" name="ip" id="ipInput" class="form-control" value="104.18.8.7" required>
            </div>

            <div class="form-group">
                <label>الهوست (Host / Bug):</label>
                <input type="text" name="host" id="hostInput" class="form-control" value="speedtest.zain.com" required>
            </div>

            <div class="form-group">
                <label>المعرّف (UUID): <button type="button" class="btn-uuid" onclick="generateUUID('')">🎲 توليد</button></label>
                <input type="text" name="uuid" id="uuidInput" class="form-control" placeholder="12345678-abcd..." required>
            </div>

            <button type="submit" class="btn-primary">حفظ وربط السيرفر</button>
        </form>

        <!-- قائمة السيرفرات -->
        {% for acc in accounts %}
        <div class="account-card">
            <div class="account-header">
                <div>
                    <span class="account-title">{{ acc.username }}</span>
                    <span class="badge-country">{{ acc.country }}</span>
                    <span class="badge-carrier">{{ acc.carrier }}</span>
                </div>
                <span class="{% if acc.status == 'نشط' %}badge-status-active{% else %}badge-status-inactive{% endif %}">{{ acc.status }}</span>
            </div>
            <div class="info-grid">
                <div>IP/CDN: <span>{{ acc.server_ip }}</span></div>
                <div>Host: <span>{{ acc.host }}</span></div>
                <div>UUID: <span>{{ acc.uuid }}</span></div>
            </div>
            <div class="actions-row">
                <button class="action-btn btn-copy" onclick="navigator.clipboard.writeText('{{ acc.config }}'); alert('تم نسخ الرابط!');">
                    📋 نسخ
                </button>
                <a href="/toggle/{{ acc.id }}" class="action-btn btn-toggle">
                    🔄 الحالة
                </a>
                <a href="/edit/{{ acc.id }}" class="action-btn btn-edit">
                    ✏️ تعديل
                </a>
                <a href="/delete/{{ acc.id }}" class="action-btn btn-delete" onclick="return confirm('حذف هذا السيرفر؟');">
                    🗑️ حذف
                </a>
            </div>
        </div>
        {% endfor %}

        <!-- إعدادات تغيير كلمة المرور -->
        <div id="settings" class="settings-card" style="margin-top: 30px;">
            <h3 style="margin-bottom: 12px; font-size: 15px; color: #38bdf8;">⚙️ إعدادات حساب المشرف</h3>
            <form action="/update-credentials" method="POST">
                <div class="form-group">
                    <label>اسم المستخدم الجديد:</label>
                    <input type="text" name="new_username" class="form-control" value="{{ current_user }}" required>
                </div>
                <div class="form-group">
                    <label>كلمة المرور الجديدة:</label>
                    <input type="password" name="new_password" class="form-control" placeholder="أدخل كلمة المرور الجديدة" required>
                </div>
                <button type="submit" class="btn-primary" style="background: #3b82f6;">تحديث بيانات الدخول</button>
            </form>
        </div>

    </div>
</body>
</html>
'''

EDIT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تعديل السيرفر</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 500px; }
        .form-card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
        .form-group { margin-bottom: 12px; text-align: right; }
        .form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
        .form-control, .form-select { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; font-size: 14px; }
        .btn-primary { background: #06b6d4; color: #fff; border: none; padding: 12px; border-radius: 8px; font-size: 15px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 10px; }
        .btn-back { display: block; text-align: center; margin-top: 10px; color: #94a3b8; text-decoration: none; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <form action="/edit/{{ account.id }}" method="POST" class="form-card">
            <h3 style="margin-bottom: 15px; font-size: 18px; color: #38bdf8; text-align: right;">✏️ تعديل إعدادات السيرفر</h3>
            
            <div class="form-group">
                <label>اسم الحساب:</label>
                <input type="text" name="username" class="form-control" value="{{ account.username }}" required>
            </div>

            <div class="form-group">
                <label>الدولة:</label>
                <select name="country" class="form-select">
                    <option value="{{ account.country }}" selected>{{ account.country }} (الحالي)</option>
                    <option value="🇩🇪 ألمانيا (Frankfurt)">🇩🇪 ألمانيا (Frankfurt)</option>
                    <option value="🇫🇷 فرنسا (Paris)">🇫🇷 فرنسا (Paris)</option>
                    <option value="🇳🇱 هولندا (Amsterdam)">🇳🇱 هولندا (Amsterdam)</option>
                    <option value="🇺🇸 أمريكا (New York)">🇺🇸 أمريكا (New York)</option>
                    <option value="🇸🇬 سنغافورة (Singapore)">🇸🇬 سنغافورة (Singapore)</option>
                </select>
            </div>

            <div class="form-group">
                <label>الشبكة:</label>
                <select name="carrier" class="form-select">
                    <option value="{{ account.carrier }}" selected>{{ account.carrier }} (الحالي)</option>
                    <option value="⚡ زين Zain">⚡ زين Zain</option>
                    <option value="🇸🇦 سوا STC">🇸🇦 سوا STC</option>
                    <option value="🇸🇦 جوي Jawwy">🇸🇦 جوي Jawwy</option>
                    <option value="📱 موبايلي Mobily">📱 موبايلي Mobily</option>
                    <option value="🟣 فيرجن Virgin">🟣 فيرجن Virgin</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>عنوان السيرفر (IP):</label>
                <input type="text" name="ip" class="form-control" value="{{ account.server_ip }}" required>
            </div>

            <div class="form-group">
                <label>الهوست (Host):</label>
                <input type="text" name="host" class="form-control" value="{{ account.host }}" required>
            </div>

            <div class="form-group">
                <label>المعرّف (UUID):</label>
                <input type="text" name="uuid" class="form-control" value="{{ account.uuid }}" required>
            </div>

            <button type="submit" class="btn-primary">حفظ التعديلات</button>
            <a href="/" class="btn-back">إلغاء والعودة للرئيسية</a>
        </form>
    </div>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    creds = load_credentials()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == creds['username'] and password == creds['password']:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="اسم المستخدم أو كلمة المرور غير صحيحة!")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    accounts = load_accounts()
    # فلترة السيرفرات النشطة فقط لروابط الاشتراك الشامل
    active_configs = [acc['config'] for acc in accounts if acc['status'] == 'نشط']
    all_configs = "\\n".join(active_configs)
    creds = load_credentials()
    return render_template_string(HTML_TEMPLATE, accounts=accounts, all_configs=all_configs, current_user=creds['username'])

@app.route('/sub')
def subscription():
    accounts = load_accounts()
    active_configs = [acc['config'] for acc in accounts if acc['status'] == 'نشط']
    config_text = "\n".join(active_configs)
    return Response(config_text, mimetype='text/plain')

@app.route('/export/json')
def export_json():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    accounts = load_accounts()
    return Response(json.dumps(accounts, ensure_ascii=False, indent=4), mimetype='application/json')

@app.route('/export/csv')
def export_csv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    accounts = load_accounts()
    csv_data = "ID,Username,Country,IP,Host,UUID,Carrier,Type,Status\n"
    for acc in accounts:
        csv_data += f"{acc['id']},{acc['username']},{acc['country']},{acc['server_ip']},{acc['host']},{acc['uuid']},{acc['carrier']},{acc['sub_type']},{acc['status']}\n"
    return Response(csv_data, mimetype='text/csv')

@app.route('/export/txt')
def export_txt():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    accounts = load_accounts()
    txt_data = "\n".join([acc['config'] for acc in accounts])
    return Response(txt_data, mimetype='text/plain')

@app.route('/add', methods=['POST'])
def add_account():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    username = request.form.get('username')
    server_ip = request.form.get('ip')
    host = request.form.get('host')
    u_id = request.form.get('uuid')
    country = request.form.get('country', '🇩🇪 ألمانيا (Frankfurt)')
    carrier = request.form.get('carrier', '⚡ زين Zain')
    
    if username and server_ip and host and u_id:
        config = f"vless://{u_id}@{server_ip}:443?type=ws&security=tls&host={host}#{username}"
        accounts = load_accounts()
        new_id = (max([acc['id'] for acc in accounts]) + 1) if accounts else 1
        accounts.append({
            "id": new_id,
            "username": username,
            "country": country,
            "server_ip": server_ip,
            "host": host,
            "uuid": u_id,
            "carrier": carrier,
            "sub_type": "غير محدود (مفتوح)",
            "status": "نشط",
            "config": config
        })
        save_accounts(accounts)
    return redirect(url_for('home'))

@app.route('/delete/<int:acc_id>')
def delete_account(acc_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    accounts = load_accounts()
    accounts = [acc for acc in accounts if acc['id'] != acc_id]
    save_accounts(accounts)
    return redirect(url_for('home'))

@app.route('/toggle/<int:acc_id>')
def toggle_status(acc_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    accounts = load_accounts()
    for acc in accounts:
        if acc['id'] == acc_id:
            acc['status'] = "معطل" if acc['status'] == "نشط" else "نشط"
    save_accounts(accounts)
    return redirect(url_for('home'))

@app.route('/edit/<int:acc_id>', methods=['GET', 'POST'])
def edit_account(acc_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    accounts = load_accounts()
    account = next((acc for acc in accounts if acc['id'] == acc_id), None)
    
    if not account:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        account['username'] = request.form.get('username')
        account['country'] = request.form.get('country')
        account['carrier'] = request.form.get('carrier')
        account['server_ip'] = request.form.get('ip')
        account['host'] = request.form.get('host')
        account['uuid'] = request.form.get('uuid')
        # إعادة بناء رابط الإعدادات بالقيم الجديدة
        account['config'] = f"vless://{account['uuid']}@{account['server_ip']}:443?type=ws&security=tls&host={account['host']}#{account['username']}"
        save_accounts(accounts)
        return redirect(url_for('home'))
        
    return render_template_string(EDIT_TEMPLATE, account=account)

@app.route('/update-credentials', methods=['POST'])
def update_credentials():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    new_user = request.form.get('new_username')
    new_pass = request.form.get('new_password')
    if new_user and new_pass:
        save_credentials({"username": new_user, "password": new_pass})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
