(() => {
  const coreHost=document.getElementById('p1-core');
  const core=window.Panels.Core3D.create(coreHost,window.IHSG_DATA,window.HUD);
  window.DASHBOARD_PANELS ||= {};window.DASHBOARD_PANELS.Core3D=core;
  if(new URLSearchParams(location.search).get('debug')==='1')window.P1_DEBUG=window.P1Debug.start(document.body);
  const introFinished=()=>{
    window.__P1_INTRO_DONE__=true;
    window.dispatchEvent(new CustomEvent('p1-intro-finished'));
  };
  window.P1_INTRO=window.Intro.create(document.body,{
    panels:Object.values(window.DASHBOARD_PANELS),
    onDone:introFinished,
  });
})();
