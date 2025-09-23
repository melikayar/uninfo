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
@app.route("/")
def root():
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
        app.logger.error("root() failed:\n" + traceback.format_exc())
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

@app.route("/home")
def home_page():
    return render_template("home.html")

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
