@app.route('/download-npvt/<int:acc_id>')
def download_npvt(acc_id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    ssh_list = load_ssh_accounts()
    acc = next((s for s in ssh_list if s['id'] == acc_id), None)
    if not acc: return "الملف غير موجود", 404

    # الهيكل المتكامل لملف الـ SSH WSS بصيغة JSON ليتوافق مع تطبيق NPV Tunnel
    json_structure = {
        "remarks": acc.get('username', 'SSH-Server'),
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
                }
            }
        ],
        "outbounds": [
            {
                "tag": "proxy",
                "protocol": "vless", # أو البروتوكول المناسب حسب دعم التطبيق للـ SSH/WSS
                "settings": {
                    "vnext": [
                        {
                            "address": acc.get('host'),
                            "port": int(acc.get('port', 443)),
                            "users": [
                                {
                                    "id": acc.get('ssh_user'), # استخدام بيانات الحساب
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
                        "path": "/",
                        "headers": {
                            "Host": acc.get('host')
                        }
                    },
                    "tlsSettings": {
                        "allowInsecure": True,
                        "serverName": acc.get('host')
                    }
                }
            },
            {
                "tag": "direct",
                "protocol": "freedom"
            },
            {
                "tag": "block",
                "protocol": "blackhole"
            }
        ],
        "ssh": {
            "username": acc.get('ssh_user'),
            "password": acc.get('ssh_pass'),
            "payload": acc.get('wss_payload')
        }
    }

    file_stream = io.BytesIO(json.dumps(json_structure, ensure_ascii=False, indent=4).encode('utf-8'))
    return send_file(file_stream, mimetype='application/octet-stream', as_attachment=True, download_name=f"{acc.get('username', 'config')}.npvt")
