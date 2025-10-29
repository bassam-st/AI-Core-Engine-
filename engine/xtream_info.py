import requests
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/xtream", tags=["Xtream Info"])

XTREAM_SERVER = "http://mhiptv.info:2095"
USERNAME = "47482"
PASSWORD = "395847"

@router.get("/account")
def get_account_info():
    """
    يجلب بيانات حسابك (عدد الاتصالات، الحالة، تاريخ الانتهاء)
    """
    try:
        url = f"{XTREAM_SERVER}/player_api.php?username={USERNAME}&password={PASSWORD}"
        r = requests.get(url, timeout=10)
        data = r.json()
        info = data.get("user_info", {})
        return JSONResponse({
            "status": info.get("status"),
            "active_cons": info.get("active_cons"),
            "max_connections": info.get("max_connections"),
            "exp_date": info.get("exp_date"),
            "message": "✅ تم جلب بيانات الاشتراك بنجاح"
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/live")
def get_live_streams():
    """
    يجلب قائمة القنوات المباشرة
    """
    try:
        url = f"{XTREAM_SERVER}/player_api.php?username={USERNAME}&password={PASSWORD}&action=get_live_streams"
        r = requests.get(url, timeout=10)
        channels = r.json()
        return JSONResponse({"ok": True, "count": len(channels), "channels": channels[:20]})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
