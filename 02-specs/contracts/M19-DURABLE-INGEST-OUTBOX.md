# Contract `M19-DURABLE-INGEST-OUTBOX` — Cổng Tiếp nhận Bền vững, Điều phối Gửi tin Ngoài, Backfill/Replay, Zero-Trust Media Fetch & Bàn giao Offboarding

- **Contract ID:** `CONTRACT-M19-INTEGRATION-OUTBOX-v1.2`
- **Provider Owner:** `M19` (**Chỉ cho Tích hợp Kênh ngoài, PMS `UC-W10`, POS `API_READ`, ERP/Payment/HRM Devices** — không dùng cho Internal Domain Outbox `M23-F12` theo `ADR-005`)
- **Consumers:** `M01`, `M02`, `M03`, `M04`, `M09`, `M11`, `M12`, `M13`, `M14` (`M14-F06` Offboarding), `M16` (`PMS sync UC-W10`), `M18`, `M20`, `M21` (`API_READ`), `M22` (`M22-F10` thiết bị chấm công & `M22-F28` ngân hàng chi lương), `M23` (`M23-F08` Security/Ops Alerts, `M23-F12` Platform Health/DR)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`2.4–2.7`, `3.12.5`, `3.12.11–12`, `4.23 UC-W10`, `5.16 L2816–2829`, `5.17 L2845–2848`, `5.18 L2893/2897`, `7.6 ONFR01–06`, `9.16 W-T32/33`, `Phụ lục E CR11/CR12`, `Phụ lục G L4713`, `OC01`, `OC05`, `OC06`, `OC07`, `OC08`, `OC14`, `OC19`, `INT15`, `INT25`, `SEC-U01`, `SEC-U02`, `SEC-U04`, `H-NFR08`), [ADR-002](../../01-architecture/decisions/ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-004](../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-005](../../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](../../01-architecture/decisions/ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-008](../../01-architecture/decisions/ADR-008-OMNICHANNEL-CONTRACTS-RECEIPTS-AND-CROSS-EVENTS.md), [ADR-009](../../01-architecture/decisions/ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md), [M14-PRINCIPAL-ACCESS-DECISION.md](M14-PRINCIPAL-ACCESS-DECISION.md), [M16-TASK-CORE-COMMANDS.md](M16-TASK-CORE-COMMANDS.md), [M20-SUPPRESSION-PRIVACY-GATE.md](M20-SUPPRESSION-PRIVACY-GATE.md)
- **Trạng thái:** `Reviewed (CR-20261116-WAVE1-RECONCILIATION Applied; CR-20261116-WAVE1-5-HARDENING Applied; CR-20261116-WAVE1-REVIEW-FIXES Applied; CR-20261116-SKILL-TEMPLATE-ALIGN Applied)`
- **Approved_Scope:** `Wave 1/1.5 External Durable Ingest & Outbox Dispatch Public Contract`
- **Approved_By:** `Chủ dự án`
- **Decision_Ref:** `CR-20261116-SKILL-TEMPLATE-ALIGN`
- **Approved_At:** `2026-11-16`
- **Chính sách Breaking Change:** Mọi thay đổi schema payload hoặc tập `channel`/`provider` phải giữ tương thích ngược cho `Inbound_Events` / `Outbound_Intents` đang tồn đọng (`replay_compatible = true`) và cập nhật đồng thời `M03`, `M14`, `M16`, `M20`, `M21`.

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | Chuẩn hóa **5 trụ cột/cổng tích hợp ngoài** + **1 cổng bàn giao Offboarding** của `M19`: (1) `IngestWebhookEvent` (`Durable-Before-ACK` tại Lane 1 `REALTIME_CRITICAL`, phân giải scope qua Bootstrap `SECURITY DEFINER` Port `C14.ResolveConnectionScopeByWebhookEndpoint` trước `BindDbTransactionContext` đủ 6 GUC, giữ `Inbound_Event_Dedup_Keys` chống replay vượt mốc purge 30 ngày), (2) `EnqueueOutboundIntent` (tạo ý định gửi nguyên tử trong transaction domain, hỗ trợ `actor_type`, `hmac_key_version`, thông số `vendor_code` / `processing_record_id` / `data_classes[]`, PMS `TASK_SYNC` & `SCHEDULED_INTENT`), (3) `DispatchOutboundIntent` (điều phối gửi không giữ DB lock, recheck `M14` + `M20.EvaluateOutboundCompliance` qua `endpoint_hashes_by_version[]` + `M20.EvaluateVendorAndAiTransfer` cho `M19_EXTERNAL_WEBHOOK`/`REMOTE_VENDOR_API`, lease + `http_attempted_at` chống requeue mù sau crash, khóa `allow_auto_retry = false` cho giao dịch tiền/phí, trạng thái `CONFLICT` cho PMS `W-T32`), (4) `ExecuteSafeRemoteFetch` (tải media từ xa Zero-Trust đọc giới hạn động từ `M23.Policy_Versions`, chặn `WEB_FORM`, cấp `asset_version_id` `PENDING` ngay từ đầu tại Lane 3), (5) `ReplayConnectionEvents` (`POST /v1/connections/{id}/replay` — `CONTRACT-L2845`: replay giới hạn thời gian, `DRY_RUN -> EXECUTE`, audit & qua lại dedup/ACL), và (6) `ListOpenIntentsForPrincipal` (liệt kê `SCHEDULED_INTENT`, `CHANNEL_CONNECTION_OWNER`, `ADAPTER_DLQ_OWNER` cho `M14-F06` tách `owner_user_id` khỏi `actor_id` gốc `INT15`). |
| **Actor/scope** | `External Provider Webhook` (qua route `/v1/webhooks/{provider}/{webhook_endpoint_token}` hoặc resolver kiểm chữ ký) và `Authenticated Internal Service / Worker` (`M03`, `M04`, `M12`, `M14-F06`, `M16` PMS sync, `M21`, `M22`, `M09`), hỗ trợ `actor_type: USER | SERVICE_PRINCIPAL | PORTAL_CLIENT`. Dưới `FORCE RLS` (`ADR-002`), webhook endpoint gọi trước Bootstrap `SECURITY DEFINER` Port **`C14.ResolveConnectionScopeByWebhookEndpoint(provider, provider_namespace, webhook_endpoint_token [nullable])`** trả về đủ **`(connection_id, tenant_id, workspace_id, workspace_type, connection_status, acting_principal_id, permission_version)`** rồi gọi ngay **`M14.BindDbTransactionContext(tenant_id, workspace_id, workspace_type, acting_principal_id, permission_version, 'SYSTEM_WORKER', correlation_id)`** (**đủ 6 GUC + `correlation_id`** theo `C14`) trước mọi thao tác đọc/ghi bảng `Nhóm A/C` — **tuyệt đối không tin `workspace_id` từ webhook ngoài (`INV-07`)**. |
| **Preconditions** | `Channel_Connections` có trạng thái `ACTIVE` và `requires_reauth = false` (chặn `REAUTHORIZATION_REQUIRED -> PAUSED -> ACTIVE` qua `ResumeConnection` cho tới khi hoàn tất `CompleteReconnectOAuth`; riêng `Processing_Records` bên `M20` phải đạt `ACTIVE` trước khi bật kết nối `Master 6.3 L3159`); `Connection_Capabilities` đạt `CAPABILITY_VERIFIED` cho hành động tương ứng (`OM-G01`, `OC15`); kết nối `API_READ` (`M21-F06`) bị khóa allowlist chỉ đọc (`INV-21`). **Khóa chống Cướp Webhook Xuyên Tenant (`SEC-U02`, `ADR-008`):** `UNIQUE (provider, provider_namespace, external_account_id) WHERE status IN ('ACTIVE', 'DEGRADED', 'REAUTHORIZATION_REQUIRED', 'PAUSED')` (toàn cục xuyên Tenant) **VÀ** `webhook_endpoint_token char(64) NN UNIQUE`. `ExecuteSafeRemoteFetch` **cấm tuyệt đối kích hoạt từ `provider = 'WEB_FORM'`**. |
| **Input** | Xem 6 cặp Input JSON Schema đầy đủ ở Mục 2 (`12 JSON Schemas`): `IngestWebhookEventInput`, `EnqueueOutboundIntentInput`, `DispatchOutboundIntentInput`, `ExecuteSafeRemoteFetchInput`, `ReplayConnectionEventsInput`, `ListOpenIntentsForPrincipalInput`. |
| **Output** | Xem 6 Output JSON Schema đầy đủ ở Mục 2: `InboundIngestAck`, `EnqueueOutboundIntentOutput`, `OutboundDispatchResult`, `RemoteFetchResult`, `ReplayConnectionEventsOutput`, `ListOpenIntentsForPrincipalOutput`. |
| **Errors** | Chuẩn Error Envelope `{code, message, field_errors, correlation_id}`. Mã lỗi chính: `401 INGEST_SIGNATURE_INVALID`; `403 BREAK_GLASS_REQUIRED`; `409 CONNECTION_OWNERSHIP_CONFLICT` (non-disclosure xuyên Tenant/Workspace `SEC-U02`), `409 AUTH_PERMISSION_VERSION_STALE` (từ `M14`), `409 IDEMPOTENCY_PAYLOAD_CONFLICT`, `409 PMS_VERSION_OR_STATE_CONFLICT` (`W-T32`); `422 CAPABILITY_NOT_VERIFIED`, `422 READ_ONLY_ADAPTER_WRITE_FORBIDDEN`, `422 PRIVACY_PURPOSE_UNAPPROVED` (`M20.Processing_Records` chưa `ACTIVE`), `422 VENDOR_TRANSFER_POLICY_BLOCKED`, `422 PROHIBITED_DATA_CLASS_INCLUDED` (từ `M20.EvaluateVendorAndAiTransfer`), `422 REAUTHORIZATION_REQUIRED` (chặn `ResumeConnection` khi `requires_reauth = true`), `422 EGRESS_SSRF_BLOCKED`, `422 WEB_FORM_REMOTE_FETCH_FORBIDDEN`, `422 MEDIA_SIZE_OR_MIME_EXCEEDED`, `422 DRY_RUN_REQUIRED`, plus mọi mã chặn từ `M20` (`OUTBOUND_SUPPRESSED_UNSUBSCRIBE | OUTBOUND_SUPPRESSED_CONSENT_REVOKED | OUTBOUND_SUPPRESSED_HARD_BOUNCE | OUTBOUND_SUPPRESSED_SOFT_BOUNCE_COOLDOWN | OUTBOUND_SUPPRESSED_SPAM_COMPLAINT | OUTBOUND_SUPPRESSED_REFUSED_CALLBACK | OUTBOUND_SUPPRESSED_MANUAL_DNC | OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD`); `429 PROVIDER_RATE_LIMITED`; `503 DURABLE_WRITE_UNAVAILABLE` (cấm trả `2xx` ACK khi ghi DB thất bại `ONFR02`). |
| **Concurrency** | **Tuyệt đối không giữ DB lock khi gọi HTTP ra ngoài (`INV-06`).** Áp dụng optimistic locking (`row_version` + CAS `QUEUED/RETRY_WAITING -> DISPATCHING`) kèm **`lease_owner_id` + `lease_token` (fencing token duy nhất) + `lease_expires_at` + `http_attempted_at`** để chỉ 1 worker thực thi một `Outbound_Intent` tại một thời điểm (`INV-09`, `W1-02`). **Micro-commit trước khi mở socket HTTP bắt buộc kiểm tra CAS `WHERE id = $1 AND status = 'DISPATCHING' AND lease_owner_id = $2 AND lease_token = $3 AND lease_expires_at > now()`** (nếu `affected_rows == 0`, worker phải dừng ngay trước HTTP); Pha 3 ghi kết quả kiểm tra khớp `lease_token` (hoặc hợp nhất có điều kiện từ `UNKNOWN_OUTCOME -> ACCEPTED` khi kết quả `2xx` về muộn khớp `last_attempted_lease_token`). **Bảng Quyết định Reaper 8 Nhánh (`status = 'DISPATCHING' AND now() > lease_expires_at`, `ADR-005`, `W1-03`):** (1) nếu `http_attempted_at IS NOT NULL` (bất kể TTL hay `allow_auto_retry`) $\rightarrow$ **bắt buộc chuyển `UNKNOWN_OUTCOME`** (`allow_auto_retry = false`, `reconcile_due_at`, tăng `attempt_count`, cấm đẩy về `QUEUED`/`RETRY_WAITING` mù); (2) nếu `http_attempted_at IS NULL` và `now() >= expires_at` $\rightarrow$ **`EXPIRED_CANCELLED`** (`INTENT_TTL_EXPIRED_BEFORE_SOCKET`); (3) nếu `http_attempted_at IS NULL` và `now() < expires_at` và `allow_auto_retry = true` $\rightarrow$ **`RETRY_WAITING`** (tăng `pre_socket_reclaim_count <= 3`, giữ nguyên `attempt_count`); (4) nếu `http_attempted_at IS NULL` và `now() < expires_at` và `allow_auto_retry = false` $\rightarrow$ **`QUEUED`** (vì chắc chắn 100% chưa mở socket, tăng `pre_socket_reclaim_count <= 3`, giữ `attempt_count = 0`; vượt `3` lần chuyển `FAILED_TERMINAL` `PRE_SOCKET_WORKER_CRASH_LIMIT`). `Send_Attempts` chỉ `INSERT` một lần tại Pha 3 sau khi HTTP hoàn tất. `Message_Status_Events` tiếp nhận webhook receipt đến sớm trước khi Pha 3 commit `ACCEPTED` (neo theo `provider_message_id`) và giảm trạng thái đơn điệu (hỗ trợ cả `DELIVERED/READ -> COMPLAINED/FAILED`). |
| **Idempotency** | `Inbound_Events` & `Inbound_Event_Dedup_Keys`: **`UNIQUE (tenant_id, connection_id, event_key)`** (`ON CONFLICT (tenant_id, connection_id, event_key) DO NOTHING`), trong đó `Inbound_Event_Dedup_Keys` lưu `event_key` & `occurred_at` lâu hơn `timestamp_skew` và tách khỏi việc xóa raw `payload_ref` sau 30 ngày (`GAP-M19-08`) để chặn replay webhook thanh toán/đơn hàng cũ; riêng status-update event dùng `Message_Status_Events` `UNIQUE (tenant_id, connection_id, provider_event_id, receipt_status)` per `5.17 L2848`. `Outbound_Intents`: **`UNIQUE (tenant_id, workspace_id, idempotency_key)`** (`OC05`) — cùng key khác payload trả `409 IDEMPOTENCY_PAYLOAD_CONFLICT`. `ListOpenIntentsForPrincipal` thuần đọc, phân trang cursor tất định. |
| **Transaction** | `IngestWebhookEvent`: gọi `C14.ResolveConnectionScopeByWebhookEndpoint(provider, provider_namespace, webhook_endpoint_token [nullable])` (`SECURITY DEFINER`) nhận `(connection_id, tenant_id, workspace_id, workspace_type, connection_status, acting_principal_id, permission_version)` $\rightarrow$ gọi ngay `M14.BindDbTransactionContext(tenant_id, workspace_id, workspace_type, acting_principal_id, permission_version, 'SYSTEM_WORKER', correlation_id)` (**6 GUC + `correlation_id`**) $\rightarrow$ commit `Inbound_Events` + `Inbound_Event_Dedup_Keys` + `Internal_Outbox_Events` (`M19.InboundEventPersisted`) xong mới trả `2xx` ACK (`ONFR02`). `EnqueueOutboundIntent`: commit chung 1 DB transaction với bản ghi nguồn (`INV-06`). `DispatchOutboundIntent`: Pha 1 claim `CAS` + gắn `lease_owner_id`/`lease_token`/`lease_expires_at` và nhả transaction $\rightarrow$ Pha 2 check `M14` (`actor_type`) + `M20` (`EvaluateOutboundCompliance` với `endpoint_hashes_by_version[]` + `EvaluateVendorAndAiTransfer` khi truyền bên thứ 3), thực thi **micro-commit CAS `http_attempted_at = now()` kiểm khớp `(status = 'DISPATCHING', lease_owner_id, lease_token, lease_expires_at > now())`** trước khi mở socket HTTP và đóng DB Tx trước khi gọi mạng $\rightarrow$ Pha 3 mở Tx mới `INSERT Send_Attempts` (gắn `lease_token`) + cập nhật `Outbound_Intents` (CAS `lease_token`, xóa lease) + event kết quả. |
| **Compatibility** | Hỗ trợ đồng thời nhiều version adapter và tra cứu đa phiên bản khóa `hmac_key_version` (`ACTIVE + VERIFY_ONLY` qua `endpoint_hashes_by_version[]` theo `ADR-007`); hỗ trợ `M16` PMS sync (`UC-W10`, `W-T32/33`, `CONFLICT`). **Tuyệt đối tuân thủ lệnh cấm giả định trong Master `3.12.12` & `Phụ lục G`**: thuật toán xác minh webhook Zalo (`ZALO_OA`) và bộ Meta Message Tags (`FACEBOOK_PAGE`) đánh dấu `UNVERIFIED_UNTIL_POC` (`Fail-Closed` nếu bật cờ live mà chưa có contract xác minh PoC, `GAP-M19-03/04`). |
| **Audit/privacy** | Không lưu token, secret hay PII nội dung tin nhắn thô trong `Send_Attempts` (`5.16 L2826`) và logs (`NFR11`); lưu `endpoint_masked_redacted` có kiểm soát thay PII thô. Lưu `subject_hmac_sha256` & `endpoint_lookup_hash` (từ payload đã xác minh) trên `Inbound_Events` & `Quarantined_Events` để `M20.SubjectErasureExecuted` (`erased_subject_refs[]`) tìm và xóa sạch `Inbound_Events`, `Quarantined_Events`, `Adapter_Dead_Letter_Queue`. Bàn giao `M14-F06` tách `owner_user_id` khỏi `actor_id` gốc (`INT15`). Xem raw payload trong `Quarantined_Events` / `Adapter_Dead_Letter_Queue` bắt buộc `Break-glass` Grant (`M14`/`M23-F03`, `INV-22`). |
| **Tests** | `M19-AC01..03`, `SEC-U01`, `SEC-U02`, `SEC-U04`, `OC01`, `OC05`, `OC06`, `OC07`, `OC08`, `OC09`, `OC13`, `OC14`, `OC15`, `OC16`, `OC17`, `OC19`, `OC21`, `OC22`, `INT15`, `INT23`, `INT24`, `INT25`, `INT26`, `ONFR01..06`, `OM-G01`, `OM-G02`, `OM-G08`, `P-T17`, `RV15`, `RV17`, `W-T32`, `W-T33`, `CR11`, `CR12`. Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas Đầy đủ cho 5 Cổng/Lệnh Tích hợp Ngoài & Cổng Bàn giao Offboarding (`12 JSON Schemas`)

### 2.1. Trụ cột 1 — `IngestWebhookEventInput` & `InboundIngestAck`

```json
{
  "IngestWebhookEventInput": {
    "provider": "ZALO_OA | FACEBOOK_PAGE | TIKTOK_BM | TELEGRAM | GMAIL | MS_GRAPH | WEB_FORM | VOIP_SIP | PAYMENT_GW | PANCAKE | ERP_MISA | PMS | BIOMETRIC_DEVICE | PAYROLL_BANK",
    "provider_namespace": "string (NN — OA ID / Page ID / Bot ID / Mailbox / Shop ID)",
    "webhook_endpoint_token": "string | null (char(64) NN khi route qua /v1/webhooks/{provider}/{webhook_endpoint_token}; null chỉ khi provider dùng app-level URL và giải bằng resolver kiểm chữ ký qua provider + provider_namespace)",
    "signature_headers": "object (header xác minh theo adapter manifest đã verify; Zalo để adapter_verifier_pending_poc cho tới khi hoàn tất PoC)",
    "raw_body_ref": "string (reference tới payload thô được bảo vệ/mã hóa trước parse sâu)",
    "event_key": "string (NN — canonical provider event key dùng chống trùng)",
    "event_type": "INBOUND_MESSAGE | STATUS_RECEIPT | EMAIL_BOUNCE_OR_COMPLAINT | CALL_CDR | LEAD_FORM | ORDER_SYNC | PAYMENT_CALLBACK | TASK_SYNC | ATTENDANCE_PUNCH | PAYROLL_BATCH_STATUS",
    "source_domain_ref": "string | null (tùy chọn cho TASK_SYNC / PMS UC-W10)",
    "external_task_id": "string | null (tùy chọn cho TASK_SYNC / PMS UC-W10)",
    "external_version": "string | null (tùy chọn cho TASK_SYNC / PMS UC-W10)",
    "echo_operation_key": "string | null (khóa chống echo hai chiều W-T33 cho TASK_SYNC)",
    "occurred_at": "timestamptz | null",
    "received_at": "timestamptz (UTC, server time NN)",
    "source_mode": "LIVE | BACKFILL | REPLAY",
    "correlation_id": "uuid (NN)"
  },
  "InboundIngestAck": {
    "accepted": "boolean (true sau COMMIT DB)",
    "http_status": "integer (200 | 202 — 200 OK cho provider đòi ACK đồng bộ, 202 Accepted khi xếp tiếp xử lý nền)",
    "ingest_status": "PERSISTED_DURABLE | DUPLICATE_NOOP | QUARANTINED",
    "inbound_event_id": "uuid | null",
    "quarantined_event_id": "uuid | null",
    "connection_id": "uuid",
    "correlation_id": "uuid"
  }
}
```

**Ví dụ (`Example`) `IngestWebhookEventInput` & `InboundIngestAck`:**

```json
{
  "ExampleIngestWebhookEventInput": {
    "provider": "ZALO_OA",
    "provider_namespace": "oa_99887766",
    "webhook_endpoint_token": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    "signature_headers": {
      "x-event-source": "adapter_verifier_pending_poc"
    },
    "raw_body_ref": "vault://inbound-raw/2026/11/16/evt-1001.enc",
    "event_key": "zalo:msg:evt_1001",
    "event_type": "INBOUND_MESSAGE",
    "occurred_at": "2026-11-16T09:30:00Z",
    "received_at": "2026-11-16T09:30:01Z",
    "source_mode": "LIVE",
    "correlation_id": "55555555-5555-4555-8555-555555555555"
  },
  "ExampleInboundIngestAck": {
    "accepted": true,
    "http_status": 200,
    "ingest_status": "PERSISTED_DURABLE",
    "inbound_event_id": "66666666-6666-4666-8666-666666666666",
    "quarantined_event_id": null,
    "connection_id": "77777777-7777-4777-8777-777777777777",
    "correlation_id": "55555555-5555-4555-8555-555555555555"
  }
}
```

> **Bootstrap `FORCE RLS` & SQL Bền vững Chuẩn hóa:**  
> 1. **Gỡ Deadlock `FORCE RLS`:** Trước mọi truy vấn bảng `Nhóm A/C`, webhook handler gọi Bootstrap `SECURITY DEFINER` Port **`C14.ResolveConnectionScopeByWebhookEndpoint(provider, provider_namespace, webhook_endpoint_token [nullable])`** (hoặc resolver kiểm chữ ký đối với app-level webhook) để nhận đủ **`(connection_id, tenant_id, workspace_id, workspace_type, connection_status, acting_principal_id, permission_version)`** $\rightarrow$ gọi ngay **`M14.BindDbTransactionContext(tenant_id, workspace_id, workspace_type, acting_principal_id, permission_version, 'SYSTEM_WORKER', correlation_id)`** (**đủ 6 GUC `SET LOCAL` + `correlation_id`** theo `C14`).  
> 2. **Kiểm `timestamp_skew` & Ghi bền Dedup Dài hạn:** Kiểm tra sai lệch `timestamp_skew` (nếu có chữ ký thời gian); đồng thời chèn bảng dedup tách rời **`Inbound_Event_Dedup_Keys`** (`INSERT INTO inbound_event_dedup_keys (id, tenant_id, workspace_id, connection_id, event_key, event_type, occurred_at, dedup_retain_until, ...) VALUES (...) ON CONFLICT (tenant_id, connection_id, event_key) DO NOTHING;`) giữ `event_key` & `occurred_at` lâu hơn `timestamp_skew` và lâu hơn mốc xóa raw `payload_ref` 30 ngày (`GAP-M19-08`) để chặn replay webhook thanh toán/đơn hàng cũ, cùng `INSERT INTO inbound_events (...) ON CONFLICT (tenant_id, connection_id, event_key) DO NOTHING;`. Trích xuất `subject_hmac_sha256` & `endpoint_lookup_hash` (từ payload đã xác minh) lưu vào `Inbound_Events` / `Quarantined_Events` phục vụ `M20.SubjectErasureExecuted` (`erased_subject_refs[]`).  
> 3. **Tách Status/Bounce & Hỗ trợ Receipt Đến sớm:** Nếu là `STATUS_RECEIPT` hoặc `EMAIL_BOUNCE_OR_COMPLAINT`, ghi tách vào `Message_Status_Events` (`UNIQUE (tenant_id, connection_id, provider_event_id, receipt_status)`) / `Email_Delivery_Events` (`5.17 L2848`); hỗ trợ ghi nhận trực tiếp receipt đến sớm (kể cả `DELIVERED/READ/COMPLAINED/FAILED`) theo `provider_message_id` trước khi Pha 3 `DispatchOutboundIntent` kịp commit `ACCEPTED`, và hỗ trợ chuyển tiếp `DELIVERED/READ -> COMPLAINED/FAILED`.

### 2.2. Trụ cột 2A — `EnqueueOutboundIntentInput` & `EnqueueOutboundIntentOutput` (Chạy trong Transaction Nghiệp vụ)

```json
{
  "EnqueueOutboundIntentInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "connection_id": "uuid (NN)",
    "actor_id": "uuid (NN — actor gốc khởi tạo, bất biến theo INT15)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "owner_user_id": "uuid | null (người phụ trách xử lý SCHEDULED_INTENT có thể bàn giao qua M14-F06, tách khỏi actor_id gốc INT15)",
    "expected_permission_version": "integer (bigint NN)",
    "idempotency_key": "uuid (NN — UNIQUE (tenant_id, workspace_id, idempotency_key))",
    "message_id": "uuid | null (FK Messages theo Master 5.16 L2825 cho tin nhắn CRM)",
    "source_domain_ref": "string (NN — ví dụ m03_message / m04_step / m12_survey / m16_task / m09_payment / m22_payout)",
    "channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK (API/ERP/Bank/POS/PMS dùng WEBHOOK; VoIP dùng VOICE_CALL)",
    "purpose_code": "string (max 80 chars, khớp Master 5.9)",
    "message_category": "TRANSACTIONAL_TICKET_OR_APPOINTMENT | SERVICE_REPLY | MARKETING_PROMO | SURVEY_VOC | AUTOMATED_JOURNEY | TASK_SYNC | SYSTEM_SYNC",
    "vendor_code": "string | null (chuẩn hóa ánh xạ từ provider -> vendor_code cho M20.EvaluateVendorAndAiTransfer; bắt buộc NN khi gửi qua EXTERNAL_WEBHOOK / ERP / Bank / PMS / REMOTE_VENDOR_API)",
    "processing_record_id": "uuid | null (ref M20.Processing_Records; bắt buộc NN khi kiểm M20.EvaluateVendorAndAiTransfer)",
    "source_resource_type": "string | null (khớp resource_type trong C14, ví dụ MESSAGE | PAYMENT | PAYROLL | TASK | INVOICE_LINE)",
    "source_resource_id": "uuid | null",
    "data_classes": [
      "PUBLIC_META | INTERNAL_NOTES | CONVERSATION_TEXT | CONTACT_PII_PHONE_EMAIL | NATIONAL_ID_CCCD | BANK_ACCOUNT_OR_PAYMENT | HRM_PAYROLL | CALL_RECORDING_RAW"
    ],
    "payload_provenance": "INTERNAL_SYSTEM | CUSTOMER_MESSAGE | EXTERNAL_ATTACHMENT_TEXT | null (mặc định INTERNAL_SYSTEM)",
    "contact_id": "uuid | null",
    "sender_profile_id": "uuid | null",
    "endpoint_lookup_hash": "string (char(64) NN — với API hệ thống ERP/Bank/PMS phi cá nhân không gắn contact/người nhận thì truyền canonical system-endpoint HMAC)",
    "hmac_key_version": "string (varchar(30) NN — phiên bản khóa HMAC tạo endpoint_lookup_hash)",
    "endpoint_hashes_by_version": [
      {
        "hmac_key_version": "string",
        "hash": "string (char(64) NN — khớp trường hash của C20.EvaluateOutboundComplianceInput)"
      }
    ],
    "endpoint_masked_redacted": "string | null (chuỗi che một phần thay PII thô để hiển thị/chuyển tiếp M20 khi cần)",
    "risk_class": "STANDARD_MESSAGE | PAID_ZBS_TEMPLATE | PAYMENT_EXECUTION | PAYROLL_DISBURSEMENT | TAX_FILING | IRREVERSIBLE_EXTERNAL_WRITE",
    "allow_auto_retry": "boolean (bắt buộc false khi risk_class <> STANDARD_MESSAGE theo Master 2.5 L258)",
    "queue_lane": "REALTIME_CRITICAL | STANDARD_INTERACTIVE | HEAVY_BATCH_BACKFILL",
    "scheduled_at": "timestamptz | null (UTC — thời điểm hẹn phát cho SCHEDULED_INTENT)",
    "expires_at": "timestamptz (NN — TTL tối đa theo policy GAP-M19-01)",
    "external_task_id": "string | null (dành cho PMS TASK_SYNC UC-W10)",
    "external_version": "string | null (dành cho PMS TASK_SYNC UC-W10)",
    "echo_operation_key": "string | null (khóa chống echo hai chiều W-T33)",
    "payload_ref": "string (NN)",
    "correlation_id": "uuid (NN)"
  },
  "EnqueueOutboundIntentOutput": {
    "outbound_intent_id": "uuid",
    "status": "QUEUED",
    "enqueue_compliance_decision": "ALLOW",
    "idempotent_replay": "boolean",
    "queued_at": "timestamptz (UTC)"
  }
}
```

### 2.3. Trụ cột 2B — `DispatchOutboundIntentInput` & `OutboundDispatchResult` (`C19` $\rightarrow$ `M14` + `M20`)

```json
{
  "DispatchOutboundIntentInput": {
    "outbound_intent_id": "uuid (NN)",
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "connection_id": "uuid (NN)",
    "actor_id": "uuid (NN)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "expected_permission_version": "integer (bigint NN — kiểm tra M14 Guarded Execution trước gửi)",
    "idempotency_key": "uuid (NN)",
    "message_id": "uuid | null",
    "source_domain_ref": "string (NN — ví dụ m03_message / m16_task / m09_payment)",
    "channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK",
    "purpose_code": "string (max 80 chars NN)",
    "message_category": "TRANSACTIONAL_TICKET_OR_APPOINTMENT | SERVICE_REPLY | MARKETING_PROMO | SURVEY_VOC | AUTOMATED_JOURNEY | TASK_SYNC | SYSTEM_SYNC",
    "vendor_code": "string | null (chuẩn hóa ánh xạ từ provider -> vendor_code; bắt buộc NN khi chạy M20.EvaluateVendorAndAiTransfer cho EXTERNAL_WEBHOOK / ERP / Bank / PMS / REMOTE_VENDOR_API)",
    "processing_record_id": "uuid | null (ref M20.Processing_Records; bắt buộc NN khi chạy M20.EvaluateVendorAndAiTransfer)",
    "source_resource_type": "string | null (khớp resource_type trong C14)",
    "source_resource_id": "uuid | null",
    "data_classes": [
      "PUBLIC_META | INTERNAL_NOTES | CONVERSATION_TEXT | CONTACT_PII_PHONE_EMAIL | NATIONAL_ID_CCCD | BANK_ACCOUNT_OR_PAYMENT | HRM_PAYROLL | CALL_RECORDING_RAW"
    ],
    "payload_provenance": "INTERNAL_SYSTEM | CUSTOMER_MESSAGE | EXTERNAL_ATTACHMENT_TEXT | null",
    "contact_id": "uuid | null",
    "sender_profile_id": "uuid | null",
    "endpoint_lookup_hash": "string (char(64) NN)",
    "hmac_key_version": "string (varchar(30) NN)",
    "endpoint_hashes_by_version": [
      {
        "hmac_key_version": "string",
        "hash": "string (char(64) NN — khớp trường hash của C20.EvaluateOutboundComplianceInput)"
      }
    ],
    "risk_class": "STANDARD_MESSAGE | PAID_ZBS_TEMPLATE | PAYMENT_EXECUTION | PAYROLL_DISBURSEMENT | TAX_FILING | IRREVERSIBLE_EXTERNAL_WRITE",
    "allow_auto_retry": "boolean",
    "verified_provider_policy_manifest_version": "string | null (từ Connection_Capabilities, không hardcode Meta tags trước PoC)",
    "lease_owner_id": "uuid | null (worker giữ lease CAS trên Outbound_Intents)",
    "lease_token": "uuid | null (fencing token sinh mới mỗi lượt claim DISPATCHING — bắt buộc kiểm CAS ở cả micro-commit http_attempted_at lẫn Pha 3)",
    "lease_expires_at": "timestamptz | null (UTC)",
    "http_attempted_at": "timestamptz | null (UTC — đóng dấu qua micro-commit CAS theo lease_token trước khi phát socket HTTP)",
    "pre_socket_reclaim_count": "integer (NN >= 0 — số lần thu hồi lease khi http_attempted_at IS NULL, tối đa 3 lần)",
    "external_task_id": "string | null",
    "external_version": "string | null",
    "echo_operation_key": "string | null",
    "payload_ref": "string (NN)",
    "expires_at": "timestamptz (NN)",
    "attempt_no": "integer (NN >= 1)",
    "correlation_id": "uuid (NN)"
  },
  "OutboundDispatchResult": {
    "outbound_intent_id": "uuid",
    "status": "ACCEPTED | CONFLICT | RETRY_WAITING | BLOCKED_BY_POLICY | EXPIRED_CANCELLED | UNKNOWN_OUTCOME | FAILED_TERMINAL",
    "lease_token": "uuid | null",
    "source_domain_ref": "string (NN)",
    "external_task_id": "string | null",
    "external_version": "string | null",
    "echo_operation_key": "string | null",
    "provider_message_id": "string | null",
    "block_or_error_code": "string | null (ví dụ AUTH_PERMISSION_VERSION_STALE, OUTBOUND_SUPPRESSED_*, PRIVACY_PURPOSE_UNAPPROVED, VENDOR_TRANSFER_POLICY_BLOCKED, PROHIBITED_DATA_CLASS_INCLUDED, CAPABILITY_NOT_VERIFIED, READ_ONLY_ADAPTER_WRITE_FORBIDDEN, PMS_VERSION_OR_STATE_CONFLICT, INTENT_TTL_EXPIRED_BEFORE_SOCKET, PRE_SOCKET_WORKER_CRASH_LIMIT)",
    "next_attempt_at": "timestamptz | null",
    "reconcile_due_at": "timestamptz | null (bắt buộc khi status = UNKNOWN_OUTCOME)",
    "dispatched_at": "timestamptz (UTC)"
  }
}
```

> **Quy trình 5 bước của Worker `DispatchOutboundIntent` & Bảng Quyết định Reaper 8 Nhánh (`ADR-005`, `W1-02`, `W1-03`):**
> 1. **TTL, Lease Fencing (`lease_token`) & Connection Gate:** Kiểm `now() < expires_at` (quá hạn $\rightarrow$ `EXPIRED_CANCELLED` `OC08`); Worker claim CAS `QUEUED/RETRY_WAITING -> DISPATCHING` với **`lease_owner_id`, `lease_token` (fencing token duy nhất) & `lease_expires_at`** và nhả lock DB; kiểm `Channel_Connections.status == 'ACTIVE'`, `Connection_Capabilities` đạt `CAPABILITY_VERIFIED` và chặn cứng nếu connection gắn `READ_ONLY_PARTNER_SYNC` (`P-T17`).
> 2. **`M14` Guarded Authority Check (`ADR-003`):** Gọi `M14.EvaluateAccessDecision` truyền `principal_type = actor_type`, `execution_mode = 'GUARDED_EXECUTION'` & `expected_permission_version`. Nếu lệch/bị khóa $\rightarrow$ `BLOCKED_BY_POLICY` (`AUTH_PERMISSION_VERSION_STALE` / `AUTH_*`) + audit (`CEO-U18`, `INT23`).
> 3. **`M20` Authoritative Suppression & Vendor Transfer Gate (`ADR-007`, `ADR-008`):**
>    - Gọi `M20.EvaluateOutboundCompliance` (`DISPATCH_AUTHORITATIVE`) với đủ `contact_id`, `sender_profile_id`, `channel`, `purpose_code`, `endpoint_lookup_hash`, `hmac_key_version`, và **`endpoint_hashes_by_version[]`** (bao gồm cả khóa `ACTIVE` và `VERIFY_ONLY`) *(lưu ý: với lệnh `channel = 'WEBHOOK'` thuộc `message_category IN ('TRANSACTIONAL_TICKET_OR_APPOINTMENT', 'TASK_SYNC', 'SYSTEM_SYNC')` **khi không mang PII khách hàng**, giữ nguyên Bước 1 [`Deletion_Ledger` + `Endpoint_Suppressions`], Bước 2 [`Processing_Records == ACTIVE` + `EvaluateVendorAndAiTransfer`], và Bước 4 [`Legal_Hold`] của `M20`; chỉ miễn Bước 3 Consent tiếp thị và miễn Bước 5 Sender Profile `EMAIL/SMS/ZALO` theo `C20`)*.
>    - **Kiểm truyền dữ liệu Bên thứ 3 (`M20.EvaluateVendorAndAiTransfer`):** Khi lệnh gửi thuộc `EXTERNAL_WEBHOOK` / ERP / Bank / PMS / `REMOTE_VENDOR_API` hoặc truyền dữ liệu sang bên thứ 3, bắt buộc gọi **`M20.EvaluateVendorAndAiTransfer`** truyền `feature_code = 'M19_EXTERNAL_WEBHOOK' | 'REMOTE_VENDOR_API'`, `source_provider = provider`, `vendor_code` (ánh xạ từ `provider`), `processing_record_id`, `source_resource_type`, `source_resource_id`, `data_classes[]`, `payload_text_or_ref = payload_ref`, `payload_provenance`. Nếu bất kỳ cổng `M20` nào trả `BLOCK` (bao gồm `VENDOR_TRANSFER_POLICY_BLOCKED`, `PROHIBITED_DATA_CLASS_INCLUDED`, `PRIVACY_PURPOSE_UNAPPROVED` hoặc `OUTBOUND_SUPPRESSED_*`) $\rightarrow$ `BLOCKED_BY_POLICY` (`OC17`, `RV17`).
> 4. **Pre-Socket Stamp CAS theo `lease_token` & Gọi Adapter Ngoài (Không giữ DB lock `INV-06`, `W1-02`):** Dùng secret từ Vault (`ADR-005`). Kiểm kích thước MIME (`+33%` base64 cho Email) & `min(policy.remote_fetch_max_bytes, verified_provider_method_limit)`. Ngay trước khi mở socket ghi HTTP ra ngoài, đánh dấu **`http_attempted_at = now()`, `last_attempted_lease_token = lease_token`** qua micro-commit CAS: **`WHERE id = $1 AND status = 'DISPATCHING' AND lease_owner_id = $2 AND lease_token = $3 AND lease_expires_at > now()`** rồi đóng hoàn toàn DB transaction trước khi gọi mạng. **Nếu micro-commit CAS trả `affected_rows == 0` (lease đã hết hạn hoặc bị Reaper thu hồi), Worker bắt buộc hủy bỏ ngay lập tức và tuyệt đối KHÔNG mở socket gọi HTTP.**
> 5. **Xử lý Kết quả Pha 3 CAS, Bảng Quyết định Reaper 8 Nhánh & Chống Retry Mù (`INT25`, `W-T32`, `Master 2.5 L258`, `W1-02`, `W1-03`):**
>    - **Pha 3 Commit (`Send_Attempts` chỉ `INSERT` tại đây):** Mở DB transaction mới, **`INSERT` đúng 1 dòng mới vào `Send_Attempts`** (`Nhóm C`, kèm `lease_token`), cập nhật trạng thái `Outbound_Intents` kiểm tra khớp `WHERE id = $1 AND status = 'DISPATCHING' AND lease_token = $2` (xóa `lease_owner_id`/`lease_token`/`lease_expires_at`), và phát `M19.OutboundDispatchResulted` (nếu kết quả `2xx` kèm `provider_message_id` về muộn sau khi Reaper đã chuyển sang `UNKNOWN_OUTCOME`, chỉ hợp nhất có điều kiện `UNKNOWN_OUTCOME -> ACCEPTED` khi `last_attempted_lease_token = $2`, không ghi đè lượt xử lý mới hơn).
>    - Nếu PMS ngoài trả HTTP `409` / lệch `external_version` / từ chối `due` hoặc `parent closed` (`W-T32`) $\rightarrow$ chuyển ngay **`CONFLICT`** kèm `(source_domain_ref, external_task_id, external_version, echo_operation_key)` để `M16.External_Task_Mappings` hiển thị xung đột trung thực.
>    - **Bảng Quyết định Reaper 8 Nhánh khi `status = 'DISPATCHING' AND now() > lease_expires_at` (`ADR-005`, `W1-03`):**
>      1. **Nhánh 1–4 (`http_attempted_at IS NOT NULL` — bất kể TTL còn/hết hay `allow_auto_retry = true/false`, hoặc timeout/lỗi mơ hồ sau socket):** Chuyển ngay **`UNKNOWN_OUTCOME`** (`allow_auto_retry = false`, đặt `reconcile_due_at`, tăng `attempt_count = attempt_count + 1`, **tuyệt đối không đẩy về `QUEUED` hay `RETRY_WAITING` mù**).
>      2. **Nhánh 5–6 (`http_attempted_at IS NULL` VÀ `now() >= expires_at` — chưa phát socket nhưng đã hết hạn TTL):** Chuyển sang **`EXPIRED_CANCELLED`** (`INTENT_TTL_EXPIRED_BEFORE_SOCKET`, giữ nguyên `attempt_count`).
>      3. **Nhánh 7 (`http_attempted_at IS NULL` VÀ `now() < expires_at` VÀ `allow_auto_retry = true`):** Thu hồi về **`RETRY_WAITING`** (tăng `pre_socket_reclaim_count <= 3`, đặt `next_attempt_at`, giữ nguyên `attempt_count` gọi provider; vượt `3` lần chuyển `FAILED_TERMINAL` `PRE_SOCKET_WORKER_CRASH_LIMIT`).
>      4. **Nhánh 8 (`http_attempted_at IS NULL` VÀ `now() < expires_at` VÀ `allow_auto_retry = false`):** Thu hồi về **`QUEUED`** (vì chắc chắn 100% chưa phát socket HTTP, tăng `pre_socket_reclaim_count <= 3`, giữ `attempt_count = 0`; vượt `3` lần chuyển `FAILED_TERMINAL` `PRE_SOCKET_WORKER_CRASH_LIMIT`).
>    - Nếu lỗi định dạng `4xx / 422` xác định thất bại đồng bộ (hoặc `allow_auto_retry = false` bị provider từ chối rõ ràng chưa ghi sổ ngoài) $\rightarrow$ chuyển **`FAILED_TERMINAL`**.
>    - Nếu `TRANSIENT_ERROR` / `429` sau HTTP và `allow_auto_retry = true` $\rightarrow$ `RETRY_WAITING` theo lịch `[1, 5, 15, 60]` phút + jitter hoặc header `Retry-After` (`GAP-M19-01`).

### 2.4. Trụ cột 4 — `ExecuteSafeRemoteFetchInput` & `RemoteFetchResult` (`SEC04`, `ADR-006`)

```json
{
  "ExecuteSafeRemoteFetchInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "connection_id": "uuid (NN — cấm provider = WEB_FORM kích hoạt Remote Fetch)",
    "inbound_event_id": "uuid | null",
    "fetch_request_id": "uuid (NN — gom nhóm chuỗi append-only Remote_Fetch_Logs)",
    "source_url": "string (HTTPS URL từ provider payload đã xác minh chữ ký)",
    "expected_mime_types": ["string"],
    "provider_reported_limit_bytes": "integer | null (chỉ là hint tham khảo, không tin nếu chưa verify trong Connection_Capabilities)",
    "follow_redirects": "boolean (mặc định false; chỉ mở allowlist hop kiểm IP/TLS khi policy manifest bật rõ ràng)",
    "total_timeout_ms": "integer | null (đọc từ M23.Policy_Versions GAP-M19-02)",
    "queue_lane": "HEAVY_BATCH_BACKFILL",
    "correlation_id": "uuid (NN)"
  },
  "RemoteFetchResult": {
    "fetch_log_id": "uuid",
    "fetch_request_id": "uuid",
    "supersedes_id": "uuid | null (trỏ tới dòng Remote_Fetch_Logs trước đó khi cập nhật kết quả quét AV)",
    "decision": "ALLOWED | BLOCKED_SSRF | BLOCKED_ALLOWLIST | BLOCKED_SIZE_OR_MIME | QUARANTINED_INFECTED",
    "effective_max_bytes": "integer (min(policy.remote_fetch_max_bytes từ M23.Policy_Versions, verified_provider_method_limit); không tin provider_reported_limit_bytes chưa verify)",
    "actual_size_bytes": "integer | null",
    "resolved_mime_type": "string | null (kiểm chứng bằng magic bytes thực tế; cấm SVG/HTML active; Email tính tổng MIME +33%)",
    "content_sha256": "string | null",
    "scan_status": "PENDING | CLEAN | INFECTED | FAILED",
    "asset_id": "uuid | null (cấp ngay ở trạng thái PENDING khi tệp vào Quarantine; chỉ cho tải qua Download Gateway SEC03 khi CLEAN)",
    "asset_version_id": "uuid | null (cấp ngay cùng asset_id với scan_status = PENDING tại Shared Platform Asset Registry ENTITY-L2783)",
    "quarantined_event_id": "uuid | null",
    "fetched_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Zero-Trust Remote Fetch (`SEC04`, `ADR-006`):**
> - **Cấm `WEB_FORM` kích hoạt Remote Fetch:** Nguồn `provider = 'WEB_FORM'` bị chặn cứng (`422 WEB_FORM_REMOTE_FETCH_FORBIDDEN`) không được phép sai worker tải URL tự do; tệp đính kèm từ form phải đi qua tải trực tiếp có kiểm soát và quét AV.
> - **Chặn Toàn bộ Dải IP Nội bộ/Đặc biệt sau DNS Resolve (DNS-Pinning) & Redirect:** Bắt buộc chặn `0.0.0.0/8`, `10.0.0.0/8`, `100.64.0.0/10` (CGNAT), `127.0.0.0/8`, `169.254.0.0/16` (cloud metadata `169.254.169.254`), `172.16.0.0/12`, `192.168.0.0/16`, multicast/reserved IPv4; và `::1/128`, `::/128`, `::ffff:0:0/96` (`::ffff:*` IPv4-mapped IPv6), `fc00::/7` (IPv6 ULA), `fe80::/10` (IPv6 link-local), multicast/reserved IPv6. Mặc định `follow_redirects = false` (chỉ cho phép redirect khi policy/manifest của connector bật rõ, kiểm allowlist + DNS-pinning từng hop và strip toàn bộ header xác thực).
> - **Giới hạn Động, Magic Bytes & `asset_version_id` (`PENDING` ngay từ đầu):** Đọc `remote_fetch_max_bytes` và `total_timeout_ms` từ **`M23.Policy_Versions`** (`[OPEN-GAP: GAP-M19-02]`), áp dụng `min(product_safe_default, verified_provider_method_limit)` (tính tổng Email MIME `+33%`), xác minh MIME bằng **magic bytes thực tế**, cấm tuyệt đối **`SVG` (`image/svg+xml`) & `HTML` (`text/html`, `application/xhtml+xml`) active**. Tệp vượt qua bước tải an toàn được cấp ngay `asset_id` + **`asset_version_id`** ở trạng thái `scan_status = 'PENDING'` trong Quarantine (`Download Gateway SEC03` khóa tải cho tới khi `Remote_Fetch_Logs` mới nối `supersedes_id` ghi nhận `CLEAN`).

### 2.5. Trụ cột 5 — `ReplayConnectionEventsInput` & `ReplayConnectionEventsOutput` (`POST /v1/connections/{id}/replay` — `CONTRACT-L2845`, `ADR-008`)

```json
{
  "ReplayConnectionEventsInput": {
    "tenant_id": "uuid (NN — suy xuất từ session)",
    "workspace_id": "uuid (NN — suy xuất từ session)",
    "connection_id": "uuid (NN)",
    "actor_id": "uuid (NN)",
    "expected_permission_version": "integer (bigint NN — GUARDED_EXECUTION)",
    "idempotency_key": "uuid (NN)",
    "mode": "DRY_RUN | EXECUTE (bắt buộc DRY_RUN hợp lệ trước khi gọi EXECUTE)",
    "range_from": "timestamptz (UTC NN — bắt buộc range_to > range_from trong cửa sổ GAP-M19-09)",
    "range_to": "timestamptz (UTC NN)",
    "reason": "string (NN — lý do kiểm toán bắt buộc)",
    "approved_by_user_id": "uuid | null (bắt buộc != actor_id khi phạm vi rủi ro cao / TEAM)",
    "queue_lane": "HEAVY_BATCH_BACKFILL",
    "correlation_id": "uuid (NN)"
  },
  "ReplayConnectionEventsOutput": {
    "replay_job_id": "uuid",
    "mode": "DRY_RUN | EXECUTE",
    "status": "DRY_RUN_READY | RUNNING | COMPLETED | FAILED | CANCELLED",
    "estimated_count": "integer (>= 0)",
    "executed_count": "integer (>= 0)",
    "blocked_by_policy_count": "integer (>= 0)",
    "correlation_id": "uuid"
  }
}
```

> **Quy tắc Kiểm duyệt `ReplayConnectionEvents` (`CONTRACT-L2845`):**
> - Kiểm `M14.EvaluateAccessDecision(resource_type = 'REPLAY_JOB', action = 'REPLAY', execution_mode = 'GUARDED_EXECUTION')`. Nếu gọi `EXECUTE` khi chưa có phiếu `DRY_RUN_READY` khớp `(connection_id, range_from, range_to)` $\rightarrow$ trả ngay `422 DRY_RUN_REQUIRED`.
> - Chạy hoàn toàn trên **`Lane 3 (HEAVY_BATCH_BACKFILL)`**, luôn gắn `source_mode = 'REPLAY'` (không tạo SLA/Journey live `OC09`), đi qua cùng bảng dedup `Inbound_Event_Dedup_Keys` / `Inbound_Events` và kiểm lại `M20` (qua `endpoint_hashes_by_version[]`) trước mọi side-effect (`OC08`, `OC19`).

### 2.6. Cổng 6 — `ListOpenIntentsForPrincipalInput` & `ListOpenIntentsForPrincipalOutput` (`M14-F06` Offboarding Handover, `INT15`)

```json
{
  "ListOpenIntentsForPrincipalInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid | null (NULL để quét toàn tenant khi OFFBOARD; non-null khi BRANCH_TRANSFER/ROLE_CHANGE theo phạm vi cũ)",
    "offboarding_case_id": "uuid (NN)",
    "principal_id": "uuid (NN — user đang bị khóa hoặc chuyển bộ phận)",
    "case_type": "OFFBOARD | BRANCH_TRANSFER | ROLE_CHANGE",
    "from_branch_id": "uuid | null",
    "include_categories": [
      "SCHEDULED_INTENT",
      "CHANNEL_CONNECTION_OWNER",
      "ADAPTER_DLQ_OWNER"
    ],
    "cursor": "string | null",
    "limit": "integer (default 100, max 500)",
    "correlation_id": "uuid (NN)"
  },
  "ListOpenIntentsForPrincipalOutput": {
    "offboarding_case_id": "uuid",
    "principal_id": "uuid",
    "total_open_items": "integer (>= 0)",
    "items": [
      {
        "item_category": "SCHEDULED_INTENT | CHANNEL_CONNECTION_OWNER | ADAPTER_DLQ_OWNER",
        "item_id": "uuid",
        "workspace_id": "uuid",
        "branch_id": "uuid | null",
        "connection_id": "uuid | null",
        "current_status": "string",
        "original_actor_id": "uuid | null (bất biến theo INT15, không bị ghi đè khi bàn giao)",
        "current_owner_user_id": "uuid | null",
        "scheduled_or_due_at": "timestamptz | null (UTC)",
        "recommended_custodian_id": "uuid (ưu tiên Channel_Connections.backup_owner_user_id -> Branch Manager -> Tenant Owner)"
      }
    ],
    "next_cursor": "string | null"
  }
}
```

> **Quy tắc Bàn giao `M14-F06` (`INT15`, `UC12`):**
> - Bao phủ đủ 3 hạng mục thuộc `M19`: **`SCHEDULED_INTENT`** (`Outbound_Intents` hẹn giờ/đang chờ), **`Channel_Connections.owner_user_id`** (`CHANNEL_CONNECTION_OWNER`), và **`Adapter_Dead_Letter_Queue.owner_user_id`** (`ADAPTER_DLQ_OWNER`).
> - Bắt buộc tách bạch **`owner_user_id`** (người quản lý/vận hành có thể bàn giao qua Pha 1 `Custodian` và Pha 2 `Confirmed Recipient`) khỏi **`actor_id` / `created_by` gốc** (bất biến để bảo toàn dấu vết kiểm toán theo `INT15`).
> - **Ánh xạ Rollup sang Bảng 13 `item_category` của `M14-F06` (`C14`):** `SCHEDULED_INTENT` $\rightarrow$ `SCHEDULED_INTENT`; `CHANNEL_CONNECTION_OWNER` và `ADAPTER_DLQ_OWNER` $\rightarrow$ rollup cứng vào **`QUEUE_MANAGER`** *(Custodian fallback thuộc Ops/Integration trên bảng tổng hợp 13 `item_category` của `M14-F06`, đồng thời giữ chi tiết `source_subtype` & `original_actor_id` tại `M19` để không chia đôi bucket)*.

---

## 3. Domain Events Phát hành & Tiêu thụ (Qua Internal Outbox `M23-F12` — `ADR-005`)

### 3.1. Envelope Chuẩn Mọi Sự kiện `M19` (`schema_version = "1.2"`)

Dùng cấu trúc Envelope thống nhất (`event_id`, `event_type`, `aggregate_type`, `aggregate_id`, `aggregate_version`, `schema_version`, `tenant_id`, `workspace_id`, `occurred_at`, `correlation_id`, `causation_id`, `payload`).

```json
{
  "event_id": "uuid (NN)",
  "event_type": "M19.InboundEventPersisted | M19.OutboundDispatchResulted | M19.MessageReceiptUpdated | M19.ConnectionHealthChanged | M19.SyncCoverageGapReported",
  "aggregate_type": "INBOUND_EVENT | OUTBOUND_INTENT | MESSAGE_STATUS_EVENT | CHANNEL_CONNECTION | SYNC_RUN",
  "aggregate_id": "uuid (NN)",
  "aggregate_version": "integer (bigint >= 1)",
  "schema_version": "1.2",
  "tenant_id": "uuid (NN)",
  "workspace_id": "uuid (NN)",
  "occurred_at": "timestamptz (UTC NN)",
  "correlation_id": "uuid (NN)",
  "causation_id": "uuid | null",
  "payload": {
    "connection_id": "uuid",
    "provider": "string",
    "detail_note": "Object field-map cụ thể theo từng dòng Sự kiện §3.2"
  }
}
```

### 3.2. Danh mục Sự kiện Phát hành (`Published Events`)

| Event Name | Payload Trọng yếu | Consumers Bắt buộc | Hành động Phải thực thi |
|---|---|---|---|
| `M19.InboundEventPersisted` | `inbound_event_id`, `connection_id`, `provider`, `event_type`, `source_mode` (`LIVE \| BACKFILL \| REPLAY`), `source_domain_ref`, `external_task_id`, `external_version`, `echo_operation_key`, `payload_ref`, `occurred_at` | `M03`, `M01`, `M09`, `M16`, `M21`, `M22` | `M03` chiếu hội thoại/tin nhắn; nếu `source_mode = BACKFILL` thì chỉ ghi lịch sử, không tính SLA mới hoặc chạy trigger nurture (`OC09`); `M09` đối soát `PAYMENT_GW`; `M16` đối chiếu PMS sync (`UC-W10`) theo `external_task_id`, `external_version`, `echo_operation_key` chống echo (`W-T33`); `M21`/`M22` nạp dataset/device/payroll status theo adapter |
| `M19.OutboundDispatchResulted` | `outbound_intent_id`, `message_id`, `source_domain_ref`, `external_task_id`, `external_version`, `echo_operation_key`, `channel`, `status` (`ACCEPTED \| CONFLICT \| BLOCKED_BY_POLICY \| EXPIRED_CANCELLED \| UNKNOWN_OUTCOME \| FAILED_TERMINAL`), `provider_message_id`, `reason_code` | `M03`, `M04`, `M12`, `M09`, `M16`, `M22` | Cập nhật trạng thái gửi thực tế tại màn hình nguồn; hiển thị cờ chờ đối soát `UNKNOWN_OUTCOME` (`UC19`, `INT25`) hoặc lý do bị chặn `M20`/`M14`; `M16` cập nhật `External_Task_Mappings` (`SYNCED \| CONFLICT \| UNKNOWN_OUTCOME \| FAILED_TERMINAL`) và hiển thị xung đột `CONFLICT` (`W-T32`) mà không báo đã áp dụng ở nguồn |
| `M19.MessageReceiptUpdated` *(từ `Message_Status_Events` `ENTITY-L2823` & `Email_Delivery_Events` `ENTITY-L2893` do `M19-F04` ingest)* | `message_status_event_id`, `provider_event_id`, `outbound_intent_id`, `message_id`, `connection_id`, `channel`, `purpose_code`, `endpoint_lookup_hash`, `hmac_key_version`, `endpoint_masked` *(từ `endpoint_masked_redacted`, nullable)*, `receipt_status` (`ACCEPTED \| SENT \| DELIVERED \| DEFERRED \| READ \| BOUNCED_HARD \| BOUNCED_SOFT \| COMPLAINED \| FAILED`), `occurred_at` | `M03`, `M20`, `M04`, `M12` | `M03` cập nhật trạng thái đọc/nhận/bounce theo thứ tự đơn điệu (`ACCEPTED -> READ`, `ACCEPTED/DELIVERED/READ -> COMPLAINED/FAILED` `OC07`); `M20-F03` tiêu thụ idempotent theo `provider_event_id` (`M20:226`), tiếp nhận trực tiếp `{channel, endpoint_lookup_hash, hmac_key_version, purpose_code, endpoint_masked, receipt_status}` từ payload event để ghi/cập nhật `Endpoint_Suppressions` mà **không truy vấn chéo DB `M19`** (`INDEX.md L62`, bảng `Email_Delivery_Events` đã do `M19-F04` ingest trước đó) |
| `M19.ConnectionHealthChanged` | `connection_id`, `provider`, `old_status`, `new_status` (`ACTIVE \| DEGRADED \| REAUTHORIZATION_REQUIRED \| PAUSED \| DISCONNECTED`), `requires_reauth`, `health_reason_redacted` | `M03`, `M16`, `M21`, `M22`, `M23-F08` | Vô hiệu hóa nút gửi/đồng bộ khi mất kết nối, cảnh báo owner có runbook tách rõ ngưỡng **`ONFR05` (`[MASTER]` `5 phút` phát hiện `oldest_pending_age > 5 phút`)** vs **`[OPEN-GAP: GAP-M19-11]` (`[PROPOSED]` `15 phút/đợt` gom nhóm chống bão cảnh báo theo `(tenant_id, connection_id, error_class)`)**, và báo `Availability` 2 lớp (`ONFR06`) |
| `M19.SyncCoverageGapReported` | `connection_id`, `checkpoint_id`, `stream_key`, `coverage_from`, `coverage_to`, `coverage_status` (`COMPLETE \| PARTIAL \| UNKNOWN`), `gap_reason` | `M03`, `M16`, `M18`, `M21`, `M23-F08` | Hiển thị trung thực khoảng dữ liệu lịch sử không lấy lại được trên Monitor/BI (`OC21`, `UC21`, `CMO-U25`) thay vì báo `"100%"` giả |

### 3.3. Danh mục Sự kiện Liên Module `M19` Tiêu thụ (`Subscribed Events`)

| Nguồn & Event | Hành vi Xử lý Tại `M19` |
|---|---|
| **`M14.PermissionVersionBumped`** | Làm mới kiểm tra quyền cho worker dispatch / từ chối các lệnh `DispatchOutboundIntent` hoặc `ReplayConnectionEvents` đang giữ `expected_permission_version` cũ (`409 AUTH_PERMISSION_VERSION_STALE` — `ADR-003`, `CEO-U18`) |
| **`M14.UserOffboardingLocked` / `M14.WorkHandoverAssigned`** | Thực thi bàn giao 2 pha (`M14-F06`) qua `ListOpenIntentsForPrincipal` cho 3 hạng mục (`SCHEDULED_INTENT`, `Channel_Connections.owner_user_id`, `Adapter_Dead_Letter_Queue.owner_user_id`): ngừng phát các `Outbound_Intents` theo lịch gắn `actor_id` cũ, chuyển `owner_user_id` sang `default_custodian_id` (`backup_owner_user_id` fallback) rồi sang `confirmed_recipient_id` khi `CONFIRMED`, **giữ nguyên `actor_id` / `created_by` gốc (`INT15`)**; từ chối cấp lại quyền replay/connect cho actor bị khóa |
| **`M14.WorkspaceActivated`** | Cho phép mở quyền đăng ký/kích hoạt `Channel_Connections` trong `workspace_id` vừa kích hoạt (phải kiểm `Processing_Records` ở `M20` trước khi lên `ACTIVE`) |
| **`M20.EndpointSuppressed`** | Hủy ngay toàn bộ `Outbound_Intents` còn ở trạng thái `QUEUED` hoặc `RETRY_WAITING` khớp `(tenant_id, workspace_id, channel, endpoint_lookup_hash)` (đối chiếu qua `endpoint_hashes_by_version[]` / `hmac_key_version`) + `purpose_scope` $\rightarrow$ chuyển sang `BLOCKED_BY_POLICY` (`OC17`, `RV17`) |
| **`M20.SubjectErasureExecuted`** | Tiếp nhận **`erased_subject_refs[]`** (cùng `subject_hmac_sha256` & `endpoint_hmac_hashes_by_version[]` đa phiên bản `hmac_key_version`): hủy toàn bộ `Outbound_Intents` đang xếp hàng liên quan sang `BLOCKED_BY_POLICY`, và **tìm xóa sạch PII / raw `payload_ref`** trên cả **`Inbound_Events`**, **`Quarantined_Events`**, **`Adapter_Dead_Letter_Queue`**, `Outbound_Intents` và `Remote_Fetch_Logs` temp blobs (tôn trọng `retained_legal_hold_scopes[]`; giữ tombstone non-PII `Inbound_Event_Dedup_Keys` nếu còn hạn chống replay) |
| **`M20.DataIncidentEscalated`** | Nếu `affected_connection_ids[]` không rỗng: đặt `requires_reauth = true`, đưa ngay kết nối bị nghi rò rỉ token sang `REAUTHORIZATION_REQUIRED` / `PAUSED` và thu hồi secret cũ khỏi Vault cache (`M20-F08`) |
| **`M23.FeatureFlagUpdated`** (`M23-F09`) | Khi tắt cờ kênh hoặc `M06`/`M21`/`UC-W10`, áp dụng `Feature Flag Closure` đóng toàn bộ endpoint webhook/outbox của kênh tương ứng (`RV20`) |
