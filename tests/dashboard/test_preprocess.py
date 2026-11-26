import builtins, csv, json, math, re, random, subprocess, sys, tempfile
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'dashboard/data'
sys.path.insert(0,str(ROOT/'src/dashboard'))
import preprocess as pipeline

def load(name): return json.loads((DATA/f'{name}.json').read_text())

def test_export_schema_and_counts():
 meta=load('meta'); terms=load('terms'); cooc=load('cooc')
 assert meta['n_articles'] > 0
 for m in meta['months']:
  assert m['id'] in terms and len(terms[m['id']]['freq'])<=80 and len(terms[m['id']]['khas'])<=80
  graph=cooc[m['id']]
  assert len(graph['nodes'])<=40 and len(graph['links'])<=90
  if graph['nodes']:
   adj={n['id']:set() for n in graph['nodes']}
   for e in graph['links']: adj[e['source']].add(e['target']); adj[e['target']].add(e['source'])
   seen=set(); stack=[next(iter(adj))]
   while stack:
    x=stack.pop()
    if x in seen: continue
    seen.add(x); stack.extend(adj[x]-seen)
   assert len(seen)==len(adj)

def test_january_khas_has_msci_and_no_domain_stopwords():
 terms=load('terms'); ids={x['id'] for mode in ('freq','khas') for x in terms['2026-01'][mode]}
 assert 'msci' in ids
 domain={x.strip() for x in (ROOT/'src/dashboard/stopwords_domain.txt').read_text().splitlines() if x.strip()}
 # Domain words are intentionally allowed in FREQUENSI; they must be absent from KHAS.
 khas={x['id'] for x in terms['2026-01']['khas']}
 assert not (domain & khas)

def test_copyright_12gram_guard():
 bundle=(DATA/'data.js').read_text()
 # Deterministically inspect up to 50 source records; content is never included in bundle.
 seen=set(); records=[]
 for path in [ROOT/'data/news'/f'cnbc_{s}.csv' for s in 'ABC']+[ROOT/'data/news/cnbc_ref_dosen.csv']:
  with path.open(encoding='utf-8-sig',newline='') as f:
   for row in csv.DictReader(f):
    u=row.get('url')
    if u and u not in seen: seen.add(u); records.append(row)
 rng=random.Random(20261109)
 for row in rng.sample(records,min(50,len(records))):
  toks=re.findall(r'\w+',row.get('content','').lower())
  for i in range(max(0,len(toks)-11)):
   phrase=' '.join(toks[i:i+12])
   assert phrase not in bundle

def test_sample_fixture_has_two_months_and_full_schema():
 js=(DATA/'sample.data.js').read_text()
 assert js.startswith('window.IHSG_DATA = ')
 sample=json.loads(js[len('window.IHSG_DATA = '):].rstrip(' ;\n'))
 assert len(sample['meta']['months'])==2
 for key in ('terms','cooc','bump','heat','headlines','prices','events'): assert key in sample


def test_khas_specificity_targets_and_common_coverage_guard():
 meta=load('meta'); terms=load('terms')
 assert meta['khas']['formula']=='df_share × log(M / support)'
 assert meta['khas']['support_threshold']==0.15
 assert meta['khas']['guard']['months_present_gte']==10
 assert all('df_share' in x for m in meta['months'] for x in terms[m['id']]['khas'])
 jan=terms['2026-01']['khas']; mar=terms['2026-03']['khas']; nov=terms['2026-11']['khas']
 assert next(x['rank'] for x in jan if x['id']=='free_float')<=30
 assert next(x['rank'] for x in mar if x['id']=='israel')<=10
 assert any('pemilu' in x['id'] for x in nov[:10])
 # Use the exact same support threshold as the IDF and ranking guard.
 for month in meta['months']:
  assert all(x['months_present']<10 for x in terms[month['id']]['khas'][:20])


def test_khas_score_matches_reported_idf_formula():
 meta=load('meta'); months=len(meta['months'])
 for month in meta['months']:
  for term in load('terms')[month['id']]['khas']:
   expected=term['df_share']*math.log(months/term['months_present']) if term['months_present'] else 0
   assert abs(term['score']-round(expected,6))<1e-6


def test_pipeline_determinism_and_bundle_size():
 assert (DATA/'data.js').stat().st_size<=1_500_000
 with tempfile.TemporaryDirectory(prefix='ihsg-builds-') as temp:
  first=Path(temp)/'first'; second=Path(temp)/'second'
  first.mkdir(); second.mkdir()
  stale='{"jan_validation":{"valid":false}}'
  (first/'prices.json').write_text(stale); (second/'prices.json').write_text(stale)
  command=[sys.executable,str(ROOT/'src/dashboard/preprocess.py')]
  subprocess.run(command+['--output-dir',str(first)],cwd=ROOT,check=True,capture_output=True,text=True)
  subprocess.run(command+['--output-dir',str(second)],cwd=ROOT,check=True,capture_output=True,text=True)
  first_bytes=(first/'data.js').read_bytes(); second_bytes=(second/'data.js').read_bytes()
  normalize=lambda data: re.sub(rb'("generated_at":")[^"]*(")',rb'\1<build-time>\2',data)
  assert normalize(first_bytes)==normalize(second_bytes)
  assert (first/'data.js').stat().st_size<=1_500_000
  first_obj=json.loads(first_bytes.split(b'=',1)[1].strip().rstrip(b';'))
  second_obj=json.loads(second_bytes.split(b'=',1)[1].strip().rstrip(b';'))
  assert first_obj['prices']['fetched_at']==second_obj['prices']['fetched_at']


def test_sastrawi_import_failure_is_fatal(monkeypatch):
 original=builtins.__import__
 def fail_sastrawi(name,*args,**kwargs):
  if name.startswith('Sastrawi'): raise ImportError('simulated missing Sastrawi')
  return original(name,*args,**kwargs)
 monkeypatch.setattr(builtins,'__import__',fail_sastrawi)
 with pytest.raises(RuntimeError,match='Sastrawi is required'):
  pipeline.require_sastrawi_stopwords()


def test_invalid_current_price_cache_is_fatal(tmp_path):
 cache=tmp_path/'jkse.csv'
 cache.write_text('Date,Close\n2026-01-27,9000\n2026-01-28,8900\n2026-01-29,8800\n')
 articles=[{'_date':'2026-01-28','title':'IHSG Anjlok 7%'}]
 with pytest.raises(RuntimeError,match='failed headline validation'):
  pipeline.validate_price_cache(cache,articles)

def test_terms_drop_numeric_ids_and_overlong_or_legal_entity_labels():
 terms=load('terms')
 for month_modes in terms.values():
  for mode in ('freq','khas'):
   for item in month_modes[mode]:
    assert not re.match(r'^\d',item['id'])
    assert not re.fullmatch(r'rp\d+',item['id'])
    assert len(item['label'].split())<=3
    assert not re.search(r'\b(?:pt|tbk|persero)\b',item['label'],re.I)
    if item['cat']=='ticker': assert item['label'].isupper() and len(item['label'])==4


def test_audit_contains_12_terms_for_each_month_and_global_frequency_review():
 audit=(DATA/'audit.md').read_text()
 assert '40 token FREKUENSI teratas seluruh korpus' in audit
 section=audit.split('## 12 kata KHAS per bulan\n',1)[1].split('\n## ',1)[0]
 rows=[line for line in section.splitlines() if re.match(r'- 2026-\d\d:',line)]
 assert len(rows)==11
 assert all(len(line.split(': ',1)[1].split(', '))==12 for line in rows)


def test_heat_map_dense_values_and_peak_order():
 meta=load('meta'); terms=load('terms'); heat=load('heat')
 months=[m['id'] for m in meta['months']]
 assert heat['months']==months
 assert len(heat['terms'])==len(heat['values'])
 assert len(heat['terms'])<=33
 labels=[term['label'] for term in heat['terms']]
 assert len(labels)==len(set(labels))
 peak_indices=[]
 for term,row in zip(heat['terms'],heat['values']):
  assert len(row)==len(months)
  assert all(0<=value<=1 for value in row)
  peak_index=months.index(term['peak'])
  peak_indices.append(peak_index)
  assert row[peak_index]==max(row)
 assert peak_indices==sorted(peak_indices)
 # At least one retained word is measured in a month where it is outside that month's top 80.
 dense_tail=[(term,row,j) for term,row in zip(heat['terms'],heat['values']) for j,month in enumerate(months)
             if row[j]>0 and term['id'] not in {x['id'] for x in terms[month]['khas']}]
 assert dense_tail


def test_heat_fixture_has_matching_month_columns():
 js=(DATA/'sample.data.js').read_text()
 sample=json.loads(js.split('=',1)[1].strip().rstrip(';'))
 heat=sample['heat']
 assert len(heat['terms'])==len(heat['values'])
 assert all(len(row)==len(heat['months']) for row in heat['values'])
