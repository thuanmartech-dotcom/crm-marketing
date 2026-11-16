# ADR-005 — Dual Outbox, Cô lập 3 Làn Queue (`M24-F07`), Secret Vault & Guard `API_READ` / Giao dịch Tài chính

**Status:** `Approved (Proposed Extension trong Baseline v1.9 — Logical PG/Modular Monolith Architecture)`  
**Phạm vi:** `M19` (`C19`), `M23-F12`, `M24-F07`, `M21-F06` (`INV-21`), `M09`, `M22-F10/28`, `SL01`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`2.4 L250`, `2.5 L258`, `2.6 L272`, `5.16 L2816–2829`, `7.6 L3312–3319`, `ONFR02`, `ONFR05`, `H-NFR08`), [INVARIANTS.md](../INVARIANTS.md) (`INV-06`, `INV-07`, `INV-08`, `INV-13`, `INV-21`, `INV-23`)

---

## Context

1. `SL01-INTERNAL-WORK.md` (`L96`) vẫn trỏ Outbox/DLQ nội bộ cho `M16` vào `M19`, trong khi `INDEX.md L123` & `INV-23` phân tách `M19` (tích hợp kênh ngoài) với `M23-F12` (hệ thống Outbox/DLQ nội bộ).
2. `M19-F06` (Backfill 30 ngày), `M19-F08` (Replay + Remote Fetch 25MB) và gửi chiến dịch hàng loạt đang dùng chung worker pool với `M19-F04` webhook live — đe dọa SLO `ONFR02 p95 <= 1s` (`NFR04 <= 2s`).
3. `M19-F05` áp mặc định backoff retry `[1, 5, 15, 60]` phút mà thiếu cờ `allow_auto_retry = false` cho giao dịch tiền/chi lương/tin trả phí (vi phạm `Master 2.5 L258`), và thiếu rào chặn lệnh ghi ở tầng Adapter cho chế độ `API_READ` (`M21-F06`, `P-T17`, `INV-21`).

## Đề nghị

1. **Dual Outbox Boundary (`INV-23`, tách dứt khoát tại cấp Database & Topic):**
   - **External Integration Platform (`M19`):** Chỉ quản lý `Channel_Connections`, `Inbound_Events`, `Outbound_Intents`, `Send_Attempts`, `Message_Status_Events`, `Email_Delivery_Events` ingest, `Sync_Checkpoints/Runs`, `Quarantined_Events`, `Adapter_Dead_Letter_Queue`, `Replay_Jobs` cho **giao tiếp với hệ thống bên ngoài** (Zalo, Meta, TikTok, Telegram, Email, VoIP, POS `API_READ`, thiết bị chấm công/ngân hàng/ERP/Payment Gateway).
   - **Internal Domain Outbox & DLQ (`M23-F12`):** Quản lý bảng `Internal_Outbox_Events` + `Internal_Dead_Letter_Queue` cho toàn bộ sự kiện liên module nội bộ (`M14.*`, `M16.*`, `M20.*`, `M22.*`, Notification `M24-F05`, BI projection `M18`) và diễn tập Backup Drill logs. Mọi domain module publish vào `Internal_Outbox_Events` trong cùng DB transaction nghiệp vụ (`INV-06`).
2. **Cô lập 3 Làn Queue (`M24-F07` Logic — Tương thích PG Worker Pools theo `ADR-001`):**
   - **Lane 1 (`REALTIME_CRITICAL`):** `M19-F04` Live Webhook Ingest-Before-ACK (`ONFR02 p95 <= 1s`) & trả lời trực tiếp Agent Inbox (`M03`, `ONFR01 <= 5s`).
   - **Lane 2 (`STANDARD_INTERACTIVE`):** Sự kiện nội bộ `M23-F12`, đẩy cập nhật UI/360, gửi đơn lẻ transactional (`Ticket`, `Appointment`, `OTP/CSKH`).
   - **Lane 3 (`HEAVY_BATCH_BACKFILL`):** `M19-F06` Sync/Backfill nhiều ngày, `M19-F08` Replay Jobs, `M19-F08` `Remote_Fetch`, Bulk Campaign (`M04`), `M24-F08` Async Export, `M21` file/batch sync. **Cấm Lane 3 dùng chung worker/connection pool với Lane 1**; áp backpressure tự động giảm tải Lane 3 khi `oldest_pending_age` của Lane 1 tăng.
3. **Secret Vault Envelope & Tách DB Role (`INV-13`, `Master 2.4 L250`):**
   - Toàn bộ OAuth `access_token`, `refresh_token`, `webhook_secret`, signing key nằm ở Vault/KMS (mã hóa envelope theo Tenant/Connection), **tuyệt đối không lưu plaintext vào PostgreSQL và không in ra log (`NFR11`)**.
   - Tách riêng 3 PostgreSQL role: `migration_owner_role` (chạy DDL qua CI/deploy), `app_runtime_role` (web API), `worker_runtime_role` (`M19`/`M23`/`M24` background jobs — không `BYPASSRLS`, luôn gắn `BindDbTransactionContext`).
4. **Rào An toàn Adapter (`Master 2.5 L258` & `INV-21`):**
   - **`allow_auto_retry = false` bắt buộc:** Với mọi intent có `risk_class IN ('PAYMENT_EXECUTION', 'PAYROLL_DISBURSEMENT', 'TAX_FILING', 'PAID_ZBS_TEMPLATE', 'IRREVERSIBLE_EXTERNAL_WRITE')`, nếu timeout/lỗi mơ hồ $\rightarrow$ chuyển ngay `UNKNOWN_OUTCOME` để đối soát (`INT25`), **tuyệt đối không tự động retry mù**.
   - **Read-Only Adapter Enforcement (`M21-F06`, `BR-P18`, `P-T17`):** Connection gắn `capability_profile = 'READ_ONLY_PARTNER_SYNC'` hoặc `M21 API_READ` bắt buộc kiểm allowlist HTTP method/operation tại lớp Adapter trước khi phát mạng (`GET`/read endpoint đã khai báo) — từ chối cứng `POST/PUT/PATCH/DELETE` ghi ngược ngay cả khi credential phía đối tác được cấp quyền rộng.
   - **Non-Messaging Connector Scope (`O04/O06/O08`):** Khai báo rõ `provider_category` (`MESSAGING | EMAIL | VOIP | PARTNER_POS_READ | ERP_FINANCE | HRM_DEVICE_OR_BANK`) để áp đúng versioning, quarantine, và `allow_auto_retry` mà không ép chung vào khung tin nhắn khách hàng.

## So sánh

- **Cho `M19` ôm cả Outbox nội bộ như `SL01` cũ:** Khi một đợt Backfill Facebook/Email hay lỗi DLQ đối tác xảy ra, việc trộn bảng/worker sẽ làm nghẽn sự kiện bàn giao/quyền nội bộ (`M14`/`M20`) và vi phạm `INV-23`.

## Hệ quả và điều kiện thay đổi

- Cập nhật [M19-INTEGRATION-ADAPTERS-OUTBOX.md](../../02-specs/modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md) (`4.2`, `4.3`, `5.2`), [M19-DURABLE-INGEST-OUTBOX.md](../../02-specs/contracts/M19-DURABLE-INGEST-OUTBOX.md), [INDEX.md](../INDEX.md) và vá ghi chú delta cho [SL01-INTERNAL-WORK.md](../../02-specs/slices/SL01-INTERNAL-WORK.md) + [M24-PERFORMANCE-AND-PRODUCTIVITY.md](../../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md).
