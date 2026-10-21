// usage: node shot.js page.html "t1,t2" prefix [w h]
const puppeteer=require('puppeteer-core'),serve=require('./serve');
(async()=>{const [page,ts,prefix,w='1920',h='1080']=process.argv.slice(2);
const srv=await serve(__dirname,8765);
const b=await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=d3d11','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage();await p.setViewport({width:+w,height:+h});
p.on('console',m=>console.log('PAGE:',m.text()));p.on('pageerror',e=>console.log('ERR:',e.message));
await p.goto('http://localhost:8765/'+page);await p.waitForFunction('window.ready===true',{timeout:60000});
for(const t of ts.split(',')){await p.evaluate(t=>window.renderAt(+t),t);await p.screenshot({path:`${prefix}_${t}.png`});}
await b.close();srv.close();})();
