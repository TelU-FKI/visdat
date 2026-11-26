#!/usr/bin/env python3
"""Fetch and cache ^JKSE prices, validating the Jan 28 crash against source headlines."""
import csv, json, sys
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'data/prices/jkse_2026.csv'
OUT=ROOT/'dashboard/data/prices.json'

def main():
 try:
  import yfinance as yf
  frame=yf.download('^JKSE',start='2026-01-01',end='2026-11-10',auto_adjust=False,progress=False,threads=False)
  if frame is None or frame.empty: raise RuntimeError('yfinance returned no rows')
  if getattr(frame.columns,'nlevels',1)>1:
   close=frame['Close'].iloc[:,0]
  else: close=frame['Close']
  rows=[]
  for d,c in close.items():
   if c is None: continue
   try: rows.append((d.strftime('%Y-%m-%d'),float(c)))
   except (ValueError,TypeError): pass
  if not rows: raise RuntimeError('no close prices')
  CACHE.parent.mkdir(parents=True,exist_ok=True)
  with CACHE.open('w',newline='') as f:
   w=csv.writer(f); w.writerow(['Date','Close']); w.writerows(rows)
 except Exception as exc:
  print(f'Price fetch failed: {exc}; writing unavailable prices.',file=sys.stderr)
  CACHE.unlink(missing_ok=True)
  rows=[]
 # In-memory headline evidence is taken directly from the local CSVs.
 headlines=[]
 for path in [ROOT/'data/news'/f'cnbc_{s}.csv' for s in 'ABC']+[ROOT/'data/news/cnbc_ref_dosen.csv']:
  if not path.exists(): continue
  with path.open(encoding='utf-8-sig',newline='') as f:
   headlines.extend(list(csv.DictReader(f)))
 event_titles=[r for r in headlines if (r.get('publish_date') or '')[:10] in ('2026-01-28','2026-01-29') and any(x in (r.get('title','').lower()) for x in ('anjlok','ambruk','halt','msci'))]
 bydate={d:c for d,c in rows}
 evidence=[{'d':d,'close':bydate.get(d)} for d in ('2026-01-27','2026-01-28','2026-01-29')]
 valid=len(event_titles)>0 and all(x['close'] is not None for x in evidence)
 obj={'data':[{'d':d,'c':c} for d,c in rows],'source':'yfinance ^JKSE' if valid else 'unavailable','fetched_at':datetime.now().astimezone().isoformat(timespec='seconds') if rows else None,'jan_validation':{'valid':valid,'prices':evidence,'headline_titles':[r.get('title','') for r in event_titles[:8]],'note':'Prices are cross-checked against titles describing the Jan 28 decline; titles are context, not proof of causation.' if valid else 'No reliable match between price dates and matching local headline evidence; omit price track.'}}
 OUT.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 if not valid: print('^JKSE prices not validated; price track disabled.')
 else: print('Validated ^JKSE Jan 27-29: '+str(evidence))
if __name__=='__main__': main()
