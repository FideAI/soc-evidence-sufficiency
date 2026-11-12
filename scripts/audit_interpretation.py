"""Post-review descriptive audit of retained outputs, not a new experiment.

Default: the permitted Splunk replay. --replay accepts an authorized fuller replay.
No inference, source execution, relabeling or modification of preserved data.
Lexical flags describe the recorded wording, not a general semantic classifier.
Flags may overlap; request wording does not by itself rule out an outcome claim.
"""
import argparse, collections, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--package', type=Path, default=ROOT / ('study' if (ROOT / 'study').exists() else 'companion'))
parser.add_argument('--replay', type=Path)
args = parser.parse_args()
package = args.package
replay = args.replay or package / 'data/splunk-replay.jsonl'
rows = [json.loads(line) for line in replay.read_text().splitlines()]
ledger = {r['id']: r for r in json.loads((package / 'data/decision-ledger.json').read_text())}
assert len({r['id'] for r in rows}) == len(rows)
assert all(r['id'] in ledger for r in rows)

def answer(r):
    return json.loads(r['response']['message']['content'])
def packet(r):
    return json.loads(r['request']['messages'][1]['content'])
def choose(**kw):
    return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]
def normalize(value, key=''):
    # Mask identifiers, timestamps and byte values, retaining field names, shapes,
    # event names, withheld lists, nulls and instructions. This is a descriptive
    # input-template comparison, not a measure of statistical independence.
    masked = {'record_id', 'bucket', 'key', 'principal', 'eventTime', 'from', 'through',
              'bytesTransferredOut', 'bytesTransferredIn'}
    if key in masked:
        return '<' + key + '>'
    if isinstance(value, dict):
        return {k: normalize(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
result = {'audit': 'post-review descriptive interpretation audit',
          'replay_sha256': sha(replay), 'ledger_sha256': sha(package / 'data/decision-ledger.json'),
          'retained_responses_read': len(rows), 'new_inference': False,
          'reference_labels_changed': False, 'scope': 'full private replay' if len(rows) == 996 else 'included replay only',
          'lexical_flags': 'case-insensitive substrings; inspect explanations before interpreting flags',
          'template_masked_keys': sorted({'record_id','bucket','key','principal','eventTime','from','through','bytesTransferredOut','bytesTransferredIn'})}
summary = []
for study in ['initial', 'transfer']:
    for model in ['gemma4:e4b-mlx', 'qwen3.8:latest']:
        for arm in ['request_only', 'volume_only']:
            group = choose(study=study, phase='primary', tier='primary', contract='original', model=model, arm=arm)
            if not group:
                continue
            premature = [r for r in group if ledger[r['id']]['premature']]
            reasons = [answer(r)['reason'].lower() for r in premature]
            summary.append({'study': study, 'model': model, 'arm': arm, 'calls': len(group),
                            'reference_scored_premature': len(premature),
                            'successful_or_no_reported_error': sum('successful' in s or 'no reported error' in s for s in reasons),
                            'no_reported_error': sum('no reported error' in s for s in reasons),
                            'request_wording_without_success_error_or_null': sum(
                                ('recorded' in s or 'observed' in s or 'documents a getobject event' in s)
                                and not any(w in s for w in ['success','error','null']) for s in reasons),
                            'premature_ids': [r['id'] for r in premature]})
result['original_contract_explanations'] = summary
splunk = [r for r in choose(study='transfer',phase='primary',tier='primary',contract='clarified',
                           model='gemma4:e4b-mlx',arm='volume_only') if r['case_id'] != 'T25']
assert len(splunk) == 24
packets = [packet(r) for r in splunk]
assert all(len(p['records']) == 1 for p in packets)
assert len({json.dumps(p,sort_keys=True) for p in packets}) == 24
assert len({json.dumps(normalize(p),sort_keys=True) for p in packets}) == 1
assert all('errorCode' not in p['records'][0] and 'errorCode' in p['records'][0]['withheld_fields'] for p in packets)
assert all('An unavailable errorCode is unknown, not null.' in p['question'] for p in packets)
result['splunk_template'] = {'histories':24,'records_per_history':1,'normalized_templates':1,
    'event_times':sorted({p['records'][0]['eventTime'] for p in packets}),
    'byte_range':[min(p['records'][0]['bytesTransferredOut'] for p in packets),max(p['records'][0]['bytesTransferredOut'] for p in packets)],
    'explicit_null_errorCode_explanations':sum('null errorCode' in answer(r)['reason'] for r in splunk)}
result['exact_repeat_time_range_utc'] = [min(r['response']['created_at'] for r in choose(study='transfer',phase='repeat')),max(r['response']['created_at'] for r in choose(study='transfer',phase='repeat'))]
result['format_time_range_utc'] = [min(r['response']['created_at'] for r in choose(study='transfer',phase='format')),max(r['response']['created_at'] for r in choose(study='transfer',phase='format'))]
formatted = choose(study='transfer',phase='format')
for r in formatted:
    original = next(x for x in rows if x['study']=='transfer' and x['phase']=='primary' and x['case_id']==r['case_id'] and x['arm']==r['arm'] and x['model']==r['model'] and x['contract']==r['contract'])
    assert packet(r) == packet(original)
    assert r['request']['messages'][0] == original['request']['messages'][0]
    assert r['request']['messages'][1]['content'] == json.dumps(packet(original),sort_keys=True,indent=2)
result['formatting'] = {'calls_checked':len(formatted), 'values_and_system_instructions_identical':True,
    'top_level_order_original':list(packet(original)), 'top_level_order_formatted':list(packet(r))}
if len(rows) == 996:
    ref = {(r['study'],r['case_id']):ledger[r['id']]['reference'] for r in rows if r['phase']=='primary' and r['arm']=='full_history'}
    transfers = [r for r in choose(study='transfer',phase='primary',tier='primary') if ledger[r['id']]['premature']]
    result['transfer_hidden_outcome'] = {'premature_verdicts':len(transfers), 'normalized_verdict_matches_hidden_outcome':sum(ledger[r['id']]['verdict']==ref[('transfer',r['case_id'])] for r in transfers), 'interpretation':'normalized labels only; does not turn ambiguous read_observed explanations into explicit success assertions'}
    exploratory = [r for r in choose(study='initial',phase='contract',model='gemma4:e4b-mlx',arm='volume_only') if ledger[r['id']]['premature']]
    result['exploratory_gemma'] = {'remaining_premature':len(exploratory), 'false_success_on_failed_histories':sum(ref[('initial',r['case_id'])]=='service_error_response' and answer(r)['verdict']=='object_data_response' for r in exploratory)}
    initial_qwen = [r for r in choose(study='initial',phase='primary',model='qwen3.8:latest',arm='volume_only') if ref[('initial',r['case_id'])]=='service_error_response']
    result['initial_qwen_failed_histories'] = {'calls':len(initial_qwen), 'success_or_read_occurred_wording':sum('successful' in answer(r)['reason'] or 'read occurred' in answer(r)['reason'] for r in initial_qwen)}
print(json.dumps(result,indent=2))
