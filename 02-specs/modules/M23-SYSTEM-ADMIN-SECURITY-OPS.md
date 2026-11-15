# M23 — Quản trị Hệ thống, Bảo mật Vận hành & Nền tảng Cấu hình

> **[Đề xuất mở rộng sau Master v1.9 — `CR-SYSADMIN-SEC-20261115`]**  
> Tài liệu này cụ thể hóa thành các chức năng vận hành và giao diện quản trị cho các quy chuẩn bảo mật, phân tách thẩm quyền và cấu hình nền tảng vốn đã được đặt nguyên tắc trong [Master v1.9 (Chương 6, 7, 8)](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md#chuong-6) nhưng chưa tách thành module độc lập trong 22 module baseline (`M01–M22`).

---

## 1. Manifest

- **Baseline tham chiếu:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`), trọng tâm Mục `6.1` (Mô hình quyền & Thẩm quyền cấp quyền), `6.2` (Bảo vệ dữ liệu, Export, Audit, Download Gateway), `7.2–7.5` (Độ sẵn sàng, DRP, Feature flags).
- **Trạng thái:** `Draft (Proposed Extension — chưa phê duyệt đưa vào Baseline v1.9; chưa có code/DDL/test chạy)`.
- **Domain Owner (đề xuất):** Technical/Security Lead (vận hành cấu hình kỹ thuật) + Owner/CEO hoặc Security/Privacy Approver (phê duyệt thẩm quyền, Break-glass, Export).
- **Thực thể sở hữu (Owned Entities — Đề xuất):** `Auth_Session_Policies`, `Break_Glass_Grants`, `Approval_Matrix_Rules`, `Tenant_Operating_Modes`, `Export_Requests`, `Security_Anomaly_Alerts`, `Feature_Flag_Configs`, `System_Calendars`, `Shared_Dictionaries`, `Shared_Templates`, `Backup_Drill_Logs`.
- **Module tiêu thụ (Consumers):** Toàn bộ `M01–M24` (đặc biệt `M07`, `M10`, `M14`, `M15`, `M17`, `M18`, `M19`, `M20`, `M22`, `M24`).
- **Ranh giới tuyệt đối (*Single Source of Truth* — `INV-23`, `INV-24`):**
  - **`M23` vs `M14` (Quyền & Break-glass):** `M14` vẫn sở hữu cây tổ chức (`Tenant/Branch/Legal Entity/Workspace`), `Membership`, `Entity_Team_Grants` và là **cổng kiểm tra quyền thực thi (`RBAC + ABAC`) duy nhất**. `M23-F03` chỉ quản lý quy trình xin–duyệt–TTL của `Break-glass` và ghi grant tạm thời sang `M14`.
  - **`M23` vs `M20` (Privacy):** `M20` sở hữu mục đích xử lý dữ liệu cá nhân, `Consent`, `Suppression`, `Privacy_Requests` và `Retention/Legal Hold`.
  - **`M23` vs `M19` (Sức khỏe, Outbox & DLQ):** `M19` (`M19-F07`) sở hữu `Connector/OAuth` và DLQ/health cho **tích hợp bên ngoài**; `M23-F12` chỉ quản lý **hệ thống nội bộ dùng chung** (trạng thái `Queue Priority` của `M24-F07`, Outbox/DLQ nội bộ và nhật ký diễn tập Backup/Restore).
  - **`M23` vs `M22/M11/M04/M16` (Lịch chuẩn):** `M23-F10` sở hữu Lịch chuẩn Tenant/Pháp nhân, Ngày lễ & `Quiet Hours`; `M22-F07` kế thừa để phân ca từng nhân viên; `M04`/`M11`/`M16` đọc từ `M23-F10`.
  - **Chuỗi Export thống nhất:** Mọi xuất dữ liệu lớn/báo cáo định kỳ đi qua `M18-F10` / màn hình nguồn $\rightarrow$ `M23-F07` (Duyệt 2 lớp & Watermark) $\rightarrow$ [`M24-F08`](M24-PERFORMANCE-AND-PRODUCTIVITY.md) (Worker chạy nền) $\rightarrow$ Download Gateway.
  - **Nguyên tắc Chương 6.1:** Technical Admin triển khai chính sách đã duyệt, không mặc nhiên được tự cấp quyền xem dữ liệu kinh doanh, tài chính hay lương (`M22`).
- **Read first:** [INVARIANTS.md](../../01-architecture/INVARIANTS.md) (`INV-01`, `INV-02`, `INV-09`, `INV-13`, `INV-14`, `INV-22`, `INV-23`, `INV-24`), [INDEX.md](../../01-architecture/INDEX.md), [M24-PERFORMANCE-AND-PRODUCTIVITY.md](M24-PERFORMANCE-AND-PRODUCTIVITY.md).

---

## 2. Requirement Trace (Truy vết nguồn Master v1.9 & Đề xuất mới)

| ID chức năng | Nguồn Master v1.9 / Đề xuất | Ý nghĩa | Owner / Consumer | Priority | Applicability | Test | Evidence |
|---|---|---|---|---|---|---|---|
| `M23-F01` | Master `6.2` (MFA/Session) + Đề xuất | Chính sách đăng nhập, MFA bắt buộc theo vai trò rủi ro, Session Timeout & IP Allowlist | Technical Admin + Security Approver / All | P0 | Mọi tenant | `S-T01` (đề xuất) | Not Run |
| `M23-F02` | Master `6.1/6.2`, `M14-F06` + Đề xuất | Theo dõi phiên đang hoạt động & thu hồi phiên khẩn cấp (cá nhân/hàng loạt) | Technical Admin + Security Approver / `M14` | P0 | Mọi tenant | `S-T02` (đề xuất) | Not Run |
| `M23-F03` | Master `6.1` (Break-glass, TTL) + Đề xuất | Cấp, duyệt và tự thu hồi quyền khẩn cấp `Break-glass` có TTL ngắn (2–4h) & scope hẹp | Security Approver / `M14`, Support | P0 | Mọi tenant | `S-T03` (đề xuất) | Not Run |
| `M23-F04` | Master `3.6.1/3.6.4/3.9/3.10.2` + Đề xuất | Ma trận Thẩm quyền & Ngưỡng duyệt tập trung (`M07`, `M10`, `M15`, `M17`, `M22`) | Owner/CEO + Finance / `M07/10/15/17/22` | P0 | Mọi tenant | `S-T04` (đề xuất) | Not Run |
| `M23-F05` | Master `6.1` (Solo vs Team) + Đề xuất | Quản lý chế độ `SOLO/PILOT` $\leftrightarrow$ `TEAM` & khóa Maker–Checker tự động | Owner/CEO / `M14`, `M23` | P0 | Mọi tenant | `S-T05` (đề xuất) | Not Run |
| `M23-F06` | Master `6.2` (Audit redact/immutable) + Đề xuất | Trung tâm điều tra `Immutable Audit Log` (đã redact PII, cấm Admin xóa log) | Security/Audit / All | P0 | Mọi tenant | `S-T06` (đề xuất) | Not Run |
| `M23-F07` | Master `6.2` (Export, Watermark, Gateway) + Đề xuất | Hàng đợi Phê duyệt Export 2 lớp, đóng dấu watermark & cấp link Gateway có TTL | Approver + Steward / `M01–M22` | P0 | Khi bật Export | `S-T07` (đề xuất) | Not Run |
| `M23-F08` | Master `6.2` (DLP/cảnh báo) + Đề xuất | Giám sát bất thường truy cập & cảnh báo DLP (bulk export, login lạ, dò quyền 403) | Security Owner / All | P1 | Mọi tenant | `S-T08` (đề xuất) | Not Run |
| `M23-F09` | Master `2.3`, `7.5`, `INV-14` + Đề xuất | Quản trị `Feature Flags`, Gói ngành & Release Profile kèm dependency closure | Technical Admin + PO / All | P0 | Mọi tenant | `S-T09` (đề xuất) | Not Run |
| `M23-F10` | Master `3.7.1`, `3.14`, `3.16` + Đề xuất | Quản lý Lịch làm việc, Ngày lễ, Múi giờ & `Quiet Hours` dùng chung | Ops Lead / `M04/11/13/16/22` | P0 | Mọi tenant | `S-T10` (đề xuất) | Not Run |
| `M23-F11` | Master `3.2/3.6/3.9` + Đề xuất | Quản lý Từ điển Danh mục & Thư viện Mẫu Dùng chung có phiên bản | Ops/BA Admin / `M02/03/07/11/15` | P0 | Mọi tenant | `S-T11` (đề xuất) | Not Run |
| `M23-F12` | Master `7.2–7.3`, `7.6`, `M19-F07` + Đề xuất | Console Sức khỏe Hệ thống, Outbox/DLQ dùng chung & Nhật ký Diễn tập Backup/Restore | Ops/SRE / `M19`, All Workers | P0 | Mọi tenant | `S-T12` (đề xuất) | Not Run |

---

## 3. Hành vi Chi tiết theo Trụ cột

### Trụ cột A — Xác thực, Phiên & Quyền khẩn cấp (`M23-F01..03`)
- **`M23-F01` (Chính sách Đăng nhập, MFA & Mạng):**
  - Nguồn Master: Bắt buộc MFA cho quản lý, Admin, kế toán (`6.2`); session timeout cấu hình.
  - Đề xuất thiết kế: Policy theo vai trò và tenant (`require_mfa_roles`, `idle_timeout_minutes`, `absolute_timeout_hours`, `max_concurrent_sessions`, `ip_allowlist_optional`). Thiếu cấu hình áp dụng bộ mặc định an toàn (`fail-closed` cho quyền Admin/Finance).
- **`M23-F02` (Quản lý Phiên & Thu hồi khẩn cấp):**
  - Hiển thị danh sách phiên đang hoạt động (ẩn token thật, chỉ hiện thiết bị/IP rút gọn/thời điểm hoạt động).
  - Cho phép ép đăng xuất một phiên hoặc toàn bộ phiên của nhân sự (kích hoạt tự động khi nhận event `M14-F06` nghỉ việc hoặc phát hiện mất thiết bị), tăng `permission_version` để vô hiệu JWT/session cache tức thì.
- **`M23-F03` (Quyền khẩn cấp `Break-glass` có TTL):**
  - Tác nhân kỹ thuật/hỗ trợ tạo yêu cầu kèm `target_workspace`, `reason`, `incident_ticket_id` và `ttl_minutes` (tối đa đề xuất 120–240 phút).
  - Bắt buộc qua cơ chế duyệt ở `M23-F05`: **cấm mở mặc định sang dữ liệu lương `M22` hoặc ví tài chính nếu không được Security/CEO chỉ định riêng**. Tự động thu hồi khi hết TTL và khóa mọi session/download đang mở bằng grant đó (`Download Gateway` recheck).

### Trụ cột B — Ma trận Thẩm quyền & Cơ chế Maker–Checker Thích ứng (`M23-F04..05`)
- **`M23-F04` (Ma trận Thẩm quyền & Ngưỡng Duyệt tập trung):**
  - Định nghĩa quy tắc theo `(module, action_type, legal_entity/branch, currency, amount_or_discount_threshold)` $\rightarrow$ danh sách `approver_roles`, số cấp duyệt và `sla_hours`.
  - Mọi thay đổi tạo phiên bản mới (`DRAFT` $\rightarrow$ `REVIEWED` $\rightarrow$ `ACTIVE`) có `effective_at`; giao dịch cũ đang chờ duyệt giữ đúng phiên bản tại thời điểm trình (`INV-14`, tránh đổi luật giữa đường).
- **`M23-F05` (Chế độ Vận hành `SOLO/PILOT` vs `TEAM` & Khóa Maker–Checker):**
  - Theo quyết định chốt từ phiên `/grill-me` (khớp Chương 6.1):
    - Ở `SOLO/PILOT` (khi số quản lý có thẩm quyền $< 3$): cho phép chủ dự án/người được ủy quyền thực hiện thao tác nhạy cảm có lý do bắt buộc, TTL ngắn, đánh dấu `self_approved_in_pilot_mode = true` và bắn cảnh báo ngay tức thì tới Chủ dự án/CEO.
    - Khi chuyển tenant sang `TEAM` (một chiều nâng mức hoặc cần chữ ký Owner để hạ): hệ thống **tự động khóa hoàn toàn tự duyệt** cho Technical Admin và bắt buộc 2 người độc lập (*Maker $\neq$ Checker*) đối với Break-glass, duyệt Export PII, đổi Ma trận thẩm quyền và điều chỉnh chính sách bảo mật.

### Trụ cột C — Audit Log, Duyệt Export 2 lớp & DLP (`M23-F06..08`)
- **`M23-F06` (Trung tâm Điều tra Audit Log Bất biến):**
  - Ghi mọi sự kiện bảo mật và thay đổi nhạy cảm (`actor`, `impersonator_or_breakglass_id`, `action`, `target_scope`, `before_redacted`, `after_redacted`, `reason`, `correlation_id`, `ip_masked`).
  - Technical Admin **không có quyền `DELETE/UPDATE`** trên bảng log; xuất log điều tra phải đi qua kiểm quyền riêng và không ghi tràn CCCD/số tài khoản/nội dung mật vào trường text log.
- **`M23-F07` (Hàng đợi Duyệt Export 2 lớp & Watermark):**
  - Khi người dùng yêu cầu export danh sách có PII/tài chính hoặc vượt ngưỡng dòng cho phép (`M01–M22`, `M18-F10`): tạo `Export_Request (PendingApproval)`.
  - Người duyệt (khác người yêu cầu ở chế độ `TEAM`) rà xét mục đích, số dòng, trường nhạy cảm. Sau khi duyệt, worker nền mới kết xuất tệp, nhúng watermark (`user_id`, `request_id`, `exported_at`), thoát công thức CSV (`=,+,-,@`), đẩy về `Download Gateway` với link TTL ngắn.
- **`M23-F08` (Cảnh báo Bất thường Truy cập & DLP):**
  - Phát hiện theo rule định lượng (ví dụ: nhiều yêu cầu export liên tiếp, tải file vượt ngưỡng giờ, đăng nhập từ IP/vị trí lạ sau giờ làm, bùng phát lỗi `403/404` nghi rà quét ID) $\rightarrow$ tạo `Security_Anomaly_Alert`, đề xuất khóa phiên tạm thời (`M23-F02`) cho người trực xử lý.

### Trụ cột D — Cấu hình Hệ thống, Dữ liệu nền & Vận hành Nền tảng (`M23-F09..12`)
- **`M23-F09` (Feature Flags, Gói ngành & Release Profile):**
  - Quản lý trạng thái từng capability (`OFF / SHADOW / PILOT / ON`) ở mức Tenant hoặc Workspace.
  - Kiểm tra **dependency closure** trước khi bật: ví dụ không cho bật `M21 API_READ` khi chưa bật `M19 Connector + M20 Processing_Record`; không cho bật `M22 HR-C` khi chưa hoàn tất policy lương và khóa `HR-A`.
- **`M23-F10` (Lịch làm việc, Ngày lễ & `Quiet Hours`):**
  - Cung cấp bảng lịch chuẩn (`timezone`, giờ hành chính, cuối tuần, ngày lễ quốc gia/công ty, `quiet_hours`) có hiệu lực theo `effective_date` để `M11` tính đồng hồ SLA, `M04` lập lịch gửi tin, `M16` nhắc việc và `M22-F07` kế thừa phân ca nhân viên mà không hard-code rời rạc.
- **`M23-F11` (Từ điển Danh mục & Thư viện Mẫu Dùng chung):**
  - Quản trị tập trung danh mục dùng chung (lý do Won/Lost/OnHold/Cancel/Reject, mã thuế/tiền tệ, mẫu SOW/Email/ZNS/Survey/Quick Replies `M24-F04`) theo phiên bản, không cho xóa cứng danh mục đã phát sinh giao dịch lịch sử (`archive only`).
- **`M23-F12` (Bảng điều khiển Sức khỏe Nền tảng, Outbox/DLQ & Diễn tập Backup):**
  - Hiển thị tập trung trạng thái hàng đợi ưu tiên (`M24-F07`), số lượng job lỗi/Dead-Letter Queue nội bộ (tách riêng khỏi DLQ adapter tích hợp ngoài ở `M19-F07`), cho phép retry/replay an toàn có idempotency key và lưu nhật ký diễn tập khôi phục định kỳ (`RPO/RTO`, kiểm chứng áp lại `Deletion_Ledger` theo `NFR06` / Chương 7.3).

---

## 4. Data / API (Logical Contracts — Đề xuất)

> **Lưu ý:** Chưa sinh SQL DDL hay OpenAPI vật lý trong giai đoạn tài liệu; tên thực thể dưới đây là hợp đồng logic cần chốt trong giai đoạn thiết kế DB chi tiết.

- **Thực thể chính (tất cả có `tenant_id`, `version`, `created_by`, `created_at`):**
  - `Auth_Session_Policies` (`policy_id`, `role_scope`, `mfa_required`, `idle_ttl_min`, `max_sessions`, `ip_allowlist`, `effective_from`)
  - `Break_Glass_Grants` (`grant_id`, `requester_id`, `approver_id`, `target_scope`, `reason`, `ticket_ref`, `expires_at`, `revoked_at`, `status`)
  - `Approval_Matrix_Rules` (`rule_id`, `domain_module`, `action_code`, `threshold_json`, `approver_chain`, `version`, `status`, `effective_from`)
  - `Export_Requests` (`request_id`, `requester_id`, `approver_id`, `dataset_scope`, `row_count_est`, `purpose`, `status`, `watermark_hash`, `download_expires_at`)
  - `Feature_Flag_Configs` (`flag_key`, `scope_type`, `scope_id`, `state`, `dependencies`, `updated_by`, `reason`)
  - `System_Calendars` & `Shared_Dictionaries` (`calendar_id` / `dict_type`, `code`, `version`, `effective_from`, `archived_at`)
- **Commands chính (`/admin/v1` — Đề xuất):**
  - `POST /admin/v1/sessions/{id}/revoke`, `POST /admin/v1/users/{id}/revoke-all-sessions`
  - `POST /admin/v1/break-glass/requests`, `POST /admin/v1/break-glass/{id}/approve`, `POST /admin/v1/break-glass/{id}/revoke`
  - `POST /admin/v1/approval-matrix/versions`, `POST /admin/v1/approval-matrix/{id}/activate`
  - `POST /admin/v1/exports/{id}/approve`, `POST /admin/v1/exports/{id}/reject`
  - `POST /admin/v1/feature-flags/{key}/toggle`, `POST /admin/v1/dlq/{job_id}/replay`
- **Bảo vệ API:** Mọi command bắt buộc `idempotency_key`, `expected_version`, `reason` cho thao tác nhạy cảm và kiểm tra chế độ `SOLO/PILOT` vs `TEAM` ở server (`Maker != Checker` khi `TEAM`).

---

## 5. UI / Operations & Ranh giới Độc lập

- **Màn hình tối thiểu:** Security Posture & Active Sessions, Break-Glass Center, Approval Matrix Studio, Immutable Audit & DLP Explorer, Export Approval Queue, Feature Flags & Dependency Gate, Shared Calendars & Dictionaries, System Jobs/DLQ & Backup Drill Monitor.
- **Trạng thái bắt buộc:** Khi chưa cấu hình Ma trận thẩm quyền cho một ngưỡng tiền hoặc một danh mục bắt buộc, hệ thống hiển thị rõ trạng thái `Policy Missing — Chặn phê duyệt tự động` (`INV-14`), không tự suy đoán cho qua.

---

## 6. Migration & Gate Nghiệm thu (Đề xuất)

- **Thứ tự triển khai:** Nền `M23-F01/02/05/06/09/10` gắn vào **SL00 (Foundation)**; `M23-F03/04/07/11/12` hoàn thiện đồng bộ theo **SL01–SL05**; `M23-F08` (DLP/Anomaly) kích hoạt cùng gói bảo mật nâng cao.
- **Trạng thái kiểm thử:** Mọi ca kiểm thử `S-T01..12` hiện ở trạng thái **`Not Run`** (chưa có mã nguồn ứng dụng).
