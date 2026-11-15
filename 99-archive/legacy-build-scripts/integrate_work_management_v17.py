from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
master = root / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
report = root / 'docs/BA_RESEARCH_QUAN_LY_CONG_VIEC_TEAM_TO_CHUC_2026-10-16.md'
s = master.read_text(encoding='utf-8')
r = report.read_text(encoding='utf-8')
assert 'CR-WORK-20261016' not in s, 'Already integrated; do not run twice.'
original = s

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:100], s.count(old))
    s = s.replace(old, new, 1)

def section(name):
    start = r.index('## ' + name)
    end = re.search(r'^##? ', r[start + 3:], re.M)
    return r[start:start + 3 + end.start()].strip() if end else r[start:].strip()

def retitle(name, title):
    text = section(name)
    lines = text.splitlines()
    lines[0] = title
    for i in range(1, len(lines)):
        if lines[i].startswith('### '):
            lines[i] = '#' + lines[i]
    return '\n'.join(lines)

def before_anchor(anchor, text):
    replace(f'<a id="{anchor}"></a>', text.strip() + '\n\n' + f'<a id="{anchor}"></a>')

replace('Phiên bản 1.6 — Đặc tả BA theo 20 module; đã hợp nhất sửa đổi vào phần thân', 'Phiên bản 1.7 — Hợp nhất quản lý công việc cá nhân, đội nhóm, tổ chức và dự án')
replace('Ngày 15 tháng 10 năm 2026  ', 'Ngày 16 tháng 10 năm 2026  ')
replace('`CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản 1.6.', '`CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản 1.7.')
replace('Nội dung 1.6 là quyết định thiết kế BA;', 'Nội dung 1.7 là quyết định thiết kế BA;')
replace('Đặc tả thiết kế BA hiện hành 1.6;', 'Đặc tả thiết kế BA hiện hành 1.7;')
replace('nguồn công khai được tra cứu ngày 15/10/2026.', 'nguồn công khai được tra cứu ngày 15–16/10/2026.')
replace('Các FR01–40/UC01–22 được giữ để truy vết.', 'Các FR01–40/UC01–22 được giữ để truy vết; bổ sung UC-W01–10, WF01–14, BR-W01–10 và W-T01–40 cho Work Management. Đọc 3.14 → 4.23 → 5.20 → 6.6 → 8.5 → 9.16 để triển khai miền công việc dùng chung.')
replace('## Kiểm soát tài liệu', '**Hợp nhất 1.7 — CR-WORK-20261016:** theo yêu cầu chủ dự án, đã tích hợp Task Core vào M16 và phần thân Chương 3–9, nguồn nghiên cứu ở Phụ lục H. My Work, giao/nhận việc, Team Board, review, gia hạn, checklist/subtask, dependency FS và mẫu/việc định kỳ cơ bản là P0 của miền công việc; capacity theo giờ/Gantt/portfolio nâng cao là P1. Quyền tích hợp tài liệu không đồng nghĩa ngân sách, lịch go-live, license hay UAT đã được duyệt. Master là nguồn chuẩn; báo cáo nghiên cứu giữ vai trò bằng chứng lịch sử.\n\n## Kiểm soát tài liệu')
replace('## Mục lục', '**Phiên bản 1.7 (16/10/2026):** CR-WORK-20261016 mở rộng M16 cho personal/internal/CRM/project work; giữ invariant Omnichannel của 1.6; đồng bộ use case, schema/API, quyền, KPI và 40 ca UAT.\n\n## Mục lục')
replace('- [Phụ lục G — Nghiên cứu Pancake và Omnichannel ngày 16/10/2026](#phu-luc-g)', '- [Phụ lục G — Nghiên cứu Pancake và Omnichannel ngày 16/10/2026](#phu-luc-g)\n- [Quản lý công việc — đặc tả lõi 3.14](#work-core)\n- [Phụ lục H — Nghiên cứu giao việc và quyết định hợp nhất 1.7](#phu-luc-h)')
replace('| Công cụ quản lý dự án hiện có | Dự án, milestone, người phụ trách và nghiệm thu | P1; CRM giữ liên kết và trạng thái cần cho chăm sóc, không nhân đôi toàn bộ quản lý task. |', '| Công cụ quản lý dự án hiện có | Dự án, task, milestone, người phụ trách và nghiệm thu | Task Core CRM là nguồn chuẩn mặc định ở pilot. Connector PMS ngoài P1; project dùng PMS có source authority rõ theo 5.20/UC-W10, CRM là giao diện/projection; không hai master ghi đè. |')
replace('| [M16](#module-m16) | Dự án, milestone, đầu ra, sửa đổi và nghiệm thu | AM, Delivery, khách có quyền | Project/deliverable/version/acceptance/change | M08/M11/M13/M15/M17 | P0 đầu ra/milestone; task/capacity chi tiết P1 |', '| [M16](#module-m16) | Quản lý công việc cá nhân, đội nhóm, tổ chức, dự án và nguồn lực | Nhân viên, trưởng nhóm, PM, AM, Delivery, reviewer, khách có quyền | Task/assignment/review/recurrence/project/deliverable/acceptance | M02/M03/M04/M08/M11/M13/M14/M15/M17/M18 | P0 Task Core, My Work/Team Board, delivery; P1 effort/capacity/Gantt/portfolio nâng cao; P2 OKR/AI nâng cao |')
replace('#### 3.10.1 FR25 Task và capacity', '#### 3.10.1 FR25 Quản lý công việc dùng chung và capacity')
replace('**Mục đích và trách nhiệm:** FR25 Tasks/capacity — Delivery Lead. Không nhận vượt nguồn lực và không quên dependency.', '**Mục đích và trách nhiệm:** FR25 Work Management — Ops/Team Lead/Project Manager. Quản lý việc cá nhân, nội bộ, follow-up CRM và dự án bằng Task Core chung, rõ trách nhiệm, hạn và kết quả; Delivery Lead quản thực thi đầu ra khách hàng.')
replace('**Liên kết đầu vào → đầu ra:** SOW/milestone/availability → planned work → actual effort/acceptance.', '**Liên kết đầu vào → đầu ra:** Nhu cầu cá nhân/team/CRM/SOW/milestone → Task Core và assignment → thực hiện/review/completion; client acceptance và effort/cost là nghiệp vụ liên kết riêng.')
replace('**Nghiệm thu và giai đoạn:** Đổi scope cập nhật tải; tránh hai nơi cùng sửa task; nghỉ phép không bị tính thiếu năng suất; P0 milestone/P1 capacity.', '**Nghiệm thu và giai đoạn:** P0 gồm WF01–09 tại 3.14 và milestone/deliverable; P1 capacity theo giờ, Gantt, portfolio nâng cao. Claim/review/recurrence không nhân hiệu ứng, ACL không bị mở ngầm; nghỉ phép/khách chờ không bị tính thiếu năng suất. W-T01–40 tại 9.16 áp theo capability được phát hành.')
replace('P0 quản milestone/deliverable, owner/reviewer, due, QA, acceptance và dependency thiết yếu. Task nội bộ khác đầu ra khách mua. Chọn PMS hoặc CRM module làm nguồn ghi task duy nhất; đồng bộ external ID/version/status, không hai master ghi đè.', 'P0 quản Task Core dùng chung: việc độc lập hoặc có context, giao/nhận/chuyển, My Work/Team Board, due và gia hạn, result/review, checklist/subtask, dependency Finish-to-Start, template/calendar recurrence. Giữ milestone/deliverable, QA và client acceptance riêng. Mặc định CRM là nguồn ghi task ở pilot; nếu project dùng PMS đã chọn thì khai báo source authority và mapping 5.20/UC-W10 trước bật, không hai master ghi đè.')
replace('Khi cần task chi tiết: estimate/actual, definition of done, dependency không cycle, reviewer/evidence.', 'Task P0 có definition of done, dependency không cycle, reviewer/evidence. Estimate/actual có thể chưa nhập ở P0; lập kế hoạch effort chi tiết và availability thuộc P1, thiếu dữ liệu không coi bằng 0.')
replace('#### ĐẶC TẢ MODULE M16 — Delivery và nguồn lực', '#### ĐẶC TẢ MODULE M16 — Quản lý công việc, dự án và nguồn lực')
replace('**Mục đích, tác nhân và phạm vi:** Delivery Lead phân việc; thực hiện tạo đầu ra; reviewer QA; AM điều phối; approver khách nghiệm thu. P0 milestone/deliverable/acceptance; capacity chi tiết P1; timesheet khi có nhu cầu. CRM hoặc PMS là một nguồn ghi task.', '**Mục đích, tác nhân và phạm vi:** Nhân viên quản việc cá nhân; Team Lead/PM giao việc nội bộ/dự án; Sales/AM quản follow-up; reviewer kiểm kết quả; approver khách nghiệm thu riêng. P0 Task Core và delivery, P1 effort/capacity chi tiết; timesheet khi có nhu cầu. Quy tắc nguồn ghi ở FR25. M16-F01–07 dưới đây giữ phần delivery; WF01–14 và 3.14 đặc tả phần công việc dùng chung, không tạo module/task engine thứ hai.')
replace('Bắt buộc contract/SOW/handoff link, scope, owner, deliverable, planned/committed due riêng, acceptance criteria.', 'Client delivery project bắt buộc contract/SOW/handoff link theo gate M08 cùng scope, owner, deliverable, planned/committed due riêng và acceptance criteria. Internal project không bắt hợp đồng; personal/internal/CRM task độc lập không bắt project. Field và validation cho Task Core ở 3.14.')
replace('| Tasks, Time_Entries, Availability | owner_id uuid, project_id uuid, due_at timestamptz, estimate/actual numeric, reviewer_id uuid | Không dependency cycle; giờ không âm; holiday/calendar riêng. |', '| Tasks và miền Work Management | Task/assignment/participants/submission/review/change request/dependency/recurrence tại 5.20 | project_id nullable theo work_type; scoped FK; lifecycle riêng; không gộp schema Task, Time_Entries và Availability thành một bảng. |\n| Time_Entries, Resource_Allocations, Availability | Task/user/period/duration và availability theo lịch, hiệu lực | P1; schema tách ở 5.20; không double count parent/child, không coi missing estimate là 0. |')
replace('| FR25–27 Work/budget | UC04/06/08/16 | Tasks, availability, cost, budget | U19/U20 và kiểm commitment→actual |', '| FR25 Work Management | UC-W01–10; UC06/08/12 | Tasks/assignment/review/dependency/recurrence; 3.14/5.20/6.6 | W-T01–40, WF01–14; 9.16 |\n| FR26–27 Budget/people | UC04/06/08/16 | Availability, cost, budget; quyền dữ liệu nhân sự | U19/U20, commitment→actual; không dùng task count làm scorecard duy nhất |')
replace('P1 theo nhu cầu: connector kế toán/PMS/calendar/spend, workload, referral nhẹ,', 'P1 theo nhu cầu: connector kế toán/PMS/calendar/spend, workload theo effort/availability và Gantt/portfolio nâng cao (My Work/Team Board/WIP cơ bản đã ở P0), referral nhẹ,')

# Existing module touchpoints must use the same task identity.
replace('#### 3.8.2 FR21 Phân quyền hai chi nhánh', '**Bổ sung Work Management 1.7:** M14 quản authority giao việc/duyệt/ủy nhiệm theo 6.6, không coi membership hoặc chức danh cấp trên là quyền xem mọi private/client task. Offboarding phải chuyển cả task đang mở, assignment offer, review đang chờ, queue manager và owner của template/recurrence; không chỉ chuyển lead/deal. Lịch sử actor giữ nguyên; thiếu người nhận thì queue quản lý chịu trách nhiệm.\n\n#### 3.8.2 FR21 Phân quyền hai chi nhánh')
replace('### 3.14 ', '### 3.14 ') if '### 3.14 ' in s else None

core = '<a id="work-core"></a>\n### 3.14 Hợp đồng nghiệp vụ Task Core dùng chung — FR25/M16\n\n'
core += 'CR-WORK-20261016: các quy tắc sau đã hợp nhất thành baseline thiết kế 1.7. Tham số vận hành chưa chốt quản tại A.6; không phải các tính năng đã code/test. Nguồn và lý do thiết kế tại Phụ lục H.\n\n'
core += 'M02/M03/M04/M11 tạo hoặc liên kết Task Core bằng source event/business key; không giữ bản Task thứ hai. Activities giữ sự kiện đã xảy ra, Task giữ việc cần làm; cùng xuất hiện trong My Work dưới projection có loại nguồn. Đánh dấu Task Done không tự dừng request SLA, đóng Ticket hay phát client acceptance; dùng evidence/response targets theo nghiệp vụ nguồn.\n\n'
for name,title in [('B.1.','#### 3.14.1 Cấu trúc tổ chức và phân loại việc'),('B.3.','#### 3.14.2 Lifecycle, assignment và business rules'),('B.6.','#### 3.14.3 Danh mục chức năng WF01–14 và ưu tiên'),('B.7.','#### 3.14.4 Dữ liệu và giao diện'),('B.11.','#### 3.14.5 Sơ đồ Task Core'),('B.12.','#### 3.14.6 Kịch bản xuyên phòng ban')]:
    core += retitle(name,title) + '\n\n'
core = core.replace('P0 nếu có việc tuần/tháng', 'P0 calendar recurrence cơ bản')
core = core.replace('P0 ở đây là đề xuất cho **release Work Management**, không tự thay P0 ngân sách và lịch 90 ngày hiện hành. Nếu nguồn lực hạn chế, pilot WF01–07 trước; WF08–09 phải khóa khỏi UI khi chưa triển khai, không giả đã có.', 'WF01–09 là P0 của miền Work Management đã tích hợp. Pilot có thể triển khai WF01–07 trước rồi WF08–09, nhưng chưa hoàn tất scope thì không tuyên bố đạt toàn bộ P0. Nếu nguồn lực không đủ, điều chỉnh release scope/lịch có quyết định; không tự giữ cam kết 90 ngày mà tăng việc. WF10–12 P1 và WF13–14 P2. Calendar recurrence cơ bản P0; completion-based recurrence và catch-up nâng cao P1, guards vẫn bắt buộc khi bật.')
before_anchor('chuong-4', core)

uc = '### 4.23 UC-W01–10 — Luồng quản lý công việc dùng chung\n\nMã UC-W01–10 là mã canonical mới của Master, giữ UC01–22 nguyên trạng. Quy tắc tại 3.14, quyền 6.6, API 5.20 và UAT 9.16.\n\n'
uc += retitle('B.4.','#### 4.23.1 Tổng quan use case') + '\n\n' + retitle('B.5.','#### 4.23.2 Luồng chính, rẽ nhánh và ngoại lệ')
before_anchor('chuong-5',uc)

data = retitle('B.8.','### 5.20 Schema và API Work Management — FR25')
data += '\n\n**Quyết định vật lý:** PostgreSQL theo 5.1 là DB thiết kế ban đầu; 5.20 là hợp đồng logical để lập migration, chưa là DDL đã chạy. Tất cả bảng có id UUID, tenant_id/workspace_id, created_at và scoped FK theo 5.1; bảng mutable có row_version. Assignment history là nguồn; assignee/queue hiện tại trên Tasks nếu có chỉ là projection được cập nhật trong cùng transaction. Draft có thể chưa có active assignment; việc OPEN phải có assignee hoặc queue chịu trách nhiệm.\n\n**Migration:** kiểm kê task/next action/reminder cũ và task bên PMS; map source_id→task_id có unique key, dry-run count/status/owner/due/ACL; giữ original_created_at và nguồn; không replay notification/recurrence lịch sử. Freeze nguồn cũ khi cutover, đối soát delta, checkpoint và orphan tasks; rollback app không được xóa tác vụ mới, cần reconcile trước trả nguồn ghi cũ. Việc CRM chưa đủ dữ liệu giữ queue làm rõ, không tạo hợp đồng giả.\n'
before_anchor('chuong-6',data)

before_anchor('chuong-7', retitle('B.2.','### 6.6 Quyền và trách nhiệm quản lý công việc'))
before_anchor('chuong-8', retitle('B.10.','### 7.7 NFR và vận hành Task Core'))
before_anchor('chuong-9', retitle('B.9.','### 8.5 Capacity và KPI quản lý công việc'))

tests = '### 9.16 Nghiệm thu Work Management và rollout 1.7\n\nCR-WORK-20261016 thêm scope nghiệp vụ, không xác nhận ngân sách/effort hoặc go-live. Trình tự: pilot cá nhân → một team có reviewer → nhiều team/dự án; lựa chọn nguồn ghi CRM/PMS phải xong trước migration. NFR theo 7.7, cấu hình còn mở tại A.6. Các ca dưới là yêu cầu kiểm thử, chưa có kết quả Pass.\n\n'
for name,title in [('C.1.','#### 9.16.1 Bộ test W-T01–40'),('C.2.','#### 9.16.2 Rủi ro và kiểm soát'),('C.3.','#### 9.16.3 Definition of Ready / Done'),('C.4.','#### 9.16.4 Truy vết chức năng')]:
    tests += retitle(name,title) + '\n\n'
tests += '**Đào tạo và rollout:** nhân viên thực hành create/accept/block/submit, trưởng nhóm thực hành queue/change request/review/offboarding; dùng dữ liệu giả có hai workspace để kiểm scope. Pilot WF01–07 trước, bổ sung WF08–09 trong release P0; estimate/timesheet/Gantt chỉ bật P1 khi có owner dữ liệu. API sync/capacity nâng cao N/A có lý do nếu chưa bật; các guard quyền/version/idempotency không được miễn. Bổ sung công việc này vào gate 9.1/9.5, lập lại estimate trước cam kết thời hạn.\n'
before_anchor('chuong-10',tests)

decisions = '''### A.7 Quyết định và tham số Work Management 1.7

CR-WORK-20261016 đã hợp nhất phạm vi và quy tắc theo yêu cầu chủ dự án. Mặc định thiết kế: CRM Task Core làm nguồn ghi pilot; một owner + collaborators; offer/accept cho việc giao, personal autoaccepted; review theo task type; delegated due change cần authority; private scope không tự mở cho cấp trên; chỉ deliverable/task publish mới tới khách; calendar recurrence cơ bản; WIP ở P0, effort/capacity chi tiết P1.

| ID | Tham số còn cần cấu hình trước bật | Khi thiếu / owner |
| --- | --- | --- |
| W-O01 | Team queue manager, offer timeout, escalation recipient và lịch | Không activate queue/offer automation khi thiếu quản lý; việc cá nhân vẫn dùng; Ops |
| W-O02 | Task type cần review, reviewer/backup và review due | Không phát hành loại có review nếu không có reviewer hợp lệ; simple task không review hiển thị rõ; Team Lead |
| W-O03 | Calendar/timezone, quiet hours và reminder | Lưu UTC, business timezone Asia/Ho_Chi_Minh; chưa có lịch được duyệt thì không tự áp business-day rules; Ops |
| W-O04 | Personal visibility, retention, client publish | Private mặc định, không cấp quyền theo cấp trên; không tự publish; owner/privacy |
| W-O05 | Nguồn task từng project và connector authority | Mặc định CRM; PMS chưa verified không nhận là đã sync; technical owner/PM |
| W-O06 | Capacity, estimate/time entry policy | WIP có type; thiếu estimate/availability hiện Unknown, không auto-route bằng giờ; PM |
| W-O07 | License/chi phí, nhân lực và lịch release | Chưa có dự toán thì không hứa đủ P0 mới trong 90 ngày; chủ dự án |

Đây là tham số cấu hình, không trì hoãn viết schema/use case hoặc yêu cầu đọc báo cáo riêng. Tất cả default và policy override phải có version/effective date và authority; hướng dẫn cấu hình không được vượt guard của Master.
'''
before_anchor('phu-luc-b', decisions)

sources = '\n\n<a id="phu-luc-h"></a>\n## PHỤ LỤC H NGHIÊN CỨU GIAO VIỆC VÀ QUYẾT ĐỊNH HỢP NHẤT 1.7\n\n'
sources += 'CR-WORK-20261016, ngày 16/10/2026: chủ dự án yêu cầu hợp nhất vào Master. Nội dung normative đã nằm trong 3.14/4.23/5.20/6.6/7.7/8.5/9.16/A.7; phụ lục này lưu bằng chứng và tiêu chí chọn engine. Báo cáo nghiên cứu riêng không là baseline thứ hai. Nguồn là tài liệu công khai, chưa đăng nhập demo/benchmark/PoC; chưa xác nhận edition, giá hoặc API thực tế của doanh nghiệp.\n\n'
for n in range(2,10):
    sources += retitle(f'A.{n}.',f'### H.{n-1} ' + section(f'A.{n}.').splitlines()[0].split('. ',1)[1]) + '\n\n'
sources += retitle('B.14.','### H.9 PoC và quyết định build/buy') + '\n\n'
sources += retitle('Danh mục nguồn và mức chắc chắn','### H.10 Danh mục nguồn và giới hạn xác minh')
sources = sources.replace('**Kết luận bàn giao:** đã có cơ sở nghiệp vụ để review một Task Core dùng chung và lập backlog. Chưa có căn cứ để khẳng định vendor nào thắng PoC, tổng chi phí cụ thể, lịch triển khai chắc chắn hoặc các kiểm thử đã chạy đạt. Bước baseline tiếp theo là chốt các quyết định tại B.13 rồi hợp nhất thay đổi vào Master theo một CR có tác động phạm vi/ngân sách.', '**Trạng thái bàn giao 1.7:** Task Core đã hợp nhất vào phần thân Master. Chưa chọn vendor qua PoC hoặc có UAT đã chạy. Các tham số cấu hình và ngân sách/lịch còn mở tại A.7; baseline không yêu cầu đọc báo cáo nguồn mới hiểu chức năng.')
s += sources + '\n'

# Sanity checks before writing.
for marker in ['### 3.14 ', '### 4.23 ', '### 5.20 ', '### 6.6 ', '### 7.7 ', '### 8.5 ', '### 9.16 ', '### A.7 ']:
    assert s.count(marker) == 1, marker
assert len(re.findall(r'^\| W-T\d{2} \|', s, re.M)) == 40
assert len(re.findall(r'^\| UC-W\d{2} ', s, re.M)) == 10
assert 'task/capacity chi tiết P1' not in s
assert 'Bắt buộc contract/SOW/handoff link' not in s
assert len(re.findall(r'^```',s,re.M)) % 2 == 0
archive = root / 'docs/archive/CRM_MASTER_v1.6_BEFORE_WORK_2026-10-16.md'
assert not archive.exists(), 'Archive already exists; inspect before overwriting.'
archive.write_text(original,encoding='utf-8')
master.write_text(s,encoding='utf-8')
status = '**Trạng thái cập nhật 16/10/2026:** theo yêu cầu chủ dự án, các đề xuất Task Core đã được hợp nhất vào Master 1.7 (3.14/4.23/5.20/6.6/7.7/8.5/9.16/A.7 và Phụ lục H). Báo cáo này giữ nội dung nghiên cứu tại thời điểm lập; câu chữ đề xuất/“chưa sửa Master” bên dưới là lịch sử, không thay trạng thái hiện hành. Master là nguồn chuẩn.\n\n'
r = r.replace('## Kết luận điều hành',status+'## Kết luận điều hành',1)
r = r.replace('**Chưa sửa Master trong lượt nghiên cứu này:** báo cáo đưa ra thay đổi phạm vi đáng kể so với P0 hiện hành; giữ đề xuất và tác động minh bạch để không biến nghiên cứu thành cam kết triển khai đã chốt.', '**Đã hợp nhất theo yêu cầu tiếp theo của chủ dự án:** xem Master 1.7. Phạm vi thiết kế đã cập nhật; ngân sách/lịch/UAT vẫn có gate riêng, không mặc định được duyệt cùng việc cập nhật tài liệu.')
report.write_text(r,encoding='utf-8')
print(f'Integrated Master 1.7: {len(s.splitlines())} lines; 10 UC-W; 40 W-T scenarios. Prior Master archived. Research status updated.')
