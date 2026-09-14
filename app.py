from flask import Flask, render_template_string, request, redirect, url_for, Response
import json

app = Flask(__name__)

# قائمة الحسابات الافتراضية
accounts = [
    {
        "id": 1,
        "username": "STC-VIP",
        "ip": "172.65.90.47",
        "host": "m.youtube.com",
        "uuid": "12345678-abcd-1234-abcd-123456789abc",
        "carrier": "🇸🇦 سوا STC",
        "sub_type": "غير محدود (مفتوح)",
        "status": "نشط",
        "config": "vless://12345678-abcd-1234-abcd-123456789abc@172.65.90.47:443?type=ws&security=tls&host=m.youtube.com#STC-VIP"
    }
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة سيطرة VLESS الاحترافية</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 15px; }
        .container { max-width: 600px; margin: auto; }
        
        .header { margin-bottom: 20px; }
        .header h1 { font-size: 22px; font-weight: bold; margin-bottom: 5px; color: #38bdf8; }
        .header p { color: #94a3b8; font-size: 13px; }
        
        .top-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; }
        .btn-secondary { background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 10px; border-radius: 8px; font-size: 13px; cursor: pointer; text-align: center; text-decoration: none; font-weight: bold; }
        
        .sub-box { background: #1e293b; border: 1px solid #334155; padding: 12px; border-radius: 10px; margin-bottom: 15px; text-align: right; }
        .sub-box label { font-size: 12px; color: #38bdf8; display: block; margin-bottom: 5px; font-weight: bold; }
        .sub-input { width: 100%; padding: 8px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; font-size: 12px; margin-bottom: 8px; }
        
        .form-card { background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        .form-group { margin-bottom: 10px; text-align: right; }
        .form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
        .form-control, .form-select { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; font-size: 14px; }
        
        .btn-primary { background: #06b6d4; color: #fff; border: none; padding: 14px; border-radius: 10px; font-size: 16px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 5px; }
        .btn-primary:hover { background: #0891b2; }

        .account-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 12px; text-align: right; }
        .account-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .account-title { font-weight: bold; font-size: 16px; color: #38bdf8; }
        .badge-carrier { background: #3b82f620; color: #3b82f6; border: 1px solid #3b82f640; padding: 3px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; margin-right: 5px; }
        .badge-status { background: #10b98120; color: #10b981; border: 1px solid #10b98140; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        
        .info-grid { font-size: 12px; color: #94a3b8; line-height: 1.8; }
        .info-grid span { color: #f1f5f9; }
        
        .copy-btn { width: 100%; background: #334155; color: #38bdf8; border: 1px solid #475569; padding: 10px; border-radius: 8px; margin-top: 10px; font-weight: bold; cursor: pointer; }
    </style>
    
    <script>
        // دالة تعبئة الآيباد والهوست أوتوماتيكياً حسب اختيار الشركة
        function updateNetworkData() {
            var select = document.getElementById("carrierSelect");
            var ipInput = document.getElementById("ipInput");
            var hostInput = document.getElementById("hostInput");
            var selectedValue = select.value;
            
            if (selectedValue.includes("سوا")) {
                ipInput.value = "172.65.90.47";
                hostInput.value = "m.youtube.com";
            } else if (selectedValue.includes("جوي")) {
                ipInput.value = "104.16.120.28";
                hostInput.value = "jawwy.sa";
            } else if (selectedValue.includes("موبايلي")) {
                ipInput.value = "104.18.38.8";
                hostInput.value = "portal.mobily.com.sa";
            } else if (selectedValue.includes("زين")) {
                ipInput.value = "";
                hostInput.value = "speedtest.zain.com";
            } else if (selectedValue.includes("فيرجين")) {
                ipInput.value = "";
                hostInput.value = "virginmobile.sa";
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>لوحة سيطرة VLESS</h1>
            <p>إدارة الآيبادات والهوستات لكل الشبكات ورابط الاشتراك الشامل</p>
        </div>

        <div class="top-actions">
            <a href="/export/csv" class="btn-secondary">📥 تصدير إلى CSV</a>
            <a href="/export/json" class="btn-secondary">📄 تصدير إلى JSON</a>
        </div>

        <!-- صندوق رابط الاشتراك الشامل -->
        <div class="sub-box">
            <label>🔗 رابط الاشتراك الشامل لتحديث كل السيرفرات بالتطبيق:</label>
            <input type="text" class="sub-input" readonly value="{{ request.url_root }}sub" id="subLink">
            <button class="copy-btn" style="margin-top:0; background:#0891b2;" onclick="navigator.clipboard.writeText(document.getElementById('subLink').value); alert('تم نسخ رابط الاشتراك الشامل!');">
                📋 نسخ رابط الاشتراك الشامل
            </button>
        </div>

        <!-- نموذج إضافة حساب مع اختيار شبكة الاتصال -->
        <form action="/add" method="POST" class="form-card">
            <h3 style="margin-bottom: 12px; font-size: 15px; color: #38bdf8;">+ إضافة حساب وإعدادات الشبكة</h3>
            
            <div class="form-group">
                <label>اختر شبكة الاتصال (تعبئة الـ IP والهوست أوتوماتيكياً):</label>
                <select name="carrier" id="carrierSelect" class="form-select" onchange="updateNetworkData()">
                    <option value="🇸🇦 سوا STC">🇸🇦 سوا STC (آيباد: 172.65.90.47)</option>
                    <option value="🇸🇦 جوي Jawwy">🇸🇦 جوي Jawwy (آيباد: 104.16.120.28)</option>
                    <option value="🇸🇦 موبايلي Mobily">🇸🇦 موبايلي Mobily (آيباد: 104.18.38.8)</option>
                    <option value="🇸🇦 زين Zain">🇸🇦 زين Zain</option>
                    <option value="🇸🇦 فيرجن Virgin">🇸🇦 فيرجن Virgin</option>
                </select>
            </div>

            <div class="form-group">
                <label>اسم المستخدم / الحساب:</label>
                <input type="text" name="username" class="form-control" placeholder="مثال: STC-VIP" required>
            </div>
            
            <div class="form-group">
                <label>عنوان السيرفر (IP):</label>
                <input type="text" name="ip" id="ipInput" class="form-control" value="172.65.90.47" placeholder="172.65.90.47" required>
            </div>

            <div class="form-group">
                <label>الهوست (Host / Bug / SNI):</label>
                <input type="text" name="host" id="hostInput" class="form-control" value="m.youtube.com" placeholder="m.youtube.com" required>
            </div>

            <div class="form-group">
                <label>المعرّف (UUID):</label>
                <input type="text" name="uuid" class="form-control" placeholder="12345678-abcd..." required>
            </div>

            <div class="form-group">
                <label>نوع الاشتراك:</label>
                <select name="sub_type" class="form-select">
                    <option value="غير محدود (مفتوح)">غير محدود (مفتوح دائماً)</option>
                    <option value="محدد (باقة مؤقتة)">محدد بمدة أو بيانات</option>
                </select>
            </div>

            <button type="submit" class="btn-primary">حفظ وإضافة الحساب</button>
        </form>

        <!-- عرض الحسابات -->
        {% for acc in accounts %}
        <div class="account-card">
            <div class="account-header">
                <div>
                    <span class="account-title">{{ acc.username }}</span>
                    <span class="badge-carrier">{{ acc.carrier }}</span>
                </div>
                <span class="badge-status">{{ acc.status }}</span>
            </div>
            <div class="info-grid">
                <div>IP: <span>{{ acc.ip }}</span></div>
                <div>Host: <span>{{ acc.host }}</span></div>
                <div>UUID: <span>{{ acc.uuid }}</span></div>
            </div>
            <button class="copy-btn" onclick="navigator.clipboard.writeText('{{ acc.config }}'); alert('تم نسخ رابط السيرفر الفردي!');">
                📋 نسخ رابط NPV الفردي
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

@app.route('/sub')
def subscription():
    config_text = "\n".join([acc['config'] for acc in accounts])
    return Response(config_text, mimetype='text/plain')

@app.route('/export/json')
def export_json():
    return Response(json.dumps(accounts, ensure_ascii=False, indent=4), mimetype='application/json')

@app.route('/export/csv')
def export_csv():
    csv_data = "Username,IP,Host,UUID,Carrier,Type,Status\n"
    for acc in accounts:
        csv_data += f"{acc['username']},{acc['ip']},{acc['host']},{acc['uuid']},{acc['carrier']},{acc['sub_type']},{acc['status']}\n"
    return Response(csv_data, mimetype='text/csv')

@app.route('/add', methods=['POST'])
def add_account():
    username = request.form.get('username')
    ip = request.form.get('ip')
    host = request.form.get('host')
    uuid = request.form.get('uuid')
    carrier = request.form.get('carrier', '🇸🇦 سوا STC')
    sub_type = request.form.get('sub_type', 'غير محدود (مفتوح)')
    
    if username and ip and host and uuid:
        config = f"vless://{uuid}@{ip}:443?type=ws&security=tls&host={host}#{username}"
        new_id = len(accounts) + 1
        accounts.append({
            "id": new_id,
            "username": username,
            "ip": ip,
            "host": host,
            "uuid": uuid,
            "carrier": carrier,
            "sub_type": sub_type,
            "status": "نشط",
            "config": config
        })
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
