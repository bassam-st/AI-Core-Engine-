import os, zipfile, io, textwrap
from .config import cfg

TEMPLATE_FASTAPI = lambda name: textwrap.dedent(f"""
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def hi():
    return {{"ok": True, "msg": "Hello from {name}!"}}
""")

TEMPLATE_HTML = lambda name: textwrap.dedent(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><title>{name}</title></head>
<body><h2>{name}</h2><p>App scaffold generated.</p></body></html>
""")

class Scaffolder:
    def scaffold(self, kind: str, name: str) -> str:
        proj = name.replace(" ", "_")
        base = os.path.join(cfg.DATA_DIR, "scaffold", proj)
        os.makedirs(base, exist_ok=True)
        if kind == "fastapi":
            with open(os.path.join(base, "main.py"), "w", encoding="utf-8") as f:
                f.write(TEMPLATE_FASTAPI(name))
            with open(os.path.join(base, "requirements.txt"), "w") as f:
                f.write("fastapi\nuvicorn\n")
        else:
            with open(os.path.join(base, "index.html"), "w", encoding="utf-8") as f:
                f.write(TEMPLATE_HTML(name))
        # zip
        zpath = os.path.join(cfg.DATA_DIR, f"{proj}.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(base):
                for fn in files:
                    p = os.path.join(root, fn)
                    z.write(p, os.path.relpath(p, base))
        return zpath
