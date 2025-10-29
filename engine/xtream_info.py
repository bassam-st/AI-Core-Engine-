# تابع للكود الموجود لديك
from __future__ import annotations
import httpx, json, time
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from engine.xtream_store import load_xtream
from engine.config import cfg

router = APIRouter(prefix="/xtream", tags=["Xtream"])

LOCK_FILE = Path(cfg.DATA_DIR) / "session_locks.json"
LOCK_TTL = 60 * 60  # 60 دقيقة لكل جلسة افتراضيًا

def _load_locks():
    if LOCK_FILE.exists():
        try: return json.loads(LOCK_FILE.read_text(encoding="utf-8"))
        except: return {}
    return {}

def _save_locks(data): 
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

def _cleanup_locks():
    now = int(time.time())
    data = _load_locks()
    data = {k:v for k,v in data.items() if v.get("exp",0) > now}
    _save_locks(data)
    return data

def _base_params(action: str | None = None) -> str:
    cfgx = load_xtream()
    if not cfgx:
        raise HTTPException(400, "Xtream not configured.")
    base = f"{cfgx['server']}/player_api.php?username={cfgx['username']}&password={cfgx['password']}"
    if action: base += f"&action={action}"
    return base

@router.get("/account")
def account():
    url = _base_params()
    r = httpx.get(url, timeout=20)
    r.raise_for_status()
    info = r.json().get("user_info", {})
    return {
        "status": info.get("status"),
        "active_cons": int(info.get("active_cons", 0) or 0),
        "max_connections": int(info.get("max_connections", 0) or 0),
        "exp_date": info.get("exp_date"),
    }

@router.post("/session/start")
def session_start(ttl: int = LOCK_TTL):
    """يحجز جلسة تشغيل إذا كان هناك سعة متاحة."""
    # تحديث القيم الحقيقية من السيرفر
    acc = account()
    if acc["status"] != "Active":
        return JSONResponse({"ok": False, "reason": "inactive"}, status_code=400)

    # تنظيف وإنزال الأقفال المنتهية
    locks = _cleanup_locks()
    active_local = len(locks)
    active_remote = acc["active_cons"]
    maxc = acc["max_connections"]

    # سياسة مُحافظة: لا نسمح بتجاوز الحد إطلاقًا
    if active_remote + 1 > maxc:  # +1 لطلب التشغيل الحالي
        return {"ok": False, "reason": "limit_reached", "active_remote": active_remote, "max": maxc}

    # إنشاء توكن للجلسة
    tok = str(int(time.time()*1000))
    locks[tok] = {"exp": int(time.time()) + int(ttl)}
    _save_locks(locks)
    return {"ok": True, "token": tok, "ttl": ttl}

@router.post("/session/stop")
def session_stop(token: str):
    locks = _load_locks()
    if token in locks:
        del locks[token]
        _save_locks(locks)
    return {"ok": True}
