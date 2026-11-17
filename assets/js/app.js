(function(){
  'use strict';
  const root=document.documentElement, ROOT=root.dataset.root||'';
  const $=(s,c)=> (c||document).querySelector(s), $$=(s,c)=>Array.from((c||document).querySelectorAll(s));
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store={get(k){try{return localStorage.getItem(k)}catch(e){return null}},set(k,v){try{localStorage.setItem(k,v)}catch(e){}}};

  /* Tema */
  const tt=$('.theme-t');
  if(tt)tt.addEventListener('click',()=>{
    const next=root.dataset.theme==='light'?'dark':'light';
    root.dataset.theme=next;store.set('arvi-theme',next);
    document.dispatchEvent(new CustomEvent('themechange'));
  });

  /* Menú móvil */
  const burger=$('.burger');
  if(burger){
    const set=o=>{document.body.classList.toggle('nav-open',o);burger.setAttribute('aria-expanded',o)};
    burger.addEventListener('click',()=>set(!document.body.classList.contains('nav-open')));
    $('.scrim')?.addEventListener('click',()=>set(false));
    addEventListener('keydown',e=>{if(e.key==='Escape')set(false)});
  }
  const cur=$('.side a[aria-current]'); if(cur&&cur.scrollIntoView){const s=cur.closest('.side');if(s)s.scrollTop=Math.max(0,cur.offsetTop-s.clientHeight/3)}

  /* Barra de progreso */
  const bar=$('#progress');
  if(bar){let tick=false;const upd=()=>{const h=document.documentElement;const m=h.scrollHeight-h.clientHeight;bar.style.transform='scaleX('+(m>0?Math.min(1,h.scrollTop/m):0)+')';tick=false};
    addEventListener('scroll',()=>{if(!tick){tick=true;requestAnimationFrame(upd)}},{passive:true});upd();}

  /* Índice lateral con seguimiento */
  const links=$$('.toc a');
  if(links.length&&'IntersectionObserver' in window){
    const map=new Map(links.map(a=>[a.getAttribute('href').slice(1),a]));
    const heads=$$('.prose h2[id],.prose h3[id]');
    const io=new IntersectionObserver(es=>{
      es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.remove('on'));const a=map.get(e.target.id);if(a){a.classList.add('on');a.scrollIntoView&&a.scrollIntoView({block:'nearest'})}}});
    },{rootMargin:'-80px 0px -70% 0px'});
    heads.forEach(h=>io.observe(h));
  }

  /* Aparición suave de bloques */
  const rv=$$('.rv');
  if(rv.length){
    if(reduce||!('IntersectionObserver' in window))rv.forEach(e=>e.classList.add('in'));
    else{const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px'});rv.forEach(e=>io.observe(e));}
  }

  /* Bloques de código: etiqueta + copiar */
  $$('.prose pre:not(.mermaid)').forEach(pre=>{
    const host=pre.closest('.highlight')||pre;
    if(host.closest('.codebox'))return;
    const code=pre.querySelector('code')||pre;
    const lang=(code.className.match(/language-(\w+)/)||[])[1]||(host.className.match(/language-(\w+)/)||[])[1]||'';
    const box=document.createElement('div');box.className='codebox';
    const barr=document.createElement('div');barr.className='codebox-bar';
    barr.innerHTML='<span>'+(lang||'código')+'</span><button class="copy" type="button">Copiar</button>';
    host.parentNode.insertBefore(box,host);box.append(barr,host);
    const b=$('.copy',barr);
    b.addEventListener('click',async()=>{
      try{await navigator.clipboard.writeText(code.innerText)}catch(e){const r=document.createRange();r.selectNodeContents(code);const s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges()}
      b.textContent='Copiado';b.classList.add('done');setTimeout(()=>{b.textContent='Copiar';b.classList.remove('done')},1600);
    });
  });

  /* Visor de imágenes y diagramas */
  const lb=document.createElement('div');lb.className='lb';lb.setAttribute('role','dialog');lb.setAttribute('aria-modal','true');lb.setAttribute('aria-label','Vista ampliada');
  document.body.appendChild(lb);
  const closeLb=()=>{lb.classList.remove('open');lb.innerHTML=''};
  lb.addEventListener('click',closeLb);
  function openLb(node,cap){lb.innerHTML='';const w=document.createElement('div');w.className='lb-in';w.appendChild(node);if(cap){const c=document.createElement('div');c.className='lb-cap';c.textContent=cap;w.appendChild(c)}lb.appendChild(w);lb.classList.add('open')}
  document.addEventListener('click',e=>{
    const img=e.target.closest('.prose img, .frame img');
    if(img){e.preventDefault();const n=document.createElement('img');n.src=img.currentSrc||img.src;n.alt=img.alt;openLb(n,img.alt);return}
    const dg=e.target.closest('.diagram-body');
    if(dg){const svg=$('svg',dg);if(svg){const w=document.createElement('div');w.className='svgwrap';w.style.borderRadius='1rem';w.appendChild(svg.cloneNode(true));openLb(w,$('figcaption',dg.parentNode)?.textContent)}}
  });
  addEventListener('keydown',e=>{if(e.key==='Escape'&&lb.classList.contains('open'))closeLb()});

  /* Diagramas Mermaid (se cargan solo si la página los tiene) */
  const diagrams=$$('pre.mermaid');
  if(diagrams.length){
    const sources=diagrams.map(d=>d.textContent),bodies=diagrams.map(d=>d.closest('.diagram-body'));
    const themeVars=()=>{const l=root.dataset.theme==='light';return l?{
        theme:'base',themeVariables:{fontFamily:'Geist, system-ui, sans-serif',primaryColor:'#e6f4f1',primaryBorderColor:'#0b8f80',primaryTextColor:'#10172e',lineColor:'#5a6684',secondaryColor:'#ece8fb',tertiaryColor:'#f3f6fd',noteBkgColor:'#fff7dd',noteTextColor:'#10172e',edgeLabelBackground:'#f3f6fd',clusterBkg:'#f3f6fd',clusterBorder:'#9aa6c4'}}:{
        theme:'base',themeVariables:{fontFamily:'Geist, system-ui, sans-serif',primaryColor:'#10203f',primaryBorderColor:'#38bdf8',primaryTextColor:'#e9edf9',lineColor:'#7f8fb8',secondaryColor:'#1a1a45',tertiaryColor:'#0a1024',noteBkgColor:'#1d2547',noteTextColor:'#e9edf9',edgeLabelBackground:'#0a1024',clusterBkg:'#0a1024',clusterBorder:'#3a4672',actorBkg:'#10203f',actorBorder:'#38bdf8',actorTextColor:'#e9edf9',signalColor:'#aab4d0',signalTextColor:'#e9edf9'}}};
    let mer;
    const render=async()=>{
      if(!mer){mer=(await import('https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs')).default}
      mer.initialize(Object.assign({startOnLoad:false,securityLevel:'strict',flowchart:{htmlLabels:true,curve:'basis'}},themeVars()));
      for(let i=0;i<diagrams.length;i++){
        const body=bodies[i];
        try{const {svg}=await mer.render('arvi-m'+i+'-'+Date.now(),sources[i]);
          body.innerHTML=svg;body.querySelector('svg').removeAttribute('height');
        }catch(err){body.innerHTML='<pre class="mermaid" style="visibility:visible;font-size:.8rem;color:inherit;white-space:pre-wrap">'+sources[i].replace(/</g,'&lt;')+'</pre>'}
      }
    };
    const start=()=>render().catch(()=>{diagrams.forEach(d=>{d.style.visibility='visible';d.style.fontSize='.8rem';d.style.color='inherit'})});
    if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)){io.disconnect();start()}},{rootMargin:'400px'});io.observe(diagrams[0])}else start();
    document.addEventListener('themechange',()=>{if(mer)render()});
  }

  /* Búsqueda */
  const pal=document.createElement('div');pal.className='pal';pal.innerHTML=
   '<div class="pal-box" role="dialog" aria-modal="true" aria-label="Buscar"><label class="pal-in"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input type="search" placeholder="Buscar en la documentación…" autocomplete="off" spellcheck="false" aria-label="Buscar"></label><div class="pal-list" role="listbox"></div><div class="pal-foot"><span><kbd>↑</kbd><kbd>↓</kbd>moverse</span><span><kbd>Enter</kbd>abrir</span><span><kbd>Esc</kbd>cerrar</span></div></div>';
  document.body.appendChild(pal);
  const inp=$('input',pal), list=$('.pal-list',pal);
  let idx=null,sel=0,results=[];
  const norm=s=>s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  async function load(){if(idx)return idx;try{const r=await fetch(ROOT+'search-index.json');idx=(await r.json()).map(d=>Object.assign(d,{nt:norm(d.t+' '+d.h),nx:norm(d.x)}))}catch(e){idx=[]}return idx}
  function hl(text,terms){let out=esc(text);terms.forEach(t=>{if(t.length<2)return;out=out.replace(new RegExp('('+t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi'),'<mark>$1</mark>')});return out}
  function snippet(d,terms){const n=d.nx;let p=-1;for(const t of terms){p=n.indexOf(t);if(p>-1)break}if(p<0)return d.x.slice(0,120);const s=Math.max(0,p-40);return (s?'…':'')+d.x.slice(s,s+130)}
  function run(){
    const q=norm(inp.value.trim());
    if(!q){results=(idx||[]).filter(d=>d.p).slice(0,8);}
    else{const terms=q.split(/\s+/).filter(Boolean);
      results=(idx||[]).map(d=>{let s=0;for(const t of terms){if(d.nt.includes(t))s+=d.p?30:14;if(d.h&&norm(d.h).startsWith(t))s+=10;if(d.nx.includes(t))s+=3;else if(!d.nt.includes(t)){s=0;break}}return {d,s}}).filter(r=>r.s>0).sort((a,b)=>b.s-a.s).slice(0,30).map(r=>r.d);}
    sel=0;paint(q?q.split(/\s+/):[]);
  }
  function paint(terms){
    if(!results.length){list.innerHTML='<div class="pal-empty">Sin resultados para «'+esc(inp.value)+'». Prueba con otra palabra.</div>';return}
    list.innerHTML=(inp.value.trim()?'':'<h3>Capítulos y secciones</h3>')+results.map((d,i)=>'<a role="option" href="'+ROOT+d.u+'" data-i="'+i+'" class="'+(i===sel?'sel':'')+'"><b>'+hl(d.p?d.t:d.h,terms)+'</b><span>'+(d.p?hl(d.s||'',terms):hl(d.t,[])+' · '+hl(snippet(d,terms),terms))+'</span></a>').join('');
  }
  function openPal(){pal.classList.add('open');document.body.style.overflow='hidden';inp.value='';load().then(run);setTimeout(()=>inp.focus(),10)}
  function closePal(){pal.classList.remove('open');document.body.style.overflow=''}
  $$('[data-search]').forEach(b=>b.addEventListener('click',openPal));
  pal.addEventListener('click',e=>{if(e.target===pal)closePal()});
  inp.addEventListener('input',run);
  list.addEventListener('mousemove',e=>{const a=e.target.closest('a');if(a){sel=+a.dataset.i;$$('a',list).forEach((x,i)=>x.classList.toggle('sel',i===sel))}});
  addEventListener('keydown',e=>{
    if((e.key==='k'&&(e.ctrlKey||e.metaKey))||(e.key==='/'&&!/input|textarea/i.test(document.activeElement.tagName))){e.preventDefault();pal.classList.contains('open')?closePal():openPal();return}
    if(!pal.classList.contains('open'))return;
    if(e.key==='Escape')closePal();
    else if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();sel=(sel+(e.key==='ArrowDown'?1:-1)+results.length)%Math.max(1,results.length);$$('a',list).forEach((x,i)=>x.classList.toggle('sel',i===sel));$$('a',list)[sel]?.scrollIntoView({block:'nearest'})}
    else if(e.key==='Enter'&&results[sel]){location.href=ROOT+results[sel].u}
  });
})();
