"""Offline score reconstruction. Standard library only; no model/network calls."""
import argparse, collections, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAP={'read_observed':'object_data_response','recorded_reads_failed':'service_error_response','unresolved':'insufficient_outcome_evidence','object_data_response':'object_data_response','service_error_response':'service_error_response','insufficient_outcome_evidence':'insufficient_outcome_evidence'}
UNKNOWN='insufficient_outcome_evidence'
def score(row):
 p=json.loads(row['request']['messages'][1]['content']);t=p['target']
 rs=[r for r in p['records'] if r['eventName']=='GetObject' and r['bucket']==t['bucket'] and r['key']==t['key'] and t['from']<=r['eventTime']<=t['through']]
 good={r['record_id'] for r in rs if 'errorCode' in r and r['errorCode'] is None and isinstance(r.get('bytesTransferredOut'),(int,float)) and r['bytesTransferredOut']>0}
 bad={r['record_id'] for r in rs if r.get('errorCode')}
 ref='object_data_response' if good else 'service_error_response' if rs and len(bad)==len(rs) else UNKNOWN
 x=None
 try:
  response=row['response'];assert response.get('done_reason')!='length'
  x=json.loads(response['message']['content']);assert set(x)=={'verdict','evidence_ids','reason'}
  allowed=list(MAP)[:3] if row['contract']=='original' else list(MAP)[3:]
  assert x['verdict'] in allowed and isinstance(x['reason'],str)
  ids=x['evidence_ids'];assert isinstance(ids,list) and len(ids)<=12 and all(isinstance(i,str) for i in ids)
  if row['study']=='transfer':assert len(set(ids))==len(ids)
 except (KeyError,TypeError,ValueError,AssertionError):x=None
 verdict=MAP[x['verdict']] if x else None;cited=set(x['evidence_ids']) if x else set();visible={r['record_id'] for r in p['records']}
 correct=bool(x and verdict==ref);supported=False
 if correct:
  if ref==UNKNOWN:supported=cited<=visible
  elif ref=='object_data_response':supported=bool(cited) and (cited<=good if row['study']=='initial' else cited<=visible and bool(cited&good))
  else:supported=(cited==bad if row['study']=='initial' else cited<=visible and bad<=cited)
 return {'valid':x is not None,'reference':ref,'verdict':verdict,'correct':correct,'supported_correct':bool(supported),'premature':bool(x and verdict!=UNKNOWN and ref==UNKNOWN)}
def aggregates(rows):
 groups=collections.defaultdict(list)
 for r in rows:groups[tuple(r[k] for k in ['study','phase','tier','model','arm','contract'])].append(r)
 return [dict(zip(['study','phase','tier','model','arm','contract'],k),n=len(v),**{f:sum(r[f] for r in v) for f in ['valid','correct','supported_correct','premature']}) for k,v in sorted(groups.items())]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--replay',type=Path,default=ROOT/'data/splunk-replay.jsonl');args=ap.parse_args()
 manifest=json.loads((ROOT/'MANIFEST.json').read_text())
 for name,digest in manifest['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 ledger=json.loads((ROOT/'data/decision-ledger.json').read_text());assert len(ledger)==996
 assert aggregates(ledger)==json.loads((ROOT/'data/aggregates.json').read_text())
 indexed={r['id']:r for r in ledger};rows=[json.loads(l) for l in args.replay.read_text().splitlines()];checked=0
 for r in rows:
  assert hashlib.sha256(json.dumps(r['request'],sort_keys=True).encode()).hexdigest()==r['request_sha256']
  s=score(r)
  for k,v in s.items():assert indexed[r['id']][k]==v,(r['id'],k,v,indexed[r['id']][k])
  checked+=1
 print(json.dumps({'passed':True,'decisions_aggregated':len(ledger),'responses_rescored':checked,'replay_scope':'Included Splunk subset' if checked==306 else 'Caller-supplied replay; see provenance','new_inference':False}))
if __name__=='__main__':main()
