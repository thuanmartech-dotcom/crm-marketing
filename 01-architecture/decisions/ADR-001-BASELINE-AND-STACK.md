# ADR-001 — Nguồn chuẩn, cách phân rã và lựa chọn stack

Status: Proposed; baseline nghiệp vụ 1.9 được kế thừa, quyết định triển khai chưa phê duyệt. Không đồng nghĩa chủ dự án đã chọn tự xây toàn bộ.

## Context

Workspace đang chứa tài liệu, script tạo tài liệu và bản tham khảo; lượt rà không thấy package.json/pyproject/go.mod/csproj hay AGENTS.md. Master 2.8 có stack tham chiếu TypeScript/React/NestJS/PostgreSQL; 1.6 và Chương 10 vẫn cho phép configure/hybrid theo PoC/ngân sách.

## Đề nghị

Giữ Master là nguồn nghiệp vụ; registry/spec slice là dẫn xuất có hash, gap và evidence. Giữ Modular Monolith/PostgreSQL định hướng; một repo khi self-build, boundary public API/ports; chưa chia service. Đơn vị thực hiện là slice nhỏ, ownership theo 22 module.

Nếu tự xây, dùng stack tham chiếu làm ứng viên đầu tiên để giảm số ngôn ngữ; chỉ pin framework/auth/ORM/queue versions sau khảo sát repo, năng lực người bảo trì và spike có migration/RLS/concurrency. Không cần Redis/Kafka/microfrontend ngay. Nếu chọn CRM nền tảng, map logical entities/commands sang capability nền tảng và giữ cùng test gate.

## So sánh

- Self-build: kiểm soát semantics sâu; phải chịu chi phí auth, migration, operations và bảo trì.
- Configure/hybrid: có thể có UI/permissions sẵn; cần PoC extension/ACL/source-of-truth, không giả nền tảng đáp ứng toàn Master.
- Stack khác đội đã biết: có lợi nếu người bảo trì thành thạo; cần chứng minh concurrency/runtime validation/observability tương đương, không chọn chỉ theo tên công cụ AI.

## Hệ quả và điều kiện thay đổi

Đợt này chưa có lệnh npm/test app để chạy và chưa được coi Ready for code. Khi chủ dự án chốt cách triển khai, tạo ADR tiếp theo cho stack/versions và physical SL01 contract. Có thể đổi thứ tự pilot nếu account/kênh và ưu tiên sử dụng thay đổi; không bỏ source trace hoặc invariant.
