"""Apply reviewed HRM specification sections once; preserve previous baseline."""
from pathlib import Path
import re, json, hashlib

root = Path(__file__).resolve().parents[1]
master = root / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
base = root / 'docs/delivery-plan'
original = master.read_bytes()
text = original.decode('utf-8-sig').replace('\r\n', '\n')
assert '### 3.16 FR42' not in text, 'Already integrated'
archive = root / 'docs/archive/CRM_MASTER_v1.8_BEFORE_HRM_2026-10-18.md'
assert not archive.exists()
archive.write_bytes(original)
parts = re.split(r'<!-- SECTION:([3456789A]) -->\s*', (root/'working/hrm_sections.md').read_text(encoding='utf8'))
sections = dict(zip(parts[1::2], parts[2::2]))
for key, anchor in [('3','chuong-4'),('4','chuong-5'),('5','chuong-6'),('6','chuong-7'),('7','chuong-8'),('8','chuong-9'),('9','chuong-10'),('A','phu-luc-b')]:
    marker = f'<a id="{anchor}"></a>'
    assert text.count(marker) == 1, marker
    text = text.replace(marker, sections[key].strip()+'\n\n'+marker)
text = text.replace('Phiên bản 1.8 — Hợp nhất kết quả kinh doanh đối tác, chia sẻ dữ liệu theo mức và lead công ty', 'Phiên bản 1.9 — Tích hợp quản trị nhân sự, chuyển đổi Excel, công và lương theo giai đoạn',1)
text = text.replace('` — phiên bản 1.8.', '` — phiên bản 1.9.',1)
text = text.replace('Đặc tả thiết kế BA hiện hành 1.8','Đặc tả thiết kế BA hiện hành 1.9')
text = text.replace('Danh mục 21 module','Danh mục 22 module').replace('Đây là 21 ranh giới','Đây là 22 ranh giới').replace('không phải 21 ứng dụng','không phải 22 ứng dụng')
text = text.replace('**Phiên bản 1.8 (18/10/2026):**','**Phiên bản 1.9 (18/10/2026):** CR-HRM-20261018 bổ sung FR42/M22 theo quyết định chủ dự án đang quản lý nhân sự bằng Excel. Tích hợp 3.16/4.25/5.22/6.8/7.9/8.7/9.18/A.9, gồm 28 chức năng, 16 UC, 24 quy tắc, 48 ca UAT, 8 NFR và 10 tham số mở. HR-A trước; HR-B công nâng cao; HR-C payroll sau đối soát. Bản1.8 lưu archive; chưa có code/UAT thực thi.\n\n**Phiên bản 1.8 (18/10/2026):**',1)
text = text.replace('- [M21 — Kết quả kinh doanh đối tác](#module-m21)', '- [M21 — Kết quả kinh doanh đối tác](#module-m21)\n- [M22 — Quản trị nhân sự, công và lương](#module-m22)')
row = '| [M22](#module-m22) | Quản trị nhân sự, công và lương | HR, nhân viên, quản lý, payroll, Finance | Employee/employment/contract/leave/attendance/payroll/import | M10/M14/M16/M18/M19/M20; M09 thanh toán theo adapter | HR-A hồ sơ/phép/công cơ bản; HR-B ca/OT; HR-C payroll sau gate; không kéo toàn bộ vào P0 CRM |'
text = re.sub(r'(^\| \[M21\].*$)', lambda m:m[0]+'\n'+row,text,count=1,flags=re.M)
text = text.replace('P0 phân quyền; hai nhánh khi có vận hành thật; không payroll', 'P0 phân quyền; hai nhánh khi có vận hành thật; payroll thuộc M22 HR-C')
text = text.replace('Scorecard nhân sự ở FR27 là P2, không kéo payroll/hồ sơ sức khỏe vào CRM.', 'Scorecard nhân sự ở FR27 là P2. M14 không sở hữu payroll; M22 HR-C sở hữu/tích hợp theo3.16. Không thu hồ sơ sức khỏe mặc định.')
text = text.replace('HRM/payroll, retail inventory và hồ sơ y tế là pack/tích hợp riêng qua dự án có phạm vi, dữ liệu và đánh giá tuân thủ riêng.', 'HRM được tích hợp tại M22 theo HR-A/B/C và gate9.18; payroll ở HR-C, không trì hoãn CRM để chờ lương. Retail inventory và hồ sơ y tế vẫn là pack/tích hợp riêng có phạm vi và đánh giá riêng.')
text = text.replace('và đưa HRM đầy đủ thành tích hợp/pack độc lập.', 'và đưa HRM thành phân hệ M22 có ranh giới dữ liệu/quyền riêng theo quyết định1.9; payroll triển khai sau theo HR-C.')
text = text.replace('Hoãn thành HRM riêng; MVP chỉ organization, capacity, delegation và cost allocation.', 'Cập nhật1.9: tích hợp M22 HR-A hồ sơ/phép/công cơ bản; HR-B công nâng cao; payroll HR-C; tuyển dụng/đào tạo mở rộng HR-D cần CR riêng.')
master.write_text(text, encoding='utf8')

module = '# M22 — Quản trị nhân sự, công và lương\n\nBản đọc theo module, dẫn xuất nguyên văn từ [Master1.9](../../../../CRM_MASTER_BRD_SRS_HOP_NHAT.md#module-m22). Master là nguồn chuẩn; không chỉnh bản dẫn xuất độc lập. Các anchor/chương giữ số của Master.\n\n' + '\n\n'.join(s.strip() for s in sections.values())+'\n'
(base/'specs/modules/M22-HUMAN-RESOURCES.md').write_text(module,encoding='utf8')

for rel in ['README.md','specs/INDEX.md','GAPS.md']:
    p=base/rel; s=p.read_text(encoding='utf8')
    if rel=='README.md':
        s=s.replace('M21 đã hợp nhất vào Master1.8.', 'M21 và M22 đã hợp nhất vào Master1.9; HRM triển khai theo giai đoạn, payroll làm sau.')
        s=s.replace('Master 1.8','Master 1.9').replace('21 module','22 module')
        s=re.sub(r', [\d,]+ dòng\. SHA-256: `[a-f0-9]+`',f", {len(text.splitlines()):,} dòng. SHA-256: `{hashlib.sha256(master.read_bytes()).hexdigest()}`",s)
        s=s.replace('## Registry máy đọc được','10. [M22 — Quản trị nhân sự](specs/modules/M22-HUMAN-RESOURCES.md): đặc tả đầy đủ HR-A/B/C, migration Excel và 48 ca UAT.\n11. [SL09–11 — Lộ trình HRM](specs/slices/SL09-11-HRM.md): pilot và gates công/lương.\n\n## Registry máy đọc được')
        s=s.replace('- [M21 feature trace]', '- [M22 feature trace](trace/hrm-trace.json): chức năng→UC/rule/test từ Master.\n- [M21 feature trace]')
        s=s.replace('Đợt đầu chỉ có map 20 module; cập nhật1.8 đã tạo file đặc tả M21 và pilot SL08.', 'Đợt đầu chỉ có map20 module; cập nhật1.8 có M21/SL08; cập nhật1.9 thêm M22/SL09–11.')
    elif rel=='specs/INDEX.md':
        s=s.replace('Baseline 1.8','Baseline 1.9').replace('21 service','22 service').replace('Master 1.8 và hash','Master 1.9 và hash')
        s=re.sub(r'(^\| M21.*$)',lambda m:m[0]+'\n| M22 | Employee/employment/leave/attendance/payroll | HR extension; same app, separate data authority | SL09 HR-A; SL10 HR-B; SL11 HR-C |',s,count=1,flags=re.M)
        s+='\n[M22 — Quản trị nhân sự](modules/M22-HUMAN-RESOURCES.md) kế thừa identity/authority M14, entitlement M10; không tạo engine quyền hoặc hoa hồng thứ hai. [SL09–11](slices/SL09-11-HRM.md) phân kỳ triển khai, không thay ưu tiên SL08 đã đề xuất.\n'
    else:
        s=s.replace('Nguồn hiện hành: Master1.8','Nguồn hiện hành: Master1.9')
        s+='\n## Cập nhật HRM1.9\n\nM22 đã có đặc tả28chức năng/16UC/24rules/48UAT/8NFR; các H-O01–10 ở Master A.9 là đầu vào triển khai còn mở. Đã xác nhận hiện trạng Excel, chưa nhận file thật; không giả đã làm sạch/import dữ liệu. Chưa chọn INTERNAL/EXTERNAL payroll, thiết bị hoặc bank adapter. Số liệu kiểm kê hiện hành lấy evidence/inventory-validation.json; snapshot1.8 phía trên là lịch sử.\n'
    p.write_text(s,encoding='utf8')

p=base/'ROADMAP.md';s=p.read_text(encoding='utf8')
s+='\n## Bổ sung HRM — CR-HRM-20261018\n\n| Slice | Kết quả | Gate |\n|---|---|---|\n| SL09 / HR-A | Hồ sơ/hợp đồng/phép/công cơ bản/tự phục vụ/nhận-nghỉ việc và chuyển Excel | Policy, quyền, dữ liệu đối soát, UAT-A và restore/cutover |\n| SL10 / HR-B | Ca nâng cao, sửa công/OT, thiết bị nếu có | UAT-B/ca đêm/offline/dedupe; không có thiết bị vẫn dùng file |\n| SL11 / HR-C | INTERNAL hoặc EXTERNAL payroll, commission route, phiếu và chi có duyệt | Hai kỳ đối chiếu, UAT-C, maker/checker; bank API gate riêng |\n\nĐọc [đặc tả slice](specs/slices/SL09-11-HRM.md). Đây là thứ tự trong miền HR; chưa cam kết ngân sách/ngày phát hành và không tự thay ưu tiên pilot M21. Ước lượng lại chi phí theo Master A.9 trước cam kết rollout.\n'
p.write_text(s,encoding='utf8')
p=base/'agent/active-task.json';m=json.loads(p.read_text(encoding='utf8'))
m.update(task_id='CRM-M22-INTEGRATED-20261018',status='M22 specification integrated into Master1.9; application not implemented',baseline_version='1.9',baseline_sha256=hashlib.sha256(master.read_bytes()).hexdigest(),proposed_next_slice='SL09 HR-A candidate; coordinate with existing SL08 priority')
m['read_first']+=['../specs/modules/M22-HUMAN-RESOURCES.md','../specs/slices/SL09-11-HRM.md']
m['owners']=list(dict.fromkeys(m['owners']+['M22','M10','M09']))
m['next_actions']=['Confirm H-O inputs for HR-A; inventory actual Excel files and assign HR owner','Decide implementation ordering with existing SL08, stack and physical schema','Keep payroll HR-C and bank capability gated; no application verification claimed']
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=base/'agent/PROGRESS.md';p.write_text(p.read_text(encoding='utf8')+'\n## 18/10/2026 — HRM1.9\n\nĐã hợp nhất M22 vào thân Master, lưu baseline1.8, tạo bản đọc module và SL09–11. Bổ sung đầy đủ A/B/C, migration Excel, ownership/quyền/UAT và tham số mở. Registry được tái sinh; validation là kiểm tài liệu, ứng dụng chưa triển khai. Không đổi kết quả thực thi hoặc mức sẵn sàng của M21.\n',encoding='utf8')
print('Integrated Master1.9 and derived planning documents')
