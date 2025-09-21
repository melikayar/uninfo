from flask import Flask, render_template, request, Response
import json, os, traceback

app = Flask(__name__)  # فقط یکبار

# ---- Absolute paths for JSON (fix 500) ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_departments():
    path = os.path.join(BASE_DIR, "data", "departments.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_departments_farsi():
    path = os.path.join(BASE_DIR, "data", "departments_farsi.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---- Routes ----
@app.route("/")           # صفحه اصلی = نسخه فارسی
def root():
    departments = load_departments_farsi()
    q = (request.args.get("q") or "").strip()
    if q:
        departments = [d for d in departments if q in d.get("name", "")]
    return render_template("index.farsi.html", departments=departments)

@app.route("/fa")
def index_farsi():
    departments = load_departments_farsi()
    q = (request.args.get("q") or "").strip()
    if q:
        departments = [d for d in departments if q in d.get("name", "")]
    return render_template("index.farsi.html", departments=departments)

@app.route("/fa/bolum/<int:id>")
def detail_farsi(id):
    departments = load_departments_farsi()
    department = next((d for d in departments if d.get("id") == id), None)
    if not department:
        return "رشته یافت نشد", 404
    return render_template("detail.farsi.html", department=department)

@app.route("/tr")
def index_tr():
    departments = load_departments()
    q = (request.args.get("q") or "").lower().strip()
    if q:
        departments = [d for d in departments if q in d.get("name", "").lower()]
    return render_template("index.html", departments=departments)

@app.route("/bolum/<int:id>")
def detail(id):
    departments = load_departments()
    department = next((d for d in departments if d.get("id") == id), None)
    if not department:
        return "Bölüm bulunamadı", 404
    return render_template("detail.html", department=department)

@app.route("/home")                   # صفحه /home
def home_page():
    return render_template("home.html")

@app.route("/universities")
def universities():
    return render_template("detail.html")

@app.route("/consult")
def consult():
    return "<h1>مشاوره با ما</h1>"

@app.route("/team")
def team():
    return "<h1>تیم ما</h1>"

@app.route("/about")
def about():
    return "<h1>درباره ما</h1>"

@app.route("/contact")
def contact():
    return "<h1>تماس با ما</h1>"

# ---- Health & Error handler (برای دیباگ سریع) ----
@app.route("/healthz")
def healthz():
    return "ok"

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()         # میره تو لاگ Render
    return Response("Internal error", status=500)
