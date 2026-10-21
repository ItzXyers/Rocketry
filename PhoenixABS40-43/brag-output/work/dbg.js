const puppeteer=require('puppeteer-core'),serve=require('./serve');
(async()=>{const srv=await serve(__dirname,8766);const b=await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const p=await b.newPage();await p.setViewport({width:1920,height:1080});await p.goto('http://localhost:8766/brag.html');await p.waitForFunction('window.ready===true');
console.log(JSON.stringify(await p.evaluate(()=>{window.renderAt(16.8);return window.dbg()})));await b.close();srv.close()})();
