# 🧠 محلل المشاعر الذكي

مشروع ويب بسيط:
- **الواجهة:** HTML + CSS + JavaScript
- **الخادم والذكاء الاصطناعي:** Python (Flask + scikit-learn)
- **قاعدة البيانات:** MySQL عبر XAMPP

يكتب المستخدم نصاً (عربي أو إنجليزي)، فيصنّفه النموذج: إيجابي أو سلبي أو محايد، مع نسبة الثقة. تُحفظ كل النتائج في MySQL، ويقدر المستخدم يصحح النتيجة فيتعلم النموذج من التصحيح.

## 📁 هيكل المشروع

```
ai-web-project/
├── backend/
│   ├── app.py            ← خادم Flask (نقطة التشغيل)
│   ├── ai_model.py       ← نموذج الذكاء الاصطناعي
│   ├── db.py             ← التعامل مع MySQL
│   ├── config.py         ← إعدادات الاتصال
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── database/
    └── schema.sql        ← إنشاء قاعدة البيانات والجداول
```

## 🚀 خطوات التشغيل

### 1) شغّل MySQL من XAMPP
افتح **XAMPP Control Panel** واضغط **Start** بجانب **MySQL** (و **Apache** إذا تبي phpMyAdmin).

### 2) أنشئ قاعدة البيانات
- افتح `http://localhost/phpmyadmin`
- اختر تبويب **Import** ← اختر ملف `database/schema.sql` ← **Go**

ستُنشأ قاعدة `ai_project` وفيها جدولان: `analyses` و `training_data`.

### 3) ثبّت مكتبات Python
لازم يكون عندك Python 3.9 أو أحدث. من داخل مجلد `backend`:
```bash
pip install -r requirements.txt
```

### 4) شغّل الخادم
```bash
cd backend
python app.py
```

### 5) افتح المتصفح
```
http://localhost:5000
```

## ⚙️ ملاحظات

- **كلمة مرور MySQL:** إذا غيّرت كلمة مرور `root` في XAMPP، عدّلها في `backend/config.py`.
- **فتح الواجهة من Apache:** تقدر تنسخ مجلد `frontend` إلى `C:\xampp\htdocs\ai-project` وتفتح `http://localhost/ai-project`، بشرط أن يكون `app.py` شغالاً (الخادم يسمح بالاتصال من منافذ أخرى).
- **تحسين الذكاء:** أضف أمثلة أكثر في `BASE_DATA` داخل `ai_model.py`، أو استخدم أزرار التصحيح في الواجهة.

## 🔌 الواجهات البرمجية (API)

| الطريقة | المسار | الوظيفة |
|---|---|---|
| POST | `/api/analyze` | تحليل نص `{ "text": "..." }` |
| GET | `/api/history` | آخر 20 تحليل |
| DELETE | `/api/history/<id>` | حذف تحليل |
| GET | `/api/stats` | عدد التحليلات لكل تصنيف |
| POST | `/api/feedback` | تصحيح التصنيف وإعادة التدريب `{ "text": "...", "label": "positive" }` |
