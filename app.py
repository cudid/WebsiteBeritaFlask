# -*- coding: utf-8 -*-
"""Flask app - Mesin Pencari Berita Kompas."""

import os

from flask import Flask, jsonify, render_template, request

from search_engine import get_engine

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")


@app.route("/")
def index():
    engine = get_engine()
    return render_template(
        "index.html",
        total_articles=engine.total_articles if engine.is_ready else 0,
        data_ready=engine.is_ready,
    )


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    top_n = min(int(data.get("top_n", 10)), 50)

    if not query:
        return jsonify({"error": "Masukkan kata kunci pencarian terlebih dahulu."}), 400

    engine = get_engine()
    if not engine.is_ready:
        return jsonify({
            "error": "Data berita belum tersedia. Letakkan hasil_scraping_kompas.xlsx di folder data/."
        }), 503

    try:
        results = engine.search(query, top_n=top_n)
        return jsonify({
            "query": query,
            "total": len(results),
            "results": results,
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500


@app.route("/api/health")
def health():
    engine = get_engine()
    return jsonify({
        "status": "ok",
        "data_ready": engine.is_ready,
        "total_articles": engine.total_articles if engine.is_ready else 0,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
