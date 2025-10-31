# engine/xtream_proxy.py
from __future__ import annotations
import os, json, urllib.parse
from typing import Optional, Any, Dict, List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse
import httpx

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

BASE_PROXY = os.getenv("BASE_PROXY", "").strip() or "https://YOUR-WORKER.workers.dev"
XTREAM_HOST = os.getenv("XTREAM_HOST", "").strip()     # مثال: mhiptv.info:2095
XTREAM_U    = os.getenv("XTREAM_U", "").strip()
XTREAM_P    = os.getenv("XTREAM_P", "").strip()

def _qs(params: Dict[str, Any]) -> str:
    return urllib.parse.urlencode(params, doseq=True, safe=":/")

def _xt_url(**extra) -> str:
    params = dict(
        host=extra.pop("host", XTREAM_HOST),
        u=extra.pop("u", XTREAM_U),
        p=extra.pop("p", XTREAM_P),
        endpoint=extra.pop("endpoint", "player_api.php"),
    )
    params.update(extra)
    return f"{BASE_PROXY}/xtream?{_qs(params)}"

async def _get_json(url: str) -> Any:
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.get(url)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, f"Upstream error {r.status_code}")
        try:
            return r.json()
        except Exception:
            # بعض البانيلات ترجع نص JSON غير قياسي
            return json.loads(r.text)

def _cfg_ok() -> bool:
    return all([BASE_PROXY, XTREAM_HOST, XTREAM_U, XTREAM_P])

@router.get("/ping")
async def ping() -> JSONResponse:
    return JSONResponse({
        "ok": _cfg_ok(),
        "base_proxy": BASE_PROXY,
        "host": XTREAM_HOST,
        "u_mask": XTREAM_U[:2] + "***" if XTREAM_U else "",
        "p_mask": XTREAM_P[:1] + "***" if XTREAM_P else "",
    })

@router.get("/categories")
async def categories(
    host: Optional[str] = None, u: Optional[str] = None, p: Optional[str] = None
):
    url = _xt_url(host=host or XTREAM_HOST, u=u or XTREAM_U, p=p or XTREAM_P,
                  action="get_live_categories")
    return await _get_json(url)

@router.get("/channels")
async def channels(
    category_id: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    host: Optional[str] = None, u: Optional[str] = None, p: Optional[str] = None
):
    url = _xt_url(host=host or XTREAM_HOST, u=u or XTREAM_U, p=p or XTREAM_P,
                  action="get_live_streams", category_id=category_id or "")
    data = await _get_json(url)
    items: List[Dict[str, Any]] = data if isinstance(data, list) else []
    if q:
        ql = q.lower().strip()
        items = [s for s in items if (s.get("name") or "").lower().find(ql) >= 0]
    # تبسيط الحقول
    out = [{
        "stream_id": s.get("stream_id"),
        "name": s.get("name"),
        "category": s.get("category_name") or s.get("category_id"),
    } for s in items]
    return {"ok": True, "count": len(out), "channels": out}

@router.get("/stream/{stream_id}.m3u8")
async def stream_hls(stream_id: str,
                     host: Optional[str] = None, u: Optional[str] = None, p: Optional[str] = None):
    # نعيد توجيه للـ Worker xplay مع النوع m3u8 ليتشغل داخل <video>
    qp = _qs({
        "host": host or XTREAM_HOST,
        "u": u or XTREAM_U,
        "p": p or XTREAM_P,
        "stream": stream_id,
        "type": "m3u8",
    })
    url = f"{BASE_PROXY}/xplay?{qp}"
    return RedirectResponse(url, status_code=302)
