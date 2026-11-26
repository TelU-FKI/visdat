(function(g){
  g.Panels=g.Panels||{};
  g.Panels.P2={create(el,data,HUD){
    let resizeObs;
    const svg=d3.select(el).append("svg"),footerLabel=document.getElementById("rank-mode-label"),footerUnit=document.getElementById("rank-unit"),hint=document.getElementById("rank-scroll-hint"),hintCount=document.getElementById("rank-scroll-count");
    function fitLabel(d,maxWidth){const ctx=fitLabel.ctx||(fitLabel.ctx=document.createElement("canvas").getContext("2d"));ctx.font="18px Chakra, sans-serif";const full=`${d.rank||""}. ${d.label||""}`;if(ctx.measureText(full).width<=maxWidth)return full;let text=full;while(text.length>1&&ctx.measureText(`${text.trimEnd()}…`).width>maxWidth)text=text.slice(0,-1);return`${text.trimEnd()}…`}
    function update(s){
      const items=(data.terms[s.month]?.[s.mode]||data.terms.ALL?.freq||[]).slice(0,15),box=el.getBoundingClientRect(),w=Math.max(220,box.width),h=Math.max(100,box.height),rowH=26,contentH=Math.max(h,items.length*rowH+6);
      const left=Math.max(120,w*.42),valueX=w-126,max=d3.max(items,d=>Number(d.score||d.df_share)||0)||1,x=d3.scaleLinear().domain([0,max]).range([left,Math.max(left+8,valueX-14)]);
      svg.attr("viewBox",`0 0 ${w} ${contentH}`).style("height",`${contentH}px`);
      const rows=svg.selectAll("g.rank-row").data(items,d=>d.id).join(enter=>{const r=enter.append("g").attr("class","rank-row");r.append("text").attr("class","rank-label");r.append("rect").attr("class","rank-bar").attr("height",14);r.append("text").attr("class","rank-value");return r;});
      rows.attr("transform",(d,i)=>`translate(0,${3+i*rowH})`).classed("selected",d=>d.id===s.term).on("click",(_,d)=>HUD.set({term:s.term===d.id?null:d.id}));
      rows.select(".rank-label").each(function(d){const t=d3.select(this).text(fitLabel(d,left-8)).attr("x",0).attr("y",21).attr("font-size",18);t.selectAll("title").data([d]).join("title").text(d=>`${d.rank||""}. ${d.label}`);});
      rows.select(".rank-bar").attr("x",left).attr("y",10).attr("width",d=>Math.max(2,x(Number(d.score||d.df_share)||0)-left));
      rows.select(".rank-value").attr("x",valueX).attr("y",22).attr("text-anchor","start").attr("font-size",18).text(d=>s.mode==="freq"?`${Math.round((Number(d.df_share)||0)*100)}%`:`${(Number(d.score)||0).toLocaleString("id-ID",{minimumFractionDigits:2,maximumFractionDigits:2})} | ${Math.round((Number(d.df_share)||0)*100)}%`).each(function(d){d3.select(this).selectAll("title").data([d]).join("title").text(d=>`${d.label}: skor KHAS ${(Number(d.score)||0).toFixed(6)}; cakupan ${((Number(d.df_share)||0)*100).toFixed(2)}% (${d.df||"?"} artikel)`)});
      if(footerLabel)footerLabel.textContent=s.mode==="freq"?"CAKUPAN ARTIKEL":"SKOR KHAS";if(footerUnit)footerUnit.textContent=s.mode==="freq"?"%":"SKOR | CAKUPAN %";
      if(hint){const visible=Math.min(items.length,Math.max(1,Math.floor((el.clientHeight||h)/rowH)));hintCount.textContent=items.length>visible?`${visible} dari ${items.length} • gulir`: `${items.length} dari ${items.length} kata`;hint.hidden=items.length<=visible;}
    }
    const off=HUD.on("*",update);resizeObs=new ResizeObserver(()=>update(HUD.state));resizeObs.observe(el);update(HUD.state);
    return{update,introIn(){},resize(){update(HUD.state)},destroy(){off();resizeObs.disconnect();svg.remove()}};
  }};
})(window);
