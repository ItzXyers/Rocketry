const exploded={nose:70,fwd:28,sled:0,aft:-22,tail:-95};
function reveal(t){ // 3–7
  const u=t-3, e=eio(seg(u,.15,1.6));
  for(const k in exploded)G[k].position.z=exploded[k]*e;
  const sp=.9+u*.22; spin.rotation.z=sp;
  // sled slides out of the e-bay and drops below the tube (in screen space, so undo the spin)
  const se=eio(seg(u,.55,1.9));
  G.sled.position.set(-Math.sin(sp)*62*se,-Math.cos(sp)*62*se,exploded.fwd*e-6*se);
  for(const f of fins)f.holder.position.set(Math.cos(f.th)*14*e,Math.sin(f.th)*14*e,39.5-CEN);
  outer.rotation.set(0,Math.PI/2,0.05);outer.position.set(0,-20,0);
  const c=eio(seg(u,0,4));
  cam.position.set(lerp(-90,30,c),lerp(130,80,c),lerp(720,670,c));cam.lookAt(0,-30,0);
  show('r1',t,3.25,7.0);show('r2',t,3.55,7.0);
  // callouts on one baseline under the rocket
  cam.updateMatrixWorld();outer.updateMatrixWorld(true);
  svgClear();
  const items=[['f','Fin can + D9‑5',G.tail,40],['c','Chute bay',G.aft,150],['s','Sled <i>v19</i>',G.sled,283],['e','E‑bay',G.fwd,300],['n','Nose',G.nose,350]];
  const LY=870;
  items.forEach(([id,txt,g,z],i)=>{const k=eo(seg(u,1.5+i*.15,1.95+i*.15))*(1-seg(t,6.75,7.0));
    const [x,y0]=proj(wpos(g,z,0)); const y=y0+(id==='s'?40:34);
    const el=lab(id,txt);el.style.opacity=k;el.style.left=(x-el.offsetWidth/2)+'px';el.style.top=(LY+10)+'px';
    if(k>0){svgAdd('line',{x1:x,y1:y,x2:x,y2:lerp(y,LY,k),stroke:'#f26a1e','stroke-width':2,opacity:k});
      svgAdd('circle',{cx:x,cy:y,r:5,fill:'#f26a1e',opacity:k});}
  });
}
