"""Verify pinned Splunk bytes, original row locators, aliases and every replay view."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://media.githubusercontent.com/media/splunk/attack_data/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject/cloudtrail.json'
SHA='c71e5bf5d092955415d3a94f446681a1bc55a66f0d765b2cf9b3718edbf7461b'
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,help='Existing original file; otherwise retrieve only the pinned public log');a=ap.parse_args()
 if a.source:content=a.source.read_bytes()
 else:
  with urllib.request.urlopen(URL,timeout=40) as f:content=f.read()
 assert sha(content)==SHA and len(content)==160393
 raw=[json.loads(l) for l in content.decode().splitlines()];locs={c['case_id']:c['source_records'] for c in json.loads((ROOT/'data/splunk-locators.json').read_text())};expected={}
 selected=sorted(raw,key=lambda r:sha('transfer-v1|'+json.dumps(('Splunk',r['requestParameters']['bucketName'],r['requestParameters']['key']))))[:24]
 assert {r['eventID'] for r in selected}=={v['event_id'] for c in locs.values() for v in c.values()}
 for cid,loc in locs.items():
  seed='heldout-transfer|'+cid;expected[cid]={}
  for rid,l in loc.items():
   r=raw[l['index']];assert r['eventID']==l['event_id'] and sha(json.dumps(r,sort_keys=True))==l['raw_sha256'];q=r['requestParameters'];ad=r['additionalEventData'];assert rid=='E'+sha(r['eventID']+seed)[:8]
   expected[cid][rid]={'record_id':rid,'eventTime':r['eventTime'],'eventName':r['eventName'],'principal':'actor-'+sha(json.dumps({k:r['userIdentity'].get(k) for k in ['type','principalId','arn']},sort_keys=True)+seed)[:8],'bucket':'bucket-'+sha(q['bucketName']+seed)[:8],'key':'object-'+sha(q['key']+seed)[:8],'errorCode':r.get('errorCode'),'responseElements':r.get('responseElements'),'bytesTransferredOut':ad.get('bytesTransferredOut'),'bytesTransferredIn':ad.get('bytesTransferredIn')}
 n=0
 for line in (ROOT/'data/splunk-replay.jsonl').read_text().splitlines():
  x=json.loads(line);p=json.loads(x['request']['messages'][1]['content'])
  for shown in p['records']:
   original=expected[x['case_id']][shown['record_id']];wanted=dict(original)
   omitted=['errorCode','responseElements']+(['bytesTransferredOut','bytesTransferredIn'] if x['arm']=='request_only' else []) if x['arm']!='full_history' else []
   if omitted:
    for k in omitted:wanted.pop(k)
    wanted['withheld_fields']=omitted
   assert shown==wanted
   assert p['target']=={'bucket':original['bucket'],'key':original['key'],'from':original['eventTime'],'through':original['eventTime']}
   n+=1
 print(json.dumps({'passed':True,'source_bytes':len(content),'selected_histories':len(locs),'projected_response_inputs_checked':n,'source_sha256':SHA}))
if __name__=='__main__':main()
