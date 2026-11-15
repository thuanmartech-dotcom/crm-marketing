# M18 — Từ điển Chỉ số, Báo cáo Điều hành, Attribution & Báo cáo Tổng hợp Mở rộng

> **Phạm vi tài liệu:** Kết nối đầy đủ **7 chức năng Baseline v1.9 (`M18-F01–07`)** trong [Master v1.9 Mục 3.11 & Chương 8](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md#chuong-8) với **4 chức năng Báo cáo Tổng hợp Mở rộng (`M18-F08–11`)** `[Đề xuất mở rộng sau v1.9 — CR-BI-REPORT-20261115]`.  
> Tài liệu tách riêng hoàn toàn domain BI/Báo cáo khỏi lớp hiệu năng/hiệu suất ([M24-PERFORMANCE-AND-PRODUCTIVITY.md](M24-PERFORMANCE-AND-PRODUCTIVITY.md)).

---

## 1. Manifest

- **Baseline tham chiếu:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`), Mục `3.11` (`FR28–FR29`, `M18-F01–07`) và `Chương 8` (`8.1–8.7`).
- **Trạng thái:**
  - `M18-F01–07`: Đã có khung yêu cầu trong Master v1.9; chờ bóc tách chi tiết DDL/API/UI theo từng slice (`Chưa có code/test chạy`).
  - `M18-F08–11`: `Draft (Proposed Extension — chưa sửa đổi Master v1.9; chưa có code/test chạy)`.
- **Domain Owner (đề xuất):** Analytics Lead + Finance Lead (đối với chỉ số tài chính/P&L) + Data Steward (Data Quality).
- **Thực thể sở hữu (Logical):** `Metric_Definitions`, `Metric_Targets`, `Metric_Facts`, `Attribution_Runs`, `Report_Snapshots`, `Adhoc_Report_Queries` *(đề xuất)*, `Report_Schedules` *(đề xuất)*, `Data_Quality_Checks` *(đề xuất)*.
- **Phụ thuộc chuẩn hóa (Single Source of Truth):**
  - Đọc projection từ [M24 (`M24-F06`)](M24-PERFORMANCE-AND-PRODUCTIVITY.md) mà **không biến projection thành nguồn ghi** (`INV-03`, `INV-04`).
  - Mọi lịch xuất/gửi báo cáo (`M18-F10`) bắt buộc đi qua luồng thống nhất: **`M18-F10` $\rightarrow$ Duyệt 2 lớp & Watermark `M23-F07` $\rightarrow$ Chạy nền `M24-F08` $\rightarrow$ Download Gateway** (`INV-24`).
  - Kiểm quyền truy cập `RBAC + ABAC` hiện hành qua `M14`.
- **Read first:** [INVARIANTS.md](../../01-architecture/INVARIANTS.md), [INDEX.md](../../01-architecture/INDEX.md), [M23-SYSTEM-ADMIN-SECURITY-OPS.md](M23-SYSTEM-ADMIN-SECURITY-OPS.md), [M24-PERFORMANCE-AND-PRODUCTIVITY.md](M24-PERFORMANCE-AND-PRODUCTIVITY.md).

---

## 2. Danh mục 11 Chức năng & Truy vết

### 2.1 Nhóm Baseline v1.9 (`M18-F01–07` — Nguồn Master 3.11)

| ID | Chức năng | Vai trò trong domain BI | Nguồn Master | Priority | Test | Evidence |
|---|---|---|---|---|---|---|
| `M18-F01` | Quản lý Từ điển chỉ số (`Metric Dictionary`) | Chuẩn hóa mã chỉ số, tử/mẫu số, grain, scope, hướng tốt/xấu và version dùng chung toàn hệ thống | `3.11`, `FR28` | P0 | Master / Chờ tách | Not Run |
| `M18-F02` | Chốt Mục tiêu KPI (`Targets`) | Lưu target đã duyệt theo kỳ và phiên bản; mẫu số 0 trả `N/A`; phân biệt hướng tốt/xấu | `3.11`, `FR28` | P0 | Master / Chờ tách | Not Run |
| `M18-F03` | Thu nhận & Hiệu chỉnh dữ kiện (`Facts`) | Nạp sự kiện theo business key chống trùng khi replay; điều chỉnh trễ giữ lineage; không điền 0 khi thiếu nguồn | `3.11`, `FR28` | P0 | Master / Chờ tách | Not Run |
| `M18-F04` | Tính toán & Hiển thị Báo cáo điều hành | Dashboard theo 8 vai trò (Chương 8.1); tách CAC agency khỏi media khách; hiển thị rõ tử/mẫu số | `3.11`, `8.1–8.2` | P0 | Master / Chờ tách | Not Run |
| `M18-F05` | Mô hình phân bổ doanh thu (`Attribution`) | Chạy các model (First/Last/...) độc lập với tổng credit $\le 1$ (thiếu để `Unknown`); không gán tràn mọi Contact | `3.11`, `FR29` | P0/P1 | Master / Chờ tách | Not Run |
| `M18-F06` | Phát hành báo cáo & Drill-down theo quyền | Áp dụng ACL đồng nhất từ số tổng xuống danh sách chi tiết & export; khách chỉ thấy bản `Published` đúng scope | `3.11`, `6.1` | P0 | Master / Chờ tách | Not Run |
| `M18-F07` | Xuất kết quả chuyển đổi về nền tảng quảng cáo | Gửi conversion feedback có kiểm `M20` purpose/consent; tách `Won != Paid` và đồng bộ hoàn tiền | `3.11`, `FR29` | P1 | Master / Chờ tách | Not Run |

### 2.2 Nhóm Mở rộng Báo cáo Tổng hợp (`M18-F08–11` — `[Đề xuất sau v1.9]`)

| ID | Nguồn liên quan | Tên chức năng | Owner / Consumer | Priority | Slice đề xuất | Test | Evidence |
|---|---|---|---|---|---|---|---|
| `M18-F08` | Master `8.1/8.2/8.7` + Đề xuất | Báo cáo P&L & Dòng tiền hợp nhất cấp Công ty (`M09 + M17 + M10 + M22`) | Finance + CEO / Kế toán, BOD | P1 | `SL05 / SL07` | `R-T01` (đề xuất) | Not Run |
| `M18-F09` | Master `3.11`, `6.1`, `8.2` + Đề xuất | Trình tự tạo Báo cáo linh hoạt (`Ad-hoc Report Builder`) trên `Metric Dictionary` | Analytics / Manager, CEO, CMO | P1 | `SL07` | `R-T02` (đề xuất) | Not Run |
| `M18-F10` | Master `6.2`, `8.1`, `M23-F07` + Đề xuất | Lập lịch xuất & gửi Báo cáo định kỳ tự động có watermark & snapshot | Analytics / Các vai trò có quyền | P1 | `SL07` | `R-T03` (đề xuất) | Not Run |
| `M18-F11` | Master `8.3` + Đề xuất | Cockpit Chất lượng dữ liệu & Adoption có owner & SLA khắc phục | Data Steward + Ops / Quản lý | P0/P1 | `SL03–SL06` | `R-T04` (đề xuất) | Not Run |

---

## 3. Hành vi Chi tiết Phần Mở rộng (`M18-F08–11`)

- **`M18-F08` — Báo cáo P&L & Dòng tiền hợp nhất cấp Công ty:**
  - Hợp nhất theo 4 lớp tách bạch tuyệt đối đúng Master Chương 8.2:
    1. **Doanh thu phí dịch vụ** (`M08/M09`, tách riêng Media khách và VAT khỏi doanh thu thuần agency).
    2. **Thực thu & Tuổi nợ** (`M09-F04/05`, tách `Unmatched Receipts` và tiền ứng chưa phân bổ).
    3. **Chi phí trực tiếp dự án, PO & Hoa hồng** (`M17-F03` Actuals + `M10-F04/05` Commission Earned/Payable).
    4. **Chi phí nhân sự phân bổ** (`M22-F25/M14-F07` theo `cost_rate_version` và timesheet hợp lệ — **cấm dùng lương net làm cost rate** và cấm lộ bảng lương cá nhân khi drill-down).
  - Thiếu dữ liệu `cost_rate` hoặc kỳ công chưa khóa hiển thị rõ `Unknown / Partial Coverage` kèm độ phủ (`%`), tuyệt đối không điền số `0`.
- **`M18-F09` — Ad-hoc Report Builder trên `Metric Dictionary`:**
  - Chỉ cho phép kéo thả các **Metric đã duyệt (`M18-F01`)**, chiều phân tích (`branch`, `legal_entity`, `owner`, `campaign`, `period`) và cột dữ liệu nằm trong quyền `RBAC + ABAC` của người tạo (`INV-02`).
  - Tự động áp dụng đúng công thức tử/mẫu số (`N/A` khi mẫu số $= 0$) và **chặn ghép sai grain** (ví dụ không cho cộng đơn tiêu dùng đối tác `M21` vào pipeline lead agency `M02`, `INV-18`).
- **`M18-F10` — Scheduled Report Delivery:**
  - Cấu hình lịch chạy ngày/tuần/tháng, bộ lọc cố định và danh sách người nhận nội bộ hoặc khách hàng (chỉ với bản `Published` của `CLIENT workspace`).
  - Trước mỗi lần kết xuất: kiểm tra lại quyền hiện hành qua `M14` (`INV-02`), loại bỏ người đã thu hồi quyền/nghỉ việc (`M14-F06`); đẩy tệp qua `M23-F07` (kiểm duyệt/watermark) và `M24-F08` (worker nền) tới Download Gateway.
- **`M18-F11` — Cockpit Chất lượng dữ liệu & Adoption (Cụ thể hóa Chương 8.3):**
  - Theo dõi tỷ lệ hồ sơ thiếu trường bắt buộc, cặp `Contact/Lead` trùng chờ merge, `Unmatched payments` quá hạn, `Identity unresolved backlog`, độ trễ connector `M19` và tỷ lệ bản ghi active thiếu `next_action`.
  - Hỗ trợ tạo nhanh task khắc phục sang `M16` (`W-F01`) kèm `dedup business key` để không sinh trùng việc.

---

## 4. Data / API & UI Operations (`M18` mở rộng)

- **Logical API (`/bi/v1` — Đề xuất):** `GET /bi/v1/pl-consolidated`, `POST /bi/v1/adhoc-queries/preview`, `POST /bi/v1/report-schedules`, `GET /bi/v1/data-quality/cockpit`, `POST /bi/v1/data-quality/remediation-tasks`.
- **UI Freshness bắt buộc:** Mọi widget đọc từ Read Model ([`M24-F06`](M24-PERFORMANCE-AND-PRODUCTIVITY.md)) hoặc P&L (`M18-F08`) phải hiển thị `last_refreshed_at`, `coverage_status` và `metric_version`; không gắn nhãn "Realtime" cho dữ liệu tính định kỳ (Master `8.1`).

---

## 5. Migration & Gate Nghiệm thu

- **Cảnh báo ranh giới:** Tài liệu này bổ sung đặc tả phân tích cho `M18` mà không chỉnh sửa Master v1.9. Trạng thái mọi ca test (`R-T01..04` và bộ test gốc `M18`) là **`Not Run`**.
