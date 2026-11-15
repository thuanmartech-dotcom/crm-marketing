from pathlib import Path
from hashlib import sha256
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from pypdf import PdfReader
import json
root=Path(__file__).parent
out=root/'working'/'sources';out.mkdir(parents=True,exist_ok=True)
manifest=[]
for i,f in enumerate(sorted((root/'docs').rglob('*')),1):
 if not f.is_file():continue
 parts=[]
 if f.suffix=='.docx':
  d=Document(f)
  for el in d.element.body:
   if el.tag.endswith('}p'):
    p=Paragraph(el,d);parts.append(p.text)
   elif el.tag.endswith('}tbl'):
    t=Table(el,d);parts.extend(' | '.join(c.text for c in row.cells) for row in t.rows)
 elif f.suffix=='.pdf':
  d=PdfReader(f)
  for n,page in enumerate(d.pages):parts.append(f'\n## PDF PAGE {n+1}\n'+page.extract_text())
 elif f.suffix=='.md':parts=[f.read_text(encoding='utf-8')]
 else:continue
 txt='\n'.join(parts); dest=out/f'{i:02}_{f.stem}.txt';dest.write_text(txt,encoding='utf-8')
 manifest.append(dict(path=str(f.relative_to(root)),hash=sha256(f.read_bytes()).hexdigest(),chars=len(txt),extracted=str(dest.relative_to(root))))
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
