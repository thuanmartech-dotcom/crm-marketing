# Dự án Đặc tả Hệ thống CRM — Agency Marketing & Quản trị Nội bộ

Trạng thái hiện tại: **Giai đoạn Tài liệu & Brainstorm Nghiệp vụ (Documentation-Only / Pre-Code)**.  
Dự án **chưa tổ chức mã nguồn ứng dụng**, chưa khởi tạo migration DB và chưa chạy UAT phần mềm; mục tiêu hiện tại là hoàn thiện bộ tài liệu đặc tả chuẩn chỉ, đầy đủ và cô lập ngữ cảnh rõ ràng trước khi giao cho AI Agent lập trình.

---

## 1. Tài liệu chuẩn & Điểm khởi đầu

- **Nguồn chuẩn nghiệp vụ duy nhất (Baseline v1.9):** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (4.861 dòng, cập nhật 18/10/2026).
- **Quy chuẩn làm việc cho AI Agent (bắt buộc đọc):** [AGENTS.md](AGENTS.md).
- **Danh mục 200 chức năng & Sơ đồ luồng (`M01–M22`):** [02-specs/FUNCTION-CATALOG.md](02-specs/FUNCTION-CATALOG.md).
- **Tổng quan kế hoạch triển khai & kiểm kê:** [03-planning/README.md](03-planning/README.md).

---

## 2. Cấu trúc thư mục dự án

| Thư mục | Vai trò | Nội dung chính |
|---|---|---|
| [`00-master/`](00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) | Tài liệu chuẩn duy nhất | Master BRD & SRS v1.9 (nguồn gốc cho mọi truy vết yêu cầu). |
| [`01-architecture/`](01-architecture/INDEX.md) | Kiến trúc & Bất biến | Ownership 22 module, 3 đồ thị phụ thuộc ([INDEX.md](01-architecture/INDEX.md)), bất biến xuyên domain ([INVARIANTS.md](01-architecture/INVARIANTS.md)), [ADR-001](01-architecture/decisions/ADR-001-BASELINE-AND-STACK.md) và sơ đồ kiến trúc. |
| [`02-specs/`](02-specs/README.md) | Đặc tả theo Module & Slice | Bảng trạng thái 22 module / 12 slice ([02-specs/README.md](02-specs/README.md)), spec chi tiết `M21`, `M22`, `SL01`, `SL08`, `SL09–11` và các mẫu chuẩn (`templates/`). |
| [`03-planning/`](03-planning/README.md) | Lộ trình, Gap & Truy vết | [ROADMAP.md](03-planning/ROADMAP.md), [GAPS.md](03-planning/GAPS.md), manifest ngữ cảnh `agent/`, registry truy vết `trace/` và bằng chứng kiểm cấu trúc `evidence/`. |
| [`04-research/`](04-research/prompts/prompt-phan-ra-goc.md) | Nghiên cứu, Prompt & Nguồn | Bộ prompt phân rã (`prompts/`), báo cáo nghiên cứu/audit (`reports/`), tài liệu nguồn `.docx`/`.pdf` và bản text trích xuất sạch (`sources/`). |
| [`05-tools/`](05-tools/build_delivery_inventory.py) | Công cụ kiểm chứng tài liệu | Script Python tái sinh `trace/` và kiểm tra tính nhất quán liên kết, hash và truy vết trên bộ tài liệu v1.9. |
| [`99-archive/`](99-archive/README.md) | Kho lưu trữ lịch sử | Các phiên bản Master cũ (`v1.2–v1.8`), bản nháp trung gian và script vá lịch sử (không dùng làm đặc tả hiện hành). |

---

## 3. Lộ trình đọc đề nghị

1. Đọc [AGENTS.md](AGENTS.md) để nắm nguyên tắc phân rã và kiểm chứng tài liệu.
2. Đọc [01-architecture/INVARIANTS.md](01-architecture/INVARIANTS.md) và [01-architecture/INDEX.md](01-architecture/INDEX.md) để hiểu ranh giới 22 module và 3 chiều phụ thuộc.
3. Đọc [03-planning/GAPS.md](03-planning/GAPS.md) và [03-planning/ROADMAP.md](03-planning/ROADMAP.md) để biết các khoảng trống cần chốt khi brainstorm.
4. Kiểm tra bảng trạng thái tại [02-specs/README.md](02-specs/README.md) trước khi mở hoặc bổ sung đặc tả chi tiết cho từng module (`M01–M20`) hoặc slice (`SL00–SL11`).

---

## 4. Lệnh kiểm chứng tính nhất quán tài liệu

Từ thư mục gốc `D:\AI Agent\CRM`, chạy:

```powershell
python 05-tools/build_delivery_inventory.py
python 05-tools/verify_delivery_plan.py
python 05-tools/verify_hrm_integration.py
```

> Lưu ý: Các lệnh trên chỉ kiểm tra cấu trúc tài liệu, checksum, liên kết Markdown và truy vết ID trong bộ đặc tả; **không** đại diện cho kiểm thử ứng dụng hay phê duyệt chính sách doanh nghiệp.
