# engine/coder.py
import os, io, zipfile, textwrap
from pathlib import Path
from engine.config import cfg

ART_DIR = Path(cfg.DATA_DIR) / "artifacts"
ART_DIR.mkdir(parents=True, exist_ok=True)

class Scaffolder:
    def _zip_bytes(self, files: dict[str, str], zip_name: str) -> str:
        out_path = ART_DIR / zip_name
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
            for rel, content in files.items():
                z.writestr(rel, content)
        return str(out_path)

    def fastapi_min(self, name: str = "my-fastapi"):
        files = {
            f"{name}/main.py": textwrap.dedent("""\
                from fastapi import FastAPI
                app = FastAPI(title="Sample FastAPI")
                @app.get("/")
                def home():
                    return {"ok": True, "msg": "Hello from FastAPI!"}
            """),
            f"{name}/requirements.txt": "fastapi==0.115.4\nuvicorn==0.32.0\n",
            f"{name}/Procfile": "web: uvicorn main:app --host 0.0.0.0 --port $PORT\n",
            f"{name}/render.yaml": textwrap.dedent("""\
                services:
                  - type: web
                    name: sample-fastapi
                    env: python
                    plan: starter
                    buildCommand: pip install -r requirements.txt
                    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
            """),
            f"{name}/README.md": "# Sample FastAPI app\nDeploy on Render Starter.\n",
        }
        return self._zip_bytes(files, f"{name}.zip")

    def html_min(self, name: str = "my-static-site"):
        files = {
            f"{name}/index.html": textwrap.dedent("""\
                <!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>موقعي السريع</title>
                <style>body{font-family:system-ui;padding:24px} .btn{padding:10px 14px;background:#0b7;color:#fff;border-radius:10px;text-decoration:none}</style>
                <h1>🎯 موقع HTML بسيط</h1>
                <p>تم توليده تلقائيًا.</p>
                <a class="btn" href="#">زر تجريبي</a>
                </html>
            """),
            f"{name}/README.md": "# Static HTML site\n",
        }
        return self._zip_bytes(files, f"{name}.zip")

    def scaffold(self, kind: str, name: str):
        if kind == "fastapi":
            return self.fastapi_min(name)
        elif kind == "html":
            return self.html_min(name)
        else:
            raise ValueError("نوع غير مدعوم. استخدم fastapi أو html.")
