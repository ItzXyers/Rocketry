const puppeteer=require('puppeteer-core'),serve=require('./serve');
(async()=>{const srv=await serve(__dirname,8767);const b=await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const p=await b.newPage();await p.setViewport({width:1920,height:1080});await p.goto('http://localhost:8767/brag.html');await p.waitForFunction('window.ready===true');
for(let i=0;i<8;i++){await p.evaluate(a=>window.sledAng(a),i*Math.PI/4);await p.screenshot({path:`stills/ang_${i}.png`,clip:{x:250,y:250,width:600,height:600}})}
await b.close();srv.close()})();
