#!/usr/bin/env python3
# Bassam Smart Core — Q&A + Code + Apps + Summarize + Analyze + Teach
import os, json, time, re
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# ========= إعدادات النماذج =========
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # ضع هذا في Render
DEFAULT_HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "35"))

# ========= مساعد الاتصال بـ Hugging Face =========
def hf_generate(prompt: str,
                model: str = DEFAULT_HF_MODEL,
                max_new_tokens: int = 512,
                temperature: float = 0.4,
                retries: int = 2) -> str:
    if not HF_API_KEY:
        return "⚠️ المتغيّر HUGGINGFACE_API_KEY غير موجود."
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": f"{prompt}",
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "return_full_text": False
        }
    }
    last_err = None
    for _ in range(retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=HTTP_TIMEOUT)
            if r.status_code in (503, 524):  # تسخين النموذج
                last_err = "⏳ الموديل يسخّن، إعادة المحاولة…"
                time.sleep(3); continue
            if r.status_code == 401:
                return "⛔ مفتاح Hugging Face غير صالح."
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"].strip()
            return json.dumps(data, ensure_ascii=False)[:2000]
        except requests.exceptions.Timeout:
            last_err = "⏳ انتهت المهلة."
        except Exception as e:
            last_err = f"❗ خطأ اتصال: {e}"
        time.sleep(1)
    return last_err or "⚠️ تعذّر الحصول على استجابة من النموذج."

# ========= لبّ “النواة الذكية” =========
class SmartCore:
    def __init__(self):
        os.makedirs("memory", exist_ok=True)
        self.notes_file = "memory/notes.json"
        if not os.path.exists(self.notes_file):
            with open(self.notes_file, "w", encoding="utf-8") as f: json.dump([], f, ensure_ascii=False)

    # 1) سؤال عام (Q&A)
    def answer_any(self, question: str) -> str:
        prompt = (
            "أجب بإيجاز ووضوح باللغة العربية. إذا احتجت أمثلة أو خطوات برمجية فاذكرها.\n"
            f"السؤال: {question}"
        )
        return hf_generate(prompt)

    # 2) توليد أكواد
    def generate_code(self, request_text: str) -> str:
        prompt = (
            "أنت مولد أكواد محترف. أعد كودًا كاملاً وجاهزًا للتشغيل مع شرح قصير بالعربية.\n"
            "التزم بوضع الكود داخل كتلة ```اللغة ...```. إن كان إطار عمل محدد فاتبعه.\n"
            f"المطلوب: {request_text}"
        )
        return hf_generate(prompt, max_new_tokens=700, temperature=0.3)

    # 3) صنع تطبيقات ذكاء اصطناعي (هيكل جاهز)
    def make_ai_app(self, idea: str) -> str:
        prompt = (
            "ولّد مشروعًا أوليًا (MVP) لتطبيق ذكاء اصطناعي مع الملفات الأساسية.\n"
            "اشرح الهيكل، ثم أعطِ ملفات رئيسية مختصرة (app.py أو main.py، requirements، README).\n"
            f"فكرة التطبيق: {idea}"
        )
        return hf_generate(prompt, max_new_tokens=900, temperature=0.35)

    # 4) تلخيص
    def summarize(self, text: str) -> str:
        prompt = (
            "لخّص النص التالي بالعربية في نقاط قصيرة وواضحة، ثم أعطِ خلاصة نهائية.\n"
            f"النص:\n{text}"
        )
        return hf_generate(prompt, max_new_tokens=400, temperature=0.2)

    # 5) تحليل/استخلاص (أفكار، كيانات، خطوات)
    def analyze(self, text: str) -> str:
        prompt = (
            "حلّل النص بالعربية: أهم الأفكار، الكيانات، الأسباب والنتائج، وخطوات عملية مقترحة."
            f"\nالنص:\n{text}"
        )
        return hf_generate(prompt, max_new_tokens=500, temperature=0.3)

    # 6) تعليم ذاتي بسيط (تخزين ملاحظات/معارف يدوية)
    def teach(self, note: str) -> str:
        try:
            with open(self.notes_file, "r", encoding="utf-8") as f: notes = json.load(f)
            notes.append({"ts": datetime.now().isoformat(), "note": note})
            with open(self.notes_file, "w", encoding="utf-8") as f: json.dump(notes, f, ensure_ascii=False, indent=2)
            return "✅ تم حفظ المعلومة للتعلّم لاحقًا."
        except Exception as e:
            return f"❗ تعذّر الحفظ: {e}"

core = SmartCore()

# ========= الويب =========
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "running", "model": DEFAULT_HF_MODEL, "ts": datetime.now().isoformat()})

# واجهة موحّدة: نوع المهمة عبر action
@app.route("/api/agent", methods=["POST"])
def api_agent():
    """
    body JSON:
    {
      "action": "ask|code|makeapp|summarize|analyze|teach",
      "input": "النص/السؤال/الفكرة"
    }
    """
    try:
        data = request.get_json(force=True)
        action = (data.get("action") or "").lower()
        text = (data.get("input") or "").strip()
        if not action or not text:
            return jsonify({"error": "أرسل action و input"}), 400

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
            return jsonify({"error": "action غير معروف"}), 400

        return jsonify({"ok": True, "action": action, "output": out, "ts": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# توافق مع /api/chat (سؤال عام)
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "لا يوجد رسالة"}), 400
    out = core.answer_any(msg)
    return jsonify({"response": out, "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
