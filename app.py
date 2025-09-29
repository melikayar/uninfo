from flask import Flask, render_template, request, Response
import json, os, traceback, logging
from pathlib import Path
from jinja2 import TemplateNotFound

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

logging.basicConfig(level=logging.INFO)

# ---- safe loaders ----
def _load_json(rel_path):
    path = os.path.join(BASE_DIR, rel_path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        app.logger.error(f"JSON not found: {path}")
        return []
    except Exception as e:
        app.logger.error(f"JSON parse error in {path}: {e}")
        return []

def load_departments():
    return _load_json(os.path.join("data", "departments.json"))

def load_departments_farsi():
    return _load_json(os.path.join("data", "departments_farsi.json"))

# ---- routes ----
# ---- routes ----
from flask import redirect, url_for, render_template, request
from jinja2 import TemplateNotFound
import traceback

# 1) ریشه سایت → ریدایرکت دائمی به /home (برای سئو هم بهتره)
@app.route("/")
def root():
    return redirect(url_for("home"), code=301)

# 2) صفحه Home
@app.route("/home")
def home():
    try:
        # اگر نسخهٔ فارسی داری، اول همونو رندر کن
        try:
            return render_template("home.farsi.html")
        except TemplateNotFound:
            return render_template("home.html")
    except Exception:
        app.logger.error("home() failed:\n" + traceback.format_exc())
        return "Internal error", 500

# 3) صفحه «رشته‌ها» (همون منطقی که قبلاً در / بود)
@app.route("/reshteha")
def majors():
    try:
        deps = load_departments_farsi()
        q = (request.args.get("q") or "").strip()
        if q:
            deps = [d for d in deps if q in d.get("name", "")]
        # اگر تمپلیت فارسی نبود، فالبک
        try:
            return render_template("index.farsi.html", departments=deps)
        except TemplateNotFound:
            return render_template("index.html", departments=deps)
    except Exception:
        app.logger.error("majors() failed:\n" + traceback.format_exc())
        return "Internal error", 500


@app.route("/fa")
def index_farsi():
    try:
        deps = load_departments_farsi()
        q = (request.args.get("q") or "").strip()
        if q:
            deps = [d for d in deps if q in d.get("name", "")]
        try:
            return render_template("index.farsi.html", departments=deps)
        except TemplateNotFound:
            return render_template("index.html", departments=deps)
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"

@app.route("/fa/bolum/<int:id>")
def detail_farsi(id):
    deps = load_departments_farsi()
    dep = next((d for d in deps if d.get("id") == id), None)
    if not dep:
        return "رشته یافت نشد", 404
    try:
        return render_template("detail.farsi.html", department=dep)
    except TemplateNotFound:
        # فالبک به تمپلیت عمومی
        return render_template("detail.html", department=dep)

@app.route("/tr")
def index_tr():
    deps = load_departments()
    q = (request.args.get("q") or "").lower().strip()
    if q:
        deps = [d for d in deps if q in d.get("name", "").lower()]
    return render_template("index.html", departments=deps)

@app.route("/bolum/<int:id>")
def detail(id):
    deps = load_departments()
    dep = next((d for d in deps if d.get("id") == id), None)
    if not dep:
        return "Bölüm bulunamadı", 404
    return render_template("detail.html", department=dep)

@app.route("/universities")
def universities():
    # قبلاً detail.html بدون context رندر می‌شد و 500 می‌داد
    deps = load_departments()
    return render_template("index.html", departments=deps)

# ---- health & debug ----
@app.route("/healthz")
def healthz():
    return "ok"

@app.errorhandler(500)
def err_500(e):
    app.logger.error("500:\n" + traceback.format_exc())
    return "Internal Server Error", 500

@app.route("/__ls")
def __ls():
    return {
        "cwd": BASE_DIR,
        "templates": os.listdir(os.path.join(BASE_DIR, "templates")),
        "data": os.listdir(os.path.join(BASE_DIR, "data")),
        "static": os.listdir(os.path.join(BASE_DIR, "static")),
    }

@app.route("/__tpl/<path:name>")
def __tpl(name):
    return render_template(name)

@app.route("/__jsoncheck")
def __jsoncheck():
    try:
        a = load_departments_farsi()
        b = load_departments()
        return {"ok": True, "fa_count": len(a), "tr_count": len(b),
                "fa_first": a[0].get("name","") if a else "",
                "tr_first": b[0].get("name","") if b else ""}
    except Exception as e:
        traceback.print_exc()
        return Response(f"json error: {e}", status=500)
    
import os, csv, datetime as dt, requests
from flask import request, jsonify
# --- WhatsApp notify helper ---
def notify_whatsapp_admin(text: str) -> bool:
    token   = os.getenv("WHATSAPP_TOKEN", "")
    phone_id= os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    admin_to= os.getenv("ADMIN_WHATSAPP", "")

    if not (token and phone_id and admin_to):
        print("⚠️ WhatsApp ENV missing; skip notify")
        return False

    url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # تلاش اول: متن ساده
    payload_text = {
        "messaging_product": "whatsapp",
        "to": admin_to,
        "type": "text",
        "text": {"preview_url": False, "body": text[:4000]}
    }
    r = requests.post(url, headers=headers, json=payload_text, timeout=12)
    if r.status_code == 200:
        return True

    # تلاش دوم: Template
    tpl = os.getenv("WHATSAPP_TEMPLATE_NAME")
    if tpl:
        payload_tpl = {
            "messaging_product": "whatsapp",
            "to": admin_to,
            "type": "template",
            "template": {
                "name": tpl,
                "language": {"code": os.getenv("WHATSAPP_TEMPLATE_LANG","fa")},
                "components": [
                    {"type": "body", "parameters": [{"type": "text", "text": text[:1000]}]}
                ]
            }
        }
        r2 = requests.post(url, headers=headers, json=payload_tpl, timeout=12)
        print("WA template:", r2.status_code, r2.text[:200])
        return r2.status_code == 200

    print("WA text failed:", r.status_code, r.text[:200])
    return False
@app.route("/api/lead", methods=["POST"])
def api_lead():
    data = request.get_json(force=True) or {}
    required = ["first_name", "last_name", "phone", "service"]
    if not all(data.get(k) for k in required):
        return jsonify(ok=False, error="missing_fields"), 400

    data_dir = os.path.join(app.root_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "leads.csv")

    row = [
        dt.datetime.now().isoformat(timespec="seconds"),
        data.get("first_name","").strip(),
        data.get("last_name","").strip(),
        data.get("email","").strip(),
        data.get("phone","").strip(),
        data.get("service","").strip(),
        # منبع صفحه (در قدم ۱ اگر hidden گذاشته‌ای)
        data.get("source",""),
    ]

    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["created_at","first_name","last_name","email","phone","service","source"])
        w.writerow(row)

    return jsonify(ok=True)
