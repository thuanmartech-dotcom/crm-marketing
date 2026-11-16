# Context nền — bất biến CRM

Nguồn chuẩn: Master 1.8, đặc biệt 2.7–2.8, 3.0, 3.13–3.14, 5.1, 5.19–5.20, 6.1/6.5/6.6, 9.5/9.11. Đây là tóm lược có điều hướng; khi có khác biệt phải mở đúng nguồn và ghi gap.

| ID dẫn xuất | Bất biến | Áp dụng / cách kiểm |
|---|---|---|
| INV-01 | Tenant/workspace/branch/legal entity khác nhau; workspace AGENCY/CLIENT rõ | M14/M20 + mọi domain; query/command lấy scope tin cậy |
| INV-02 | Link, mention, merge và vai trò cấp trên không tự mở quyền | API/list/count/search/file/notification/export đều recheck |
| INV-03 | Một nguồn ghi cho từng thực thể/field; sync không last-write-wins tùy tiện | CRM task mặc định A.7; PMS off đến khi mapping verified |
| INV-04 | Activity là việc đã xảy ra; Task là việc cần làm; một projection không nhân bản nguồn | My Work có source type và ID |
| INV-05 | Task Done khác SLA fulfilled, client accepted và paid | W-T18 + negative integration assertions |
| INV-06 | Domain change/history/outbox nguyên tử khi cần phát event; external side effect sau commit | Fault injection trước/sau commit; consumer dedup |
| INV-07 | Webhook xác minh và ghi bền trước ACK; scope từ connection mapping | SL02 durable intake test |
| INV-08 | Unknown send outcome đối soát; không retry mù | SL02 provider accepted/response lost fixture |
| INV-09 | Mutation kiểm quyền hiện hành và expected version; create idempotent | Cùng key khác payload conflict; concurrency + revoke test |
| INV-10 | Task một assignee active; queue có manager; offer khác accepted | BR-W01; W-T03/06/29 |
| INV-11 | Submission/review theo version/hash; không sửa evidence đã duyệt | BR-W08; W-T15/16/17 |
| INV-12 | Đổi hạn/snooze/block không xóa breach hoặc tự đổi cam kết khách | BR-W03/04/05; W-T11/12/13 |
| INV-13 | FK/bridge có scope; thiếu tenant context fail-closed; runtime role không bypass ngoài thiết kế | RLS dưới app/worker role; lỗi không lộ raw DB detail |
| INV-14 | Policy có owner/version/effective date; thiếu cấu hình chặn đúng thao tác | A.6/A.7, không tạo contract/consent/paid giả |
| INV-15 | Migration đã áp dụng không sửa; rollback app không tự rollback dữ liệu | Clean install, upgrade, restore/reconcile |
| INV-16 | Spec/typecheck/mock không phải bằng chứng release; test status trung thực | 9.5 release profile; actual/build/fixture/evidence |

Core giữ chức năng dùng chung; pack không thay quyền hoặc nghiệp vụ core bằng override nạp sau. Clock lưu UTC; business timezone/calendar cấu hình, không hardcode ngày công. Không đưa nội dung nhạy cảm vào log hoặc payload notification trước kiểm recipient. RLS chỉ là một lớp: storage/search/cache vẫn cần policy tương ứng.

## Bổ sung M21 — Master3.15/5.21/6.7/8.6

| ID | Bất biến | Kiểm |
|---|---|---|
| INV-17 | NONE hợp lệ; unavailable không là0; nghiệp vụ công ty không phụ thuộc data đối tác | P-T01/07/40 |
| INV-18 | Partner order/GMV và agency lead/revenue là scope/grain khác nhau | P-T02/22/26/36 |
| INV-19 | Observation provenance/verification/coverage/freshness tách nhau; correction không sửa report đã gửi | P-T09/10/28/29 |
| INV-20 | Một effective source cho mỗi reporting partition; không sum overlap file/API/summary | P-T14/23/25 |
| INV-21 | API_READ chỉ operation đọc, current authority; không default buyer PII hoặc viết ngược POS | P-T05/06/16/17/31 |
# Bổ sung HRM — Master1.9

- M22 Employee/Employment khác User/Membership M14 và Contact M01. Thay chức danh/Employment không tự cấp quyền đọc khách hàng hoặc payroll.
- M10 là nguồn quyền hưởng hoa hồng; M22 chỉ claim route để chi qua payroll. Một khoản không đồng thời chi ở M10 và M22; Unknown phải đối soát trước retry.
- Attendance, project timesheet và performance là các dữ kiện khác nhau. Missing không là0/vắng; hồ sơ kỷ luật không tự tạo deduction.
- Locked attendance/payroll giữ snapshot; correction tạo revision/adjustment có nguồn, không sửa lịch sử chi. Exported/Published không là Paid.
- Excel cutover có source of truth và thời điểm rõ; import retry không nhân dữ liệu; payroll lịch sử không thành lệnh chuyển tiền.
- Scope bảo vệ cả trường, file, export, search và AI. Manager chỉ nhận availability cần thiết, không nhận lý do riêng tư/lương do chức danh.

## Bổ sung Đề xuất M18+, M23 & M24 (15/11/2026)

| ID | Bất biến | Áp dụng / cách kiểm |
|---|---|---|
| INV-22 | Ở chế độ `TEAM`, mọi cấp Break-glass (`M23-F03`), duyệt Export PII (`M23-F07`) và sửa Ma trận thẩm quyền (`M23-F04`) bắt buộc `Maker != Checker`; chế độ `SOLO/PILOT` phải gắn cờ tường minh, TTL ngắn và cảnh báo tức thời về Owner/CEO (`M23-F05`) | Negative self-approval test; chuyển `PILOT -> TEAM` tự khóa |
| INV-23 | Một nguồn chuẩn cho quyền, lịch và DLQ: `M14` kiểm quyền runtime (kể cả grant Break-glass từ `M23-F03`), `M23-F10` sở hữu Lịch chuẩn/Ngày lễ/`Quiet Hours` (`M22-F07` chỉ kế thừa phân ca), `M19-F07` lo adapter ngoài vs `M23-F12` lo nền tảng nội bộ | Boundary & dependency check giữa `M14/M19/M22/M23` |
| INV-24 | Mọi Export lớn hoặc báo cáo định kỳ đi qua đúng 1 chuỗi: `M18-F10` / màn hình nguồn $\rightarrow$ Duyệt 2 lớp & Watermark `M23-F07` $\rightarrow$ Chạy nền `M24-F08` $\rightarrow$ Download Gateway kiểm ACL từng request; không tạo link tải tắt | Kiểm thử bypass Gateway & revoke trước khi tải (`Chương 6.2`) |
| INV-25 | Read Model & Cache (`M24-F06`) bắt buộc gắn `permission_version` và invalidate khi revoke, không bao giờ làm nguồn ghi; Bulk Action (`M24-F03`) bắt buộc Dry-run + `expected_version` và cấm dùng cho duyệt tài chính hoặc xóa PII | Stale-cache permission revoke test; Bulk negative guard |

## Bổ sung Chuẩn Hóa Kỹ Thuật Phân Tán (`Wave 1 Review — CR-20261116-WAVE1-REVIEW-FIXES`, 16/11/2026)

| ID | Bất biến | Áp dụng / cách kiểm |
|---|---|---|
| INV-26 | Worker/Job nhả DB lock giữa các pha xử lý bắt buộc dùng `lease_token` fencing CAS ở **cả micro-commit trước tác động ngoài lẫn pha ghi kết quả cuối** (kèm hợp nhất có điều kiện theo `last_attempted_lease_token`); mọi tài liệu (`ADR`, Module, Contract) dùng chung **1 Bảng Quyết định Reaper 8 Nhánh** (`http_attempted_at IS NOT NULL` $\rightarrow$ `UNKNOWN_OUTCOME`; `IS NULL` & hết TTL $\rightarrow$ `EXPIRED_CANCELLED`; `IS NULL` & còn TTL & `allow_auto_retry=true` $\rightarrow$ `RETRY_WAITING`; `allow_auto_retry=false` $\rightarrow$ `QUEUED`; vượt `3` lần reclaim $\rightarrow$ `FAILED_TERMINAL`) | Pause worker trước micro-commit hết lease cho worker B claim rồi resume A; ma trận `http_attempted_at × TTL × allow_auto_retry` |
| INV-27 | Bảng nội dung bất biến cho phép scrub PII (`Task_Submissions`, `Messages`, `Notes`, `AI_Drafts`, v.v.) **tuyệt đối không dùng khóa 1 lần `privacy_redacted_at IS NULL`**: bắt buộc idempotency theo từng lệnh xóa (`redacted_deletion_ledger_ids uuid[]`), kiểm `cardinality(active_legal_hold_ids) = 0`, truy tìm đa nguồn (links + HMAC + nội dung), **giữ nguyên `content_sha256` gốc**, và tính riêng `redacted_content_sha256` sau scrub | Xóa chủ thể A rồi chủ thể B trên cùng 1 bản ghi; replay event nhiều lần; xóa đồng thời; giữ rồi gỡ `Legal_Hold` rồi xóa tiếp |
| INV-28 | Ma trận kiểm thử tách riêng ca hợp lệ (`200 OK`, e.g., `WithdrawSubmission`) khỏi ca xung đột/stale (`409`); cuối mỗi Wave/CR bắt buộc đồng bộ `active-task.json` (`spec_review_status`, `implementation_readiness`, `wave*_specs`) với `DECOMPOSITION-PLAN.md` và `02-specs/README.md` | Cross-doc consistency check trong `verify_module_spec.py` + đối chiếu từng lệnh trong test matrix |

