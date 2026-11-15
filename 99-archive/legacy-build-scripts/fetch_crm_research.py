from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures
out=Path(__file__).parent/'crm_research';out.mkdir(exist_ok=True)
repos={
'twenty':('twentyhq/twenty','main',['packages/twenty-server/package.json','packages/twenty-front/package.json','nx.json','LICENSE']),
'chatwoot':('chatwoot/chatwoot','develop',['app/models/conversation.rb','app/models/contact_inbox.rb','app/models/inbox.rb','Gemfile','LICENSE']),
'frappe_crm':('frappe/crm','develop',['crm/hooks.py','pyproject.toml','frontend/package.json','crm/fcrm/doctype/crm_lead/crm_lead.py','LICENSE']),
'espocrm':('espocrm/espocrm','master',['composer.json','package.json','application/Espo/Modules/Crm/Resources/metadata/entityDefs/Lead.json','LICENSE.txt']),
'suitecrm':('SuiteCRM/SuiteCRM-Core','master',['composer.json','package.json','LICENSE.txt']),
'odoo':('odoo/odoo','19.0',['addons/crm/__manifest__.py','addons/crm/models/crm_lead.py','addons/crm/security/ir.model.access.csv','LICENSE'])}
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'CRM-document-research'})
 with urllib.request.urlopen(req,timeout=35) as r:return r.read()
def work(item):
 name,(repo,ref,paths)=item;d=out/name;d.mkdir(exist_ok=True)
 result={'repo':repo,'requested_ref':ref,'files':[]}
 try:
  commit=json.loads(get(f'https://api.github.com/repos/{repo}/commits/{ref}'))
  sha=commit['sha'];result.update(commit=sha,commit_date=commit['commit']['committer']['date'])
 except Exception as e:result['error']=str(e);return result
 for path in paths:
  url=f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'
  try:
   body=get(url);dest=d/path.replace('/','__');dest.write_bytes(body)
   result['files'].append({'path':path,'url':f'https://github.com/{repo}/blob/{sha}/{path}','local':str(dest),'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)})
  except Exception as e:result['files'].append({'path':path,'error':str(e)})
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(work,repos.items()))
(out/'manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
