# engine/coder.py
from __future__ import annotations
import os, io, zipfile, textwrap, datetime
from pathlib import Path
from typing import Tuple

from .config import cfg

# مجلد التصدير نفسه الذي نعرضه في /exports
EXPORT_DIR = Path(cfg.DATA_DIR) / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


class Scaffolder:
    """
    صانع هياكل مشاريع سريعة.
    الأنواع المدعومة:
      - fastapi
      - fastapi-crud-jwt (جديد)
      - telegram-bot
      - html
    يعيد مسار ملف ZIP النهائي داخل EXPORT_DIR.
    """

    def scaffold(self, kind: str, name: str) -> str:
        kind = (kind or "").strip().lower()
        name = self._safe_name(name or "my-app")

        if kind == "fastapi":
            files = self._fastapi_basic(name)
        elif kind == "fastapi-crud-jwt":
            files = self._fastapi_crud_jwt(name)
        elif kind == "telegram-bot":
            files = self._telegram_bot(name)
        elif kind == "html":
            files = self._html_widget(name)
        else:
            raise ValueError(f"نوع غير مدعوم: {kind}")

        zip_path = self._write_zip(name, files)
        return zip_path

    # ------------------------- قوالب -------------------------

    def _fastapi_basic(self, name: str) -> dict:
        app_py = textwrap.dedent(f"""
        from fastapi import FastAPI
        app = FastAPI(title="{name}")

        @app.get("/")
        def root():
            return {{"ok": True, "app": "{name}"}}
        """).strip()

        req = "fastapi==0.115.0\nuvicorn==0.30.6\n"
        return {
            f"{name}/app.py": app_py,
            f"{name}/requirements.txt": req,
            f"{name}/README.md": f"# {name}\\n\\nتشغيل محلي:\\n\\n```bash\\npip install -r requirements.txt\\nuvicorn app:app --reload\\n```\\n",
        }

    def _fastapi_crud_jwt(self, name: str) -> dict:
        # تطبيق CRUD بسيط لعناصر مع مصادقة JWT وSQLite
        app_py = textwrap.dedent(f"""
        from datetime import datetime, timedelta
        from typing import List, Optional
        from fastapi import FastAPI, Depends, HTTPException, status
        from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
        from pydantic import BaseModel
        from jose import jwt, JWTError
        from passlib.context import CryptContext
        from sqlalchemy import create_engine, Column, Integer, String, DateTime
        from sqlalchemy.orm import sessionmaker, declarative_base, Session

        SECRET_KEY = "change-me-please"
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 60

        # قاعدة البيانات
        SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={{"check_same_thread": False}})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()

        class Item(Base):
            __tablename__ = "items"
            id = Column(Integer, primary_key=True, index=True)
            title = Column(String, index=True)
            description = Column(String, default="")
            created_at = Column(DateTime, default=datetime.utcnow)

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True, index=True)
            username = Column(String, unique=True, index=True)
            hashed_password = Column(String)

        Base.metadata.create_all(bind=engine)

        # مستخدم افتراضي: admin / admin
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        def _bootstrap_user():
            db = SessionLocal()
            try:
                u = db.query(User).filter(User.username=="admin").first()
                if not u:
                    u = User(username="admin", hashed_password=pwd_context.hash("admin"))
                    db.add(u); db.commit()
            finally:
                db.close()
        _bootstrap_user()

        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

        app = FastAPI(title="{name} (CRUD+JWT)")

        # نماذج
        class ItemIn(BaseModel):
            title: str
            description: Optional[str] = ""
        class ItemOut(ItemIn):
            id: int
            created_at: datetime
            class Config:
                orm_mode = True

        class Token(BaseModel):
            access_token: str
            token_type: str = "bearer"

        # تبعيات
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        def authenticate(db: Session, username: str, password: str):
            user = db.query(User).filter(User.username==username).first()
            if not user: return None
            if not pwd_context.verify(password, user.hashed_password): return None
            return user

        def create_access_token(data: dict, expires_delta: timedelta | None = None):
            to_encode = data.copy()
            expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            to_encode.update({{"exp": expire}})
            return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={{"WWW-Authenticate": "Bearer"}},
            )
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str | None = payload.get("sub")
                if username is None:
                    raise credentials_exception
            except JWTError:
                raise credentials_exception
            user = db.query(User).filter(User.username==username).first()
            if user is None:
                raise credentials_exception
            return user

        @app.post("/token", response_model=Token)
        def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
            user = authenticate(db, form_data.username, form_data.password)
            if not user:
                raise HTTPException(status_code=400, detail="Incorrect username or password")
            token = create_access_token({{"sub": user.username}})
            return Token(access_token=token)

        @app.get("/")
        def root():
            return {{"ok": True, "endpoints": ["/items", "/token"], "auth": "use Bearer token"}}

        # CRUD محمي
        @app.get("/items", response_model=List[ItemOut])
        def list_items(db: Session = Depends(get_db), user=Depends(get_current_user)):
            return db.query(Item).order_by(Item.id.desc()).all()

        @app.post("/items", response_model=ItemOut)
        def create_item(payload: ItemIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
            it = Item(title=payload.title, description=payload.description or "")
            db.add(it); db.commit(); db.refresh(it)
            return it

        @app.get("/items/{{item_id}}", response_model=ItemOut)
        def get_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
            it = db.query(Item).get(item_id)
            if not it: raise HTTPException(404, "Not found")
            return it

        @app.delete("/items/{{item_id}}")
        def delete_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
            it = db.query(Item).get(item_id)
            if not it: raise HTTPException(404, "Not found")
            db.delete(it); db.commit()
            return {{"ok": True}}
        """).strip()

        req = textwrap.dedent("""
        fastapi==0.115.0
        uvicorn==0.30.6
        python-multipart==0.0.9
        passlib[bcrypt]==1.7.4
        python-jose==3.3.0
        sqlalchemy==2.0.36
        pydantic==2.9.2
        """).strip() + "\n"

        readme = textwrap.dedent(f"""
        # {name} — FastAPI + CRUD + JWT

        ## تشغيل محلي
        ```bash
        python -m venv .venv && . .venv/bin/activate  # على ويندوز: .venv\\Scripts\\activate
        pip install -r requirements.txt
        uvicorn app:app --reload
        ```
        ### تسجيل الدخول
        - Endpoint: `POST /token` (form-data: username=admin, password=admin)
        - بعد الحصول على `access_token` استخدمه كـ Bearer في الطلبات إلى /items
        """)

        return {
            f"{name}/app.py": app_py,
            f"{name}/requirements.txt": req,
            f"{name}/README.md": readme,
            f"{name}/.gitignore": ".venv/\n__pycache__/\n*.db\n",
        }

    def _telegram_bot(self, name: str) -> dict:
        bot_py = textwrap.dedent(f"""
        import os, requests, time

        TOKEN = os.environ.get("TELEGRAM_TOKEN", "PUT-YOUR-TOKEN")
        CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", None)

        def send(msg: str, chat_id: str | None = CHAT_ID):
            if not TOKEN or not chat_id:
                print("ضع TELEGRAM_TOKEN و TELEGRAM_CHAT_ID في المتغيرات.")
                return
            requests.get("https://api.telegram.org/bot{{}}/sendMessage".format(TOKEN),
                        params={{"chat_id": chat_id, "text": msg}})

        if __name__ == "__main__":
            print("Bot ready. CTRL+C للخروج.")
            while True:
                send("Hello from {name}!")
                time.sleep(60)
        """).strip()

        req = "requests==2.32.3\n"
        return {
            f"{name}/bot.py": bot_py,
            f"{name}/requirements.txt": req,
            f"{name}/README.md": f"# {name} (Telegram Bot)\\n\\nشغّل بـ:\\n```bash\\npython bot.py\\n```\\n",
        }

    def _html_widget(self, name: str) -> dict:
        index_html = textwrap.dedent(f"""
        <!doctype html><html lang="ar" dir="rtl">
        <meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title>{name}</title>
        <style>body{{font-family:Arial;background:#0f1222;color:#fff;padding:20px}} .box{{background:#161a2d;border-radius:14px;padding:16px}}</style>
        <div class="box">
          <h2>عنصر واجهة — {name}</h2>
          <p>مثال بسيط لودجت HTML.</p>
          <input id="inp" placeholder="اكتب أي شيء"/>
          <button onclick="go()">عرض</button>
          <pre id="out"></pre>
        </div>
        <script>
          function go(){{
            const v=document.getElementById('inp').value||'—';
            document.getElementById('out').textContent='أدخلت: '+v;
          }}
        </script>
        </html>
        """).strip()

        return {
            f"{name}/index.html": index_html,
            f"{name}/README.md": f"# {name} (HTML Widget)\\nافتح index.html في المتصفح.\\n",
        }

    # ------------------------- أدوات -------------------------

    def _write_zip(self, name: str, files: dict) -> str:
        """يكتب القوالب إلى ZIP داخل EXPORT_DIR ويعيد المسار."""
        ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        zip_name = f"{name}-{ts}.zip"
        zip_path = EXPORT_DIR / zip_name

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for rel, content in files.items():
                data = content.encode("utf-8")
                zf.writestr(rel.replace("\\\\", "/"), data)

        return str(zip_path)

    def _safe_name(self, s: str) -> str:
        s = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in s.strip())
        while "--" in s: s = s.replace("--", "-")
        return s.strip("-_") or "my-app"
