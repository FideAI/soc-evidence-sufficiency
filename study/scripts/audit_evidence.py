"""Inspect the included Splunk examples behind the unavailable-field finding.

This checks one exact observed explanation pattern, not arbitrary entailment.
No inference or external service is called. Output contains only included material.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(line) for line in (ROOT / 'data/splunk-replay.jsonl').read_text().splitlines()]
examples = []
for row in rows:
    if not (row['phase'] == 'primary' and row['tier'] == 'primary'
            and row['model'] == 'gemma4:e4b-mlx' and row['contract'] == 'clarified'
            and row['arm'] == 'volume_only'):
        continue
    packet = json.loads(row['request']['messages'][1]['content'])
    answer = json.loads(row['response']['message']['content'])
    records = {r['record_id']: r for r in packet['records']}
    assert answer['evidence_ids'], row['id']
    cited = [records[i] for i in answer['evidence_ids']]
    assert all('errorCode' not in r and 'errorCode' in r['withheld_fields'] for r in cited)
    assert 'null errorCode' in answer['reason'], answer['reason']
    examples.append({'case_id': row['case_id'], 'reason': answer['reason'],
                     'verdict': answer['verdict'], 'cited_visible_records': cited})
assert len(examples) == 24, len(examples)
print(json.dumps({'scope': '24 included Splunk histories; the 25th main-study history is excluded from this export',
                  'interpretation': 'Post-observation exact-pattern check, not a general factuality classifier',
                  'count': len(examples), 'examples': examples}, indent=2))
