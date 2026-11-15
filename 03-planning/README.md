# Phân rã CRM — đợt đầu

Trạng thái: đã lập bộ chuẩn bị triển khai để review; chưa viết ứng dụng. Cập nhật 18/10/2026 (M21 và M22 hợp nhất vào Master 1.9); cập nhật cấu trúc 15/11/2026 (chuẩn hóa cây thư mục `00-master/` → `99-archive/`, giữ nguyên Master 1.9).

Baseline duy nhất: [Master 1.9](../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md), 4,861 dòng. SHA-256: `b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`. Các tài liệu dưới đây dẫn xuất hoặc đề xuất từ baseline; không thay thế Master và không tự phê duyệt chính sách doanh nghiệp.

## Đường đọc đề nghị

1. [Khoảng trống và kết quả kiểm kê](GAPS.md): điều gì đã biết, điều gì chưa được phép suy.
2. [Ownership và ba đồ thị phụ thuộc](../01-architecture/INDEX.md): 22 module, vai trò core/gói ngành, chiều phụ thuộc.
3. [Bất biến xuyên domain](../01-architecture/INVARIANTS.md): context nền cho mọi slice.
4. [Roadmap và quyết định pilot](ROADMAP.md): so sánh hai lựa chọn và exit gates.
5. [SL01 — Giao việc nội bộ đến duyệt kết quả](../02-specs/slices/SL01-INTERNAL-WORK.md): pilot đề xuất đủ để review thiết kế; chưa Ready for implementation vô điều kiện.
6. [Mẫu module spec](../02-specs/templates/MODULE-SPEC.md), [mẫu contract](../02-specs/templates/CONTRACT.md), [manifest đang hoạt động](agent/active-task.json), [tiến độ](agent/PROGRESS.md).
7. [ADR nguồn chuẩn và stack](../01-architecture/decisions/ADR-001-BASELINE-AND-STACK.md).

8. [M21 — Kết quả kinh doanh đối tác](../02-specs/modules/M21-PARTNER-BUSINESS-RESULTS.md): 14 chức năng, 10 UC, 20 rules, 40 tests, data/API/quyền/NFR/KPI.
9. [SL08 — Pilot kết quả đối tác](../02-specs/slices/SL08-PARTNER-RESULTS.md): NONE/SUMMARY/FILE trước API.

10. [M22 — Quản trị nhân sự](../02-specs/modules/M22-HUMAN-RESOURCES.md): đặc tả đầy đủ HR-A/B/C, migration Excel và 48 ca UAT.
11. [SL09–11 — Lộ trình HRM](../02-specs/slices/SL09-11-HRM.md): pilot và gates công/lương.
12. [Danh mục 224 chức năng (`M01–M24`)](../02-specs/FUNCTION-CATALOG.md): 200 chức năng Baseline v1.9 + 24 chức năng đề xuất mở rộng tại [M23](../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), [M18+](../02-specs/modules/M18-BI-REPORTING-EXPANSION.md) và [M24](../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md).
13. [Kế hoạch Ưu tiên Bóc tách Đặc tả (`Wave 1 -> Wave 6`)](DECOMPOSITION-PLAN.md): thứ tự 24 module theo đồ thị phụ thuộc (`M14 -> M20 -> M19 -> M16...`), `public contracts/` cần khóa và DoD từng Wave *(chờ lệnh khởi chạy)*.

## Registry máy đọc được

- [M22 feature trace](trace/hrm-trace.json): chức năng→UC/rule/test từ Master.
- [M21 feature trace](trace/partner-results-trace.json): mapping feature→UC/rule/test có review.
- [Requirements](trace/requirements.json): ID, vị trí nguồn/hash, owner hoặc gap, consumer candidates, slice candidate, priority, applicability, tests và evidence.
- [Coverage CSV](trace/coverage.csv): bản xem gọn; JSON mới giữ đầy đủ occurrences và giới hạn suy luận.
- [22 module](trace/modules.json): trích danh mục 3.0, gồm người dùng, dữ liệu sở hữu và priority nguyên văn.
- [Entity/contract declarations](trace/entities-contracts.json): giữ nhóm tên và alias nguồn, chưa giả lập schema vật lý hoàn chỉnh.
- [Quy tắc chưa có mã](trace/unnumbered-rules.json): ứng viên theo câu chữ, gồm cả đoạn lịch sử cần phân loại.
- [Findings](trace/findings.json): trùng ứng viên định nghĩa, reference-only, owner/test link chưa xác lập và shorthand.
- [Mục nguồn](trace/source-sections.json): chỉ mục heading/line cho toàn Master.
- [Bằng chứng kiểm inventory](evidence/inventory-validation.json): số lượng và kết quả kiểm cấu trúc, không phải test CRM.

SL01/SL02 là mã slice mới, tránh dùng S01/S02 vốn là mã nguồn tham khảo trong Master. ENTITY-L/CONTRACT-L/UNNUMBERED-L là ID dẫn xuất gắn hash/line, không được thay ID nghiệp vụ trong Master. Khi Master đổi hash phải chạy lại và review diff; số dòng không phải định danh ổn định xuyên phiên bản.

## Tái chạy

Từ workspace `D:\AI Agent\CRM`, chạy:

```powershell
python 05-tools/build_delivery_inventory.py
python 05-tools/verify_delivery_plan.py
python 05-tools/verify_hrm_integration.py
```

Builder chỉ cập nhật các file registry/evidence do nó sinh, không sửa Master hoặc các quyết định thủ công. Sửa owner/trace lâu dài cần cập nhật mapping builder hoặc tạo lớp override versioned; không sửa JSON generated rồi kỳ vọng tồn tại qua lần chạy sau. Parser không chứng minh coverage ngữ nghĩa 100%.

Đợt đầu chỉ có map20 module; cập nhật1.8 có M21/SL08; cập nhật1.9 thêm M22/SL09–11. 20 module cũ chưa tách toàn văn. Chưa tạo DDL/code ứng dụng hoặc bật integration. Các việc đó nằm sau gate chọn phạm vi/stack/schema.
