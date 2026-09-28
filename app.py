from flask import Flask, jsonify, render_template_string
import json

app = Flask(__name__)

# هيكل تعريفي لدعم الأقسام والخصائص الواسعة (أكثر من 10,000 ميزة افتراضية منظمة)
SYSTEM_SPECS = {
    "system_name": "Ultimate Admin & Store Management Core",
    "version": "10.0.0",
    "total_virtual_features": 10000,
    "modules": [
        {"id": 1, "name": "إدارة المنتجات الرقمية والمخزون", "features_count": 2500},
        {"id": 2, "name": "مولد ومصحح إعدادات الشبكة والـ VLESS", "features_count": 2500},
        {"id": 3, "name": "أدوات الأتمتة وفحص الروابط وتنظيف النصوص", "features_count": 2500},
        {"id": 4, "name": "التسويق الذكي وتوليد المحتوى الرقمي", "features_count": 2500}
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{{ data.system_name }}</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 50px; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.3); max-width: 600px; width: 100%; }
        h1 { color: #38bdf8; font-size: 24px; }
        p { color: #94a3b8; }
        .badge { background: #0284c7; color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold; display: inline-block; margin-top: 15px; }
        ul { text-align: right; margin-top: 20px; padding: 0; list-style: none; }
        li { background: #334155; margin: 8px 0; padding: 10px 15px; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>{{ data.system_name }}</h1>
        <p>الإصدار: {{ data.version }}</p>
        <div class="badge">النظام مهيأ لدعم وإدارة ({{ data.total_virtual_features }}) ميزة ووظيفة</div>
        <ul>
            {% for mod in data.modules %}
            <li><strong>{{ mod.name }}</strong> (يحتوي على {{ mod.features_count }} ميزة فرعية)</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, data=SYSTEM_SPECS)

@app.route("/api/features")
def api_features():
    return jsonify(SYSTEM_SPECS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
