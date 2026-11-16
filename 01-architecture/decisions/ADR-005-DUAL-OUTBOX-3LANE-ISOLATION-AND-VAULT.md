# ADR-005 — Dual Outbox, Cô lập 3 Làn Queue (`M24-F07`), Lease Chống Treo `Outbound_Intents`, Secret Vault & Guard `API_READ` / `PMS` / Tài chính

**Status:** `Approved (Wave 1.5 Hardening — CR-20261116-WAVE1-5-HARDENING)`  
**Phạm vi:** `M19` (`C19`), `M23-F12` (`C23`), `M24-F07` (`C24`), `M16` (`UC-W10`), `M21-F06` (`INV-21`), `M09`, `M22-F10/28`, `SL01`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`2.4 L250`, `2.5 L258`, `2.6 L272`, `5.16 L2816–2829`, `7.6 L3312–3319`, `ONFR02`, `ONFR05`, `H-NFR08`, `UC-W10`), [INVARIANTS.md](../INVARIANTS.md) (`INV-03`, `INV-06`, `INV-07`, `INV-08`, `INV-13`, `INV-21`, `INV-23`)

---

## Context

1. `SL01-INTERNAL-WORK.md` từng trỏ Outbox/DLQ nội bộ cho `M16` vào `M19`, trong khi `INDEX.md` & `INV-23` phân tách `M19` (tích hợp kênh ngoài) với `M23-F12` (Outbox/DLQ nội bộ dùng chung).
2. `M19-F06` (Backfill 30 ngày), `M19-F08` (Replay + Remote Fetch) và gửi chiến dịch hàng loạt cần tách cô lập khỏi `M19-F04` webhook live để bảo vệ SLO `ONFR02 p95 <= 1s` (`NFR04 <= 2s`).
3. Rà soát Wave 1.5 chỉ ra thêm 2 lỗ hổng kỹ thuật trên `M19`:
   - Khi Worker Pha 2 chuyển `Outbound_Intents` sang `DISPATCHING`, nhả DB lock để gọi HTTP rồi crash hoặc kẹt mạng giữa đường, bản ghi `DISPATCHING` bị **treo vĩnh viễn** hoặc dễ bị reaper retry mù sau khi HTTP POST đã rời đi.
   - `provider_category` của `M19` chưa khai báo `PMS` và `TASK_SYNC` để phục vụ luồng đồng bộ dự án/công việc bên ngoài cho `M16` (`UC-W10`).

## Đề nghị

1. **Dual Outbox Boundary (`INV-23`, tách dứt khoát tại cấp Database & Topic):**
   - **External Integration Platform (`M19` — TUYỆT ĐỐI KHÔNG làm Internal Outbox):** Chỉ quản lý `Channel_Connections`, `Inbound_Events`, `Inbound_Event_Dedup_Keys`, `Outbound_Intents`, `Send_Attempts`, `Message_Status_Events`, `Email_Delivery_Events` ingest, `Sync_Checkpoints/Runs`, `Quarantined_Events`, `Adapter_Dead_Letter_Queue`, `Replay_Jobs` cho **giao tiếp với hệ thống bên ngoài** (Zalo, Meta, TikTok, Telegram, Email, VoIP, POS `API_READ`, PMS ngoài `UC-W10`, thiết bị chấm công/ngân hàng/ERP/Payment Gateway).
   - **Internal Domain Outbox & DLQ (`M23-F12`):** Quản lý bảng `Internal_Outbox_Events` + `Internal_Dead_Letter_Queue` cho toàn bộ sự kiện liên module nội bộ (`M14.*`, `M16.*`, `M20.*`, `M22.*`, `M23.*`, Notification `M24-F05`, BI projection `M18`) và diễn tập Backup Drill logs. Mọi domain module publish vào `Internal_Outbox_Events` trong cùng DB transaction nghiệp vụ (`INV-06`).

2. **Cô lập 3 Làn Queue (`M24-F07` Logic — Tương thích PG Worker Pools theo `ADR-001`):**
   - **Lane 1 (`REALTIME_CRITICAL`):** `M19-F04` Live Webhook Ingest-Before-ACK (`ONFR02 p95 <= 1s`), trả lời trực tiếp Agent Inbox (`M03`, `ONFR01 <= 5s`), giao dịch tiền `M09`, đồng hồ SLA `M11`, thu hồi phiên/quyền `M23-F02`.
   - **Lane 2 (`STANDARD_INTERACTIVE`):** Sự kiện nội bộ `M23-F12` (`Internal_Outbox_Events`), đẩy cập nhật UI/360 (`M24-F06`), gửi đơn lẻ transactional (`Ticket`, `Appointment`, `OTP/CSKH`), `M16` Task/Project events.
   - **Lane 3 (`HEAVY_BATCH_BACKFILL`):** `M19-F06` Sync/Backfill nhiều ngày, `M19-F08` Replay Jobs & `Remote_Fetch`, Bulk Campaign (`M04`), `M24-F08` Async Export, `M21`/`M22` batch import, `M18` BI tính toán nặng. **Cấm Lane 3 dùng chung worker/connection pool với Lane 1**; áp backpressure tự động giảm tải Lane 3 khi `oldest_pending_age` của Lane 1 tăng.

3. **Cập nhật Lease Fencing (`lease_token`) & Bảng Quyết định Reaper 8 Nhánh trên `Outbound_Intents` (`INT25`, `INV-08`, `W1-02`, `W1-03`):**
   - Bổ sung **6 cột Lease & Fencing bắt buộc** vào hợp đồng dữ liệu `Outbound_Intents`:
     - `lease_owner_id uuid NULL`: định danh worker instance đang giữ lease Pha 2.
     - `lease_token uuid NULL`: fencing token duy nhất sinh mới ở mỗi lần CAS claim sang `DISPATCHING`.
     - `last_attempted_lease_token uuid NULL`: lưu lại `lease_token` của lượt đã đóng dấu `http_attempted_at` thành công.
     - `lease_expires_at timestamptz NULL`: hạn tối đa của chu kỳ gọi mạng trước khi bị coi là hết lease.
     - `http_attempted_at timestamptz NULL`: timestamp được ghi nhận qua micro-commit CAS ngay trước khi worker mở socket gọi HTTP ra provider.
     - `pre_socket_reclaim_count int NOT NULL DEFAULT 0`: số lần bị Reaper thu hồi lease khi `http_attempted_at IS NULL` (chưa chạm mạng).
   - **Khóa CAS Fencing 3 Pha Chống Worker Cũ Sống Dậy Gửi Trùng (`W1-02`):**
     - **Pha 1 (Claim):** `UPDATE Outbound_Intents SET status = 'DISPATCHING', lease_owner_id = $worker_id, lease_token = $lease_token, lease_expires_at = $exp, row_version = row_version + 1 WHERE id = $id AND status IN ('QUEUED', 'RETRY_WAITING') AND row_version = $expected_version`.
     - **Pha 2 Micro-commit (Pre-Socket Stamp CAS):** Ngay trước khi mở socket HTTP, Worker bắt buộc chạy `UPDATE Outbound_Intents SET http_attempted_at = now(), last_attempted_lease_token = lease_token, row_version = row_version + 1 WHERE id = $id AND status = 'DISPATCHING' AND lease_owner_id = $worker_id AND lease_token = $lease_token AND lease_expires_at > now()`. **Chỉ khi `affected_rows == 1` mới được phát HTTP request**; nếu `affected_rows == 0` (đã hết hạn lease hoặc bị Reaper thu hồi), Worker phải hủy ngay trước khi mở socket.
     - **Pha 3 (Result Commit & Late-Response Merge):** Mở Tx mới, `INSERT INTO Send_Attempts` (gắn `attempt_no`, `lease_token`) và cập nhật `Outbound_Intents` kiểm tra `WHERE id = $id AND lease_token = $lease_token AND status = 'DISPATCHING'` (hoặc hợp nhất có điều kiện từ `UNKNOWN_OUTCOME -> ACCEPTED` khi `last_attempted_lease_token = $lease_token` và có `provider_message_id` `2xx` về muộn, tuyệt đối không ghi đè lượt xử lý mới hơn).
   - **Bảng Quyết định Reaper 8 Nhánh Dùng Chung đối với `DISPATCHING` quá hạn (`status = 'DISPATCHING' AND now() > lease_expires_at` — `W1-03`):**
     - **Nhánh 1–4 (`http_attempted_at IS NOT NULL` — bất kể TTL còn/hết hay `allow_auto_retry = true/false`):** Chuyển thẳng sang **`UNKNOWN_OUTCOME`** (xóa `lease_owner_id`/`lease_token`/`lease_expires_at`, giữ `last_attempted_lease_token`, đặt `allow_auto_retry = false`, đặt `reconcile_due_at = now() + 15m`, tăng `attempt_count = attempt_count + 1`). **Tuyệt đối KHÔNG retry mù** (`Master 2.5 L258`, `INT25`).
     - **Nhánh 5–6 (`http_attempted_at IS NULL` VÀ `now() >= expires_at` — chắc chắn chưa mở socket nhưng đã hết hạn TTL, bất kể `allow_auto_retry`):** Chuyển sang **`EXPIRED_CANCELLED`** (xóa lease, đặt `block_reason_code = 'INTENT_TTL_EXPIRED_BEFORE_SOCKET'`, giữ nguyên `attempt_count`).
     - **Nhánh 7 (`http_attempted_at IS NULL` VÀ `now() < expires_at` VÀ `allow_auto_retry = true` — chắc chắn chưa mở socket, còn TTL, cho phép auto-retry):** Nhả lease về **`RETRY_WAITING`** (tăng `pre_socket_reclaim_count = pre_socket_reclaim_count + 1`, đặt `next_attempt_at` theo backoff, **giữ nguyên `attempt_count` gọi provider**; nếu `pre_socket_reclaim_count > max_pre_socket_reclaims` [mặc định `3`] $\rightarrow$ chuyển `FAILED_TERMINAL` với `PRE_SOCKET_WORKER_CRASH_LIMIT`).
     - **Nhánh 8 (`http_attempted_at IS NULL` VÀ `now() < expires_at` VÀ `allow_auto_retry = false` — chắc chắn 100% chưa mở socket HTTP vì chưa qua micro-commit CAS, còn TTL, lệnh `allow_auto_retry = false`):** Nhả lease về **`QUEUED`** (tăng `pre_socket_reclaim_count = pre_socket_reclaim_count + 1`, giữ `attempt_count = 0`; nếu `pre_socket_reclaim_count > max_pre_socket_reclaims` [mặc định `3`] $\rightarrow$ chuyển `FAILED_TERMINAL` với `PRE_SOCKET_WORKER_CRASH_LIMIT` để chống vòng lặp nhận lại vô tận).

4. **Secret Vault Envelope & Tách DB Role (`INV-13`, `Master 2.4 L250`):**
   - Toàn bộ OAuth `access_token`, `refresh_token`, `webhook_secret`, `endpoint_lookup_hmac_key`, `deletion_ledger_hmac_key` nằm ở Vault/KMS (mã hóa envelope theo Tenant/Connection), **tuyệt đối không lưu plaintext vào PostgreSQL và không in ra log (`NFR11`)**.
   - Tách riêng các PostgreSQL role thực thi (tuyệt đối không bật `SUPERUSER` hay `BYPASSRLS` trên mọi role vận hành): `migration_owner_role` (chạy DDL qua CI/deploy), `app_runtime_role` (web API), `worker_runtime_role` (`M19`/`M23`/`M24` background jobs dưới `BindDbTransactionContext`), `privacy_erasure_system_role` (chỉ scrub có kiểm soát theo từng `deletion_ledger_id` trên `Task_Submissions` ngoài `Legal_Hold` với `redacted_deletion_ledger_ids[]` & `redacted_content_sha256` theo `ADR-004`), và **`maintenance_compliance_role`** (`NOINHERIT`, **chỉ** dùng trong bảo trì DR để `M20.VerifyPostRestoreComplianceGate` chạy fan-out theo `Tenants -> Workspaces` dưới `BindDbTransactionContext(workspace_type = 'SYSTEM', acting_mode = 'SYSTEM_WORKER')` qua `MAINTENANCE_COMPLIANCE_LOCK`).

5. **Rào An toàn Adapter, `PMS` & `TASK_SYNC` (`Master 2.5 L258`, `INV-03`, `INV-21`, `UC-W10`):**
   - **`allow_auto_retry = false` bắt buộc:** Với mọi intent có `risk_class IN ('PAYMENT_EXECUTION', 'PAYROLL_DISBURSEMENT', 'TAX_FILING', 'PAID_ZBS_TEMPLATE', 'IRREVERSIBLE_EXTERNAL_WRITE')`, nếu timeout/lỗi mơ hồ $\rightarrow$ chuyển ngay `UNKNOWN_OUTCOME` để đối soát (`INT25`).
   - **Read-Only Adapter Enforcement (`M21-F06`, `BR-P18`, `P-T17`):** Connection gắn `capability_profile = 'READ_ONLY_PARTNER_SYNC'` hoặc `M21 API_READ` bị chặn mọi HTTP write (`POST/PUT/PATCH/DELETE` ghi ngược) ở lớp Adapter (`422 READ_ONLY_ADAPTER_WRITE_FORBIDDEN`).
   - **Mở rộng `provider_category` & `TASK_SYNC` (`UC-W10`):** Bổ sung **`PMS`** vào `provider_category` (`MESSAGING | EMAIL | VOIP | PARTNER_POS_READ | ERP_FINANCE | HRM_DEVICE_OR_BANK | PMS`) và luồng **`TASK_SYNC`** hỗ trợ đồng bộ 2 chiều có thẩm quyền theo từng field cho `M16` (`W-O05`, phát hiện xung đột chuyển `CONFLICT`, cấm last-write-wins `INV-03`, chặn echo loop `W-T33`), **vẫn giữ nguyên tắc `M19` chỉ lo cầu nối tích hợp ngoài và KHÔNG làm Internal Outbox của `M16`/`M23-F12`**.

## So sánh

- **Để `DISPATCHING` không có `lease_expires_at` / `http_attempted_at` hoặc cho `M19` ôm Internal Outbox:** Một worker sập giữa Pha 2 sẽ khóa kẹt intent vô thời hạn (hoặc reaper vô tình gửi lặp tin/lệnh tiền đã rời mạng); và trộn Outbox nội bộ vào `M19` gây nghẽn sự kiện domain khi Backfill đối tác quá tải. Thiết kế Lease 3 cột + Dual Outbox tách biệt xử lý triệt để cả hai rủi ro.

## Hệ quả và điều kiện thay đổi

- Cập nhật [M19-INTEGRATION-ADAPTERS-OUTBOX.md](../../02-specs/modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md) (`4.2`, `4.3`, `5.2`), [M19-DURABLE-INGEST-OUTBOX.md](../../02-specs/contracts/M19-DURABLE-INGEST-OUTBOX.md), [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), `C23`, [M24-PERFORMANCE-AND-PRODUCTIVITY.md](../../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md), `C24`, [M16-WORK-PROJECTS-TASK-CORE.md](../../02-specs/modules/M16-WORK-PROJECTS-TASK-CORE.md) (`UC-W10` `CONFLICT`), và [INDEX.md](../INDEX.md).
