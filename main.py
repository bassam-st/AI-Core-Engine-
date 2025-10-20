#!/usr/bin/env python3
# Bassam Smart Core - نسخة شاملة ومحسّنة (إجابة + أكواد + تلخيص + تحليل + تعليم)
import os, json, time, re
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# ========= إعدادات النماذج =========
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # مفتاح Hugging Face
DEFAULT_HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"  # نموذج افتراضي
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "35"))

# ========= دالة الاتصال بالنموذج =========
BASE_URL = "https://api-inference.huggingface.co/models/"

def hf_generate(prompt: str,
                model: str = DEFAULT_HF_MODEL,
                max_new_tokens: int = 512,
                temperature: float = 0.4,
                retries: int = 2) -> str:
    if not HF_API_KEY:
        return "⚠️ المتغيّر HUGGINGFACE_API_KEY غير موجود في البيئة."
    
    model = (model or DEFAULT_HF_MODEL).strip()
    url = BASE_URL + model
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "return_full_text": False
        }
    }

    print("📡 HF URL =>", url)  # للتشخيص في اللوجز

    last_err = None
    for _ in range(retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=HTTP_TIMEOUT)
            if r.status_code in (503, 524):
                last_err = f"⏳ النموذج يسخّن ({r.status_code})"
                time.sleep(3)
                continue
            if r.status_code == 404:
                return f"❗ خطأ 404: لم يتم العثور على النموذج ({url})"
            if r.status_code == 401:
                return "⛔ مفتاح Hugging Face غير صالح أو منتهي."
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"].strip()
            return json.dumps(data, ensure_ascii=False)[:1500]
        except requests.exceptions.Timeout:
            last_err = "⏳ انتهت مهلة الاتصال بالموديل."
        except Exception as e:
            last_err = f"❗ خطأ اتصال: {e}"
        time.sleep(1)
    return last_err or "⚠️ تعذّر الحصول على استجابة من الموديل."

# ========= النواة الذكية =========
class SmartCore:
    def __init__(self):
        os.makedirs("memory", exist_ok=True)
        self.notes_file = "memory/notes.json"
        if not os.path.exists(self.notes_file):
            with open(self.notes_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)

    def answer_any(self, question: str) -> str:
        prompt = f"أجب بإيجاز ووضوح بالعربية عن السؤال التالي:\n{question}"
        return hf_generate(prompt)

    def generate_code(self, text: str) -> str:
        prompt = f"أنشئ كودًا جاهزًا مع شرح بالعربية:\n{text}"
        return hf_generate(prompt, max_new_tokens=700, temperature=0.3)

    def make_ai_app(self, idea: str) -> str:
        prompt = (
            "صمّم مشروعًا أوليًا لتطبيق ذكاء اصطناعي.\n"
            "اشرح الفكرة، الملفات الأساسية، ثم قدّم كودًا رئيسيًا مختصرًا.\n"
            f"الفكرة: {idea}"
        )
        return hf_generate(prompt, max_new_tokens=900, temperature=0.35)

    def summarize(self, text: str) -> str:
        prompt = f"لخّص النص التالي بالعربية في نقاط واضحة:\n{text}"
        return hf_generate(prompt, max_new_tokens=400, temperature=0.25)

    def analyze(self, text: str) -> str:
        prompt = f"حلّل النص التالي بالعربية: استخرج الأفكار، الأسباب، النتائج، والاقتراحات:\n{text}"
        return hf_generate(prompt, max_new_tokens=500, temperature=0.3)

    def teach(self, note: str) -> str:
        try:
            with open(self.notes_file, "r", encoding="utf-8") as f:
                notes = json.load(f)
            notes.append({"time": datetime.now().isoformat(), "note": note})
            with open(self.notes_file, "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            return "✅ تم حفظ المعلومة للتعلّم لاحقًا."
        except Exception as e:
            return f"❗ خطأ أثناء الحفظ: {e}"

core = SmartCore()

# ========= واجهات الويب =========
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "running", "model": DEFAULT_HF_MODEL, "time": datetime.now().isoformat()})

@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json(force=True)
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "لا يوجد رسالة"}), 400
    result = core.answer_any(msg)
    return jsonify({"response": result, "timestamp": datetime.now().isoformat()})

@app.route("/api/agent", methods=["POST"])
def agent_api():
    """
    body JSON:
    {
      "action": "ask|code|makeapp|summarize|analyze|teach",
      "input": "النص أو السؤال"
    }
    """
    try:
        data = request.get_json(force=True)
        action = (data.get("action") or "").lower()
        text = (data.get("input") or "").strip()
        if not action or not text:
            return jsonify({"error": "يجب إرسال action و input"}), 400

        if action == "ask":
            out = core.answer_any(text)
        elif action == "code":
            out = core.generate_code(text)
        elif action == "makeapp":
            out = core.make_ai_app(text)
        elif action == "summarize":
            out = core.summarize(text)
        elif action == "analyze":
            out = core.analyze(text)
        elif action == "teach":
            out = core.teach(text)
        else:
            out = "⚠️ نوع العملية غير معروف."

        return jsonify({"ok": True, "action": action, "output": out, "time": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
