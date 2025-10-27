# engine/coder.py
from __future__ import annotations
import os, io, textwrap, zipfile, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

class Scaffolder:
    """
    مُوَلِّد مشاريع جاهزة: ينشئ مجلدات وملفات وتشغيل فوري.
    الأنواع المدعومة: fastapi | telegram-bot | html
    يعيد مسار ZIP جاهز للتحميل.
    """
    def scaffold(self, kind: str, name: str) -> str:
        kind = (kind or "").strip().lower()
        name = self._slug(name)

        if kind not in {"fastapi", "telegram-bot", "html"}:
            raise ValueError("kind يجب أن يكون: fastapi | telegram-bot | html")

        files: dict[str, str] = {}
        if kind == "fastapi":
            files = self._tpl_fastapi(name)
        elif kind == "telegram-bot":
            files = self._tpl_telegram(name)
        elif kind == "html":
            files = self._tpl_html_widget(name)

        # إنشاء ZIP داخل data/exports
        stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        zip_path = EXPORT_DIR / f"{kind}-{name}-{stamp}.zip"
        self._make_zip(files, zip_path)
        return str(zip_path)

    # --------------- قوالب ---------------

    def _tpl_fastapi(self, name: str) -> dict[str, str]:
        pkg = name.replace("-", "_")
        return {
            f"{name}/README.md": textwrap.dedent(f"""
            # {name} — FastAPI Starter

            مشروع FastAPI جاهز للتشغيل على Render/Heroku أو محليًا.

            ## التشغيل المحلي
            ```bash
            python -m venv .venv && . .venv/bin/activate
            pip install -r requirements.txt
            uvicorn {pkg}.app:app --reload --port 8000
            ```
            ثم افتح: http://127.0.0.1:8000/docs

            ## نشر سريع على Render
            - أضف المشروع كمستودع
            - اضبط الأمر: `uvicorn {pkg}.app:app --host 0.0.0.0 --port 10000`
            """).strip(),
            f"{name}/requirements.txt": textwrap.dedent("""
            fastapi==0.115.0
            uvicorn==0.30.6
            requests==2.32.3
            """).strip(),
            f"{name}/render.yaml": textwrap.dedent(f"""
            services:
              - type: web
                name: {name}
                env: python
                plan: free
                buildCommand: pip install -r requirements.txt
                startCommand: uvicorn {pkg}.app:app --host 0.0.0.0 --port 10000
            """).strip(),
            f"{name}/.gitignore": textwrap.dedent("""
            __pycache__/
            .venv/
            *.pyc
            """).strip(),
            f"{name}/{pkg}/__init__.py": "",
            f"{name}/{pkg}/app.py": textwrap.dedent(f"""
            from fastapi import FastAPI
            from pydantic import BaseModel
            import datetime, os

            app = FastAPI(title="{name} — FastAPI Starter")

            class Echo(BaseModel):
                text: str

            @app.get("/ping")
            def ping():
                return {{"ok": True, "time": datetime.datetime.utcnow().isoformat()+"Z"}}

            @app.post("/echo")
            def echo(e: Echo):
                return {{"you_said": e.text, "env": dict(os.environ)}}
            """).strip(),
        }

    def _tpl_telegram(self, name: str) -> dict[str, str]:
        pkg = name.replace("-", "_")
        return {
            f"{name}/README.md": textwrap.dedent(f"""
            # {name} — Telegram Bot (python-telegram-bot)

            بوت تيليجرام بسيط.

            ## الإعداد
            1) أنشئ التوكن من @BotFather
            2) ضع المتغير `TELEGRAM_BOT_TOKEN` في بيئة التشغيل أو ملف `.env`

            ## تشغيل
            ```bash
            python -m venv .venv && . .venv/bin/activate
            pip install -r requirements.txt
            python {pkg}/bot.py
            ```
            """).strip(),
            f"{name}/requirements.txt": textwrap.dedent("""
            python-telegram-bot==21.6
            python-dotenv==1.0.1
            """).strip(),
            f"{name}/.env.example": "TELEGRAM_BOT_TOKEN=put-your-token-here\n",
            f"{name}/{pkg}/__init__.py": "",
            f"{name}/{pkg}/bot.py": textwrap.dedent("""
            import os
            from dotenv import load_dotenv
            from telegram import Update
            from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

            load_dotenv()
            TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

            async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await update.message.reply_text("أهلًا! أرسل أي رسالة وسأكررها لك 🤖")

            async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await update.message.reply_text(update.message.text)

            def main():
                if not TOKEN:
                    raise RuntimeError("ضع TELEGRAM_BOT_TOKEN في .env أو البيئة")
                app = ApplicationBuilder().token(TOKEN).build()
                app.add_handler(CommandHandler("start", start))
                app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
                app.run_polling()

            if __name__ == "__main__":
                main()
            """).strip(),
        }

    def _tpl_html_widget(self, name: str) -> dict[str, str]:
        return {
            f"{name}/README.md": f"# {name} — HTML Widget\nافتح الملف `index.html` في المتصفح.",
            f"{name}/index.html": textwrap.dedent("""
            <!doctype html>
            <html lang="ar" dir="rtl">
            <head>
              <meta charset="utf-8"/>
              <meta name="viewport" content="width=device-width,initial-scale=1"/>
              <title>Widget</title>
              <style>
                body{font-family:system-ui; background:#0f1222; color:#fff; margin:0; padding:40px}
                .card{background:#161a2d; border-radius:14px; padding:18px; max-width:680px}
                input,button{padding:10px; border-radius:10px; border:0}
                input{width:70%} button{background:#10b981; color:#012}
              </style>
            </head>
            <body>
              <div class="card">
                <h2>ودجت تفاعلي بسيط</h2>
                <p>أدخل نصًا وسيظهر أسفله:</p>
                <input id="t" placeholder="اكتب هنا..."/>
                <button onclick="show()">عرض</button>
                <pre id="out"></pre>
              </div>
              <script>function show(){out.textContent = t.value}</script>
            </body>
            </html>
            """).strip(),
        }

    # --------------- أدوات ---------------

    def _make_zip(self, files: dict[str, str], zip_path: Path):
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel, content in files.items():
                data = content.encode("utf-8")
                zf.writestr(rel, data)

    def _slug(self, s: str) -> str:
        s = s.strip().lower().replace(" ", "-")
        allowed = "abcdefghijklmnopqrstuvwxyz0123456789-_"
        return "".join(ch for ch in s if ch in allowed) or "my-app"
