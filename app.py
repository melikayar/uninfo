from flask import Flask, render_template, request
import json
import os

# 'Templates' klasörü burada manuel olarak belirtiliyor
app = Flask(__name__, template_folder="Templates")

def load_departments():
    with open("data/departments.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    departments = load_departments()
    query = request.args.get("q", "").lower()
    if query:
        departments = [d for d in departments if query in d["name"].lower()]
    return render_template("index.html", departments=departments)

@app.route("/bolum/<int:id>")
def detail(id):
    departments = load_departments()
    department = next((d for d in departments if d["id"] == id), None)
    if not department:
        return "Bölüm bulunamadı", 404
    return render_template("detail.html", department=department)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

@app.route("/fa")
def index_farsi():
    departments = load_departments_farsi()
    query = request.args.get("q", "").lower()
    if query:
        departments = [d for d in departments if query in d["name"]]
    return render_template("index.farsi.html", departments=departments)

def load_departments_farsi():
    with open("data/departments_farsi.json", "r", encoding="utf-8") as f:
        return json.load(f)
    
@app.route("/fa/bolum/<int:id>")
def detail_farsi(id):
    with open("data/departments_farsi.json", "r", encoding="utf-8") as f:
        departments = json.load(f)
    department = next((d for d in departments if d["id"] == id), None)
    if not department:
        return "رشته یافت نشد", 404
    return render_template("detail.farsi.html", department=department)
