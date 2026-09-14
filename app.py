from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# قائمة الحسابات والاشتراكات
accounts = [
    {
        "id": 1,
        "username": "ee1",
        "ip": "104.16.1.1",
        "host": "m.youtube.com",
        "uuid": "12345678-abcd-1234-abcd-123456789abc",
        "port": "443",
        "status": "نشط",
        "status_class": "active",
        "config": "vless://12345678-abcd-1234-abcd-123456789abc@104.16.1.1:443?type=ws&security=tls&host=m.youtube.com#ee1"
    }
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة الحسابات - VPN & SSH</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 15px; }
        .container { max-width: 600px; margin: auto; }
        
        /* Header */
        .header { margin-bottom: 20px; }
        .header h1 { font-size: 22px; font-weight: bold; margin-bottom: 5px; }
        .header p { color: #94a3b8; font-size: 13px; }
        
        /* Top Action Buttons */
        .top-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
        .btn-secondary { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; padding: 10px; border-radius: 8px; font-size: 13px; cursor: pointer; text-align: center; }
        .btn-primary { background: #06b6d4; color: #fff; border: none; padding: 14px; border-radius: 10px; font-size: 16px; font-weight: bold; width: 100%; cursor: pointer; margin-bottom: 15px; }
        
        /* Form Section */
        .form-card { background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        .form-group { margin-bottom: 10px; text-align: right; }
        .form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
        .form-control { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; font-size: 14px; }
        
        /* Filters */
        .filter-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
        .tag { background: #1e293b; color: #94a3b8; padding: 6px 12px; border-radius: 20px; font-size: 12px; border: 1px solid #334155; }
        .tag.active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
        
        /* Account Card */
        .account-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 12px; }
        .account-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .account-title { font-weight: bold; font-size: 16px; color: #38bdf8; }
        .badge-status { background: #10b98120; color: #10b981; border: 1px solid #10b98140; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        
        .info-grid { font-size: 12px; color: #94a3b8; line-height: 1.8; }
        .info-grid span { color: #f1f5f9; }
        
        .copy-btn { width: 100%; background: #334155; color: #38bdf8; border: 1px solid #475569; padding: 10px; border-radius: 8px; margin-top: 10px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>إدارة الحسابات</h1>
            <p>إدارة وحظر وتجديد اشتراكات SSH و VPN</p>
        </div>

        <!-- أزرار الإجراءات السريعة -->
        <div class="top-actions">
            <div class="btn-secondary">📥 تصدير إلى CSV</div>
            <div class="btn-secondary">📄 تصدير إلى JSON</div>
        </div>

        <!-- نموذج إضافة حساب جديد -->
        <form action="/add" method="POST" class="form-card">
            <h3 style="margin-bottom: 10px; font-size: 15px; color: #38bdf8;">+ إضافة حساب جديد</h3>
            
            <div class="form-group">
                <label>اسم المستخدم / الحساب:</label>
                <input type="text" name="username" class="form-control" placeholder="مثال: ee1" required>
            </div>
            
            <div class="form-group">
                <label>عنوان السيرفر (IP):</label>
                <input type="text" name="ip" class="form-control" placeholder="104.16.1.1" required>
            </div>

            <div class="form-group">
                <label>الهوست (Host / Bug):</label>
                <input type="text" name="host" class="form-control" placeholder="m.youtube.com" required>
            </div>

            <div class="form-group">
                <label>المعرّف (UUID):</label>
                <input type="text" name="uuid" class="form-control" placeholder="12345678-abcd..." required>
            </div>

            <button type="submit" class="btn-primary" style="margin-top: 10px; margin-bottom: 0;">حفظ الحساب</button>
        </form>

        <!-- الفلاتر -->
        <div class="filter-tags">
            <span class="tag active">الجميع</span>
            <span class="tag">🟢 عبر الإنترنت</span>
            <span class="tag">🔴 غير متصل</span>
            <span class="tag">منتهي الصلاحية</span>
        </div>

        <!-- قائمة الحسابات -->
        {% for acc in accounts %}
        <div class="account-card">
            <div class="account-header">
                <span class="account-title">{{ acc.username }}</span>
                <span class="badge-status">{{ acc.status }}</span>
            </div>
            <div class="info-grid">
                <div>IP: <span>{{ acc.ip }}</span></div>
                <div>Host: <span>{{ acc.host }}</span></div>
                <div>UUID: <span>{{ acc.uuid }}</span></div>
            </div>
            <button class="copy-btn" onclick="navigator.clipboard.writeText('{{ acc.config }}'); alert('تم نسخ رابط NPV بنجاح!');">
                📋 نسخ رابط NPV
            </button>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, accounts=accounts)

@app.route('/add', methods=['POST'])
def add_account():
    username = request.form.get('username')
    ip = request.form.get('ip')
    host = request.form.get('host')
    uuid = request.form.get('uuid')
    
    if username and ip and host and uuid:
        config = f"vless://{uuid}@{ip}:443?type=ws&security=tls&host={host}#{username}"
        new_id = len(accounts) + 1
        accounts.append({
            "id": new_id,
            "username": username,
            "ip": ip,
            "host": host,
            "uuid": uuid,
            "port": "443",
            "status": "نشط",
            "config": config
        })
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
