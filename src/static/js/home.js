(function(){
  'use strict';
  const $=(s,c)=>(c||document).querySelector(s),$$=(s,c)=>Array.from((c||document).querySelectorAll(s));
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Esfera + demostración de estados ── */
  const canvas=$('#orb');
  if(canvas){
    const orb=ARVIOrb(canvas,{});
    const label=$('#say-state'),line=$('#say-line'),btns=$$('.states button');
    const TXT={
      idle:['En espera','Pulsa la esfera para ver cómo responde.'],
      listening:['Escuchando','¿Qué tiempo hace hoy en Madrid?'],
      thinking:['Pensando','Consultando n8n y la memoria…'],
      speaking:['Hablando','Hoy hay sol y 17 grados. Te recomiendo una chaqueta ligera.']
    };
    const order=['idle','listening','thinking','speaking'];
    let typing=0,auto=!reduce,timer=0,i=0;
    function type(text){clearInterval(typing);if(reduce){line.textContent=text;return}line.textContent='';let n=0;typing=setInterval(()=>{line.textContent=text.slice(0,++n);if(n>=text.length)clearInterval(typing)},22)}
    function set(s){
      orb.setState(s);i=order.indexOf(s);
      label.textContent=TXT[s][0];
      type(TXT[s][1]);
      btns.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.s===s)));
    }
    const dur={idle:2400,listening:3400,thinking:2800,speaking:4600};
    function loop(){clearTimeout(timer);if(!auto)return;timer=setTimeout(()=>{set(order[(i+1)%4]);loop()},dur[order[i]])}
    const manual=s=>{auto=false;clearTimeout(timer);set(s)};
    btns.forEach(b=>b.addEventListener('click',()=>manual(b.dataset.s)));
    const wrap=$('.orb-wrap');
    wrap.addEventListener('click',()=>manual(order[(i+1)%4]));
    wrap.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();manual(order[(i+1)%4])}if(e.key==='Escape')manual('idle')});
    set('idle');
    if(auto)setTimeout(()=>{if(auto){set('listening');loop()}},1600);
  }

  /* ── Contadores ── */
  const nums=$$('[data-count]');
  if(nums.length){
    const run=el=>{const to=+el.dataset.count,suf=el.dataset.suf||'';if(reduce){el.textContent=to+suf;return}const t0=performance.now(),d=1100;const f=t=>{const p=Math.min(1,(t-t0)/d),e=1-Math.pow(1-p,3);el.textContent=Math.round(to*e)+suf;if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)};
    const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){run(e.target);io.unobserve(e.target)}}),{threshold:.6});
    nums.forEach(n=>io.observe(n));
  }

  /* ── Recorrido de una orden ── */
  const steps=$$('.steps button'),card=$('#step-card');
  if(steps.length&&card){
    const data=JSON.parse($('#steps-data').textContent);
    let cur=0,auto=!reduce,t=0,seen=false;
    const base=card.dataset.root||'';
    function show(n,user){
      cur=n;
      steps.forEach((b,k)=>{b.setAttribute('aria-selected',String(k===n));b.classList.toggle('past',k<n)});
      $('.steps').style.setProperty('--p',n/(steps.length-1));
      const d=data[n];
      card.innerHTML='<div class="step-body" role="tabpanel"><h3>'+d.t+'</h3><p>'+d.d+'</p><div class="tags">'+d.tags.map(x=>'<span class="tag">'+x+'</span>').join('')+'</div><a class="more" href="'+base+d.u+'">Leer el capítulo '+d.n+'</a></div>';
      if(user){auto=false;clearTimeout(t)}
    }
    function next(){if(!auto)return;clearTimeout(t);t=setTimeout(()=>{show((cur+1)%steps.length);next()},4200)}
    steps.forEach((b,k)=>{
      b.addEventListener('click',()=>show(k,true));
      b.addEventListener('keydown',e=>{
        const dn=e.key==='ArrowDown'||e.key==='ArrowRight',up=e.key==='ArrowUp'||e.key==='ArrowLeft';
        if(dn||up){e.preventDefault();const n=(k+(dn?1:steps.length-1))%steps.length;steps[n].focus();show(n,true)}
      });
    });
    show(0);
    new IntersectionObserver(es=>{if(es[0].isIntersecting&&!seen){seen=true;next()}},{threshold:.4}).observe(card);
    card.addEventListener('pointerenter',()=>clearTimeout(t));
    card.addEventListener('pointerleave',()=>{if(auto&&seen)next()});
  }

  /* ── Foco que sigue al cursor en las tarjetas ── */
  $$('.card').forEach(c=>c.addEventListener('pointermove',e=>{const r=c.getBoundingClientRect();c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px')}));

  /* ── Galería ── */
  const gal=$('.gal');
  if(gal){
    const tabs=$$('.gal-tabs button',gal),imgs=$$('.frame img',gal),cap=$('.cap',gal),fr=$('.frame',gal);
    const load=im=>{if(!im.getAttribute('src')&&im.dataset.src)im.src=im.dataset.src};
    function pick(n){
      tabs.forEach((b,k)=>b.setAttribute('aria-selected',String(k===n)));
      imgs.forEach((im,k)=>{im.classList.toggle('on',k===n);if(k===n)load(im)});
      fr.classList.toggle('phone',imgs[n].dataset.phone==='1');
      cap.textContent=tabs[n].dataset.cap;
    }
    tabs.forEach((b,k)=>{b.addEventListener('click',()=>pick(k));b.addEventListener('mouseenter',()=>load(imgs[k]))});
    pick(0);
  }
})();
