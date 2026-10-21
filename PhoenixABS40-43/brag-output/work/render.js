const puppeteer=require('puppeteer-core'),serve=require('./serve');
(async()=>{const srv=await serve(__dirname,8768);
const b=await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--ignore-gpu-blocklist']});
const p=await b.newPage();await p.setViewport({width:1920,height:1080});
p.on('pageerror',e=>console.log('ERR:',e.message));
await p.goto('http://localhost:8768/brag.html');await p.waitForFunction('window.ready===true',{timeout:60000});
const N=630,S0=+(process.argv[2]||0);for(let i=S0;i<N;i++){await p.evaluate(t=>window.renderAt(t),i/30);
 await p.screenshot({path:`frames/f${String(i).padStart(4,'0')}.png`});if(i%60==0)console.log(i)}
await b.close();srv.close();console.log('done')})();
