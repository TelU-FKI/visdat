(function(global){
  const listeners=new Map();
  const months=(global.IHSG_DATA.meta?.months||[]).map(m=>m.id);
  const firstMonth=months[0]||"ALL",firstMeta=(global.IHSG_DATA.meta?.months||[]).find(m=>m.id===firstMonth);
  const HUD={state:{month:firstMonth,mode:firstMeta?.n<30?"freq":"khas",term:null,motion:!matchMedia("(prefers-reduced-motion: reduce)").matches},
    set(patch){const next={...this.state,...patch};if(next.mode!=="freq"&&next.mode!=="khas")next.mode="khas";if(next.month!=="ALL"&&!months.includes(next.month))next.month=months[0]||"ALL";const selectedMonth=(global.IHSG_DATA.meta?.months||[]).find(m=>m.id===next.month);if(next.month==="ALL"||selectedMonth?.n<30)next.mode="freq";if(JSON.stringify(next)===JSON.stringify(this.state))return;this.state=next;Object.entries(patch).forEach(([k,v])=>(listeners.get(k)||[]).forEach(fn=>fn(v,next)));(listeners.get("*")||[]).forEach(fn=>fn(next));},
    on(key,fn){if(!listeners.has(key))listeners.set(key,[]);listeners.get(key).push(fn);return()=>listeners.set(key,(listeners.get(key)||[]).filter(f=>f!==fn));},
    months};global.HUD=HUD;
})(window);
