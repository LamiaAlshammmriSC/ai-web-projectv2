"""
خادم Flask: يربط الواجهة (HTML/CSS/JS) بنموذج الذكاء الاصطناعي وقاعدة MySQL.
شغّله بالأمر:  python app.py
ثم افتح:       http://localhost:5000
"""
import os
from flask import Flask, jsonify, request, send_from_directory

import db
from ai_model import SentimentModel
from config import SERVER_PORT , DEBUG 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
# احتياط: لو مجلد frontend موضوع داخل backend
if not os.path.isfile(os.path.join(FRONTEND_DIR, "index.html")):
    alt = os.path.join(BASE_DIR, "frontend")
    if os.path.isfile(os.path.join(alt, "index.html")):
        FRONTEND_DIR = alt
VALID_LABELS = {"positive", "negative", "neutral"}

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
model = SentimentModel()


def train_model():
    """تدريب النموذج على البيانات الأساسية + تصحيحات المستخدم من MySQL."""
    try:
        extra = db.get_training_examples()
    except Exception as e:
        print(f"⚠️  تعذر قراءة بيانات التدريب من MySQL: {e}")
        extra = []
    return model.train(extra)


try:
    db.init_db()
    print("✅ قاعدة البيانات جاهزة")
except Exception as e:
    print(f"⚠️ قاعدة البيانات غير جاهزة: {e}")

_trained = train_model()
# السماح للواجهة بالاتصال حتى لو فُتحت من Apache في XAMPP (منفذ مختلف)
@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    return resp


@app.route("/")
def index():
    if not os.path.isfile(os.path.join(FRONTEND_DIR, "index.html")):
        return (
            f"<h2 dir='rtl'>ملف الواجهة غير موجود</h2>"
            f"<p dir='rtl'>تأكد أن مجلد <b>frontend</b> موجود بجانب مجلد backend.<br>"
            f"المسار المتوقع: <code>{FRONTEND_DIR}</code></p>",
            500,
        )
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    text = (request.get_json(silent=True) or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "الرجاء كتابة نص"}), 400
    if len(text) > 2000:
        return jsonify({"error": "النص طويل جدا (الحد 2000 حرف)"}), 400

    result = model.predict(text)
    try:
        result["id"] = db.save_analysis(text, result["sentiment"], result["confidence"])
    except Exception as e:
        return jsonify({"error": f"خطأ في قاعدة البيانات: {e}"}), 500
    return jsonify(result)


@app.route("/api/history")
def history():
    try:
        return jsonify(db.get_history())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/<int:analysis_id>", methods=["DELETE"])
def delete(analysis_id):
    try:
        db.delete_analysis(analysis_id)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats")
def stats():
    try:
        return jsonify(db.get_stats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
def feedback():
    """المستخدم يصحح التصنيف -> يُحفظ في MySQL ويُعاد تدريب النموذج."""
    data = request.get_json(silent=True) or {}
    text, label = data.get("text", "").strip(), data.get("label")
    if not text or label not in VALID_LABELS:
        return jsonify({"error": "بيانات غير صحيحة"}), 400
    try:
        db.add_training_example(text, label)
        total = train_model()
        return jsonify({"ok": True, "trained_on": total})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"✅ تم تدريب النموذج على {_trained} مثال")
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=DEBUG, use_reloader=False)
    
    
#if __name__ == "__main__":
#   print(f"✅ تم تدريب النموذج على {n} مثال")
#   ok = os.path.isfile(os.path.join(FRONTEND_DIR, "index.html"))
#   print(f"{'✅' if ok else '❌'} مجلد الواجهة: {FRONTEND_DIR}")
#   print(f"🌐 افتح المتصفح على: http://localhost:{SERVER_PORT}")
#   app.run(host="0.0.0.0", port=SERVER_PORT, debug=True)
