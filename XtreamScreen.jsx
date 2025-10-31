import React, { useEffect, useMemo, useRef, useState } from "react";

const BASE_PROXY = "https://ai-core-proxy.bassam-7111111.workers.dev";

export default function XtreamScreen() {
  const [host, setHost] = useState(localStorage.getItem("xt_host") || "");
  const [u, setU]       = useState(localStorage.getItem("xt_u") || "");
  const [p, setP]       = useState(localStorage.getItem("xt_p") || "");
  const [status, setStatus] = useState("جاهز");
  const [cats, setCats] = useState([]);
  const [streams, setStreams] = useState([]);
  const [allStreams, setAllStreams] = useState([]);
  const [catId, setCatId] = useState(null);
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("name");
  const videoRef = useRef(null);

  const needCreds = useMemo(()=> !(host && u && p), [host,u,p]);
  const qp = (obj)=> Object.entries(obj).map(([k,v])=>`${k}=${encodeURIComponent(v)}`).join("&");

  const save = ()=>{
    localStorage.setItem("xt_host", host);
    localStorage.setItem("xt_u", u);
    localStorage.setItem("xt_p", p);
    loadCats();
  };

  async function loadCats(){
    if (needCreds){ setStatus("أدخل بيانات Xtream ثم احفظ"); setCats([]); setStreams([]); return; }
    setStatus("جلب التصنيفات…");
    try{
      const res = await fetch(`${BASE_PROXY}/xtream?`+qp({host,u,p,endpoint:"player_api.php",action:"get_live_categories"}));
      const data = await res.json(); setCats(data || []); setStatus("اختر تصنيفًا");
    }catch(e){ console.error(e); setStatus("تعذر جلب التصنيفات"); }
  }

  async function loadStreams(category_id){
    setCatId(category_id); setStatus("جلب القنوات…"); setStreams([]);
    try{
      const res = await fetch(`${BASE_PROXY}/xtream?`+qp({host,u,p,endpoint:"player_api.php",action:"get_live_streams",category_id}));
      const data = await res.json(); setAllStreams(Array.isArray(data)?data:[]); setStatus("تم");
    }catch(e){ console.error(e); setStatus("تعذر جلب القنوات"); }
  }

  useEffect(()=>{ loadCats(); /* eslint-disable-next-line */ },[]);
  useEffect(()=>{
    let items = allStreams.slice();
    if (q) items = items.filter(s => (s.name||"").toLowerCase().includes(q.toLowerCase()));
    items.sort((a,b)=> sort==="id" ? ((+a.stream_id||0)-(+b.stream_id||0)) : (a.name||"").localeCompare(b.name||""));
    setStreams(items);
  }, [q, sort, allStreams]);

  const canNativeHLS = ()=>{
    const v = document.createElement("video");
    return v.canPlayType('application/vnd.apple.mpegURL') || v.canPlayType('application/x-mpegURL');
  };

  const startVideo = async (hlsUrl)=>{
    const video = videoRef.current;
    if (!video) return;
    if (canNativeHLS()){ video.src = hlsUrl; video.play().catch(()=>{}); return; }
    if (!window.Hls){
      await new Promise((ok,err)=>{ const s=document.createElement("script"); s.src="https://cdn.jsdelivr.net/npm/hls.js@latest"; s.onload=ok; s.onerror=err; document.head.appendChild(s); });
    }
    if (window.Hls && window.Hls.isSupported()){
      const hls = new window.Hls(); hls.loadSource(hlsUrl); hls.attachMedia(video);
      hls.on(window.Hls.Events.MANIFEST_PARSED, ()=> video.play().catch(()=>{}));
    }else{ video.src = hlsUrl; video.play().catch(()=>{}); }
  };

  const playStream = (stream_id)=>{
    const url = `${BASE_PROXY}/xplay?`+qp({host,u,p,stream:stream_id,type:"m3u8"});
    startVideo(url); setStatus(`تشغيل: #${stream_id}`);
  };

  return (
    <div style={{background:"#0b0f17", color:"#e9edf1", minHeight:"100vh"}}>
      <div style={{padding:16, background:"#111827", borderBottom:"1px solid #1f2937"}}>
        <b>🎯 شاشة Xtream</b> <span style={{opacity:.7, fontSize:13}}>— أدخل بياناتك مرة ثم افتح مباشرة</span>
      </div>

      <div style={{display:"grid", gridTemplateColumns:"320px 1fr", gap:14, padding:14}}>
        <section style={{background:"#0f172a", border:"1px solid #1f2937", borderRadius:14, padding:12}}>
          <h3>إعدادات Xtream</h3>
          <div style={{display:"flex", gap:8, marginTop:8, flexWrap:"wrap"}}>
            <input value={host} onChange={e=>setHost(e.target.value)} placeholder="host:port" style={inp}/>
            <input value={u} onChange={e=>setU(e.target.value)} placeholder="u" style={inp}/>
            <input value={p} onChange={e=>setP(e.target.value)} placeholder="p" type="password" style={inp}/>
            <button onClick={save} style={btnPrimary}>حفظ/تحديث</button>
          </div>
          <h3 style={{marginTop:10}}>التصنيفات</h3>
          <div style={{display:"flex", gap:8, flexWrap:"wrap", maxHeight:"46vh", overflow:"auto"}}>
            {cats.map(c=>(
              <button key={c.category_id}
                onClick={()=>loadStreams(c.category_id)}
                style={{...chip, ...(c.category_id===catId?chipActive:{})}}>
                {c.category_name || ("تصنيف #"+c.category_id)}
              </button>
            ))}
          </div>
        </section>

        <section style={{background:"#0f172a", border:"1px solid #1f2937", borderRadius:14, padding:12}}>
          <div style={{display:"flex", justifyContent:"space-between"}}>
            <h3>المشغّل</h3>
            <div style={{opacity:.7, fontSize:13}}>{status}</div>
          </div>
          <video ref={videoRef} controls playsInline style={{width:"100%", maxHeight:"62vh", background:"#000", borderRadius:12, border:"1px solid #1f2937"}} />

          <div style={{display:"flex", gap:8, marginTop:10}}>
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="ابحث باسم القناة…" style={{...inp, flex:1}}/>
            <select value={sort} onChange={e=>setSort(e.target.value)} style={inp}>
              <option value="name">الاسم (أ-ي)</option>
              <option value="id">حسب المعرّف</option>
            </select>
          </div>

          <h4 style={{margin:"10px 0 6px"}}>القنوات</h4>
          <div style={{display:"grid", gap:8, maxHeight:"54vh", overflow:"auto"}}>
            {streams.map(s=>(
              <div key={s.stream_id} style={item}>
                <div style={{flex:1}}>{s.name || "بدون اسم"}</div>
                <div style={{opacity:.75, fontSize:12}}>#{s.stream_id}</div>
                <button onClick={()=>playStream(s.stream_id)} style={btn}>تشغيل ▶</button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

const inp = {padding:"10px 12px", borderRadius:10, border:"1px solid #374151", background:"#0f172a", color:"#e5e7eb"};
const btn = {padding:"10px 12px", borderRadius:10, border:"1px solid #374151", background:"#0f172a", color:"#e5e7eb", cursor:"pointer"};
const btnPrimary = {...btn, background:"#2563eb", borderColor:"#1d4ed8"};
const chip = {border:"1px solid #334155", background:"#0b1220", borderRadius:999, padding:"8px 12px"};
const chipActive = {background:"#1d4ed8", borderColor:"#1d4ed8"};
const item = {display:"flex", alignItems:"center", gap:10, padding:10, borderRadius:10, border:"1px solid #1f2937", background:"#0b1220"};
