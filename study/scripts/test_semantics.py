"""Adversarial boundary cases for the extracted scorer, not new research data."""
import copy,json,unittest
from reproduce import score
class Boundaries(unittest.TestCase):
 def row(self,records,verdict,ids,study='transfer'):
  p={'target':{'bucket':'b','key':'k','from':'1','through':'3'},'records':records};return {'study':study,'contract':'clarified','request':{'messages':[{}, {'content':json.dumps(p)}]},'response':{'done_reason':'stop','message':{'content':json.dumps({'verdict':verdict,'evidence_ids':ids,'reason':'Fixture.'})}}}
 def event(self,**kw):return dict({'record_id':'e','eventName':'GetObject','eventTime':'2','bucket':'b','key':'k','errorCode':None,'bytesTransferredOut':277},**kw)
 def test_error_bytes_are_failure(self):
  r=score(self.row([self.event(errorCode='NoSuchKey')],'service_error_response',['e']));self.assertTrue(r['supported_correct'])
 def test_withheld_is_not_null(self):
  e=self.event();del e['errorCode'];e['withheld_fields']=['errorCode'];r=score(self.row([e],'object_data_response',['e']));self.assertTrue(r['premature'])
 def test_complete_success_abstention_has_cost(self):self.assertFalse(score(self.row([self.event()],'insufficient_outcome_evidence',[]))['correct'])
 def test_invented_citation_is_distinct_from_verdict(self):
  r=score(self.row([self.event()],'object_data_response',['fiction']));self.assertTrue(r['correct']);self.assertFalse(r['supported_correct'])
 def test_other_object_does_not_resolve_target(self):self.assertTrue(score(self.row([self.event(key='other')],'insufficient_outcome_evidence',[]))['correct'])
 def test_outside_window_does_not_resolve_target(self):self.assertTrue(score(self.row([self.event(eventTime='4')],'insufficient_outcome_evidence',[]))['correct'])
 def test_mixed_errors_and_success_need_success_citation(self):
  es=[self.event(record_id='bad',errorCode='AccessDenied'),self.event()];self.assertFalse(score(self.row(es,'object_data_response',['bad']))['supported_correct']);self.assertTrue(score(self.row(es,'object_data_response',['e']))['supported_correct'])
 def test_extra_context_rule_differs_between_stages(self):
  es=[self.event(),self.event(record_id='setup',eventName='PutObject')]
  self.assertTrue(score(self.row(es,'object_data_response',['e','setup']))['supported_correct']);self.assertFalse(score(self.row(es,'object_data_response',['e','setup'],study='initial'))['supported_correct'])
 def test_zero_bytes_do_not_establish_nonzero_response(self):self.assertTrue(score(self.row([self.event(bytesTransferredOut=0)],'insufficient_outcome_evidence',[]))['correct'])
 def test_truncation_remains_invalid(self):
  row=self.row([self.event()],'object_data_response',['e']);row['response']['done_reason']='length';self.assertFalse(score(row)['valid'])
if __name__=='__main__':unittest.main()
