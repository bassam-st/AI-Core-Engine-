import express from "express";
import fetch from "node-fetch";

const app = express();

// إعداد CORS
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  if (req.method === "OPTIONS") return res.sendStatus(200);
  next();
});

// ✅ جلب تصنيفات Xtream / القنوات / التفاصيل
app.get("/xtream", async (req, res) => {
  try {
    const { host, endpoint = "player_api.php", ...params } = req.query;
    if (!host) return res.status(400).send("Missing host");

    const url = new URL(`http://${host}/${endpoint}`);
    for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);

    const r = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0" } });
    const text = await r.text();

    res.set("content-type", "application/json; charset=utf-8");
    return res.send(text);
  } catch (err) {
    console.error(err);
    res.status(500).send("Proxy error");
  }
});

// ✅ تشغيل روابط m3u8 للقنوات
app.get("/x", async (req, res) => {
  try {
    const { url } = req.query;
    if (!url) return res.status(400).send("Missing url");

    const r = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0" } });
    res.set("content-type", "application/vnd.apple.mpegurl; charset=utf-8");
    r.body.pipe(res);
  } catch (err) {
    console.error(err);
    res.status(500).send("Stream proxy error");
  }
});

// ✅ الصفحة الافتراضية
app.get("/", (req, res) => {
  res.send("✅ Xtream Proxy is running successfully");
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Xtream Proxy running on port ${PORT}`);
});
