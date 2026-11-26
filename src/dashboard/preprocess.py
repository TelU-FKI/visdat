#!/usr/bin/env python3
"""Build the offline IHSG dashboard data bundle from CNBC CSV shards."""
from __future__ import annotations
import argparse, csv, json, math, re
from functools import lru_cache
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'dashboard' / 'data'
INPUTS = [ROOT / 'data/news' / f'cnbc_{s}.csv' for s in 'ABC'] + [ROOT / 'data/news/cnbc_ref_dosen.csv']
START, END = '2026-01-01', '2026-11-09'
VERSION = '1.0.0'
MONTHS = [f'2026-{m:02d}' for m in range(1,12)]
LABELS = ['JAN','FEB','MAR','APR','MEI','JUN','JUL','AGU','SEP','OKT','NOV']
def require_sastrawi_stopwords():
 try:
  from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
 except ImportError as exc:
  raise RuntimeError('Sastrawi is required to build dashboard data; install it in py313 before running this pipeline.') from exc
 return set(StopWordRemoverFactory().get_stop_words())

SW = require_sastrawi_stopwords()
TOKEN = re.compile(r"[a-z][a-z0-9_]{1,}")
PHRASE_RE = None
BOILER = re.compile(r'https?://\S+|\b\d+(?:[.,]\d+)*\b|\(\s*[a-z]{2,}/[a-z]{2,}\s*\)', re.I)

def read_lines(file):
 return {x.strip().lower() for x in file.read_text(encoding='utf-8-sig').splitlines() if x.strip() and not x.lstrip().startswith('#')}
DOMAIN = read_lines(ROOT/'src/dashboard/stopwords_domain.txt')
NOISE = set(DOMAIN)
ENTITY_ROWS=[]
for line in (ROOT/'src/dashboard/entities.txt').read_text().splitlines():
 if '|' in line:
  a,b=line.split('|',1); ENTITY_ROWS.append((a.strip().lower(),b.strip()))
ENTITY_LOOKUP={re.sub(r'[^a-z0-9]+','_',a).strip('_'):b for a,b in ENTITY_ROWS}
COMPANY_ALIASES={}
TICKER_CODES=set()

def month_id(date): return date[:7]
def load_articles():
 by_url={}
 for path in INPUTS:
  if not path.exists(): continue
  with path.open(encoding='utf-8-sig',newline='') as f:
   for row in csv.DictReader(f):
    url=(row.get('url') or '').strip()
    d=(row.get('publish_date') or '')[:10]
    if not url or not re.fullmatch(r'2026-\d\d-\d\d',d) or not START<=d<=END: continue
    row['_date']=d; row['_source']=path.name
    # Deterministic precedence: reference dataset, then shard order.
    priority={'cnbc_ref_dosen.csv':0,'cnbc_A.csv':1,'cnbc_B.csv':2,'cnbc_C.csv':3}.get(path.name,9)
    old=by_url.get(url)
    if old is None or priority < old['_priority']:
     row['_priority']=priority; by_url[url]=row
 return sorted(by_url.values(),key=lambda r:(r['_date'],r.get('url','')))

def validate_price_cache(cache_path, articles):
 cache_path=Path(cache_path)
 if not cache_path.is_file():
  raise RuntimeError(f'Missing current ^JKSE cache at {cache_path}; run src/dashboard/fetch_prices.py and rebuild.')
 closes={}
 try:
  with cache_path.open(encoding='utf-8-sig',newline='') as stream:
   for row in csv.DictReader(stream):
    date=(row.get('Date') or '')[:10]
    if not date or not row.get('Close'): continue
    try: close=float(row['Close'])
    except (TypeError,ValueError): continue
    if math.isfinite(close) and close>0: closes[date]=close
 except OSError as exc:
  raise RuntimeError(f'Cannot read current ^JKSE cache at {cache_path}: {exc}') from exc
 dates=('2026-01-27','2026-01-28','2026-01-29')
 if any(date not in closes for date in dates):
  raise RuntimeError(f'Current ^JKSE cache failed validation: require valid closes for {", ".join(dates)}.')
 evidence=[{'d':date,'close':closes[date]} for date in dates]
 change=(closes[dates[1]]/closes[dates[0]]-1)*100
 titles=[(article.get('title') or '').strip() for article in articles
         if article.get('_date') in dates[1:] and re.search(r'anjlok|ambruk|halt|msci|terkoreksi',article.get('title',''),re.I)]
 if change>-5 or not titles:
  raise RuntimeError(f'Current ^JKSE cache failed headline validation: Jan 27→28 change {change:.2f}%; matching Jan 28-29 CNBC headline count {len(titles)}.')
 try:
  fetched_at=datetime.fromtimestamp(cache_path.stat().st_mtime).astimezone().isoformat(timespec='seconds')
 except OSError as exc:
  raise RuntimeError(f'Cannot read ^JKSE cache timestamp at {cache_path}: {exc}') from exc
 validation={'valid':True,'prices':evidence,'headline_titles':titles[:8],
             'note':'Current cache closes are checked against matching Jan 28-29 CNBC headlines; titles are context, not proof of causation.'}
 price_rows=[{'d':date,'c':close} for date,close in sorted(closes.items()) if START<=date<=END]
 return price_rows,validation,fetched_at

def clean_text(s):
 s=re.sub(r'(?im)^\s*(?:baca juga|foto:|video:|simak:).*$', ' ', s or '')
 s=re.sub(r'(?i)jakarta\s*,?\s*cnbc indonesia\s*[-:]', ' ',s)
 return BOILER.sub(' ',s)
@lru_cache(maxsize=50000)
def normalize_token(t, use_domain):
 t=t.lower().strip('_')
 if len(t)<3 or t in SW or (use_domain and t in NOISE): return None
 if t in ENTITY_LOOKUP: return t
 if len(t)<3 or t in SW or (use_domain and t in NOISE): return None
 return t

def company_aliases(articles):
 """Learn legal company-name to ticker aliases from explicit source patterns."""
 counts=Counter()
 pattern=re.compile(r'\bPT\.?\s+(.{2,90}?)\s*(?:\(\s*Persero\s*\)\s*)?Tbk\.?\s*\(([A-Z]{4})\)',re.I)
 for article in articles:
  for match in pattern.finditer((article.get('content','') or '')+' '+(article.get('title','') or '')):
   name=re.sub(r'\b(?:pt|persero|tbk)\b',' ',match.group(1),flags=re.I)
   words=re.findall(r'[a-z]+',name.lower())
   if 2<=len(words)<=3: counts[('_'.join(words),match.group(2).lower())]+=1
 aliases={}
 by_name=defaultdict(list)
 for (name,code),count in counts.items(): by_name[name].append((count,code))
 for name,choices in by_name.items():
  choices.sort(key=lambda x:(-x[0],x[1]))
  if len(choices)==1 or choices[0][0]>choices[1][0]: aliases[name]=choices[0][1]
 return aliases

def phrase_map(articles):
 """Return recurring keyword phrases and high-NPMI adjacent corpus bigrams."""
 keyword_counts=Counter()
 for article in articles:
  for kw in re.split(r'[,;|]',article.get('keywords','') or ''):
   words=re.findall(r'[a-z]+',kw.lower())
   if 2<=len(words)<=3: keyword_counts['_'.join(words)]+=1

 unigram=Counter(); bigram=Counter(); n_tokens=0
 for article in articles:
  words=re.findall(r'[a-z]+',clean_text((article.get('title','') or '')+' '+(article.get('content','') or '')).lower())
  unigram.update(words); n_tokens+=len(words)
  bigram.update(zip(words,words[1:]))
 n_pairs=max(1,n_tokens-1)
 phrases={p for p,count in keyword_counts.items() if count>=5 and 2<=len(p.split('_'))<=3}
 for (left,right),count in bigram.items():
  if count<10: continue
  pxy=count/n_pairs; px=unigram[left]/max(1,n_tokens); py=unigram[right]/max(1,n_tokens)
  denom=-math.log(pxy) if 0<pxy<1 else 0
  npmi=math.log(pxy/(px*py))/denom if denom and px and py else 0
  if npmi>=.5: phrases.add(left+'_'+right)
 phrases.update(COMPANY_ALIASES)
 return {p:p.replace('_',' ') for p in sorted(phrases)}

def tokenize(text, phrases, use_domain):
 s=clean_text(text).lower()
 s=re.sub(r'\b(?:pt|persero|tbk)\b',' ',s)
 global TICKER_CODES
 TICKER_CODES.update(COMPANY_ALIASES.values())
 # One compiled alternation keeps repeated phrase matching bounded.
 global PHRASE_RE
 if PHRASE_RE is None and phrases:
  keys=sorted(phrases,key=lambda x:(-len(x),x))
  PHRASE_RE=re.compile(r'(?<![a-z0-9_])(?:'+ '|'.join(re.escape(k.replace('_',' ')) for k in keys)+r')(?![a-z0-9_])')
 if PHRASE_RE:
  def replace_phrase(match):
   phrase=match.group(0).replace(' ','_')
   if phrase in COMPANY_ALIASES: return COMPANY_ALIASES[phrase]
   return phrase
  s=PHRASE_RE.sub(replace_phrase,s)
 out=[]
 for t in TOKEN.findall(s):
  if re.match(r'^\d',t) or re.fullmatch(r'rp\d+',t): continue
  if t in ENTITY_LOOKUP:
   out.append(t); continue
  if use_domain and '_' in t and any(part in NOISE or part in SW for part in t.split('_')): continue
  norm=normalize_token(t,use_domain)
  if norm: out.append(norm)
 return out

def category(term): return 'ticker' if term in TICKER_CODES else ('entity' if term in ENTITY_LOOKUP else 'term')

def build_heat(terms_by_month, month_shares):
 """Build a dense word-by-month frequency heat map from full document coverage."""
 selected={}
 for month in MONTHS:
  for term in terms_by_month[month]['khas'][:3]:
   selected.setdefault(term['id'],term)
 rows=[]
 for term_id,term in selected.items():
  values=[round(month_shares.get(term_id,{}).get(month,0.0),6) for month in MONTHS]
  peak_index=max(range(len(MONTHS)),key=lambda i:(values[i],-i))
  rows.append({
   'term':{'id':term_id,'label':term['label'],'cat':term['cat'],'peak':MONTHS[peak_index]},
   'values':values,
   'peak_share':values[peak_index],
   'peak_index':peak_index,
  })
 # Label uniqueness keeps the rendered heat-map axis unambiguous.
 rows.sort(key=lambda row:(row['peak_index'],-row['peak_share'],row['term']['id']))
 unique=[]; labels=set()
 for row in rows:
  label=row['term']['label']
  if label in labels: continue
  labels.add(label); unique.append(row)
 return {
  'months':MONTHS,
  'terms':[row['term'] for row in unique],
  'values':[row['values'] for row in unique],
}

def cooc_for(docs, freq, khas):
 candidates={x['id'] for x in khas[:60]} | {x['id'] for x in freq if x['id'] not in NOISE}
 # paragraph-level pair counts
 pc=Counter(); node_para=Counter()
 for doc in docs:
  for para in doc:
   present=sorted(set(para)&candidates)
   node_para.update(present)
   for i,a in enumerate(present):
    for b in present[i+1:]: pc[a,b]+=1
 total=max(1,sum(len(doc) for doc in docs)); edges=[]
 for (a,b),count in pc.items():
  if count<4: continue
  p=count/total; pa=node_para[a]/total; pb=node_para[b]/total
  den=-math.log(p) if p>0 else 0
  npmi=(math.log(p/(pa*pb))/den) if den and pa and pb else 0
  if npmi>=.1: edges.append({'source':a,'target':b,'npmi':round(npmi,5),'count':count})
 # degree top 3 per node, then choose nodes by df; construct connected spanning forest.
 edges.sort(key=lambda e:(-e['npmi'],-e['count'],e['source'],e['target']))
 chosen=[]; degree=Counter()
 for e in edges:
  if degree[e['source']]<3 and degree[e['target']]<3:
   chosen.append(e); degree[e['source']]+=1; degree[e['target']]+=1
 nodes=sorted(degree,key=lambda x:(-node_para[x],x))[:40]; node_set=set(nodes)
 chosen=[e for e in chosen if e['source'] in node_set and e['target'] in node_set]
 # Build a spanning tree for the strongest connected component, then fill to 90.
 parent={n:n for n in nodes}
 def find(x):
  while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
  return x
 tree=[]; rest=[]
 for e in chosen:
  a,b=e['source'],e['target']; ra,rb=find(a),find(b)
  if ra!=rb: parent[ra]=rb; tree.append(e)
  else: rest.append(e)
 comps=Counter(find(n) for n in nodes)
 if comps:
  root=max(comps,key=lambda r:(comps[r],r)); keep={n for n in nodes if find(n)==root}
 else: keep=set()
 if nodes:
  # Keep only the largest connected component; never emit a disconnected graph.
  nodes=sorted(keep); node_set=keep
 tree=[e for e in tree if e['source'] in node_set and e['target'] in node_set]
 rest=[e for e in rest if e['source'] in node_set and e['target'] in node_set]
 final=tree+rest[:max(0,90-len(tree))]
 used={v for e in final for v in (e['source'],e['target'])}
 terms={x['id']:x for x in freq+khas}
 return {'nodes':[{'id':t,'label':terms.get(t,{'label':t})['label'],'cat':terms.get(t,{}).get('cat','term'),'df':node_para[t]} for t in nodes if t in used], 'links':final,'n_pairs_before_prune':len(pc)}

def main(output_dir=OUT):
 output_dir=Path(output_dir)
 output_dir.mkdir(parents=True,exist_ok=True)
 articles=load_articles()
 price_path=ROOT/'data/prices/jkse_2026.csv'
 prices,price_validation,prices_fetched_at=validate_price_cache(price_path,articles)
 global COMPANY_ALIASES,TICKER_CODES
 COMPANY_ALIASES=company_aliases(articles)
 TICKER_CODES=set(COMPANY_ALIASES.values())
 phrases=phrase_map(articles)
 limit=int(__import__('os').environ.get('IHSG_SAMPLE_LIMIT','0') or 0)
 if limit:
  counts=Counter(); subset=[]
  for a in articles:
   m=month_id(a['_date'])
   if m in ('2026-01','2026-02') and counts[m]<limit: subset.append(a); counts[m]+=1
  articles=subset
 grouped=defaultdict(list); article_tokens={}; empty=0; source_counts=Counter()
 for a in articles:
  m=month_id(a['_date']); content=(a.get('content') or '').strip()
  if not content or content.lower()=='nan': empty+=1
  source_counts[a['_source']]+=1
  # Keep only source rows in memory here; tokenization happens once per mode below.
  grouped[m].append(a)
 # per-month docs and term tables. FREQUENSI intentionally excludes domain list, but does remove general stopwords.
 terms={}; cooc={}; month_counts={}; month_docs={}; raw_frequency_documents=[]
 for m,label in zip(MONTHS,LABELS):
  rawdocs=grouped[m]; month_counts[m]=len(rawdocs)
  docs_freq=[]; docs_khas=[]
  for a in rawdocs:
   c=(a.get('content') or '').strip()
   fallback_keywords=(a.get('keywords','') or '') if not c or c.lower()=='nan' else ''
   raw_paragraphs=[(a.get('title','') or '')+' '+fallback_keywords]
   raw_paragraphs += [p for p in clean_text(c).splitlines() if p.strip()]
   docs_freq.append([tokenize(p,phrases,False) for p in raw_paragraphs])
   khas_paragraphs=[tokenize(p,phrases,True) for p in raw_paragraphs]
   docs_khas.append(khas_paragraphs)
   article_tokens[a['url']]=set(sum(khas_paragraphs,[]))
  raw_frequency_documents.extend(set(sum(doc,[])) for doc in docs_freq)
  def rank(docs, domain):
   presence=[set(sum(d,[])) for d in docs]; dfs=Counter(t for d in presence for t in d)
   arr=[]
   for t,n in dfs.items():
    if n<max(3,math.ceil(.05*len(docs))): continue
    share=n/max(1,len(docs))
    arr.append({'id':t,'label':display_label(t,docs),'cat':category(t),'df':n,'df_share':round(share,6),'score':round(share,6)})
   arr.sort(key=lambda x:(-x['df_share'],x['id']))
   f=[dict(x,rank=i+1,score=x['df_share']) for i,x in enumerate(arr[:80])]
   k=arr if domain else arr[:80]
   return f,[dict(x,rank=i+1) for i,x in enumerate(k)]
  # Keep all KHAS candidates until their cross-month specificity scores are known.
  freq,_=rank(docs_freq,False)
  _,khas=rank(docs_khas,True)
  terms[m]={'freq':freq,'khas':khas}
  month_docs[m]=docs_khas
 raw_frequency_df=Counter(t for doc in raw_frequency_documents for t in doc)
 raw_frequency_top40=raw_frequency_df.most_common(40)
 # ALL frequency over combined documents; KHAS mirrors frequency with domain exclusions; selector handles no khas.
 all_freq=[]
 all_docs=[d for m in MONTHS for d in month_docs[m]]
 allpresence=[set(sum(d,[])) for d in all_docs]; nall=len(allpresence); dfs=Counter(t for d in allpresence for t in d)
 for t,n in dfs.items():
  if n<max(3,math.ceil(.05*nall)): continue
  all_freq.append({'id':t,'label':display_label(t,all_docs),'cat':category(t),'df':n,'df_share':round(n/max(1,nall),6),'score':round(n/max(1,nall),6)})
 all_freq.sort(key=lambda x:(-x['df_share'],x['id']))
 terms['ALL']={'freq':[dict(x,rank=i+1) for i,x in enumerate(all_freq[:80])], 'khas':[]}
 # Recompute monthly KHAS rarity with actual month coverage.
 shares=defaultdict(dict)
 for m in MONTHS:
  docs=[set(sum(d,[])) for d in month_docs[m]]; cnt=Counter(t for d in docs for t in d)
  for t,n in cnt.items(): shares[t][m]=n/max(1,len(docs))
 for m in MONTHS:
  for x in terms[m]['khas']:
   support=sum(shares[x['id']].get(mm,0)>=.15 for mm in MONTHS)
   idf=math.log(len(MONTHS)/support) if support else 0.0
   x['score']=round(x['df_share']*idf,6)
   x['months_present']=support
  # Reserve the top 20 for terms below the common-coverage guard.
  terms[m]['khas'].sort(key=lambda x:(x['months_present']>=10,-x['score'],-x['df_share'],x['id']))
  terms[m]['khas']=terms[m]['khas'][:80]
  for i,x in enumerate(terms[m]['khas']): x['rank']=i+1
 for m in MONTHS:
  cooc[m]=cooc_for(month_docs[m],terms[m]['freq'],terms[m]['khas'])
 heat=build_heat(terms,shares)
 # headline metadata, terms only from displayed vocabulary; no content ever exported
 vocab_rank=Counter()
 for m in MONTHS:
  for mode in ('freq','khas'):
   for x in terms[m][mode]: vocab_rank[x['id']]+=x['df']
 vocab={t for t,_ in vocab_rank.most_common(600)}
 headlines=[]
 for i,a in enumerate(articles):
  d=a['_date']; kw=[x.strip() for x in re.split(r'[,;|]',a.get('keywords','') or '') if x.strip()]
  toks=article_tokens.get(a['url'],set())
  headlines.append({'i':i,'d':d,'t':a.get('title','').strip(),'u':a.get('url','').strip(),'k':kw[:4],'m':month_id(d),'terms':sorted(toks&vocab)[:20]})
 bump_ids=[]; scores=Counter()
 for m in MONTHS:
  for x in terms[m]['khas'][:20]: scores[x['id']]+=1/(x['rank'] or 100)
 bump_ids=[t for t,_ in sorted(scores.items(),key=lambda x:(-x[1],x[0]))[:12]]
 bump={'months':MONTHS,'terms':[]}
 for t in bump_ids:
  bym=[]
  label=t
  for m in MONTHS:
   match=next((x for x in terms[m]['khas'][:20] if x['id']==t),None)
   if match: label=match['label']; bym.append(match['rank'])
   else: bym.append(None)
  bump['terms'].append({'id':t,'label':label,'ranks':bym})
 events=[]
 for a in articles:
  if a['_date'] in ('2026-01-28','2026-01-29') and re.search(r'msci|ambruk|anjlok|halt',a.get('title',''),re.I):
   if len(events)<6: events.append({'d':a['_date'],'label':a.get('title','')[:120],'term':'msci','headline_ids':[next((h['i'] for h in headlines if h['u']==a['url']),-1)]})
 months=[{'id':m,'label':lab,'n':month_counts[m],'thin':month_counts[m]<50,'too_thin':month_counts[m]<30} for m,lab in zip(MONTHS,LABELS) if month_counts[m]]
 price_source='yfinance ^JKSE cache; Jan 27-29 validated against CNBC headlines'
 meta={'generated_at':datetime.now().astimezone().isoformat(timespec='seconds'),'khas':{'formula':'df_share × log(M / support)','support_threshold':0.15,'guard':{'months_present_gte':10,'effect':'rank_below_terms_with_lower_support'},'M':len(MONTHS)},'n_articles':len(articles),'n_empty_content':empty,'period':[START,END],'months':months,'pipeline_version':VERSION,'sources':dict(sorted(source_counts.items()))}
 payload={'meta':meta,'terms':terms,'cooc':cooc,'bump':bump,'heat':heat,'headlines':headlines,'prices':{'data':prices,'source':price_source,'fetched_at':prices_fetched_at,'jan_validation':price_validation},'events':events}
 def dump(name,obj): (output_dir/name).write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
 for key in ('meta','terms','cooc','bump','heat','headlines','prices','events'): dump(key+'.json',payload[key])
 # full browser bundle excludes contents and provenance internals by design
 js='window.IHSG_DATA = '+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n'
 (output_dir/'data.js').write_text(js,encoding='utf-8')
 make_sample(payload,output_dir)
 with (output_dir/'terms_review.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f); w.writerow(['month','mode','rank','id','label','df','df_share','score'])
  for m in MONTHS:
   for mode in ('freq','khas'):
    for x in terms[m][mode]: w.writerow([m,mode,x['rank'],x['id'],x['label'],x['df'],x['df_share'],x['score']])
 write_audit(articles,empty,source_counts,month_counts,terms,price_source,price_validation,raw_frequency_top40,heat,meta['khas'],output_dir)
 print(f'articles={len(articles)} empty_content={empty} data.js={len(js.encode())} bytes')
 for m in MONTHS: print(f'{m} n={month_counts[m]} KHAS={", ".join(x["label"] for x in terms[m]["khas"][:10])}')

def display_label(t,docs):
 if t in TICKER_CODES: return t.upper()
 if t in ENTITY_LOOKUP: return ENTITY_LOOKUP[t]
 return t.replace('_',' ')
def make_sample(payload,output_dir=OUT):
 p=json.loads(json.dumps(payload))
 chosen=[m['id'] for m in p['meta']['months'] if p['meta']['n_articles'] and m['n']][:2]
 p['meta']['months']=[m for m in p['meta']['months'] if m['id'] in chosen]
 p['terms']={m:p['terms'][m] for m in chosen}; p['cooc']={m:p['cooc'][m] for m in chosen}
 p['bump']['months']=chosen
 original_heat=p['heat']; original_idx={month:i for i,month in enumerate(original_heat['months'])}
 chosen_ids={term['id'] for month in chosen for term in p['terms'][month]['khas'][:3]}
 heat_rows=[]
 for term,values in zip(original_heat['terms'],original_heat['values']):
  if term['id'] not in chosen_ids: continue
  row_values=[values[original_idx[month]] for month in chosen]
  peak_index=max(range(len(chosen)),key=lambda i:(row_values[i],-i))
  heat_rows.append({'term':dict(term,peak=chosen[peak_index]),'values':row_values,'peak_share':row_values[peak_index],'peak_index':peak_index})
 heat_rows.sort(key=lambda row:(row['peak_index'],-row['peak_share'],row['term']['id']))
 p['heat']={'months':chosen,'terms':[row['term'] for row in heat_rows],'values':[row['values'] for row in heat_rows]}
 for t in p['bump']['terms']: t['ranks']=[t['ranks'][MONTHS.index(m)] for m in chosen]
 p['headlines']=[h for h in p['headlines'] if h['m'] in chosen][:60]
 p['events']=[e for e in p['events'] if e['d'][:7] in chosen]
 p['meta']['n_articles']=len(p['headlines']); p['meta']['n_empty_content']=0
 (output_dir/'sample.data.js').write_text('window.IHSG_DATA = '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
def write_audit(articles,empty,sources,counts,terms,price_source,price_validation,raw_frequency_top40,heat,khas_meta,output_dir=OUT):
 price_note='Harga ^JKSE: tidak tersedia / belum tervalidasi; timeline perlu fallback tanpa harga.'
 if price_validation and price_validation.get('valid'):
  p=price_validation['prices']; change=(p[1]['close']/p[0]['close']-1)*100
  price_note=f"Harga ^JKSE tervalidasi terhadap headline 27-29 Jan: {p[0]['d']} {p[0]['close']:.2f}, {p[1]['d']} {p[1]['close']:.2f} ({change:.2f}%), {p[2]['d']} {p[2]['close']:.2f}."
 lines=['# Audit pipeline berita IHSG','',f'- Artikel unik URL: **{len(articles)}**',f'- Konten kosong: **{empty}**',f'- {price_note}','', '## Per sumber (setelah deduplikasi, sumber prioritas yang dipilih)','']
 lines += [f'- `{k}`: {v}' for k,v in sorted(sources.items())]
 lines += ['', '## Artikel per bulan','']
 for m in MONTHS: lines.append(f'- {m}: {counts[m]}'+(' — DATA TIPIS' if counts[m]<50 else ''))
 lines += ['', '## 12 kata KHAS per bulan','']
 for m in MONTHS: lines.append(f'- {m}: '+', '.join(x['label'] for x in terms[m]['khas'][:12]))
 lines += ['', '## Pilihan peta panas (kata, puncak, coverage puncak)','']
 lines += [f"- {term['label']}: {term['peak']} ({max(values):.6f})" for term,values in zip(heat['terms'],heat['values'])]
 lines += ['', '## 40 token FREKUENSI teratas seluruh korpus (df artikel)','']
 lines += [f'{i}. `{term}` — {df} artikel' for i,(term,df) in enumerate(raw_frequency_top40,1)]
 lines += ['', '## Definisi skor KHAS','', f"Skor kekhasan berbasis cakupan artikel = `{khas_meta['formula']}`; support: df_share >= {khas_meta['support_threshold']:.2f}; guard: months_present >= {khas_meta['guard']['months_present_gte']} diperingkatkan di bawah istilah yang lebih khas. Ini bukan c-TF-IDF. Stopword domain hanya berlaku untuk KHAS, jaringan, dan ALL. Frasa dibentuk dari kata kunci berulang (≥5) dan bigram berfrekuensi ≥10 dengan NPMI ≥0,5.", '', 'Isi artikel tidak diekspor; `data.js` hanya memuat metadata headline dan statistik turunan.']
 (output_dir/'audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output-dir',type=Path,default=OUT)
 args=parser.parse_args()
 main(args.output_dir)
