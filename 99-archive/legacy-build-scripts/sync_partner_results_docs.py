"""Synchronize human navigation and current-baseline metadata after M21 integration."""
from pathlib import Path
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
base=root/'docs/delivery-plan'
summary=json.loads((base/'evidence/inventory-validation.json').read_text(encoding='utf8'))
assert summary['version']=='1.8'
def edit(path, fn):
    p=base/path
    p.write_text(fn(p.read_text(encoding='utf8')),encoding='utf8')

def readme(t):
    t=t.replace('Ngày 16/10/2026.', 'Cập nhật 18/10/2026; M21 đã hợp nhất vào Master1.8.')
    t=re.sub(r'Baseline duy nhất:.*?Các tài liệu dưới đây',f"Baseline duy nhất: [Master 1.8](../../CRM_MASTER_BRD_SRS_HOP_NHAT.md), {summary['source_lines']:,} dòng. SHA-256: `{summary['sha256']}`. Các tài liệu dưới đây",t,count=1)
    t=t.replace('20 module','21 module')
    t=t.replace('## Registry máy đọc được','8. [M21 — Kết quả kinh doanh đối tác](specs/modules/M21-PARTNER-BUSINESS-RESULTS.md): 14 chức năng, 10 UC, 20 rules, 40 tests, data/API/quyền/NFR/KPI.\n9. [SL08 — Pilot kết quả đối tác](specs/slices/SL08-PARTNER-RESULTS.md): NONE/SUMMARY/FILE trước API.\n\n## Registry máy đọc được') if '[M21 —' not in t else t
    t=t.replace('Đợt đầu không tạo toàn văn 21 module, không tạo DDL giả định, không thay rule công cụ và không bật integration.', 'Đợt đầu chỉ có map 20 module; cập nhật1.8 đã tạo file đặc tả M21 và pilot SL08. 20 module cũ chưa tách toàn văn. Chưa tạo DDL/code ứng dụng hoặc bật integration.')
    if 'partner-results-trace.json' not in t:
        t=t.replace('- [Requirements]', '- [M21 feature trace](trace/partner-results-trace.json): mapping feature→UC/rule/test có review.\n- [Requirements]')
    return t
edit(Path('README.md'),readme)

def gaps(t):
    t=t.replace('Nguồn: Master 1.7, hash ở README;', 'Nguồn hiện hành: Master1.8, hash ở README; số liệu phần “Kết quả ban đầu” bên dưới là snapshot lịch sử1.7;')
    current='\n## Cập nhật M21 ngày18/10/2026\n\n'
    if current not in t:
        c=summary['counts']
        block=f"Sau tích hợp1.8: {c['modules']} module, {c['unique_id_candidates']} ID ứng viên; {c['missing_owner']} ID cũ chưa có owner giữ nguyên để review. M21 đã có owner domain, feature/UC/rule/test matrix và P-NFR; chưa có code/UAT đã chạy. Findings/evidence hiện hành thay số snapshot dưới cho báo cáo coverage mới.\n\nCác khoảng trống M21 có P-O01–08 trong Master A.8: volume chính xác, authority/scope chia sẻ, sản phẩm/quyền Pancake, metric/tolerance, mapping/precedence, retention/audience, schedule/budget và exception rules. API thiếu chỉ chặn API; không ép đối tác cấp data để dùng nghiệp vụ công ty. Physical DDL/OpenAPI và người phụ trách thực vẫn cần chốt trước enable.\n\n"
        t=t.replace('## Kết quả ban đầu', current+block+'## Kết quả ban đầu — snapshot1.7 ngày16/10/2026',1)
    return t
edit(Path('GAPS.md'),gaps)

def index(t):
    t=t.replace('Baseline 1.7','Baseline 1.8').replace('không tạo 20 service','không tạo 21 service').replace('Master 1.7 và hash','Master 1.8 và hash')
    if '| M21 |' not in t:
        line=next(l for l in t.splitlines() if l.startswith('| M20 |'))
        t=t.replace(line,line+'\n| M21 | Partner sharing profiles/datasets/imports/reconciliation/reports | Agency outcome integration, core theo mức chia sẻ | SL08 sau foundation; API theo capability |')
        t += '\n## Module đã tách file\n\n[M21 — Kết quả kinh doanh đối tác](modules/M21-PARTNER-BUSINESS-RESULTS.md) là file module chi tiết đầu tiên. 20 module cũ mới có bản đồ/inventory, chưa có đầy đủ file riêng. [SL08](slices/SL08-PARTNER-RESULTS.md) có thể triển khai sớm, không theo số thứ tự ID.\n\nM21→M19 public ingest/connection contract; M21→M18 metric definitions; M21→M14/M20 quyền/purpose; M21→M16 exception task. CLIENT dataset có scope riêng; publish summary về AGENCY qua grant/bridge. Không import private repository, không sync write ngược Pancake mặc định.\n'
    return t
edit(Path('specs/INDEX.md'),index)

def invariants(t):
    t=t.replace('Master 1.7','Master 1.8')
    if 'INV-17' not in t:
        t+='''\n## Bổ sung M21 — Master3.15/5.21/6.7/8.6\n\n| ID | Bất biến | Kiểm |
|---|---|---|
| INV-17 | NONE hợp lệ; unavailable không là0; nghiệp vụ công ty không phụ thuộc data đối tác | P-T01/07/40 |
| INV-18 | Partner order/GMV và agency lead/revenue là scope/grain khác nhau | P-T02/22/26/36 |
| INV-19 | Observation provenance/verification/coverage/freshness tách nhau; correction không sửa report đã gửi | P-T09/10/28/29 |
| INV-20 | Một effective source cho mỗi reporting partition; không sum overlap file/API/summary | P-T14/23/25 |
| INV-21 | API_READ chỉ operation đọc, current authority; không default buyer PII hoặc viết ngược POS | P-T05/06/16/17/31 |
'''
    return t
edit(Path('specs/INVARIANTS.md'),invariants)
edit(Path('specs/slices/SL01-INTERNAL-WORK.md'),lambda t:t.replace('Baseline 1.7/hash','Baseline 1.8/hash'))
edit(Path('decisions/ADR-001-BASELINE-AND-STACK.md'),lambda t:t.replace('baseline nghiệp vụ 1.7','baseline nghiệp vụ 1.8').replace('ownership theo 20 module','ownership theo 21 module'))

def roadmap(t):
    t=t.replace('Master 1.7','Master 1.8').replace('thiết kế lại 20 module','thiết kế lại các module')
    heading='## Cập nhật ưu tiên18/10/2026 — M21'
    if heading not in t:
        t=t.replace('## So sánh hai pilot',heading+'\n\nLead B2C công ty chưa chuyển đổi vẫn ưu tiên intake/routing/follow-up. Đơn đối tác không đưa vào phễu công ty. Sau foundation, SL08 NONE/SUMMARY/FILE có thể làm sớm cùng kế hoạch nghiệp vụ; API_READ chỉ sau quyền/PoC. Số SL08 là ID ổn định, không là cam kết thứ tự. SL01 là nền task/review và exception, không cần hoàn tất toàn bộ Work trước báo cáo đối tác; không hoãn Work P0 rồi tuyên bố hoàn tất scope. Retail OMS/inventory không chuyển thành P0 chỉ vì đối tác có nhiều đơn.\n\n## So sánh hai pilot',1)
        row=next(l for l in t.splitlines() if l.startswith('| SL07 |'))
        t=t.replace(row,row+'\n| SL08 | Đối tác NONE/SUMMARY/FILE vẫn quản dịch vụ và báo cáo đúng giới hạn; API theo cấp quyền | Profile/binding/observations/batches/datasets/reconciliation/reports, scoped grants | API/detail off core; file/summary fixture sạch | P-T core, source overlap/correction/ACL/restore; P-NFR theo mode; gap A.8 |')
    return t
edit(Path('ROADMAP.md'),roadmap)

manifest=json.loads((base/'agent/active-task.json').read_text(encoding='utf8'))
manifest.update(task_id='CRM-M21-INTEGRATED-20261018',status='M21 specification integrated into Master1.8; application not implemented',baseline_version='1.8',baseline_sha256=summary['sha256'],proposed_next_slice='SL08',owners=['M21','M14','M18','M19','M20','M16'])
manifest['read_first']=['../README.md','../GAPS.md','../specs/INVARIANTS.md','../specs/modules/M21-PARTNER-BUSINESS-RESULTS.md','../specs/slices/SL08-PARTNER-RESULTS.md','PROGRESS.md']
manifest['next_actions']=['Resolve P-O parameters for chosen NONE/SUMMARY/FILE mode and physical schema/API','Assign concrete data/report/QA owners','Select implementation stack; preserve capability gate for API without partner authorization']
(base/'agent/active-task.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(base/'agent/PROGRESS.md').write_text('''# Tiến độ — M21 tích hợp ngày18/10/2026

Baseline hiện hành Master1.8; hash/version ở active-task.json và evidence/inventory-validation.json. Master1.7 đã archive nguyên vẹn tại docs/archive/CRM_MASTER_v1.7_BEFORE_PARTNER_RESULTS_2026-10-18.md. Không có code ứng dụng, migration chạy hoặc UAT thực thi.

Đã hợp nhất FR41/M21 vào Master3.15, UC-P ở4.24, schema/API5.21, quyền6.7, NFR7.8, KPI8.6, tests9.17 và A.8. Có14 feature,10 UC,20 rules,8 NFR,40 UAT và8 open parameter. Module file riêng ở specs/modules, SL08 ở specs/slices; 20 module cũ chưa tách toàn văn.

Quyết định: lead B2C công ty chưa chuyển đổi là AGENCY; order đối tác dùng Pancake là CLIENT. Mode NONE/SUMMARY/FILE core, API_READ/detail theo quyền/PoC; partner data không điều kiện để chạy lead/hợp đồng/task/thu phí. Sizing mốc mới chưa chuẩn hóa, không sử dụng100 lead/50 khách như hiện trạng.

Registry rebuilt theo Master hash mới, M21 trace review riêng ở trace/partner-results-trace.json; các owner gap cũ vẫn mở. Fixture synthetic ở evidence/partner-results-fixture.json là expected oracle, không là pass evidence.

Kiểm: build_delivery_inventory.py, verify_delivery_plan.py và verify_partner_results_v18.py. Evidence tương ứng trong evidence/. Các kiểm là validation tài liệu, không xác nhận nghiệp vụ trên phần mềm. Test app hiện Not Run; Mermaid chưa render.

Phiên tiếp theo kiểm baseline hash/repo thực, đọc M21/SL08 và chọn mode pilot; chốt physical schema/API/retention/metric/authority trước code. Không cần credential Pancake để bắt đầu core; P-O03 chỉ chặn API. Không ghi đè dữ liệu generated bằng sửa tay vì rebuild sẽ thay thế.
''',encoding='utf8')
proposal=root/'docs/DE_XUAT_DIEU_CHINH_B2C_RETAIL_2026-10-18.md'
pt=proposal.read_text(encoding='utf8')
notice='**Cập nhật bàn giao:** CR-PARTNER-RESULTS-20261018 đã được hợp nhất vào Master1.8 theo yêu cầu chủ dự án. Phần đề xuất/kịch bản bên dưới là lịch sử; quy tắc hiện hành là Master3.15/4.24/5.21/6.7/7.8/8.6/9.17/A.8 và file M21 trong delivery-plan/specs/modules. Không hiểu các câu “Master chưa sửa” lịch sử là trạng thái hiện tại.\n\n'
if not pt.startswith('# Đề xuất điều chỉnh CRM cho B2C và bán lẻ trên sàn\n\n'+notice):
    pt=pt.replace('\n\n','\n\n'+notice,1)
proposal.write_text(pt,encoding='utf8')
print('Navigation, roadmap, current-baseline metadata and progress synchronized to1.8')
