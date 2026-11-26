(function(g){
  g.Panels=g.Panels||{};
  g.Panels.P6={create(el,data,HUD){
    let observer,scroll,renderedMonth=null;const root=document.createElement("div");root.className="heat-panel";el.replaceChildren(root);
    function render(state){
      const heat=data.heat||{months:[],terms:[],values:[]},months=heat.months||[],terms=heat.terms||[],values=heat.values||[];
      const w=Math.max(500,root.clientWidth),left=Math.max(180,Math.min(280,w*.22)),right=24,headH=34,rowH=28;
      const ordered=terms.map((term,i)=>({term,i,peakIndex:(values[i]||[]).indexOf(Math.max(...(values[i]||[0]))),peak:+term.peak||0})).sort((a,b)=>a.peakIndex-b.peakIndex||b.peak-a.peak);
      const gridW=Math.max(months.length*34,w-left-right),totalW=left+gridW+right,cellW=gridW/Math.max(1,months.length),max=Math.max(.01,d3.max(values.flat())||0),color=d3.scaleLinear().domain([0,max]).range(["#0a1520","#3fe0ff"]).clamp(true);
      root.replaceChildren();
      const head=document.createElement("div");head.className="heat-month-head";root.append(head);
      const hsvg=d3.select(head).append("svg").attr("width",totalW).attr("height",headH).attr("viewBox",`0 0 ${totalW} ${headH}`);
      months.forEach((id,j)=>{const month=data.meta?.months?.find(m=>m.id===id),x=left+j*cellW;hsvg.append("text").attr("class","heat-month").attr("x",x+cellW/2).attr("y",24).attr("text-anchor","middle").text(month?.label||id.slice(5));if(id===state.month)hsvg.append("rect").attr("class","heat-active-head").attr("x",x+1).attr("y",2).attr("width",Math.max(2,cellW-2)).attr("height",30).attr("rx",3)});
      scroll=document.createElement("div");scroll.className="heat-scroll";root.append(scroll);
      const svg=d3.select(scroll).append("svg").attr("width",totalW).attr("height",Math.max(1,ordered.length*rowH)).attr("viewBox",`0 0 ${totalW} ${Math.max(1,ordered.length*rowH)}`);
      if(state.month!=="ALL"){const mi=months.indexOf(state.month);if(mi>=0)svg.append("rect").attr("class","heat-active-col").attr("x",left+mi*cellW+1).attr("y",0).attr("width",Math.max(2,cellW-2)).attr("height",ordered.length*rowH)}
      ordered.forEach(({term,i},ri)=>{const y=ri*rowH,row=svg.append("g").attr("class","heat-row").classed("selected",term.id===state.term).attr("data-term",term.id).attr("tabindex",0).attr("role","button").attr("aria-label",`Pilih ${term.label}`);
        if(term.id===state.term)row.append("rect").attr("class","heat-selected-row").attr("x",0).attr("y",y).attr("width",totalW).attr("height",rowH);
        row.append("text").attr("class","heat-term-label").attr("x",left-12).attr("y",y+rowH/2).attr("text-anchor","end").attr("dominant-baseline","middle").text(term.label);
        months.forEach((month,j)=>{const value=Number(values[i]?.[j])||0,x=left+j*cellW;row.append("rect").attr("class","heat-cell").attr("x",x+2).attr("y",y+2).attr("width",Math.max(1,cellW-4)).attr("height",rowH-4).attr("fill",color(value)).attr("data-month",month).attr("data-value",value).append("title").text(`${term.label} • ${month} • df_share ${(value*100).toFixed(1)}%`)});
        const select=()=>HUD.set({term:HUD.state.term===term.id?null:term.id});row.on("click",select).on("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();select()}});
      });
      const footer=document.createElement("div");footer.className="heat-legend";footer.innerHTML=`<span class="heat-range">BARIS — DARI ${ordered.length}</span><span class="heat-scale-title">df_share</span><span class="heat-gradient" style="background:linear-gradient(90deg,${color(0)},${color(max)})"></span><span>0%</span><span>${(max*100).toFixed(0)}%</span>`;root.append(footer);
      root.dataset.months=months.length;root.dataset.terms=terms.length;root.dataset.activeMonth=state.month;root.dataset.rowHeight=rowH;
      const peakRows=ordered.map((d,i)=>({d,i})).filter(x=>months[x.d.peakIndex]===state.month),start=peakRows[0]?.i??0;
      const jump=()=>{const visible=Math.max(1,Math.floor(scroll.clientHeight/rowH)),first=Math.max(0,Math.min(ordered.length-visible,start));scroll.scrollTo({top:first*rowH,behavior:HUD.state.motion?"smooth":"auto"});updateRange()};
      function updateRange(){const first=Math.min(ordered.length||1,Math.floor(scroll.scrollTop/rowH)+1),last=Math.min(ordered.length,Math.max(first,Math.ceil((scroll.scrollTop+scroll.clientHeight)/rowH)));footer.querySelector(".heat-range").textContent=`BARIS ${first}–${last} DARI ${ordered.length}`}
      scroll.addEventListener("scroll",updateRange,{passive:true});requestAnimationFrame(jump);if(renderedMonth!==state.month)renderedMonth=state.month;
    }
    const off=HUD.on("*",render);observer=new ResizeObserver(()=>render(HUD.state));observer.observe(root);render(HUD.state);
    return{update:render,introIn(){},resize(){render(HUD.state)},destroy(){off();observer.disconnect();el.replaceChildren()}};
  }};
})(window);
