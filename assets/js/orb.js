/* Esfera de ARVI: nube de partículas 3D con cuatro estados (en espera, escuchando, pensando, hablando).
   Canvas 2D, sin dependencias. Se pausa fuera de pantalla y respeta «reducir movimiento». */
(function(){
  const STATES={
    idle:     {spin:.16, wob:.035, pulse:.012, dust:.35, a:[34,211,238],  b:[79,140,255], glow:.55},
    listening:{spin:.22, wob:.06,  pulse:.07,  dust:.9,  a:[94,234,212],  b:[34,211,238], glow:.85},
    thinking: {spin:.9,  wob:.16,  pulse:.02,  dust:1.0, a:[139,92,255],  b:[79,140,255], glow:.8},
    speaking: {spin:.28, wob:.09,  pulse:.1,   dust:.8,  a:[56,189,248],  b:[94,234,212], glow:1}
  };
  const lerp=(a,b,t)=>a+(b-a)*t;
  function ARVIOrb(canvas,opts){
    opts=opts||{};
    const ctx=canvas.getContext('2d');
    const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
    const N=opts.points||760, D=opts.dust||260;
    const pts=[],dust=[];
    const ga=Math.PI*(3-Math.sqrt(5));
    for(let i=0;i<N;i++){const y=1-(i/(N-1))*2,r=Math.sqrt(1-y*y),t=ga*i;pts.push({x:Math.cos(t)*r,y,z:Math.sin(t)*r,s:Math.random()*6.28});}
    for(let i=0;i<D;i++){const u=Math.random()*6.28,v=Math.acos(2*Math.random()-1);dust.push({u,v,r:1.12+Math.random()*.55,sp:(Math.random()-.5)*.4,s:Math.random()*6.28,z:Math.random()});}
    let W=0,H=0,dpr=1,state=opts.state||'idle',cur=Object.assign({},STATES[state]);
    cur.a=cur.a.slice();cur.b=cur.b.slice();
    let rotY=0,rotX=.35,tx=0,ty=0,mx=0,my=0,t0=performance.now(),running=false,visible=true,raf=0,env=0,syl=0;
    function size(){const r=canvas.getBoundingClientRect();dpr=Math.min(devicePixelRatio||1,2);W=Math.max(1,r.width);H=Math.max(1,r.height);canvas.width=W*dpr;canvas.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);}
    function setState(s){if(STATES[s]){state=s;if(reduce)frame(performance.now());}}
    function amp(t){ // envolvente simulada según el estado
      if(state==='listening') return .5+.5*Math.sin(t*5.1)*Math.sin(t*2.3+1)+.25*Math.sin(t*11);
      if(state==='speaking'){syl+= .016; const e=Math.max(0,Math.sin(t*7.5)*.6+Math.sin(t*3.1+2)*.5+.15);return e;}
      if(state==='thinking') return .35+.2*Math.sin(t*2.2);
      return .12+.1*Math.sin(t*.9);
    }
    function frame(now){
      raf=0;
      const t=(now-t0)/1000, k=STATES[state];
      const f=reduce?1:.06;
      for(const key of ['spin','wob','pulse','dust','glow'])cur[key]=lerp(cur[key],k[key],f);
      for(let i=0;i<3;i++){cur.a[i]=lerp(cur.a[i],k.a[i],f);cur.b[i]=lerp(cur.b[i],k.b[i],f);}
      env=lerp(env,amp(t),.18);
      tx=lerp(tx,mx,.05);ty=lerp(ty,my,.05);
      rotY+=cur.spin*.016;
      draw(t);
      if(running&&visible&&!reduce)raf=requestAnimationFrame(frame);
    }
    function col(c,a){return 'rgba('+(c[0]|0)+','+(c[1]|0)+','+(c[2]|0)+','+a+')';}
    function draw(t){
      ctx.clearRect(0,0,W,H);
      const cx=W/2,cy=H/2,R=Math.min(W,H)*.255*(1+env*cur.pulse*2+Math.sin(t*1.3)*cur.pulse*.4);
      // halo
      let g=ctx.createRadialGradient(cx,cy,R*.4,cx,cy,Math.min(W,H)*.5);
      g.addColorStop(0,col(cur.a,.30*cur.glow));g.addColorStop(.45,col(cur.b,.12*cur.glow));g.addColorStop(1,col(cur.b,0));
      ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
      // anillos de onda al hablar / escuchar
      if(state==='speaking'||state==='listening'){
        for(let i=0;i<3;i++){const p=((t*.5+i/3)%1);ctx.beginPath();ctx.arc(cx,cy,R*(1.05+p*.9),0,6.283);ctx.strokeStyle=col(cur.a,(1-p)*.28);ctx.lineWidth=1.4;ctx.stroke();}
      }
      // cuerpo
      g=ctx.createRadialGradient(cx-R*.3,cy-R*.35,R*.1,cx,cy,R*1.05);
      g.addColorStop(0,col(cur.a,.95));g.addColorStop(.7,col(cur.b,.78));g.addColorStop(1,col(cur.b,.35));
      ctx.beginPath();ctx.arc(cx,cy,R*.97,0,6.283);ctx.fillStyle=g;ctx.fill();
      // malla de puntos
      const cyA=Math.cos(rotY),syA=Math.sin(rotY),cxA=Math.cos(rotX+ty*.35),sxA=Math.sin(rotX+ty*.35);
      const proj=[];
      for(let i=0;i<N;i++){
        const p=pts[i];
        const d=1+Math.sin(p.x*3+t*1.4+p.s)*cur.wob+Math.sin(p.y*4-t*1.9)*cur.wob*.7+env*cur.pulse*Math.sin(p.z*5+t*6)*.9;
        let x=p.x*d,y=p.y*d,z=p.z*d;
        let x1=x*cyA+z*syA+tx*.25,z1=-x*syA+z*cyA;
        let y1=y*cxA-z1*sxA,z2=y*sxA+z1*cxA;
        proj.push([cx+x1*R,cy+y1*R,z2,i]);
      }
      proj.sort((a,b)=>a[2]-b[2]);
      for(const q of proj){
        const front=(q[2]+1)/2;
        ctx.fillStyle=col([lerp(cur.b[0],255,front*.5),lerp(cur.b[1],255,front*.55),lerp(cur.b[2],255,front*.5)],.2+front*.7);
        const s=.7+front*1.5;ctx.fillRect(q[0]-s/2,q[1]-s/2,s,s);
      }
      // polvo orbital
      for(const d of dust){
        d.u+=d.sp*.016*(1+cur.dust*1.2);
        const rr=d.r*(1+env*cur.pulse*.8);
        let x=Math.sin(d.v)*Math.cos(d.u)*rr,y=Math.cos(d.v)*rr*.9,z=Math.sin(d.v)*Math.sin(d.u)*rr;
        const x1=x*cyA+z*syA,z1=-x*syA+z*cyA,y1=y*cxA-z1*sxA,z2=y*sxA+z1*cxA;
        const a=(.12+((z2+1.7)/3.4)*.55)*cur.dust*(.6+.4*Math.sin(t*2+d.s));
        ctx.fillStyle=col(cur.a,Math.min(.8,a));ctx.fillRect(cx+x1*R-.8,cy+y1*R-.8,1.6,1.6);
      }
      // brillo
      g=ctx.createRadialGradient(cx-R*.35,cy-R*.4,0,cx-R*.35,cy-R*.4,R*.5);
      g.addColorStop(0,'rgba(255,255,255,.22)');g.addColorStop(1,'rgba(255,255,255,0)');
      ctx.fillStyle=g;ctx.beginPath();ctx.arc(cx,cy,R,0,6.283);ctx.fill();
    }
    function start(){if(running)return;running=true;if(!raf)raf=requestAnimationFrame(frame);}
    function stop(){running=false;if(raf){cancelAnimationFrame(raf);raf=0;}}
    size();
    new ResizeObserver(()=>{size();if(!running||reduce)draw((performance.now()-t0)/1000);}).observe(canvas);
    new IntersectionObserver(e=>{visible=e[0].isIntersecting;if(visible&&running&&!raf&&!reduce)raf=requestAnimationFrame(frame);}).observe(canvas);
    document.addEventListener('visibilitychange',()=>{if(document.hidden){if(raf){cancelAnimationFrame(raf);raf=0;}}else if(running&&!reduce)raf=requestAnimationFrame(frame);});
    if(opts.parallax!==false)addEventListener('pointermove',e=>{const r=canvas.getBoundingClientRect();mx=Math.max(-1,Math.min(1,(e.clientX-(r.left+r.width/2))/innerWidth*2.2));my=Math.max(-1,Math.min(1,(e.clientY-(r.top+r.height/2))/innerHeight*2.2));},{passive:true});
    start();
    if(reduce)draw(0);
    return {setState,get state(){return state},stop,start,redraw(){draw((performance.now()-t0)/1000);}};
  }
  window.ARVIOrb=ARVIOrb;
})();
