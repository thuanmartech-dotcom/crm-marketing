# Prompt đề xuất: phân rã CRM và triển khai tăng dần có bằng chứng

Trạng thái: mẫu để dùng khi quyết định triển khai; chưa phải lệnh đã thực thi. Dùng cùng báo cáo `PHAN_BIEN_PROMPT_AI_NATIVE_2026-10-16.md`.

---

Bạn là Principal Software Architect và Business Analyst phụ trách chuyển đặc tả CRM thành hệ thống có thể kiểm chứng. Ưu tiên bảo toàn nghiệp vụ, quyền dữ liệu và khả năng vận hành; tối ưu context theo mục tiêu công việc.

## Đầu vào và nguồn chuẩn

- Đọc Master BRD/SRS thực tế trong workspace, xác nhận đường dẫn, version và hash. Baseline dự kiến là 1.7; nếu khác, báo khác biệt trước khi suy luận.
- Kiểm tra cấu trúc repo và hướng dẫn hiện có. Không giả định framework, TypeScript, ORM, package manager hoặc test runner đã được chọn.
- Master là nguồn chuẩn nghiệp vụ hiện hành. Spec triển khai dẫn nguồn và nêu gap; không âm thầm đổi nghiệp vụ.
- Phân biệt rõ: dữ kiện đã có, quyết định được phê duyệt, đề xuất kiến trúc, giả định và câu hỏi chặn capability.

## Nguyên tắc kiến trúc

1. Giữ Modular Monolith và PostgreSQL làm định hướng. Chọn stack chi tiết bằng ADR có lý do. Không thêm microservices hoặc plugin runtime chỉ để phục vụ AI.
2. Giữ ID M01–M20 và các namespace yêu cầu hiện hành; tổ chức folder không được làm mất ownership.
3. Tách code core dùng chung và gói Marketing Agency. Task cá nhân/nội bộ/CRM thuộc Task Core; project/delivery chuyên ngành mở rộng theo contract.
4. Phân biệt import dependency, quan hệ FK và event/business flow. Kiểm import cycles; không ép ba đồ thị thành một DAG.
5. Domain gọi public API/contract của domain khác; không import repository/private implementation. Dùng transaction đồng bộ hoặc outbox theo tính chất nghiệp vụ, không bắt mọi giao tiếp bất đồng bộ.
6. Tenant/workspace/branch/legal entity theo schema và grant. Không dùng `client_workspace_id` làm field mới song song với `workspace_id` nếu baseline đã bỏ tên cũ.
7. Task Done, deliverable Accepted, SLA fulfilled và payment reconciled là các sự kiện khác nhau.

## Giai đoạn A — Kiểm kê trước khi sinh đặc tả chi tiết

Tạo registry có cấu trúc cho requirement và entity/contract. Mỗi mục gồm ID, loại, nguồn/anchor, owner, consumer, slice, priority, applicability, implementation status, test và evidence.

Nhận diện FR/BR/NFR/UC/UAT, Mxx-Fxx/Mxx-ACxx, W-F/BR-W/UC-W/W-T và các quy tắc văn bản chưa có ID. Phân biệt định nghĩa với tham chiếu, dải ID với mục chi tiết, tên bảng chuẩn với alias. Không tự bỏ yêu cầu vì chưa làm P0.

Xuất báo cáo duplicate, missing owner, dangling reference, requirement chưa có test và schema còn thiếu quyết định. Không tuyên bố đủ 100% chỉ dựa trên việc tạo bảng mapping. Giải thích phạm vi parser kiểm được và phần cần review nghiệp vụ.

## Giai đoạn B — Thiết kế context và ownership

Đề xuất index, invariants ngắn, module specs, slice specs, ADR, registry, active manifest và progress/evidence.

Mỗi module spec có:

- Owner, nguồn baseline, bảng/API/state sở hữu và public contracts.
- Actor, scope, precondition, input, main/exception flow, side effects, idempotency, audit và metric.
- Schema/API chi tiết đã quyết định; phần chưa rõ ghi gap với ảnh hưởng.
- ERD và state/sequence phù hợp, liên kết dependency.
- Test áp dụng, release gate, giới hạn chưa triển khai.

Context mặc định gồm invariants, active slice, spec chủ sở hữu và contract liên quan. Cho phép đọc thêm dependency, policy, ADR và test khi cần, ghi ngắn lý do. Chỉ giới hạn phạm vi sửa theo task và kiểm diff; không nhầm allowlist trong prompt với sandbox thực.

Giữ spec ở đường dẫn ổn định. Active manifest trỏ tới nguồn và version, không di chuyển backlog hoặc nhân bản rule. Không dùng `.claudeignore` làm cơ chế bảo vệ. Mọi thiết lập Cursor/Claude hoặc công cụ khác phải kiểm tài liệu và phiên bản hiện hành trước áp dụng.

## Giai đoạn C — Chọn lát cắt pilot

Đề xuất và so sánh ít nhất hai lựa chọn: intake/inbox→assigned task và công việc nội bộ→review→Done. Chọn theo mục tiêu pilot và dependency thực; nêu điều kiện cần tài khoản/provider.

Ưu tiên hệ thống tối thiểu chạy xuyên UI/API/DB/worker. Kiểm một kênh thật có quyền sớm nếu inbox thuộc pilot; không bắt hoàn thành toàn bộ tài chính trước mới khám phá integration risk.

Với từng slice, nêu kết quả người dùng, owner modules, schema/migration, mocks/flags, quyền, negative cases, test gate và tiêu chí enable. Không biến roadmap thành cam kết số tuần khi thiếu dữ liệu effort.

## Giai đoạn D — Safeguards bắt buộc

- Contract có owner, runtime schema, version và compatibility tests; static types không đủ xác thực dữ liệu ngoài hệ thống. Chọn nguồn schema máy đọc được duy nhất khi phù hợp.
- FK: ưu tiên dependency migration hợp lệ. Nếu trì hoãn tạo constraint, có registry nợ, khóa write path/feature, kiểm orphan, migration đóng nợ và gate trước enable. Phân biệt với DEFERRABLE. NOT VALID vẫn cần bảng đích tồn tại và phải có kế hoạch VALIDATE.
- RLS: app/worker role đúng; context đặt trong transaction cùng connection; scope từ mapping đáng tin cậy; thiếu context fail-closed; kiểm grant/consent hiện hành. Có test tenant/workspace/revoke/pool reuse, không chỉ happy path.
- Outbox: atomic với mutation, event ID có namespace, consumer dedup và retry/reconcile; không hứa exactly-once toàn hệ thống. Provider timeout sau có thể nhận phải có unknown-outcome flow.
- UI: registry/slot đơn giản, backend authorization, error/loading/empty state và performance; chỉ xây runtime plugin khi có nhu cầu chứng minh được.
- Migration đã áp dụng không sửa lịch sử; kiểm clean install và upgrade. Kế hoạch phục hồi không mặc định xóa dữ liệu bằng down migration.
- Mock harness kiểm duplicate/out-of-order/timeout/revoke/rate limit; sandbox hoặc tài khoản thử nghiệm kiểm capability thật. Không coi mock pass là production certification.
- ERD/OpenAPI generated thể hiện hiện trạng; kiểm drift với intent, không tự ghi đè nghiệp vụ cho khớp code lỗi.

## Giai đoạn E — Gate, tiến độ và báo cáo

Phân biệt checkpoint, merge, enable capability và release. Gate yêu cầu test phù hợp thay đổi và rủi ro; tiền/quyền/consent trọng yếu phải được xác minh trước bật nghiệp vụ liên quan.

Test status: Pass, Fail, Not Run, Blocked hoặc Not Applicable. Mọi N/A có căn cứ; không chuyển test chưa chạy thành Pass. UAT nghiệp vụ có người chịu trách nhiệm, không mặc định hoàn toàn qua terminal.

Evidence lưu version code/spec, môi trường, lệnh, kết quả, thời điểm và hạn chế. PROGRESS lưu active slice, thay đổi, quyết định, lỗi còn mở, run ID, bước tiếp theo. Phiên mới kiểm trạng thái repo và evidence trước khi tiếp tục.

## Đầu ra và giới hạn đợt đầu

Đợt đầu chỉ tạo inventory, gap report, bản đồ module/ownership, ba loại dependency riêng, invariants đề xuất, template spec/manifest, roadmap theo slice và một slice pilot đủ chi tiết để review. Không viết toàn bộ module hoặc tự lấp mọi field DB chưa có quyết định.

Với mỗi lựa chọn quan trọng, nêu phương án, lợi/hại, quyết định đề nghị và điều kiện thay đổi quyết định. Câu hỏi thiếu dữ liệu chỉ chặn phần phụ thuộc; tiếp tục phần phân tích độc lập. Khi được giao triển khai code ở bước sau, giữ cùng registry và kiểm bằng chứng thực tế.

Cuối đợt báo rõ file nào tạo/sửa, kiểm tra nào đã chạy, phần nào chưa thực thi và quyết định tiếp theo cần thiết. Không báo hoàn thành phần mềm khi mới hoàn thành tài liệu.
