from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)  # از مسیر پیش‌فرض templates/ استفاده می‌کنیم

# ---------- Helpers ----------
def load_departments():
    with open("data/departments.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_departments_farsi():
    with open("data/departments_farsi.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ---------- Routes ----------

# روت اصلی → به نسخه فارسی هدایت می‌شود
@app.route("/")
def root():
    return redirect(url_for("index_farsi"))

# نسخه فارسی (Home)
@app.route("/fa")
def index_farsi():
    departments = load_departments_farsi()
    query = (request.args.get("q") or "").strip()
    if query:
        # برای فارسی lower ضروری نیست؛ شامل بودن ساده کفایت می‌کند
        departments = [d for d in departments if query in d.get("name", "")]
    return render_template("index.farsi.html", departments=departments)

# جزئیات رشته در نسخه فارسی
@app.route("/fa/bolum/<int:id>")
def detail_farsi(id):
    departments = load_departments_farsi()
    department = next((d for d in departments if d.get("id") == id), None)
    if not department:
        return "رشته یافت نشد", 404
    return render_template("detail.farsi.html", department=department)

# نسخه ترکی/عمومی (در صورت نیاز)
@app.route("/tr")
def index_tr():
    departments = load_departments()
    query = (request.args.get("q") or "").lower().strip()
    if query:
        departments = [d for d in departments if query in d.get("name", "").lower()]
    return render_template("index.html", departments=departments)

@app.route("/bolum/<int:id>")
def detail(id):
    departments = load_departments()
    department = next((d for d in departments if d.get("id") == id), None)
    if not department:
        return "Bölüm bulunamadı", 404
    return render_template("detail.html", department=department)

# لینک‌های منوی بالا
@app.route("/universities")
def universities():
    # فعلاً به یک صفحه واقعی رندر بده تا 500 نده
    return render_template("detail.html")


@app.route("/universities")
def universities():
    return render_template("detail.html")

@app.route("/consult")
def consult():
    return "<h1>مشاوره با ما</h1>"

@app.route("/team")
def team():
    return "<h1>تیم ما</h1>"
@app.route("/home")
def home_page():
    return render_template("home.html")
    