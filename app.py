from flask import Flask, render_template_string, request
import uuid

app = Flask(__name__)

# رابط Cloudflare Worker الثابت الأساسي
DEFAULT_WORKER = "crimson-scene-52b4.mamdaldosri.workers.dev"

TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>⚡ NEXUS-X // Advanced Proxy Matrix Control</title>
    <style>
        :root {
            --bg-deep: #030712;
            --bg-card: rgba(15, 23, 42, 0.75);
            --border-glow: rgba(56, 189, 248, 0.3);
            --accent-cyan: #38bdf8;
            --accent-green: #34d399;
            --accent-purple: #a855f7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; transition: all 0.25s ease; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.08) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.08) 0px, transparent 50%);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 750px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 25px;
        }
        .header h1 {
            font-size: 26px;
            background: linear-gradient(to right, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 5px 0;
            letter-spacing: 1px;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(6, 95, 70, 0.4);
            border: 1px solid rgba(52, 211, 153, 0.3);
            color: var(--accent-green);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            box-shadow: 0 0 15px rgba(52, 211, 153, 0.1);
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-green);
            animation: pulse 1.5px infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 12px var(--accent-green); }
            100% { transform: scale(0.95); opacity: 0.8; }
        }
        
        /* Navigation Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: rgba(15, 23, 42, 0.6);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid var(--border-glow);
        }
        .tab-btn {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 10px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }
        .tab-btn.active {
            background: var(--accent-cyan);
            color: #030712;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }

        .panel-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .section-title {
            font-size: 16px;
            font-weight: bold;
            color: var(--accent-cyan);
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding-bottom: 10px;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group.full {
            grid-column: span 2;
        }
        label {
            display: block;
            margin-bottom: 6px;
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        input, select, textarea {
            width: 100%;
            padding: 11px 14px;
            background: rgba(3, 7, 18, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            border-radius: 8px;
            font-size: 13px;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
        }
        textarea {
            font-family: monospace;
            height: 75px;
            resize: vertical;
            font-size: 11px;
            color: #38bdf8;
        }
        .action-btn {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            padding: 13px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            font-size: 15px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
            margin-top: 5px;
        }
        .action-btn:hover {
            opacity: 0.95;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
            transform: translateY(-1px);
        }
        .secondary-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            font-weight: bold;
        }
        .secondary-btn:hover {
            background: rgba(255, 255, 255, 0.12);
        }

        /* Result Matrix Box */
        .matrix-output {
            background: rgba(3, 7, 18, 0.95);
            border: 1px solid var(--accent-green);
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 0 25px rgba(52, 211, 153, 0.15);
        }
        .matrix-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .matrix-title {
            color: var(--accent-green);
            font-weight: bold;
            font-size: 14px;
        }
        pre {
            background: #020617;
            padding: 12px;
            border-radius: 8px;
            color: #e2e8f0;
            font-family: monospace;
            font-size: 11px;
            word-break: break-all;
            white-space: pre-wrap;
            border: 1px solid rgba(255,255,255,0.05);
            max-height: 120px;
            overflow-y: auto;
            margin: 0 0 15px 0;
        }
        .matrix-actions {
            display: flex;
            gap: 10px;
        }
        .matrix-actions button {
            flex: 1;
        }
