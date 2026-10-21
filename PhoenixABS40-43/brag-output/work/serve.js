const http=require('http'),fs=require('fs'),path=require('path');
const types={'.html':'text/html','.js':'text/javascript','.json':'application/json','.stl':'application/octet-stream'};
module.exports=function(root,port){return new Promise(r=>{const s=http.createServer((q,res)=>{const p=path.join(root,decodeURIComponent(q.url.split('?')[0]));fs.readFile(p,(e,d)=>{if(e){res.writeHead(404);res.end();return}res.writeHead(200,{'Content-Type':types[path.extname(p)]||'application/octet-stream'});res.end(d)})}).listen(port,()=>r(s))})};
