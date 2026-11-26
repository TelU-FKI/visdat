(function(g){
  g.Panels=g.Panels||{};
  g.Panels.P4={create(el,data,HUD){const svg=d3.select(el).append("svg");let state=HUD.state,obs;const slider=document.getElementById("month-slider");
    function months(){return data.meta.months||[]}
    function indexOf(m){return m==="ALL"?0:Math.max(0,months().findIndex(x=>x.id===m))}
    function setIndex(i){const ms=months();if(ms.length)HUD.set({month:ms[Math.max(0,Math.min(ms.length-1,i))].id,term:HUD.state.term})}
    function render(s){state=s;const ms=months(),box=el.getBoundingClientRect(),w=Math.max(320,box.width),h=Math.max(120,box.height);svg.attr("viewBox",`0 0 ${w} ${h}`);slider.max=Math.max(0,ms.length-1);slider.value=indexOf(s.month);
      const prices=Array.isArray(data.prices)?data.prices:data.prices?.data||[],events=data.events||[],pad={l:46,r:38,t:10,b:20},innerW=w-pad.l-pad.r,upper=Math.max(60,h*.61),lower=h-pad.t-upper-10;
      const priceRows=prices.map(p=>({date:new Date(p.d),value:+p.c})).filter(d=>Number.isFinite(+d.date)&&Number.isFinite(d.value));
      let xDomain=priceRows.length?d3.extent(priceRows,d=>d.date):[new Date(ms[0]?.id||"2026-01"),ms.length?new Date(`${ms.at(-1).id}-01`):new Date("2026-02-01")];
      if(!priceRows.length&&ms.length){const end=new Date(xDomain[1]);end.setMonth(end.getMonth()+1);xDomain[1]=end}
      if(+xDomain[0]===+xDomain[1])xDomain=[new Date(+xDomain[0]-86400000),new Date(+xDomain[1]+86400000)];
      const x=d3.scaleTime().domain(xDomain).range([pad.l,w-pad.r]),y=d3.scaleLinear().domain(priceRows.length?d3.extent(priceRows,d=>d.value):[0,1]).nice().range([upper,pad.t]);
      svg.selectAll("*").remove();const gsvg=svg.append("g");
      if(priceRows.length){gsvg.append("path").datum(priceRows).attr("fill","none").attr("stroke","var(--cyan)").attr("stroke-width",2.5).attr("d",d3.line().x(d=>x(d.date)).y(d=>y(d.value)));
        gsvg.append("g").attr("class","axis").attr("transform",`translate(0,${upper})`).call(d3.axisBottom(x).ticks(5).tickFormat(d3.timeFormat("%b")));
        gsvg.append("g").attr("class","axis").attr("transform",`translate(${pad.l},0)`).call(d3.axisLeft(y).ticks(3).tickFormat(d=>d3.format("~s")(d)));
      }else{gsvg.append("text").attr("x",pad.l).attr("y",30).attr("fill","var(--muted)").text("Harga tidak tersedia");}
      const active=ms[indexOf(s.month)];if(active&&priceRows.length){const a=new Date(active.id+"-01"),b=new Date(a.getFullYear(),a.getMonth()+1,1),x0=x(a),x1=x(b);gsvg.append("rect").attr("x",Math.max(pad.l,x0)).attr("y",pad.t).attr("width",Math.max(2,Math.min(w-pad.r,x1)-Math.max(pad.l,x0))).attr("height",upper-pad.t).attr("fill","var(--amber)").attr("opacity",.10).lower();}
      const by=upper+13,bh=Math.max(5,lower-16),maxN=d3.max(ms,d=>d.n)||1,barW=Math.max(12,innerW/Math.max(1,ms.length)*.58);
      ms.forEach((m,i)=>{const mid=new Date(m.id+"-15"),cx=x(mid),value=HUD.state.term?termCounts(m.id,HUD.state.term):m.n,barH=bh*value/(HUD.state.term?maxTerm(HUD.state.term):maxN);gsvg.append("rect").attr("x",cx-barW/2).attr("y",by+bh-barH).attr("width",barW).attr("height",barH).attr("fill",m.thin?"url(#thinPattern)":HUD.state.term?"var(--amber)":"var(--cyan)").attr("opacity",.75).on("click",()=>HUD.set({month:m.id}));if(i%2===0)gsvg.append("text").attr("class","timeline-month-label").attr("x",cx).attr("y",by+bh+18).attr("text-anchor","middle").attr("fill",m.thin?"var(--amber)":"var(--muted)").text(m.label);});
      const defs=gsvg.append("defs"),pat=defs.append("pattern").attr("id","thinPattern").attr("width",6).attr("height",6).attr("patternUnits","userSpaceOnUse").attr("patternTransform","rotate(45)");pat.append("line").attr("x1",0).attr("y1",0).attr("x2",0).attr("y2",6).attr("stroke","var(--amber)").attr("stroke-width",2);
      events.forEach(e=>{const date=new Date(e.d);if(date>=xDomain[0]&&date<=xDomain[1])gsvg.append("path").attr("d",`M${x(date)-7},${upper-10} l7,-11 7,11Z`).attr("fill","var(--red)").attr("tabindex",0).attr("aria-label",e.label).on("click",()=>{const match=ms.find(m=>e.d.startsWith(m.id));if(match)HUD.set({month:match.id,term:e.term||null})}).append("title").text(e.label);});
    }
    function termCounts(month,term){return (data.headlines||[]).filter(h=>h.m===month&&(h.terms||[]).includes(term)).length}
    function maxTerm(t){return Math.max(1,...months().map(m=>termCounts(m.id,t)))}
    slider.addEventListener("input",()=>setIndex(+slider.value));document.getElementById("prev-month").addEventListener("click",()=>setIndex(indexOf(HUD.state.month)-1));document.getElementById("next-month").addEventListener("click",()=>setIndex(indexOf(HUD.state.month)+1));
    const off=HUD.on("*",render);obs=new ResizeObserver(()=>render(HUD.state));obs.observe(el);render(state);return{update:render,introIn(){},resize(){render(HUD.state)},destroy(){off();obs.disconnect();svg.remove()}};
  }};
})(window);
