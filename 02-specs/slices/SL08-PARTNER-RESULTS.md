# SL08 — Kết quả đối tác, core theo mức chia sẻ

Baseline Master1.8; CR-PARTNER-RESULTS-20261018. Spec chi tiết: [M21](../modules/M21-PARTNER-BUSINESS-RESULTS.md). SL08 là ID ổn định mới, không nghĩa phải chờ SL07 mới làm. Có thể triển khai sau foundation quyền/metrics/assets tối thiểu và phối hợp lead B2C M02; không cần hoàn thành toàn bộ agency trước.

## Mục tiêu và giới hạn release

AM quản lý dịch vụ đối tác dù họ không cấp API; khi có summary/file hợp lệ thì đối soát và phát hành báo cáo có provenance/coverage. Pancake/đối tác giữ vận hành đơn. Release core gồm M21-F01–05/07–10/13–14 theo chế độ; F12 chỉ khi exception rule bật. API_READ F06 và order drill-down F11 chưa bật cho đến PoC/CR đủ controls.

NONE active không cần credential, metric value hoặc buyer PII. SUMMARY cần metric basis/người xác nhận. FILE cần thêm template/mapping/scan/precedence và atomic publish. Không xây dummy connector để làm UI hiện Active. API không được bật qua direct job hoặc endpoint dù giao diện ẩn.

## Hai flow UAT đầu tiên

1. Đối tác A chọn NONE: tạo profile → AM quản task/hợp đồng/lead công ty như thường → báo cáo có work evidence và “chưa có dữ liệu bán hàng” → không tính ROAS/conversion outcome. Không gắn partner-reported/verified khi chưa có observation.
2. Đối tác B chia summary rồi file: cấu hình scope/kỳ/basis → summary staged/confirmed → import file dry-run → thấy overlap → reviewer chọn một dataset theo policy → publish snapshot → file correction mới không làm thay bản đã phát hành → revoke recipient chặn tải mới.

User roles: AM, analyst/importer, reviewer/report approver, partner reporter và service principal; test 2 CLIENT workspace cùng tenant và một tenant khác. PII không cần cho core. Nguồn cấp file có quyền phải được ghi; fixture dev không chứa người thật.

## Data/API scope

Profile/binding, observation, batch/errors, dataset version, reconciliation/report snapshot và audit/outbox đủ cho summary-file. Order projection/crosswalk chỉ cần nếu nhận detail; FILE summary không bắt tạo order tables. Schema API cụ thể theo5.21 phải được Tech/BA review thành OpenAPI/DDL trước code. Không tự mở FK tới module chưa có bảng; chọn dependency thật hoặc khóa feature.

Mock: source adapter đọc fixture sạch; notification sink; current-grant resolver fake có revoke, không hardcoded always-allow. API provider off. Commit và publish phải test với DB thật dưới runtime role khi có implementation.

## Gate / readiness

Trước code: source profile/metric fields/currency/timezone/tolerance, reviewer/retention/audience và stack rõ cho mode đang làm; review mô hình immutable dataset và source precedence. Không cần tài khoản Pancake để bắt đầu NONE/SUMMARY/FILE; thiếu API chỉ chặn API.

Trước enable: P-T core và format đã bật chạy đạt; ACL/count/file/export; zero/unavailable, overlap/correction và restore được đối chiếu. P-NFR áp dụng được đo với build/dataset/machine rõ. UAT AM/partner đại diện xác nhận màn hình không gây hiểu nhầm. Những test API/detail chưa bật có applicability false cần evidence, chưa có code hiện vẫn Not Run.

## Vận hành và đào tạo

AM thực hành chọn mode đúng thỏa thuận, đọc unavailable khác0 và nhận biết số liệu tự khai. Analyst thực hành dry-run, sửa lỗi file, chọn nguồn/đối soát; reviewer thực hành correction và publish caveat. Ops thực hành pause profile, replay batch sau crash, kiểm watermark và escalation owner.

Runbook ngắn: ingest lỗi → xác định scope/batch/grant → dừng source lỗi, giữ báo cáo cũ có stale label → sửa template/authorization có review → dry-run/reconcile → commit version mới → publish correction khi cần. Không sửa giá trị report đã gửi để che lỗi. Khi revoke: chặn access/fetch/commit mới trước, sau đó cleanup theo retention/hold; không đợi purge xong mới thu hồi quyền.

Rollback: tắt API/sync hoặc mode gặp lỗi bằng policy version, giữ audit/dataset, quay về file/summary chỉ khi được phép và source precedence rõ. Restore drill kiểm deletion/grant ledger và hashes, không tái kích hoạt token cũ. Rủi ro sai khách/sai số tiền/giả verification là no-go của capability liên quan.

Trạng thái: spec hoàn tất cho review thiết kế; chưa có application/migration/UAT đã chạy. Fixtures ở ../../03-planning/evidence/partner-results-fixture.json là oracle thiết kế, không là data của đối tác hoặc chứng nhận API.
