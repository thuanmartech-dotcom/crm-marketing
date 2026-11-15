from pathlib import Path
import re,json,hashlib
root=Path(__file__).resolve().parents[1]
master=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
# Preserve text while fixing newline expansion from mixed-source CRLF input.
master.write_bytes(master.read_bytes().replace(b'\r\r\n',b'\r\n'))
s=master.read_text(encoding='utf8').replace('không suy rằng21 module','không suy rằng22 module')
s=s.replace('**Cách sử dụng:** bắt đầu', '**Cách sử dụng:** M22 HRM đọc3.16 → 4.25 → 5.22 → 6.8 → 7.9 → 8.7 → 9.18 → A.9. Bắt đầu',1)
master.write_text(s,encoding='utf8')
base=root/'docs/delivery-plan'
sha=hashlib.sha256(master.read_bytes()).hexdigest()
p=base/'README.md';s=p.read_text(encoding='utf8')
s=re.sub(r', [\d,]+ dòng\. SHA-256: `[a-f0-9]+`',f", {len(master.read_text(encoding='utf8').splitlines()):,} dòng. SHA-256: `{sha}`",s)
s=s.replace("python 'tài liệu tham khảo/working/verify_delivery_plan.py'", "python 'tài liệu tham khảo/working/verify_delivery_plan.py'\npython 'tài liệu tham khảo/working/verify_hrm_integration.py'")
p.write_text(s,encoding='utf8')
p=base/'agent/active-task.json';m=json.loads(p.read_text(encoding='utf8'));m['baseline_sha256']=sha;p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=base/'decisions/ADR-001-BASELINE-AND-STACK.md';s=p.read_text(encoding='utf8').replace('baseline nghiệp vụ 1.8','baseline nghiệp vụ 1.9').replace('ownership theo 21 module','ownership theo 22 module');p.write_text(s,encoding='utf8')
p=base/'specs/slices/SL09-11-HRM.md';s=p.read_text(encoding='utf8').replace('HR-T device','Các ca kiểm thiết bị');p.write_text(s,encoding='utf8')
