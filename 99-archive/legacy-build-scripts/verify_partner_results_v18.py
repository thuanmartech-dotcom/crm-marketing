"""Verify M21 integration and BA traceability; no application behavior is exercised."""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
import re, json, hashlib, sys

sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
base=root/'docs/delivery-plan'
master=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
archive=root/'docs/archive/CRM_MASTER_v1.7_BEFORE_PARTNER_RESULTS_2026-10-18.md'
text=master.read_text(encoding='utf8')
spec=(base/'specs/modules/M21-PARTNER-BUSINESS-RESULTS.md').read_text(encoding='utf8')
records={r['id']:r for r in json.loads((base/'trace/requirements.json').read_text(encoding='utf8'))['records']}
trace=json.loads((base/'trace/partner-results-trace.json').read_text(encoding='utf8'))
manifest=json.loads((base/'agent/active-task.json').read_text(encoding='utf8'))
summary=json.loads((base/'evidence/inventory-validation.json').read_text(encoding='utf8'))
checks={}
checks['baseline_1_8']=summary['version']=='1.8' and manifest['baseline_version']=='1.8'
checks['hashes_synchronized']=hashlib.sha256(master.read_bytes()).hexdigest()==summary['sha256']==manifest['baseline_sha256']==trace['source_sha256']
checks['archive_1_7_exact']=hashlib.sha256(archive.read_bytes()).hexdigest()=='70c190232df3416680f3ee768288fa53230aa4b8cc131609fa4d9a933a97affb'
blocks={k:v.strip() for k,v in re.findall(r'<!-- MASTER:([^>]+) -->\s*(.*?)(?=<!-- MASTER:|<!-- END:MASTER -->)',spec,re.S)}
checks['eight_canonical_blocks_integrated_exactly']=len(blocks)==8 and all(v in text for v in blocks.values())
checks['all_new_ids_defined_owned']=all(records.get(f'{p}{i:02}',{}).get('definition_lines') and records[f'{p}{i:02}']['owner']=='M21' for p,n in [('M21-F',14),('UC-P',10),('BR-P',20),('P-NFR',8),('P-T',40),('P-O',8)] for i in range(1,n+1))
checks['FR41_owned_and_covered']=records['FR41']['owner']=='M21' and records['FR41']['tests']==[f'P-T{i:02}' for i in range(1,41)]
matrix=trace['feature_matrix']
checks['features_14_have_uc_rule_test']=len(matrix)==14 and all(r['use_cases'] and r['rules'] and r['tests'] for r in matrix)
checks['all_uc_rules_have_trace_test']=all(records[f'{p}{i:02}']['tests'] for p,n in [('UC-P',10),('BR-P',20),('P-NFR',8)] for i in range(1,n+1))
checks['all_tests_covered_by_feature']=set().union(*(set(r['tests']) for r in matrix))=={f'P-T{i:02}' for i in range(1,41)}
checks['all_new_references_resolve']=all(ref in records for r in matrix for ref in r['use_cases']+r['rules']+r['tests'])
checks['new_test_definitions_once']=all(len(records[f'P-T{i:02}']['definition_lines'])==1 for i in range(1,41))
checks['application_tests_still_not_run']=all(r['verification_status']=='Not Run' and not r['evidence'] for r in records.values())
entities=json.loads((base/'trace/entities-contracts.json').read_text(encoding='utf8'))
new_entities=[e for e in entities['entities'] if e['owner']=='M21']
new_contracts=[e for e in entities['contracts'] if e['owner']=='M21']
checks['partner_schema_and_API_extracted']=len(new_entities)==12 and len([c for c in new_contracts if re.match(r'^\| (POST|GET) ',c['text'])])==19
checks['m21_mode_values_present']=all(mode in blocks['3.15'] for mode in ['NONE','SUMMARY','FILE','API_READ'])
checks['module_anchor_unique']=text.count('<a id="module-m21"></a>')==1

# The fixture is an expected-value sanity check, not a CRM test result.
fixture=json.loads((base/'evidence/partner-results-fixture.json').read_text(encoding='utf8'))
detail=fixture['client_b']['detail']; expected=fixture['expected']
gross=sum(Decimal(o['order_value_vnd']) for o in detail)
retained=sum(Decimal(o['order_value_vnd']) for o in detail if o['status']!='CANCELED')
attributed=sum(Decimal(o['order_value_vnd'])*Decimal(o['credit']) for o in detail if o['status']!='CANCELED' and o['attribution']=='CONFIRMED')
checks['fixture_expected_arithmetic']=gross==Decimal(expected['client_b_gross_created_vnd']) and retained==Decimal(expected['client_b_retained_vnd']) and attributed/Decimal(fixture['client_b']['spend_vnd'])==Decimal(expected['client_b_attributable_roas'])
checks['fixture_unavailable_not_zero']=fixture['client_a']['order_count'] is None and expected['agency_lead_conversion_rate'] is None
checks['fixture_agency_finance_separate']=fixture['agency']['service_fee_receivable_vnd']==expected['agency_service_fee_receivable_vnd'] and gross!=Decimal(expected['agency_service_fee_receivable_vnd'])
checks['fixture_overlap_not_double_counted']=len(detail)==expected['client_b_selected_order_count'] and expected['old_report_gross_after_correction_vnd']==str(gross)
result={'date':'2026-10-18','run_at_utc':datetime.now(timezone.utc).isoformat(),'kind':'BA document integration and trace validation only','checks':checks,'m21_entity_declarations':len(new_entities),'m21_contract_declarations':len(new_contracts),'application_test_status':'Not Run','provider_capability_status':'Not verified on partner account','mermaid_rendering':'Not Run'}
(base/'evidence/partner-results-integration-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if not all(checks.values()): raise SystemExit('M21 integration validation failed; inspect before delivery')
