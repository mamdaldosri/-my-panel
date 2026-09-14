from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# قائمة الخوادم المبدئية
servers = [
    {"id": 1, "name": "سيرفر الرياض - Main", "ip": "192.168.1.1", "status": "شغال"},
    {"id": 2, "name": "سيرفر جدة - Backup", "ip": "192.168.1.2", "status": "متوقف"}
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة السيرفرات</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f6f9; text-align: center; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .server-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        .status-on { color: green; font-weight: bold; }
        .status-off { color: red; font-weight: bold; }
        input, button { padding: 10px; margin: 5px; border-radius: 5px; border: 1px solid #ccc; }
        button { background-color: #28a745; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h1>لوحة إدارة السيرفرات 🚀</h1>
        
        <!-- نموذج إضافة سيرفر جديد -->
        <form action="/add" method="POST">
            <input type="text" name="name" placeholder="اسم السيرفر" required>
            <input type="text" name="ip" placeholder="عنوان IP" required>
            <button type="submit">إضافة سيرفر</button>
        </form>

        <hr>

        <!-- قائمة السيرفرات -->
        <h2>السيرفرات الحالية ({{ servers|length }})</h2>
        {% for server in servers %}
        <div class="server-card">
            <div>
                <strong>{{ server.name }}</strong> <br>
                <small>{{ server.ip }}</small>
            </div>
            <div>
                حالة السيرفر: 
                <span class="{% if server.status == 'شغال' %}status-on{% else %}status-off{% endif %}">
                    {{ server.status }}
                </span>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, servers=servers)

@app.route('/add', methods=['POST'])
def add_server():
    server_name = request.form.get('name')
    server_ip = request.form.get('ip')
    if server_name and server_ip:
        new_id = len(servers) + 1
        servers.append({"id": new_id, "name": server_name, "ip": server_ip, "status": "شغال"})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
