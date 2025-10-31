import express from "express";
import fetch from "node-fetch";

const app = express();

app.get("/x", async (req, res) => {
  const target = req.query.url;
  if (!target) return res.status(400).send("Missing url");

  const range = req.headers.range;

  const hdrs = {
    "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Origin": "http://127.0.0.1",
    "Referer": "http://127.0.0.1/",
    "Connection": "keep-alive",
  };
  if (range) hdrs["Range"] = range;

  const upstream = await fetch(target, { headers: hdrs });
  res.status(upstream.status);
  upstream.headers.forEach((v, k) => res.setHeader(k, v));

  // ثبّت نوع المحتوى إذا لم يكن محدد
  const ct = upstream.headers.get("content-type") || "";
  if (!ct && target.endsWith(".m3u8")) {
    res.setHeader("Content-Type", "application/vnd.apple.mpegurl; charset=utf-8");
  }

  // CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS");

  upstream.body.pipe(res);
});

app.get("/", (_req, res) => res.send("Proxy OK ✅"));
const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log("LISTEN", PORT));
