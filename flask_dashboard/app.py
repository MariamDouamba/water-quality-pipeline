"""
AquaStat — Qualité de l'eau en France
Flask backend — consomme la FastAPI water-quality-pipeline
"""
from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

def api_get(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=10)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats")
def stats():
    data, err = api_get("/stats")
    if err:
        # Fallback données statiques
        data = {
            "total_analyses": 12600000,
            "total_prelevements": 291604,
            "total_communes": 34811,
            "total_departements": 101,
            "total_parametres": 1386,
            "taux_conformite": 94.2
        }
    return jsonify(data)

@app.route("/api/departements")
def departements():
    data, err = api_get("/departements")
    return jsonify(data or [])

@app.route("/api/departements/<code>/non-conformites")
def dept_nc(code):
    data, err = api_get(f"/departements/{code}/non-conformites")
    return jsonify(data or [])

@app.route("/api/communes/top-non-conformes")
def top_communes():
    data, err = api_get("/communes/top-non-conformes")
    return jsonify(data or [])

@app.route("/api/parametres/non-conformites")
def params_nc():
    data, err = api_get("/parametres/non-conformites")
    return jsonify(data or [])

@app.route("/api/prelevements/par-mois")
def par_mois():
    data, err = api_get("/prelevements/par-mois")
    return jsonify(data or [])

if __name__ == "__main__":
    app.run(debug=True, port=5000)