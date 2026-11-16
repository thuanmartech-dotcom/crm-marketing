# M24 — Lớp Tăng Hiệu năng Hệ thống & Hiệu suất Người dùng

> **[Đề xuất mở rộng sau Master v1.9 — `CR-PERF-PRODUCTIVITY-20261115`]**  
> Tài liệu tách riêng toàn bộ năng lực tối ưu tốc độ thao tác người dùng (`M24-F01–05`) và tối ưu hiệu năng/tải hệ thống (`M24-F06–08`) để cụ thể hóa [Master v1.9 Chương 7 (`NFR01–12`, `ONFR01–06`, `P-NFR`, `H-NFR`)](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md#chuong-7) thành các hạng mục thiết kế độc lập trước khi giao code.

---

## 1. Manifest

- **Baseline tham chiếu:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`), Chương 7 (`7.1–7.9`) và Chương 6 (`6.1–6.2`).
- **Trạng thái:** `Draft (Proposed Extension — chưa phê duyệt đưa vào Baseline v1.9; chưa có code/benchmark/test chạy)`.
- **Domain Owner (đề xuất):** Tech Lead + Product UX Lead + SRE / Platform Lead.
- **Thực thể / Hạ tầng sở hữu (Logical):** `Command_Palette_Index`, `Bulk_Job_Batches`, `Quick_Reply_Templates`, `Notification_Preferences_Digest`, `Read_Model_Projections`, `Permission_Cache_Versions`, `Priority_Queue_Pools`, `Async_Export_Jobs`, `Cold_Archive_Partitions`.
- **Module tiêu thụ (Consumers):** Toàn bộ `M01–M23`.
- **Ranh giới Single Source of Truth (`ADR-003`, `ADR-005`, `ADR-006`, `ADR-007`):**
  - `M24` **không sở hữu quyền hay logic nghiệp vụ domain**: `Permission_Cache_Versions` của `M24-F06` chỉ là **bản phản chiếu Read-Model** từ SSoT **`M14.Principal_Permission_Versions` (`ADR-003`)**. Mọi đọc tương tác (`INTERACTIVE_READ`) nếu lệch cache bắt buộc invalidate & đọc lại Primary DB; mọi tác vụ nền (`M24-F03` Bulk, `M24-F08` Async Export, `M19` Worker, `Download Gateway SEC03`) chạy chế độ **`GUARDED_EXECUTION`** fail-closed `409/401` khi `permission_version` thay đổi.
  - `M24-F08` (**Async Export**) chỉ đóng vai trò **động cơ kết xuất chạy nền**, luôn đi sau bước duyệt/watermark `M23-F07` và xuất tệp qua **`Download Gateway SEC03` (`M14 ACL + M20 Privacy/Hold/6.8` — `ADR-006`)**; tiến trình Archiving/Partitioning bắt buộc tôn trọng `Legal_Holds` & `M20.VerifyPostRestoreComplianceGate` (`ADR-007`).
  - `M24-F07` (**Queue Priority Isolation**) điều phối **3 làn tài nguyên cô lập (`ADR-005`)**: Lane 1 (`M19-F04` Live Webhook Ingest `ONFR02 <= 1s`, giao dịch tiền `M09`, `M11` SLA, revoke `M23-F02`), Lane 2 (`M23-F12` Internal Outbox, Inbox push `M03`, Task `SL01`), Lane 3 (`M19-F06` Backfill, `M19-F08` Replay & Remote Fetch, Bulk Campaign, `M21/M22` import, `M18` BI, `M24-F08` Async Export). Console theo dõi và DLQ nội bộ nằm ở [`M23-F12`](M23-SYSTEM-ADMIN-SECURITY-OPS.md).
- **Read first:** [INVARIANTS.md](../../01-architecture/INVARIANTS.md) (`INV-02`, `INV-03`, `INV-04`, `INV-06`, `INV-23`, `INV-24`, `INV-25`), [INDEX.md](../../01-architecture/INDEX.md).

---

## 2. Requirement Trace (8 Chức năng Đề xuất)

| ID | Nhóm | Nguồn Master v1.9 / Đề xuất | Tên chức năng | Priority | Slice đề xuất | Test | Evidence |
|---|---|---|---|---|---|---|---|
| `M24-F01` | UX Productivity | Master `7.1 NFR09`, `7.4` + Đề xuất | Command Palette (`Ctrl+K`) & Phím tắt tác vụ nhanh | P0/P1 | `SL01–SL03` | `PF-T01` | Not Run |
| `M24-F02` | UX Productivity | Master `3.3`, `3.10`, `3.14` + Đề xuất | Split-View Workspace đa khung (Inbox + 360 + Task/Deal) | P1 | `SL02–SL04` | `PF-T02` | Not Run |
| `M24-F03` | UX Productivity | Master `6.1/6.2`, `INV-09` + Đề xuất | Bulk Actions có Dry-run, Version Guard & Audit | P1 | `SL03–SL06` | `PF-T03` | Not Run |
| `M24-F04` | UX Productivity | Master `3.3`, `M03-F04`, `M20` + Đề xuất | Thư viện Quick Replies / Macro đa kênh | P0/P1 | `SL02–SL04` | `PF-T04` | Not Run |
| `M24-F05` | UX Productivity | Master `6.6`, `7.7` + Đề xuất | Smart Notification Center, Digest & Quiet Hours | P0 | `SL01–SL06` | `PF-T05` | Not Run |
| `M24-F06` | System Scale | Master `7.1 NFR01–03`, `INV-06` + Đề xuất | Read Model Projections & Permission-aware Cache | P0 | `SL00–SL07` | `PF-T06` | Not Run |
| `M24-F07` | System Scale | Master `7.2`, `7.6`, `7.8` + Đề xuất | Queue Priority Isolation (3 làn) & Backpressure | P0 | `SL00–SL07` | `PF-T07` | Not Run |
| `M24-F08` | System Scale | Master `6.2`, `6.4`, `M20-F06` + Đề xuất | Unified Async Export & Lifecycle Archiving/Partitioning | P1 | `SL04–SL07` | `PF-T08` | Not Run |

---

## 3. Hành vi Chi tiết

### 3.1 Nhóm I — Hiệu suất Thao tác Người dùng (`M24-F01–05`, đạt chuẩn `NFR09` $\le 3$ thao tác)

- **`M24-F01` — Command Palette (`Ctrl+K`) & Phím tắt Tác vụ Nhanh:**
  - Cho phép tìm kiếm tiếng Việt có/không dấu xuyên thực thể (`Contact`, `Lead`, `Deal`, `Ticket`, `Task`, `Contract`) và chạy ngay các lệnh ngắn (`Tạo Next Action`, `Ghi kết quả gọi`, `Chuyển stage`, `Mở My Work`) chỉ bằng bàn phím (`NFR09`/`NFR10`).
  - **Guard:** Autocomplete và snippet kết quả bắt buộc lọc qua ACL hiện hành và che số điện thoại/PII theo vai trò (`Chương 6.2`), **không hiển thị số lượng bản ghi ngoài quyền**.
- **`M24-F02` — Split-View Workspace Đa khung:**
  - Mở song song trên một màn hình: danh sách hàng đợi bên trái $\rightarrow$ khung xử lý hội thoại/task ở giữa $\rightarrow$ Hồ sơ 360 + Deal/Ticket/Task liên quan ở panel phải (`M03 + M01 + M02/M11/M16`).
  - **Guard:** Mỗi panel kiểm quyền độc lập (`INV-02`); mở được hội thoại không tự mở dữ liệu hợp đồng, chi phí hay lương nếu thiếu grant tương ứng.
- **`M24-F03` — Bulk Actions Có Dry-run, `expected_version` & Audit:**
  - Chọn nhiều Lead/Deal/Task để chuyển owner, gắn nhãn, đóng hoặc dời hạn follow-up. Bắt buộc chạy bước **Dry-run Preview** liệt kê rõ bản ghi hợp lệ và bản ghi bị chặn bởi policy/version/state guard.
  - **Guard (`INV-25`):** Thực thi qua transaction từng chunk với `expected_version` và ghi đầy đủ `Audit Log` (`actor`, `reason`, `correlation_id`). **Cấm tuyệt đối dùng Bulk Action cho phê duyệt tài chính (`M09/M10/M17/M22`), ký hợp đồng hay xóa dữ liệu cá nhân (`M20`).**
- **`M24-F04` — Thư viện Quick Replies / Macro Đa kênh:**
  - Cho phép chèn nhanh câu trả lời mẫu và điền biến ngữ cảnh (`{{contact_name}}`, `{{ticket_code}}`, `{{appointment_time}}`) khi xử lý Inbox `M03` hoặc Ticket `M11`; quản lý phiên bản mẫu tại [`M23-F11`](M23-SYSTEM-ADMIN-SECURITY-OPS.md).
  - **Guard:** Macro chỉ đổ nội dung vào khung nháp để nhân sự rà soát; nút gửi vẫn bắt buộc đi qua kiểm tra `M20-F03` Suppression/Consent và capability kênh (`M19-F03`).
- **`M24-F05` — Smart Notification Center, Digest & Quiet Hours:**
  - Gom thông báo theo 3 mức ưu tiên: `Urgent` (cảnh báo SLA sắp trễ, ca `S1`, cảnh báo bảo mật `M23-F08`), `Actionable` (giao việc, chờ duyệt) và `Digest` (tổng hợp định kỳ tránh gián đoạn tập trung).
  - **Guard:** Không đưa nội dung chat nhạy cảm hoặc trường lương ra email/push ngoài hệ thống (`Chương 6.6/6.8`); tôn trọng lịch `Quiet Hours` từ [`M23-F10`](M23-SYSTEM-ADMIN-SECURITY-OPS.md); deep link bắt buộc kiểm lại session/ACL khi người dùng bấm vào.

### 3.2 Nhóm II — Hiệu năng Hệ thống & Tối ưu Tải (`M24-F06–08`, bảo đảm `NFR01–05`, `ONFR01–04`)

- **`M24-F06` — Read Model / Materialized Projections & Permission-aware Cache:**
  - Duy trì bảng chiếu đọc riêng cho các màn hình truy vấn nặng (`Customer 360 Timeline`, `Team Board Kanban Counts`, `My Work`, `BI Dashboard M18`), cập nhật bất đồng bộ qua `Internal_Outbox_Events` (`M23-F12` — `INV-06`) thay vì `JOIN` nặng trực tiếp trên bảng giao dịch.
  - **Guard (`INV-25`, `ADR-003`):** `Permission_Cache_Versions` chỉ là bản phản chiếu Read-Model của **`M14.Principal_Permission_Versions`**. Mọi đọc tương tác (`INTERACTIVE_READ`) nếu lệch version buộc xóa cache và nạp từ Primary DB; mọi tác vụ nền (`M24-F03` Bulk, `M24-F08` Export, `M19` Worker, `Download Gateway SEC03`) chạy chế độ `GUARDED_EXECUTION` fail-closed `409/401`.
- **`M24-F07` — Queue Priority Isolation & Backpressure Control (`ADR-005`):**
  - Tách tối thiểu **3 làn hàng đợi độc lập** (Bulkhead tài nguyên, `Chương 7.2/7.8`):
    - **Làn 1 (`REALTIME_CRITICAL`):** Webhook intake `M19-F04` (`ONFR02 <= 1s`), trả lời trực tiếp Agent Inbox (`M03`), ghi nhận giao dịch tiền `M09`, đồng hồ SLA `M11-F03`, thu hồi quyền/phiên `M23-F02`.
    - **Làn 2 (`STANDARD_INTERACTIVE`):** Sự kiện nội bộ `M23-F12` (`Internal_Outbox_Events`), đẩy tin Inbox `M03` & transactional, Task reminders `W-F05`, cập nhật Search index & Read Model `M24-F06`.
    - **Làn 3 (`HEAVY_BATCH_BACKFILL`):** **`M19-F06` Backfill lịch sử nhiều ngày**, **`M19-F08` Replay Jobs & Remote Fetch**, gửi chiến dịch hàng loạt (`M04`), Import Excel lớn (`M21/M22`), AI Co-Pilot `M06`, tính toán BI/P&L `M18` và Async Export `M24-F08`.
  - **Guard:** Khi Làn 3 quá tải hoặc nhà cung cấp AI/đối tác chậm, cơ chế backpressure và Circuit Breaker kích hoạt để bảo vệ tuyệt đối độ trễ Làn 1 và Làn 2.
- **`M24-F08` — Unified Async Export Pipeline & Lifecycle Archiving/Partitioning:**
  - **Async Export:** Mọi thao tác export danh sách/báo cáo lớn chạy nền theo `Export_Request` đã được [`M23-F07`](M23-SYSTEM-ADMIN-SECURITY-OPS.md) duyệt (`INV-24`), kiểm `GUARDED_EXECUTION` (`expected_permission_version` với `M14` — `CEO-U18`), tự thoát công thức CSV (`=,+,-,@`) và xuất qua **`Download Gateway SEC03` (`ADR-006`)**.
  - **Archiving & Partitioning:** Phân vùng theo thời gian (`time-based partitioning`) và chuyển dữ liệu cũ (`Activities`, `Inbound_Events` / raw payload 30 ngày `GAP-M19-08`, `Audit_Logs`) sang tầng lưu trữ lạnh theo chính sách retention `M20-F06` (`Legal_Holds` chặn xóa!). Giữ toàn vẹn `Deletion_Ledger` khi khôi phục qua **`M20.VerifyPostRestoreComplianceGate`** (`ADR-007`).

---

## 4. Data / API & Migration Gate (Đề xuất)

- **Logical API (`/productivity/v1` — Đề xuất):** `GET /productivity/v1/command-search`, `POST /productivity/v1/bulk-commands/dry-run`, `POST /productivity/v1/bulk-commands/commit`, `GET /productivity/v1/quick-replies`, `PUT /productivity/v1/notifications/preferences`, `GET /productivity/v1/async-jobs/{id}`.
- **Lộ trình tích hợp theo Slice:**
  - `M24-F06` & `M24-F07` (lõi cache phân quyền & tách làn queue): thiết lập từ **`SL00–SL02`**.
  - `M24-F01/02/03/04/05`: triển khai cuốn chiếu từ **`SL01–SL06`**.
  - `M24-F08` (Archiving/Partitioning & Async Export quy mô lớn): kích hoạt đầy đủ từ **`SL04–SL07`**.
- **Trạng thái kiểm thử (`PF-T01..08`):** **`Not Run`** (chưa có mã nguồn và chưa chạy benchmark thực tế).
