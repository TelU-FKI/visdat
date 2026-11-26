/* Offline intro media, then a brief GSAP panel assembly. */
(() => {
  function create(root, options={}) {
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches || new URLSearchParams(location.search).get('motion')==='0';
    const debug=new URLSearchParams(location.search).get('debug')==='1';
    const diag=window.HUD_DEBUG ||= {}; diag.intro={state:'boot',videoPlayed:false,source:null,skipped:false};
    const wrap=document.createElement('div');wrap.className='p1-intro';wrap.dataset.state='video';
    Object.assign(wrap.style,{position:'fixed',inset:'0',zIndex:'2100',display:'grid',placeItems:'center',background:'#030a12',overflow:'hidden'});
    const video=document.createElement('video');video.className='p1-intro__video';video.poster='assets/intro_poster.png';video.muted=true;video.playsInline=true;video.preload='auto';video.setAttribute('aria-hidden','true');
    Object.assign(video.style,{position:'absolute',inset:'0',width:'100%',height:'100%',objectFit:'cover'});
    const skip=document.createElement('button');skip.type='button';skip.className='p1-intro__skip';skip.textContent='LEWATI';skip.setAttribute('aria-label','Lewati intro');
    Object.assign(skip.style,{position:'absolute',right:'24px',bottom:'20px',zIndex:'2',padding:'12px 18px',color:'#9defff',background:'#061522',border:'1px solid #26d7f4',font:'600 18px system-ui',cursor:'pointer'});
    wrap.append(video,skip);root.append(wrap);let done=false,assembling=false,timeline=null,timer=0,sourceIndex=0;
    const sources=['assets/intro.webm','assets/intro.mp4'];
    const panelElements=[...document.querySelectorAll('.dashboard > .panel, .dashboard > .detail-tabs')];
    const panels=options.panels||Object.values(window.DASHBOARD_PANELS||{});
    function finish(skipped=false){if(done)return;done=true;clearTimeout(timer);document.removeEventListener('keydown',key);timeline?.kill?.();video.pause();diag.intro.state='done';diag.intro.skipped=!!skipped;wrap.dataset.state='done';if(window.gsap&&!reduced)window.gsap.to(wrap,{opacity:0,duration:.24,onComplete:()=>wrap.remove()});else wrap.remove();options.onDone?.();}
    function startAssembly(){if(done||assembling)return;assembling=true;clearTimeout(timer);diag.intro.state='assembly';wrap.dataset.state='assembly';video.pause();video.style.opacity='0';
      if(reduced){finish(false);return;}
      const gs=window.gsap;
      if(!gs){panelElements.forEach(el=>{el.style.opacity='1';el.style.transform='none';});finish(false);return;}
      timeline=gs.timeline({onComplete:()=>finish(false)});
      if(panelElements.length)timeline.fromTo(panelElements,{opacity:.42,y:20,scale:.985},{opacity:1,y:0,scale:1,duration:.48,stagger:.065,ease:'power2.out'},0);
      panels.forEach((panel,i)=>{if(panel?.introIn)panel.introIn(timeline,Math.min(.12,i*.025));});
      timeline.fromTo(skip,{opacity:1},{opacity:0,duration:.16},.48);
    }
    function trySource(){if(sourceIndex>=sources.length){diag.intro.source='poster';video.hidden=true;wrap.style.backgroundImage='url("assets/intro_poster.png")';wrap.style.backgroundSize='cover';startAssembly();return;}const src=sources[sourceIndex++];diag.intro.source=src;video.hidden=false;video.src=src;video.load();const play=video.play();if(play?.catch)play.catch(()=>{if(sourceIndex>=sources.length)startAssembly();});}
    const onVideoError=()=>trySource();
    video.addEventListener('error',onVideoError);video.addEventListener('playing',()=>{diag.intro.videoPlayed=true;diag.intro.state='video-playing';});video.addEventListener('ended',startAssembly);
    const key=e=>{if(e.key==='Escape'||e.key==='Enter'){e.preventDefault();finish(true);}};
    skip.addEventListener('click',()=>finish(true));document.addEventListener('keydown',key);
    if(reduced){diag.intro.source='poster';video.hidden=true;wrap.style.backgroundImage='url("assets/intro_poster.png")';wrap.style.backgroundSize='cover';timer=setTimeout(()=>finish(false),400);}
    else{trySource();timer=setTimeout(()=>{if(!assembling&&!done)startAssembly();},5200);}
    return {skip:()=>finish(true),destroy(){finish(true);document.removeEventListener('keydown',key);}};
  }
  window.Intro={create,play:create};
  function debug(root=document.body){if(new URLSearchParams(location.search).get('debug')!=='1')return null;
    const box=document.createElement('output');box.className='p1-fps';box.setAttribute('aria-live','off');Object.assign(box.style,{position:'fixed',right:'8px',top:'8px',bottom:'auto',zIndex:'2500',padding:'6px 9px',background:'#061522e8',color:'#9defff',font:'18px monospace',border:'1px solid #26d7f4'});root.append(box);
    let samples=[],long=0,maxLongTask=0,last=0,lastPaint=0,raf=0;const obs=window.PerformanceObserver?new PerformanceObserver(list=>{for(const e of list.getEntries())if(e.duration>50){long++;maxLongTask=Math.max(maxLongTask,e.duration);}}):null;try{obs?.observe({type:'longtask',buffered:true});}catch(_){}
    const onIntroFinished=()=>{box.style.top='auto';box.style.bottom='8px';};window.addEventListener('p1-intro-finished',onIntroFinished,{once:true});
    const tick=t=>{if(last){samples.push(t-last);if(samples.length>300)samples.shift();if(t-lastPaint>=250){const sorted=[...samples].sort((a,b)=>a-b),med=sorted[Math.floor(sorted.length/2)]||16.7;box.textContent=`FPS med ${Math.round(1000/med)} · long tasks ${long}`;lastPaint=t;}}last=t;raf=requestAnimationFrame(tick);};raf=requestAnimationFrame(tick);
    return {destroy(){cancelAnimationFrame(raf);obs?.disconnect();window.removeEventListener('p1-intro-finished',onIntroFinished);box.remove();},reset(){samples=[];long=0;maxLongTask=0;last=0;lastPaint=0;},snapshot(){const s=[...samples].sort((a,b)=>a-b);return {medianFps:Math.round(1000/(s[Math.floor(s.length/2)]||16.7)),longTasks:long,maxLongTaskMs:Number(maxLongTask.toFixed(1)),frames:s.length};}};
  }
  window.P1Debug={start:debug};
})();
