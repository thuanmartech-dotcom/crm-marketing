from pathlib import Path
import re,json
root=Path(__file__).resolve().parent.parent
p=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
s=p.read_text(encoding='utf-8')
assert 'Phiên bản 1.6' in s[:1000]
reasons=json.loads((root/'working/ba_function_reasons.json').read_text(encoding='utf-8'))
lines=s.splitlines()
function_rows={}
for i,line in enumerate(lines):
    m=re.match(r'^\| (M\d{2})-F(\d{2})\b',line)
    if m:
        function_rows[i]=reasons[m.group(1)][int(m.group(2))-1]
assert len(function_rows)==144
headers=[]
for i,line in enumerate(lines):
    if line.startswith('| Chức năng |') and any(j in function_rows for j in range(i+2,min(i+14,len(lines)))):
        assert 'Vì sao cần' not in line
        headers.append(i)
assert len(headers)==20
for i in headers:
    lines[i]=lines[i].rstrip()+' Vì sao cần |'
    lines[i+1]=lines[i+1].rstrip()+' --- |'
for i,why in function_rows.items():
    lines[i]=lines[i].rstrip()+' '+why+' |'
s='\n'.join(lines)+'\n'
s=s.replace('Contract Draft/PendingSignature/Signed/Active/Expired/Terminated/Cancelled theo WF03','Contract Draft/PendingSignature/Signed/Active/Expired/Terminated/Cancelled theo3.13.5')
s=s.replace('Refund có state/reservation theo DB02.', 'Refund có state/reservation theo3.13.4/4.13.')
s=s.replace('bản approved/gửi bất biến.', 'nội dung bản approved/gửi bất biến.')
s=s.replace('Draft/PendingApproval/Approved/Sent/Accepted/Rejected/Expired/Superseded, expires_at', 'Draft/PendingApproval/Approved/Sent/Accepted/Rejected/Expired/Superseded/Cancelled, expires_at')
for prefix,fields in [
 ('| Projects, Deliverables, Acceptances |','Projects.status, Deliverables.status theo3.13.5; '),
 ('| Contracts, SOW_Versions |','Contracts.status theo3.13.5; '),
 ('| Campaigns |','Campaigns.status Draft/Ready/Live/Paused/Completed/Cancelled theoM15; '),
]:
    row=next(x for x in s.splitlines() if x.startswith(prefix))
    cols=row.split('|')
    cols[2]=' '+fields+cols[2].strip()+' '
    s=s.replace(row,'|'.join(cols),1)
s=s.replace('#### G.6.','#### G.6.')
s=s.replace('mỗi module có mã chức năng, điều kiện xử lý,', 'mỗi module có mã chức năng, lý do cần chức năng, điều kiện xử lý,')
p.write_text(s,encoding='utf-8',newline='\n')
print('Added explicit business rationale for 144 functions in 20 module tables; aligned state fields.')
