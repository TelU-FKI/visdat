/* Offline fallback data; when data.js is present, this only supplies a missing heat matrix. */
const fixtureData = {
  meta:{generated_at:"2026-11-09",n_articles:7,n_empty_content:0,period:["2026-01","2026-02"],pipeline_version:"fixture-1",months:[{id:"2026-01",label:"JAN",n:4,thin:true},{id:"2026-02",label:"FEB",n:3,thin:true}]},
  terms:{
    "2026-01":{freq:[{id:"pasar",label:"pasar",cat:"term",df:4,df_share:1,score:1,rank:1},{id:"msci",label:"MSCI",cat:"entity",df:3,df_share:.75,score:.9,rank:2},{id:"asing",label:"asing",cat:"term",df:2,df_share:.5,score:.6,rank:3},{id:"free_float",label:"free float",cat:"term",df:2,df_share:.5,score:.5,rank:4}],khas:[{id:"msci",label:"MSCI",cat:"entity",df:3,df_share:.75,score:.9,rank:1},{id:"free_float",label:"free float",cat:"term",df:2,df_share:.5,score:.7,rank:2},{id:"asing",label:"asing",cat:"term",df:2,df_share:.5,score:.6,rank:3},{id:"pasar",label:"pasar",cat:"term",df:4,df_share:1,score:.3,rank:4}]},
    "2026-02":{freq:[{id:"saham",label:"saham",cat:"term",df:3,df_share:1,score:1,rank:1},{id:"asing",label:"asing",cat:"term",df:2,df_share:.67,score:.8,rank:2},{id:"bi",label:"BI",cat:"entity",df:1,df_share:.33,score:.5,rank:3},{id:"bunga",label:"bunga",cat:"term",df:1,df_share:.33,score:.4,rank:4}],khas:[{id:"bunga",label:"bunga",cat:"term",df:1,df_share:.33,score:.8,rank:1},{id:"bi",label:"BI",cat:"entity",df:1,df_share:.33,score:.7,rank:2},{id:"asing",label:"asing",cat:"term",df:2,df_share:.67,score:.6,rank:3},{id:"saham",label:"saham",cat:"term",df:3,df_share:1,score:.3,rank:4}]},
    ALL:{freq:[{id:"pasar",label:"pasar",cat:"term",df:4,df_share:.57,score:.57,rank:1},{id:"asing",label:"asing",cat:"term",df:4,df_share:.57,score:.57,rank:2},{id:"msci",label:"MSCI",cat:"entity",df:3,df_share:.43,score:.43,rank:3}]}
  },
  cooc:{"2026-01":{nodes:[{id:"msci",label:"MSCI",cat:"entity",df:3},{id:"free_float",label:"free float",cat:"term",df:2},{id:"asing",label:"asing",cat:"term",df:2},{id:"pasar",label:"pasar",cat:"term",df:4}],links:[{source:"msci",target:"free_float",npmi:.8,count:3},{source:"msci",target:"asing",npmi:.4,count:2},{source:"asing",target:"pasar",npmi:.3,count:2}],n_pairs_before_prune:12},"2026-02":{nodes:[{id:"saham",label:"saham",cat:"term",df:3},{id:"asing",label:"asing",cat:"term",df:2},{id:"bi",label:"BI",cat:"entity",df:1},{id:"bunga",label:"bunga",cat:"term",df:1}],links:[{source:"bi",target:"bunga",npmi:.8,count:1},{source:"asing",target:"saham",npmi:.35,count:2}],n_pairs_before_prune:8}},
  bump:{months:["2026-01","2026-02"],terms:[{id:"msci",label:"MSCI",ranks:[1,null]},{id:"asing",label:"asing",ranks:[3,3]},{id:"bunga",label:"bunga",ranks:[null,1]}]},
  headlines:[{i:0,d:"2026-01-28",t:"MSCI meninjau aturan free float pasar saham Indonesia",u:"https://www.cnbcindonesia.com/",k:["MSCI"],m:"2026-01",terms:["msci","free_float"]},{i:1,d:"2026-01-29",t:"Investor asing mencermati pergerakan pasar",u:"https://www.cnbcindonesia.com/",k:["pasar"],m:"2026-01",terms:["asing","pasar"]},{i:2,d:"2026-02-10",t:"BI membahas arah suku bunga dan saham",u:"https://www.cnbcindonesia.com/",k:["BI"],m:"2026-02",terms:["bi","bunga","saham"]}],
  prices:[{d:"2026-01-02",c:8100},{d:"2026-01-20",c:8200},{d:"2026-01-28",c:7600},{d:"2026-02-02",c:7750}],events:[{d:"2026-01-28",label:"MSCI meninjau free float",term:"msci",headline_ids:[0]}]
};

;
(function(g){
  const target=g.IHSG_DATA||fixtureData;
  if(!g.IHSG_DATA)g.IHSG_DATA=target;
  if(target.heat)return;
  const months=(target.meta?.months||[]).map(m=>m.id);
  const all=new Map();
  months.forEach(month=>{(target.terms?.[month]?.khas||[]).forEach((t,i)=>{const item=all.get(t.id)||{id:t.id,label:t.label,cat:t.cat||"term",scores:[]};item.scores.push({month,score:Number(t.score||t.df_share)||0,rank:Number(t.rank)||i+1});all.set(t.id,item)})});
  const terms=[...all.values()].map(t=>({...t,peak:Math.max(...t.scores.map(v=>v.score))})).sort((a,b)=>b.peak-a.peak).slice(0,18);
  terms.forEach(t=>t.scores.sort((a,b)=>a.rank-b.rank||b.score-a.score));
  terms.sort((a,b)=>{const ap=a.scores.reduce((best,v)=>v.rank<best.rank?v:best,a.scores[0]),bp=b.scores.reduce((best,v)=>v.rank<best.rank?v:best,b.scores[0]);return ap.rank-bp.rank||b.peak-a.peak});
  target.heat={months,terms:terms.map(({id,label,cat,peak})=>({id,label,cat,peak})),values:terms.map(t=>months.map(m=>t.scores.find(v=>v.month===m)?.score||0))};
})(window);
