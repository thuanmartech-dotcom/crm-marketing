# Lộ trình theo lát cắt và exit gate

Đề xuất, chưa là ngân sách/lịch được duyệt. Master 1.8 vẫn giữ scope P0 toàn CRM; SL01 chỉ là bước triển khai kiểm chứng. Không dùng các mã S01 trong nguồn làm slice ID.

## Cập nhật ưu tiên18/10/2026 — M21

Lead B2C công ty chưa chuyển đổi vẫn ưu tiên intake/routing/follow-up. Đơn đối tác không đưa vào phễu công ty. Sau foundation, SL08 NONE/SUMMARY/FILE có thể làm sớm cùng kế hoạch nghiệp vụ; API_READ chỉ sau quyền/PoC. Số SL08 là ID ổn định, không là cam kết thứ tự. SL01 là nền task/review và exception, không cần hoàn tất toàn bộ Work trước báo cáo đối tác; không hoãn Work P0 rồi tuyên bố hoàn tất scope. Retail OMS/inventory không chuyển thành P0 chỉ vì đối tác có nhiều đơn.

## So sánh hai pilot

| Tiêu chí | Giao việc nội bộ → review → Done | Intake/inbox → assigned task |
|---|---|---|
| Giá trị | Kiểm trách nhiệm, quyền và chất lượng đầu ra | Kiểm chống bỏ sót yêu cầu khách |
| Phụ thuộc | M14/M16/M20 + outbox tối thiểu | Thêm M01/M03/M19, source mapping và tài khoản kênh |
| Khả năng chạy ban đầu | Fixture nội bộ, không provider | Mock chạy được; live cần capability/account verified |
| Rủi ro phát hiện | Double claim, stale review, private leak, retry notification | Identity sai, ACK mất dữ liệu, event replay, gửi trùng |
| Giới hạn | Chưa chứng minh CRM từ lead đến cash | Nhiều quyết định provider và send policy hơn |
| Đề nghị | SL01 trước vì Task Core vừa hợp nhất và thiếu account live | SL02 ngay sau nền; không đợi finance hoàn chỉnh |

Chọn SL01 là quyết định thiết kế đề xuất dựa trên dữ kiện còn thiếu, không khẳng định người dùng ưu tiên nội bộ hơn bán hàng. Nếu chủ dự án cung cấp kênh và ưu tiên inbox, đảo SL01/SL02 sau khi giữ foundation và controls; không phải thiết kế lại các module.

## Các mốc

| Slice | Kết quả sử dụng | Dữ liệu/migration chính cần thiết kế | Mock/flag | Gate |
|---|---|---|---|---|
| SL00 | Login/scope/grants/audit; repo chạy và kiểm được | Tenants/Workspaces/principal/membership/grants/audit/outbox | Dữ liệu giả 2 tenant, 2 workspace | Runtime roles, fail-closed, CI, clean install/upgrade |
| SL01 | Giao/nhận việc, My Work, nộp và duyệt | Task/assignment/submission/review/events; indexes/constraints tại spec | Notification sink; live external off | CAS/idempotency/revoke/private/review và UAT flow |
| SL02 | Một nguồn tạo request/task, một kênh nhận/trả lời được phép | Connection/events/identity/thread/message/source links/intent/attempt | Mock đầy đủ trước; real adapter enable riêng | Durable ACK, source dedup, unknown outcome, account proof |
| SL03 | Lead/deal, follow-up và lịch đơn giản | Lead/deal/stage/activities, linked task, booking khi bật | Không resource engine nếu chưa dùng | UC01–03, scope, handoff, next action |
| SL04 | Quote/SOW→contract→delivery→acceptance/ticket | Revisions/approval/order/project/deliverable/acceptance/service | Policy thiếu giữ pending; không fake paid | UC05/06/08/09; client authority/version, recovery |
| SL05 | Receipt thủ công→allocation→reconcile; payout có điều kiện | Obligation/evidence/allocation/refund/period/commission khi bật | Bank/ERP fake fixtures, live off | Replay tiền, rounding, period close, refund concurrency |
| SL06 | Hoàn thiện Work P0 và automation cơ bản | Checklist/hierarchy/dependency/recurrence/change request | Timer chỉ Active khi lịch/manager đủ | W-F01–09 đủ phạm vi, graph race, restart scheduler |
| SL07 | Mở rộng có căn cứ | Capacity, thêm kênh, BI nâng cao, AI/referral/loyalty theo scope | Per-capability flags | Dependency closure + owner + budget + tests áp dụng |
| SL08 | Đối tác NONE/SUMMARY/FILE vẫn quản dịch vụ và báo cáo đúng giới hạn; API theo cấp quyền | Profile/binding/observations/batches/datasets/reconciliation/reports, scoped grants | API/detail off core; file/summary fixture sạch | P-T core, source overlap/correction/ACL/restore; P-NFR theo mode; gap A.8 |

SL06 cần hoàn tất các phần W-F01–09 chưa có trong SL01 trước tuyên bố đạt Work P0. Basic audit/metrics, quyền và retention có từ SL00/01, không đợi SL07. Những bảng ở roadmap là logical dependency, chưa phê duyệt SQL migration.

## Gate nhất quán

- Checkpoint: lưu tiến độ và phần chưa đạt; không gắn nhãn release-ready.
- Merge: lint/typecheck khi stack hỗ trợ, boundary, unit/integration thay đổi, migration và regression bị ảnh hưởng.
- Enable: physical schema/contract, policy, actor/owner, capability và test profile đủ; không có lối vòng qua API/job/flag.
- Release: controls tiền/quyền/consent/SLA tương ứng đạt; UAT, backup/restore, runbook, alert owner và bằng chứng môi trường đại diện.

Status test: Pass/Fail/Not Run/Blocked/Not Applicable. Capability có thể Deferred; test N/A cần applicability false có evidence. Spec chưa có code thì mọi test ở trạng thái Not Run, không ghi Pass vì đã có expected result.

## Bổ sung Đề xuất Mở rộng (`M18+`, `M23`, `M24`) theo Lát cắt `SL00–SL07`

Các hạng mục dưới đây dẫn xuất từ phiên `/grill-me` (15/11/2026), **không thay đổi tên hay thứ tự mã `SL00–SL11`**:

| Slice | Hạng mục bổ sung đề xuất | Mục tiêu đồng bộ |
|---|---|---|
| `SL00` | `M23-F01/02/05/06/09/10` + `M24-F06/07` nền | Khóa MFA/Session, Pilot↔Team Maker–Checker, Immutable Audit, Feature Flags, Lịch chuẩn/Quiet Hours, Permission Cache & 3 làn Queue |
| `SL01–SL03` | `M23-F03/11/12` + `M24-F01/02/04/05` + `M18-F11` (nền) | Break-glass TTL sang `M14`, Danh mục/Mẫu dùng chung, Outbox/DLQ nội bộ, `Ctrl+K`, Split-View, Quick Replies, Smart Digest, Data Quality Cockpit |
| `SL04–SL06` | `M23-F04/07` + `M24-F03/08` + `M18-F11` (đầy đủ) | Approval Matrix cho Quote/Budget/Commission, Export 2 lớp & Watermark, Bulk Actions dry-run, Async Export Pipeline |
| `SL07` | `M18-F08–10` + `M23-F08` + `M24-F08` (Archiving) | P&L hợp nhất (`M09+M17+M10+M22`), Ad-hoc Builder, Scheduled Delivery, Cảnh báo bất thường/DLP và Lifecycle Archiving/Partitioning |

## Bổ sung HRM — CR-HRM-20261018

| Slice | Kết quả | Gate |
|---|---|---|
| SL09 / HR-A | Hồ sơ/hợp đồng/phép/công cơ bản/tự phục vụ/nhận-nghỉ việc và chuyển Excel | Policy, quyền, dữ liệu đối soát, UAT-A và restore/cutover |
| SL10 / HR-B | Ca nâng cao, sửa công/OT, thiết bị nếu có | UAT-B/ca đêm/offline/dedupe; không có thiết bị vẫn dùng file |
| SL11 / HR-C | INTERNAL hoặc EXTERNAL payroll, commission route, phiếu và chi có duyệt | Hai kỳ đối chiếu, UAT-C, maker/checker; bank API gate riêng |

Đọc [đặc tả slice](../02-specs/slices/SL09-11-HRM.md). Đây là thứ tự trong miền HR; chưa cam kết ngân sách/ngày phát hành và không tự thay ưu tiên pilot M21. Ước lượng lại chi phí theo Master A.9 trước cam kết rollout.
