# engine/orchestrator.py
import os, re, asyncio, hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx

from engine.config import DATA_DIR
from engine.retriever import Retriever
from engine.generator import AnswerSynthesizer
from engine.ingest_web import ingest_url
from engine.ingest_youtube import ingest_youtube

CORPUS_DIR = os.path.join(DATA_DIR, "corpus")
os.makedirs(CORPUS_DIR, exist_ok=True)

# —— أدوات بسيطة ——
def _norm(q: str) -> str:
    return re.sub(r"\s+", " ", (q or "").strip())

def _dedup_links(links: List[str]) -> List[str]:
    seen, out = set(), []
    for u in links:
        k = re.sub(r"#.*$", "", u.strip())
        if k not in seen:
            seen.add(k); out.append(u)
    return out

# —— بحث ويب (Google CSE إن وجد، وإلا DuckDuckGo عبر html) ——
async def _google_cse(query: str, api_key: str, cx: str, n: int = 5) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get("https://www.googleapis.com/customsearch/v1",
            params={"key": api_key, "cx": cx, "q": query, "num": min(n,10)})
        r.raise_for_status()
        items = r.json().get("items", []) or []
        return [{"title": i.get("title"), "link": i.get("link")} for i in items][:n]

async def _ddg_lite(query: str, n: int = 5) -> List[Dict[str, Any]]:
    # بديل بسيط (غير رسمي) — يُمكنك استبداله بمكتبة أخرى
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get("https://duckduckgo.com/html/", params={"q": query, "kl":"wt-wt"})
        r.raise_for_status()
        html = r.text
    # استخراج روابط بشكل مبسّط
    links = re.findall(r'href="(https?://[^"]+)"', html)
    out = []
    for lk in _dedup_links(links)[:n*2]:
        if "duckduckgo.com" in lk: 
            continue
        out.append({"title": lk.split("//",1)[-1][:80], "link": lk})
        if len(out) >= n: break
    return out

async def web_search(query: str, n: int = 5) -> List[Dict[str, Any]]:
    key = os.getenv("GOOGLE_API_KEY","").strip()
    cx  = os.getenv("GOOGLE_CSE_ID","").strip()
    try:
        if key and cx:
            return await _google_cse(query, key, cx, n=n)
        return await _ddg_lite(query, n=n)
    except Exception:
        return []

# —— بحث يوتيوب (إرجاع روابط فيديو) ——
async def yt_search(query: str, n: int = 3) -> List[str]:
    # أبسط طريقة: استخدم بحث الويب مع site:youtube.com
    rs = await web_search(f"site:youtube.com {query}", n=n)
    links = [r["link"] for r in rs if "watch?v=" in r.get("link","")]
    return _dedup_links(links)[:n]

# —— التقاط المحتوى (ingest) ——
async def ingest_links(links: List[str]) -> List[str]:
    saved = []
    for url in links:
        try:
            if "youtube.com/watch" in url or "youtu.be/" in url:
                p = ingest_youtube(url)
            else:
                p = ingest_url(url)
            saved.append(p)
        except Exception:
            continue
    return saved

# —— خط الأنسر (RAG) ——
class MultiSourceRAG:
    def __init__(self, retriever: Optional[Retriever] = None, generator: Optional[AnswerSynthesizer] = None):
        self.retriever = retriever or Retriever()
        self.generator = generator or AnswerSynthesizer()

    async def answer(
        self,
        query: str,
        top_web: int = 5,
        top_yt: int = 3,
        ingest_after_search: bool = True,
        k_ctx: int = 6,
        style: Optional[str] = None,
    ) -> Dict[str, Any]:
        q = _norm(query)
        # 1) بحث متوازي
        web_task = asyncio.create_task(web_search(q, n=top_web))
        yt_task  = asyncio.create_task(yt_search(q, n=top_yt))
        web_res, yt_links = await asyncio.gather(web_task, yt_task)

        links = [r["link"] for r in web_res] + yt_links
        links = _dedup_links(links)

        # 2) ingest اختياري
        saved_paths = []
        if ingest_after_search and links:
            saved_paths = await ingest_links(links)
            try:
                self.retriever.build_index()
            except Exception:
                pass

        # 3) استرجاع سياق
        ctx_chunks = []
        try:
            ctx_chunks = self.retriever.search(q, top_k=k_ctx)
        except Exception:
            ctx_chunks = []

        # 4) توليد مع مراجع (بسرد الروابط بالأخير)
        answer = self.generator.generate(q, context_chunks=ctx_chunks, style=style, max_tokens=900)
        cites  = links[: min(len(links), 8)]
        return {"ok": True, "answer": answer, "sources": cites, "ingested": saved_paths}
