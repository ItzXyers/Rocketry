#pragma once

// The ground-console page served at GET / by wireless.cpp. Self-contained:
// the phone/laptop is on the flight computer's AP with no internet, so no
// external CSS/JS/fonts. Talks to /status, /logs.json, /log?n=,
// POST /log/delete?n= and POST /arm.
//
// Keep it small: it lives in the app partition and is sent in one go.

static const char WEB_UI_HTML[] = R"HTML(<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Flight Computer</title>
<style>
:root{--bg:#f4f5f7;--card:#fff;--ink:#16181d;--mute:#667085;--line:#e3e6eb;--ok:#14804a;--okb:#e3f5ea;--warn:#a15c00;--warnb:#fff3df;--bad:#c4271c;--badb:#fde8e6;--acc:#1f5fd6}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--card:#181b21;--ink:#e8eaee;--mute:#98a2b3;--line:#2a2f38;--ok:#4cc38a;--okb:#14281e;--warn:#f0b35b;--warnb:#2c2214;--bad:#ff6b5e;--badb:#2e1614;--acc:#6b9bff}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.4 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:720px;margin:0 auto;padding:16px}
header{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:12px}
h1{font-size:18px;margin:0}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);margin:0 0 10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin-bottom:12px}
.pill{display:inline-block;padding:3px 10px;border-radius:999px;font-weight:600;font-size:13px;background:var(--line)}
.ok{background:var(--okb);color:var(--ok)}.warn{background:var(--warnb);color:var(--warn)}.bad{background:var(--badb);color:var(--bad)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.k{font-size:12px;color:var(--mute)}.v{font-size:18px;font-weight:600;font-variant-numeric:tabular-nums}
.big{font-size:26px}
button,.btn{font:inherit;font-weight:600;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:8px 12px;cursor:pointer;text-decoration:none;display:inline-block}
button:disabled{opacity:.45;cursor:not-allowed}
#arm{width:100%;padding:16px;font-size:18px;background:var(--bad);border-color:var(--bad);color:#fff;margin-top:10px}
.del{color:var(--bad)}
table{width:100%;border-collapse:collapse}
td{padding:8px 4px;border-top:1px solid var(--line);vertical-align:middle}
td.r{text-align:right;white-space:nowrap}
.bar{height:6px;background:var(--line);border-radius:3px;overflow:hidden;margin-top:6px}.bar i{display:block;height:100%;background:var(--acc)}
ul{margin:6px 0 0;padding:0;list-style:none}li{margin:2px 0}
.note{color:var(--mute);font-size:13px;margin:8px 0 0}
#banner{display:none;font-weight:600}
</style></head><body><main>
<header><h1>Flight Computer</h1><span id="link" class="pill">connecting…</span></header>

<div id="banner" class="card"></div>

<section class="card">
<h2>Status</h2>
<div class="grid">
<div><div class="k">Flight state</div><div class="v big" id="state">–</div></div>
<div><div class="k">Battery</div><div class="v big" id="batt">–</div><div class="k" id="battv"></div><div class="bar"><i id="battbar" style="width:0"></i></div></div>
<div><div class="k">Boot self-test</div><div class="v" id="selftest">–</div></div>
<div><div class="k">Sensors</div><div class="v" id="sensors">–</div></div>
<div><div class="k">Altitude AGL</div><div class="v" id="alt">–</div></div>
<div><div class="k">Accel |g|</div><div class="v" id="acc">–</div></div>
<div><div class="k">Pressure</div><div class="v" id="pres">–</div></div>
<div><div class="k">Temperature</div><div class="v" id="temp">–</div></div>
<div><div class="k">Logging to</div><div class="v" id="logfile">–</div></div>
<div><div class="k">Uptime</div><div class="v" id="up">–</div></div>
</div>
</section>

<section class="card">
<h2>Arm</h2>
<ul id="checks"></ul>
<button id="arm" disabled>ARM</button>
<p class="note">Arming re-zeros the altimeter to the pad, then turns Wi-Fi off for the rest of this power cycle. Do it on the rail, last thing before you walk away. You'll hear <b>beep-beep-beeeep</b>, then a quick double chirp every 4&nbsp;s until launch. Five fast blips = arm refused.</p>
</section>

<section class="card">
<h2>Logs</h2>
<div id="space" class="note" style="margin:0 0 6px"></div>
<table><tbody id="logs"><tr><td class="note">loading…</td></tr></tbody></table>
<p class="note">Downloading or deleting pauses launch detection for a moment — fine on the bench or pad, never mid-countdown.</p>
<button id="reload">Refresh list</button>
</section>
</main>
<script>
const $=id=>document.getElementById(id);
let st=null,armed=false,busy=false;
const kb=b=>b>=1048576?(b/1048576).toFixed(2)+' MB':(b/1024).toFixed(1)+' KB';
const pill=(el,txt,cls)=>{el.textContent=txt;el.className='pill '+(cls||'')};
function fmtUp(ms){const s=Math.floor(ms/1000),h=Math.floor(s/3600),m=Math.floor(s%3600/60);return(h?h+'h ':'')+m+'m '+(s%60)+'s'}
function banner(txt,cls){const b=$('banner');b.style.display=txt?'block':'none';b.textContent=txt||'';b.className='card '+(cls||'')}

async function j(url,opt,ms){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms||4000);
 try{const r=await fetch(url,Object.assign({signal:c.signal,cache:'no-store'},opt||{}));const d=await r.json().catch(()=>({}));return{status:r.status,d}}finally{clearTimeout(t)}}

function checks(s){
 return[
  [s.flight_state==='IDLE_ARMED','On the pad (IDLE_ARMED)'],
  [s.boot_self_test_passed,'Boot self-test passed'],
  [s.baro_valid&&s.accel_valid,'Barometer and accelerometer reading'],
  [s.logger_ready&&!s.logger_full,'Logging to flash'],
  [s.batt_valid&&!s.batt_low,'Battery OK'+(s.batt_valid?'':' (no reading)')],
 ];
}

function render(s){
 st=s;
 const bad=s.flight_state==='ERROR',good=s.flight_state==='IDLE_ARMED';
 $('state').textContent=s.flight_state;$('state').style.color=bad?'var(--bad)':good?'var(--ok)':'';
 if(s.batt_valid){$('batt').textContent=s.batt_percent+'%';$('battv').textContent=s.batt_voltage_v.toFixed(2)+' V'+(s.batt_low?' — LOW':'');$('batt').style.color=s.batt_low?'var(--bad)':'';$('battbar').style.width=s.batt_percent+'%'}
 else{$('batt').textContent='–';$('battv').textContent='no reading';$('battbar').style.width='0'}
 $('selftest').textContent=s.boot_self_test_passed?'passed':'FAILED';$('selftest').style.color=s.boot_self_test_passed?'var(--ok)':'var(--bad)';
 $('sensors').textContent='baro '+(s.baro_valid?'✓':'✗')+'  accel '+(s.accel_valid?'✓':'✗');
 $('alt').textContent=s.altitude_agl_m.toFixed(1)+' m';
 $('acc').textContent=s.accel_mag_g.toFixed(2)+' g';
 $('pres').textContent=(s.pressure_pa/100).toFixed(1)+' hPa';
 $('temp').textContent=s.temperature_c.toFixed(1)+' °C';
 $('logfile').textContent=s.logger_ready?('FLIGHT'+String(s.log_file_number).padStart(3,'0')+(s.logger_full?' FULL':'')):'not ready';
 $('up').textContent=fmtUp(s.uptime_ms);
 const c=checks(s);
 $('checks').innerHTML=c.map(([ok,t])=>'<li style="color:var(--'+(ok?'ok':'bad')+')">'+(ok?'✓ ':'✗ ')+t+'</li>').join('');
 const hard=c[0][0]&&c[1][0];
 $('arm').disabled=armed||busy||!hard;
 $('arm').textContent=armed?'ARMED':busy?'Arming… hold still':'ARM';
}

async function poll(){
 if(armed)return;
 if(busy){setTimeout(poll,1000);return}
 try{const r=await j('/status');if(r.status===200){render(r.d);pill($('link'),'connected','ok')}}
 catch(e){pill($('link'),'no link','bad')}
 setTimeout(poll,1000);
}

async function loadLogs(){
 const tb=$('logs');
 try{
  const {d}=await j('/logs.json',null,8000);
  $('space').textContent=d.mounted?kb(d.free_bytes)+' free of '+kb(d.total_bytes):'Flash not mounted';
  if(!d.logs||!d.logs.length){tb.innerHTML='<tr><td class="note">No logs on the board.</td></tr>';return}
  d.logs.sort((a,b)=>b.n-a.n);
  tb.innerHTML=d.logs.map(l=>'<tr><td><b>'+l.name+'</b>'+(l.current?' <span class="pill ok">this boot</span>':'')+'<div class="note" style="margin:0">'+kb(l.bytes)+'</div></td>'+
   '<td class="r"><a class="btn" href="/log?n='+l.n+'" download="'+l.name+'">Download</a> '+
   (l.current?'':'<button class="del" data-n="'+l.n+'" data-name="'+l.name+'">Delete</button>')+'</td></tr>').join('');
 }catch(e){tb.innerHTML='<tr><td class="note">Couldn\'t load the log list.</td></tr>'}
}

$('logs').addEventListener('click',async e=>{
 const b=e.target.closest('button.del');if(!b)return;
 if(!confirm('Delete '+b.dataset.name+' from the flight computer? This can\'t be undone.'))return;
 b.disabled=true;b.textContent='Deleting…';
 try{const r=await j('/log/delete?n='+b.dataset.n,{method:'POST'},10000);
  if(!r.d.ok)alert('Delete failed: '+(r.d.reason||r.status));}
 catch(e){alert('Delete failed: no response')}
 loadLogs();
});
$('reload').onclick=loadLogs;

$('arm').onclick=async()=>{
 if(!st)return;
 const warn=checks(st).filter(c=>!c[0]).map(c=>'• '+c[1]).join('\n');
 if(!confirm('ARM the flight computer?\n\nThe altimeter re-zeros here and Wi-Fi turns OFF until the next power cycle — this page will stop updating.'+(warn?'\n\nNot OK:\n'+warn:'')))return;
 busy=true;render(st);banner('Arming — keep the rocket still (about 5 s)…','warn');
 try{
  const r=await j('/arm',{method:'POST'},20000);
  if(r.d.ok){armed=true;render(st);pill($('link'),'Wi-Fi off','');
   banner('ARMED. Pad baseline '+(r.d.pad_baseline_pressure_pa/100).toFixed(1)+' hPa. Wi-Fi is now off — listen for the double chirp every 4 s.','ok');return}
  banner('Arm refused: '+(r.d.reason||('HTTP '+r.status))+(r.d.flight_state?' ('+r.d.flight_state+')':''),'bad');
 }catch(e){
  banner('No reply — the board may have armed and dropped Wi-Fi. Listen: beep-beep-beeeep then a double chirp every 4 s = armed. Five fast blips = refused.','warn');
 }
 busy=false;if(st)render(st);
};

poll();loadLogs();
</script></body></html>)HTML";
