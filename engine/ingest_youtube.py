import os
import re
import hashlib
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp

try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None  # fallback لو ما توفّر

from engine.config import DATA_DIR

CORPUS_DIR = os.path.join(DATA_DIR, "corpus")
os.makedirs(CORPUS_DIR, exist_ok=True)

def _video_id(url: str) -> str:
    # يدعم الروابط الشائعة
    if "youtube.com" in url:
        qs = parse_qs(urlparse(url).query)
        return (qs.get("v") or [""])[0]
    if "youtu.be" in url:
        return urlparse(url).path.strip("/")
    return ""

def _filename(title_or_id: str) -> str:
    base = re.sub(r"[\W_]+", "-", title_or_id).strip("-").lower() or "video"
    h = hashlib.md5(title_or_id.encode("utf-8")).hexdigest()[:8]
    return f"youtube-{base}-{h}.txt"

def _write_doc(path: str, meta: dict, text: str):
    header = [
        f"TITLE: {meta.get('title','')}",
        f"URL: {meta.get('url','')}",
        f"CHANNEL: {meta.get('channel','')}",
        f"PUBLISHED_AT: {meta.get('published_at','')}",
        f"FETCHED_AT_UTC: {datetime.utcnow().isoformat()}",
        "-"*80, ""
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(header))
        f.write(text)
        f.write("\n")

def _get_basic_metadata(url: str) -> dict:
    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title",""),
        "channel": info.get("uploader",""),
        "published_at": info.get("upload_date",""),
        "url": url
    }

def ingest_youtube(url: str, prefer_langs=("ar","en"), use_whisper_fallback=True, whisper_model_size="small"):
    """
    يحاول أولاً جلب النصوص (Captions) من YouTube.
    لو لم تتوفر، خيارياً يحمل الصوت ويُفرّغه بـ Whisper (لو ffmpeg متوفر).
    يرجّع مسار الملف النصي داخل data/corpus.
    """
    vid = _video_id(url)
    meta = _get_basic_metadata(url)
    meta["url"] = url
    title_or_id = meta["title"] or vid or "youtube"

    # 1) حاول نصوص يوتيوب مباشرة
    try:
        transcript = None
        # جرّب العربية ثم الإنجليزية
        for lang in list(prefer_langs) + ["en"]:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(vid, languages=[lang])
                break
            except Exception:
                continue

        if transcript:
            text = "\n".join([t["text"] for t in transcript if t.get("text")])
            path = os.path.join(CORPUS_DIR, _filename(title_or_id))
            _write_doc(path, meta, text)
            return path
    except (TranscriptsDisabled, NoTranscriptFound, KeyError):
        pass
    except Exception:
        pass

    # 2) تفريغ بالصوت (Whisper) كخيار احتياطي
    if use_whisper_fallback and WhisperModel is not None:
        audio_path = os.path.join(CORPUS_DIR, f"tmp-{vid}.m4a")
        out_text = []
        ydl_opts = {
            "quiet": True,
            "format": "bestaudio/best",
            "outtmpl": audio_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "192",
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        model = WhisperModel(whisper_model_size, device="cpu")
        segments, _ = model.transcribe(audio_path, beam_size=1)
        for seg in segments:
            out_text.append(seg.text.strip())

        text = "\n".join(out_text)
        path = os.path.join(CORPUS_DIR, _filename(title_or_id))
        _write_doc(path, meta, text)

        # نظّف الملف المؤقت
        try:
            os.remove(audio_path)
        except OSError:
            pass

        return path

    # لو وصلنا هنا: لا توجد نصوص ولا تفريغ
    raise RuntimeError("لا توجد ترجمات للفيديو ولم يُفعّل التفريغ (أو Whisper غير متاح).")
