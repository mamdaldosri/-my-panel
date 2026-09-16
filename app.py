from flask import Flask, render_template_string, request, redirect, url_for, Response, session, send_file
import json
import os
import io

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_me_very_secure'

DB_FILE = "database.json"
SSH_DB_FILE = "ssh_database.json"
CRED_FILE = "credentials.json"

def load_credentials():
    if os.path.exists(CRED_FILE):
        with open(CRED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"username": "admin", "password": "admin123"}

def load_accounts():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_accounts(accounts):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=4)

def load_ssh_accounts():
    if os.path.exists(SSH_DB_FILE):
        with open(SSH_DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_ssh_accounts(accounts):
    with open(SSH_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=4)

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تسجيل الدخول</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; }
        .login-card { background: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; width: 100%; max-width: 380px; text-align: right; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 5px; }
        .form-control { width: 100%; padding: 12px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; }
        .btn-primary { background: #06b6d4; color: #fff; border: none; padding: 12px; border-radius: 8px; width: 100%; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2 style="color: #38bdf8; margin-bottom: 15px;">تسجيل الدخول للوحة</h2>
        <form method="POST">
            <div class="form-group"><label>اسم المستخدم:</label><input type="text" name="username" class="form-control" required></div>
            <div class="form-group"><label>كلمة المرور:</label><input type="password" name="password" class="form-control" required></div>
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
    <title>لوحة التحكم الشاملة</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 15px; }
        .container { max-width: 650px; margin: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header h1 { font-size: 18px; color: #38bdf8; }
        .logout-btn { background: #ef444420; color: #ef4444; border: 1px solid #ef444440; padding: 6px 12px; border-radius: 8px; font-size: 12px; text-decoration: none; font-weight: bold; }
        .form-card, .account-card { background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        .form-group { margin-bottom: 10px; text-align: right; }
        .form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
        .form-control, .form-select { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #fff; font-size: 13px; }
        .row-group { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .btn-primary { background: #06b6d4; color: #fff; border: none; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 5px; }
        .account-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #38bdf8; }
        .badge-carrier { background: #3b82f620; color: #3b82f6; border: 1px solid #3b82f640; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .info-grid { font-size: 12px; color: #94a3b8; line-height: 1.6; }
        .info-grid span { color: #f1f5f9; font-family: monospace; }
        .payload-box { background: #0f172a; padding: 8px; border-radius: 6px; font-family: monospace; font-size: 11px; color: #38bdf8; word-break: break-all; margin-top: 4px; border: 1px solid #334155; }
        .actions-row { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 10px; }
        .action-btn { padding: 8px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 12px; text-align: center; border: none; text-decoration: none; display: inline-block; }
        .section-title { color: #38bdf8; font-size: 15px; margin: 20px 0 10px 0; border-bottom: 1px solid #334155; padding-bottom: 5px; }
    </style>
    <script>
        function generateUUID() {
            var d = new Date().getTime();
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = (d + Math.random()*16)%16 | 0;
                d = Math.floor(d/16);
                return (c=='x' ? r : (r&0x3|0x8)).toString(16);
            });
            document.getElementById("uuidInput").value = uuid;
        }

        function updateDefaults() {
            var carrier = document.getElementById("carrierSelect").value;
            var ipInput = document.getElementById("ipInput");
            var hostInput = document.getElementById("hostInput");

            var sshCarrier = document.getElementById("sshCarrierSelect").value;
            var sshHostInput = document.getElementById("sshHostInput");
            var wssPayloadInput = document.getElementById("wssPayloadInput");

            let currentHost = "";
            let currentIp = "de1.wssht.to";

            if (carrier === "STC") {
                ipInput.value = "172.65.90.47";
                hostInput.value = "www.pleadcourt.org";
            } else if (carrier === "Jawwy") {
                ipInput.value = "172.65.90.47";
                hostInput.value = "www.jawwy.sa";
            } else if (carrier === "Zain") {
                ipInput.value = "104.18.8.7";
                hostInput.value = "speedtest.zain.com";
            } else if (carrier === "Mobily") {
                ipInput.value = "104.18.8.7";
                hostInput.value = "www.mobily.com.sa";
            } else if (carrier === "Virgin") {
                ipInput.value = "104.18.8.7";
                hostInput.value = "www.virginmobile.sa";
            }

            if (sshCarrier === "STC") {
                currentHost = "www.pleadcourt.org";
            } else if (sshCarrier === "Jawwy") {
                currentHost = "www.jawwy.sa";
            } else if (sshCarrier === "Zain") {
                currentHost = "speedtest.zain.com";
            } else if (sshCarrier === "Mobily") {
                currentHost = "www.mobily.com.sa";
            } else if (sshCarrier === "Virgin") {
                currentHost = "www.virginmobile.sa";
            }

            sshHostInput.value = currentIp;
            wssPayloadInput.value = `GET wss://${currentHost}/ HTTP/1.1[crlf]Host: ${currentIp}[crlf]Upgrade: Websocket[crlf]Connection: Keep-Alive[crlf][crlf]`;
        }
    </script>
</head>
<body onload="updateDefaults()">
    <div class="container">
        <div class="header">
            <h1>لوحة إدارة الهوستات والسيرفرات</h1>
            <a href="/logout" class="logout-btn">خروج</a>
        </div>

        <!-- إضافة VLESS -->
        <form action="/add" method="POST" class="form-card">
            <h3 style="margin-bottom: 10px; font-size: 14px; color: #38bdf8;">+ إضافة سيرفر VLESS جديد</h3>
            <div class="row-group">
                <div class="form-group"><label>اسم الحساب:</label><input type="text" name="username" class="form-control" value="VIP-1" required></div>
                <div class="form-group">
                    <label>الشبكة (الهوست):</label>
                    <select name="carrier" id="carrierSelect" class="form-select" onchange="updateDefaults()">
                        <option value="STC">🇸🇦 سوا STC</option>
                        <option value="Jawwy">🇸🇦 جوي Jawwy</option>
                        <option value="Zain">⚡ زين Zain</option>
                        <option value="Mobily">📱 موبايلي Mobily</option>
                        <option value="Virgin">🟢 فيرجن Virgin</option>
                    </select>
                </div>
            </div>
            <div class="row-group">
                <div class="form-group"><label>عنوان السيرفر (IP):</label><input type="text" name="ip" id="ipInput" class="form-control" required></div>
                <div class="form-group"><label>الهوست (Host / Bug):</label><input type="text" name="host" id="hostInput" class="form-control" required></div>
            </div>
            <div class="form-group">
                <label>المعرّف (UUID): <button type="button" onclick="generateUUID()" style="background:#334155; color:#38bdf8; border:none; padding:2px 6px; border-radius:4px; float:left; cursor:pointer;">توليد</button></label>
                <input type="text" name="uuid" id="uuidInput" class="form-control" required>
            </div>
            <button type="submit" class="btn-primary">حفظ سيرفر VLESS</button>
        </form>

        <!-- إضافة SSH WebSocket -->
        <form action="/add-ssh" method="POST" class="form-card" style="border-color: #3b82f6;">
            <h3 style="margin-bottom: 10px; font-size: 14px; color: #3b82f6;">+ إضافة سيرفر SSH WebSocket (الأسبوعي)</h3>
            <div class="row-group">
                <div class="form-group"><label>اسم الحساب:</label><input type="text" name="username" class="form-control" value="SSH-Server-1" required></div>
                <div class="form-group">
                    <label>الشبكة:</label>
                    <select name="carrier" id="sshCarrierSelect" class="form-select" onchange="updateDefaults()">
                        <option value="STC">🇸🇦 سوا STC</option>
                        <option value="Jawwy">🇸🇦 جوي Jawwy</option>
                        <option value="Zain">⚡ زين Zain</option>
                        <option value="Mobily">📱 موبايلي Mobily</option>
                        <option value="Virgin">🟢 فيرجن Virgin</option>
                    </select>
                </div>
            </div>
            <div class="row-group">
                <div class="form-group"><label>Host / IP:</label><input type="text" name="host" id="sshHostInput" class="form-control" required></div>
                <div class="form-group"><label>Port:</label><input type="text" name="port" class="form-control" value="443" required></div>
            </div>
            <div class="row-group">
                <div class="form-group"><label>Username:</label><input type="text" name="ssh_user" class="form-control" value="sshocean-adminlor01" required></div>
                <div class="form-group"><label>Password:</label><input type="text" name="ssh_pass" class="form-control" value="adminlor01" required></div>
            </div>
            <div class="form-group"><label>تاريخ الانتهاء:</label><input type="text" name="expiry" class="form-control" value="22 Sep 2026" required></div>
            <div class="form-group"><label>HTTP Payload:</label><textarea name="payload" class="form-control" rows="2" required>GET / HTTP/1.1[crlf]Host: de1.wssht.to[crlf]Upgrade: websocket[crlf][crlf]</textarea></div>
            <div class="form-group"><label>WSS Payload:</label><textarea name="wss_payload" id="wssPayloadInput" class="form-control" rows="2" required></textarea></div>
            <button type="submit" class="btn-primary" style="background: #3b82f6;">حفظ سيرفر SSH</button>
        </form>

        <!-- عرض السيرفرات -->
        <div class="section-title">🌐 السيرفرات المخزنة</div>
        {% for acc in accounts %}
        <div class="account-card">
            <div class="account-header">
                <div><span>{{ acc.username }}</span> <span class="badge-carrier">{{ acc.carrier }}</span></div>
                <span style="font-size:11px; color:#94a3b8;">VLESS</span>
            </div>
            <div class="info-grid">
                <div>IP: <span>{{ acc.server_ip }}</span></div>
                <div>Host: <span>{{ acc.host }}</span></div>
            </div>
            <div class="actions-row">
                <a href="/download-json/{{ acc.id }}" class="action-btn" style="background:#06b6d4; color:#fff; text-decoration:none; line-height:24px;">📥 تحميل ملف JSON</a>
                <a href="/delete/{{ acc.id }}" class="action-btn" style="background:#ef444420; color:#ef4444;" onclick="return confirm('حذف؟');">🗑️ حذف</a>
            </div>
        </div>
        {% endfor %}

        {% for ssh in ssh_accounts %}
        <div class="account-card" style="border-color: #3b82f640;">
            <div class="account-header">
                <div><span style="color:#3b82f6;">{{ ssh.username }}</span> <span class="badge-carrier">{{ ssh.carrier }}</span></div>
                <span style="font-size:11px; color:#94a3b8;">SSH WSS</span>
            </div>
            <div class="info-grid">
                <div>Host: <span>{{ ssh.host }}</span> | Port: <span>{{ ssh.port }}</span></div>
                <div>User: <span>{{ ssh.ssh_user }}</span> | Pass: <span>{{ ssh.ssh_pass }}</span></div>
                <div>الانتهاء: <span style="color:#f59e0b;">{{ ssh.expiry }}</span></div>
                <div style="margin-top:4px;">WSS Payload:</div>
                <div class="payload-box">{{ ssh.wss_payload }}</div>
            </div>
            <div class="actions-row">
                <a href="/download-npvt/{{ ssh.id }}" class="action-btn" style="background:#3b82f6; color:#fff; text-decoration:none; line-height:24px;">📥 تحميل ملف npvt</a>
                <a href="/delete-ssh/{{ ssh.id }}" class="action-btn" style="background:#ef444420; color:#ef4444;" onclick="return confirm('حذف؟');">🗑️ حذف</a>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    creds = {"username": "admin", "password": "admin123"}
    if request.method == 'POST':
        if request.form.get('username') == creds['username'] and request.form.get('password') == creds['password']:
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE, accounts=load_accounts(), ssh_accounts=load_ssh_accounts())

@app.route('/add', methods=['POST'])
def add_account():
    if not session.get('logged_in'): return redirect(url_for('login'))
    accounts = load_accounts()
    u = request.form
    accounts.append({
        "id": (max([a['id'] for a in accounts]) + 1) if accounts else 1,
        "username": u.get('username'), "carrier": u.get('carrier', 'STC'),
        "server_ip": u.get('ip'), "host": u.get('host'), "uuid": u.get('uuid'),
        "config": f"vless://{u.get('uuid')}@{u.get('ip')}:443?type=ws&security=tls&host={u.get('host')}#{u.get('username')}"
    })
    save_accounts(accounts)
    return redirect(url_for('home'))

@app.route('/add-ssh', methods=['POST'])
def add_ssh_account():
    if not session.get('logged_in'): return redirect(url_for('login'))
    ssh = load_ssh_accounts()
    u = request.form
    ssh.append({
        "id": (max([s['id'] for s in ssh]) + 1) if ssh else 1,
        "username": u.get('username'), "carrier": u.get('carrier', 'STC'),
        "host": u.get('host'), "port": u.get('port'),
        "ssh_user": u.get('ssh_user'), "ssh_pass": u.get('ssh_pass'), "expiry": u.get('expiry'),
        "payload": u.get('payload'), "wss_payload": u.get('wss_payload')
    })
    save_ssh_accounts(ssh)
    return redirect(url_for('home'))

@app.route('/download-json/<int:acc_id>')
def download_json(acc_id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    accounts = load_accounts()
    acc = next((s for s in accounts if s['id'] == acc_id), None)
    if not acc: return "الملف غير موجود", 404

    # الهيكل الطويل الكامل للـ JSON الذي يحتوي على كافة التفاصيل والأسطر الأصلية
    json_structure = {
        "remarks": acc.get('username', 'VIP-Server'),
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "tag": "socks",
                "port": 10808,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True,
                    "userLevel": 8
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls"],
                    "routeOnly": False
                }
            }
        ],
        "outbounds": [
            {
                "tag": "proxy",
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": acc.get('server_ip'),
                            "port": 443,
                            "users": [
                                {
                                    "id": acc.get('uuid'),
                                    "level": 8,
                                    "encryption": "none"
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "tls",
                    "wsSettings": {
                        "path": "/vless",
                        "headers": {
                            "Host": acc.get('host')
                        }
                    },
                    "tlsSettings": {
                        "allowInsecure": True,
                        "serverName": acc.get('host'),
                        "show": False
                    }
                },
                "mux": {
                    "enabled": False,
                    "concurrency": -1,
                    "xudpConcurrency": 8,
                    "xudpProxyUDP443": ""
                }
            },
            {
                "tag": "direct",
                "protocol": "freedom",
                "settings": {
                    "domainStrategy": "UseIP"
                },
                "mux": {
                    "enabled": False,
                    "concurrency": 8,
                    "xudpConcurrency": 8,
                    "xudpProxyUDP443": ""
                }
            },
            {
                "tag": "block",
                "protocol": "blackhole",
                "settings": {
                    "response": {
                        "type": "http"
                    }
                },
                "mux": {
                    "enabled": False,
                    "concurrency": 8,
                    "xudpConcurrency": 8,
                    "xudpProxyUDP443": ""
                }
            }
        ],
        "dns": {
            "servers": ["1.1.1.1"],
            "hosts": {
                "domain:google.com": "8.8.8.8"
            }
        }
    }

    file_stream = io.BytesIO(json.dumps(json_structure, ensure_ascii=False, indent=4).encode('utf-8'))
    return send_file(file_stream, mimetype='application/json', as_attachment=True, download_name=f"{acc.get('username', 'config')}.json")

@app.route('/download-npvt/<int:acc_id>')
def download_npvt(acc_id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    ssh_list = load_ssh_accounts()
    acc = next((s for s in ssh_list if s['id'] == acc_id), None)
    if not acc: return "الملف غير موجود", 404

    npvt_data = {
        "config_version": 2,
        "remarks": acc.get('username', 'Server'),
        "server": acc.get('host'),
        "server_port": int(acc.get('port', 443)),
        "ssh_user": acc.get('ssh_user'),
        "ssh_pass": acc.get('ssh_pass'),
        "payload": acc.get('wss_payload'),
        "sni": acc.get('host')
    }

    file_stream = io.BytesIO(json.dumps(npvt_data, ensure_ascii=False, indent=4).encode('utf-8'))
    return send_file(file_stream, mimetype='application/json', as_attachment=True, download_name=f"{acc.get('username', 'config')}.npvt")

@app.route('/delete/<int:acc_id>')
def delete_account(acc_id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    save_accounts([a for a in load_accounts() if a['id'] != acc_id])
    return redirect(url_for('home'))

@app.route('/delete-ssh/<int:acc_id>')
def delete_ssh_account(acc_id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    save_ssh_accounts([s for s in load_ssh_accounts() if s['id'] != acc_id])
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
