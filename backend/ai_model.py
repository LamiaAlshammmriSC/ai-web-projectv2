"""
نموذج الذكاء الاصطناعي: مصنّف مشاعر (إيجابي / سلبي / محايد)
يعتمد على TF-IDF + Logistic Regression من مكتبة scikit-learn.
يتعلم من بيانات أساسية + التصحيحات التي يحفظها المستخدم في MySQL.
"""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union

# ---------- بيانات التدريب الأساسية ----------
BASE_DATA = [
    # إيجابي
    ("المنتج رائع جدا وأنصح فيه", "positive"),
    ("خدمة ممتازة وسريعة شكرا لكم", "positive"),
    ("أنا سعيد جدا بهذه التجربة", "positive"),
    ("جميل ومرتب والتوصيل كان سريع", "positive"),
    ("أفضل مطعم جربته في حياتي", "positive"),
    ("الموظفين محترمين والتعامل راقي", "positive"),
    ("يستاهل كل ريال والجودة عالية", "positive"),
    ("تجربة حلوة وبكررها أكيد", "positive"),
    ("أحببت التصميم كثيرا", "positive"),
    ("مبدعين ما شاء الله", "positive"),
    ("الحمد لله كل شي ممتاز", "positive"),
    ("فرحت بالنتيجة", "positive"),
    ("I love this product, it is amazing", "positive"),
    ("Great service and very fast delivery", "positive"),
    ("Excellent quality, highly recommended", "positive"),
    ("I am very happy with the result", "positive"),
    ("Wonderful experience, thank you", "positive"),
    ("Best purchase I have ever made", "positive"),
    ("This app is awesome and good", "positive"),
    ("Nice and perfect, I like it", "positive"),
    ("حلو مرة وعجبني", "positive"),
    ("شي خرافي وممتع", "positive"),
    # سلبي
    ("المنتج سيء جدا ولا أنصح فيه", "negative"),
    ("خدمة سيئة وتأخير في التوصيل", "negative"),
    ("أنا زعلان من التعامل", "negative"),
    ("الجودة رديئة وخربان من أول يوم", "negative"),
    ("أسوأ تجربة مرت علي", "negative"),
    ("الموظف كان وقح وما ساعدني", "negative"),
    ("ما يستاهل السعر أبدا", "negative"),
    ("ندمت إني اشتريته", "negative"),
    ("مخيب للآمال وضيعت فلوسي", "negative"),
    ("الطلب وصل ناقص ومكسور", "negative"),
    ("تعبت من المشاكل اللي فيه", "negative"),
    ("كرهت الخدمة", "negative"),
    ("This is terrible, I hate it", "negative"),
    ("Very bad service and slow delivery", "negative"),
    ("Poor quality, broke after one day", "negative"),
    ("Worst experience ever, waste of money", "negative"),
    ("I am disappointed and angry", "negative"),
    ("Not worth the price at all", "negative"),
    ("Awful and horrible support", "negative"),
    ("Bad app, I don't like it", "negative"),
    ("ما عجبني أبدا وممل", "negative"),
    ("خايس وفاشل", "negative"),
    # محايد
    ("وصل الطلب اليوم", "neutral"),
    ("المتجر يفتح الساعة تسعة", "neutral"),
    ("اشتريت المنتج من الموقع", "neutral"),
    ("كم سعر هذا الجهاز", "neutral"),
    ("الاجتماع بكرة الصبح", "neutral"),
    ("المنتج متوفر بلونين", "neutral"),
    ("رحت السوق وجيت", "neutral"),
    ("هل يوجد توصيل للرياض", "neutral"),
    ("الطقس اليوم غائم", "neutral"),
    ("أرسلت الطلب أمس", "neutral"),
    ("The order arrived today", "neutral"),
    ("The store opens at nine", "neutral"),
    ("What is the price of this item", "neutral"),
    ("I bought it from the website", "neutral"),
    ("The meeting is tomorrow morning", "neutral"),
    ("It comes in two colors", "neutral"),
]


def normalize(text: str) -> str:
    """توحيد الحروف العربية وإزالة التشكيل لتحسين الدقة."""
    text = text.lower()
    text = re.sub(r"[ً-ْـ]", "", text)  # تشكيل + تطويل
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"(.)\1{2,}", r"\1", text)  # رااااائع -> رائع
    return text


class SentimentModel:
    def __init__(self):
        self.pipeline = None

    def train(self, extra_data=None):
        data = BASE_DATA + (extra_data or [])
        texts = [t for t, _ in data]
        labels = [l for _, l in data]
        features = make_union(
            TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2)),
            # n-grams على مستوى الحروف تساعد مع اختلاف كتابة الكلمات
            TfidfVectorizer(preprocessor=normalize, analyzer="char_wb", ngram_range=(2, 4)),
        )
        self.pipeline = make_pipeline(features, LogisticRegression(max_iter=1000, C=5))
        self.pipeline.fit(texts, labels)
        return len(data)

    def predict(self, text: str):
        probs = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_
        best = probs.argmax()
        return {
            "sentiment": classes[best],
            "confidence": round(float(probs[best]) * 100, 2),
            "scores": {c: round(float(p) * 100, 2) for c, p in zip(classes, probs)},
        }
