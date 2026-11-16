# Contract `M19-DURABLE-INGEST-OUTBOX` — Cổng Tiếp nhận Bền vững, Điều phối Gửi tin Ngoài, Backfill/Replay & Zero-Trust Media Fetch

- **Contract ID:** `CONTRACT-M19-INTEGRATION-OUTBOX-v1.1`
- **Provider Owner:** `M19` (**Chỉ cho Tích hợp Kênh ngoài, POS `API_READ`, ERP/Payment/HRM Devices** — không dùng cho Internal Domain Outbox `M23-F12` theo `ADR-005`)
- **Consumers:** `M01`, `M02`, `M03`, `M04`, `M09`, `M11`, `M12`, `M13`, `M18`, `M20`, `M21` (`API_READ`), `M22` (`M22-F10` thiết bị chấm công & `M22-F28` ngân hàng chi lương), `M23` (`M23-F08` Security/Ops Alerts, `M23-F12` Platform Health/DR)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`2.4–2.7`, `3.12.5`, `3.12.11–12`, `5.16 L2816–2829`, `5.17 L2845–2848`, `5.18 L2893/2897`, `7.6 ONFR01–06`, `Phụ lục G L4713`, `OC01`, `OC05`, `OC06`, `OC07`, `OC08`, `OC14`, `OC19`, `INT25`, `SEC-U01`, `SEC-U02`, `SEC-U04`, `H-NFR08`), [ADR-005](../../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-008](../../01-architecture/decisions/ADR-008-OMNICHANNEL-CONTRACTS-RECEIPTS-AND-CROSS-EVENTS.md)
- **Trạng thái:** `Reviewed (CR-20261116-WAVE1-RECONCILIATION Applied)`
- **Chính sách Breaking Change:** Mọi thay đổi schema payload hoặc tập `channel`/`provider` phải giữ tương thích ngược cho `Inbound_Events` / `Outbound_Intents` đang tồn đọng (`replay_compatible = true`) và cập nhật đồng thời `M03`, `M14`, `M20`, `M21`.

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | Chuẩn hóa **5 trụ cột/cổng tích hợp ngoài** của `M19`: (1) `IngestWebhookEvent` (`Durable-Before-ACK` tại Lane 1 `REALTIME_CRITICAL`), (2) `EnqueueOutboundIntent` (tạo ý định gửi nguyên tử trong transaction domain), (3) `DispatchOutboundIntent` (điều phối gửi không giữ DB lock, recheck `M14` + `M20`, đóng băng `UNKNOWN_OUTCOME` khi timeout & khóa `allow_auto_retry = false` cho giao dịch tiền/phí), (4) `ExecuteSafeRemoteFetch` (tải media từ xa Zero-Trust & cách ly quarantine tại Lane 3 `HEAVY_BATCH_BACKFILL`), và (5) `ReplayConnectionEvents` (`POST /v1/connections/{id}/replay` — `CONTRACT-L2845`: replay có giới hạn thời gian hữu hạn, bắt buộc `DRY_RUN -> EXECUTE`, audit & qua lại chống trùng/ACL). |
| **Actor/scope** | `External Provider Webhook` (từ `Channel_Connections` xác minh chữ ký) và `Authenticated Internal Service / Worker` (`M03`, `M04`, `M12`, `M21`, `M22`, `M09`). Mọi phạm vi `tenant_id` & `workspace_id` suy xuất từ `Channel_Connections` đã xác minh trong DB, **tuyệt đối không tin `workspace_id` từ webhook ngoài (`INV-07`)**. |
| **Preconditions** | `Channel_Connections` có trạng thái `ACTIVE` (riêng `Processing_Records` bên `M20` phải đạt `ACTIVE` trước khi bật kết nối `Master 6.3 L3159`); `Connection_Capabilities` đạt `CAPABILITY_VERIFIED` cho hành động tương ứng (`OM-G01`, `OC15`); kết nối `API_READ` (`M21-F06`) bị khóa allowlist chỉ đọc (`INV-21`). **Khóa chống Hijack `Channel_Connections`:** `UNIQUE (tenant_id, provider, provider_namespace, external_account_id) WHERE status IN ('ACTIVE', 'DEGRADED', 'REAUTHORIZATION_REQUIRED', 'PAUSED')`. |
| **Input** | Xem 5 cặp Input JSON Schema đầy đủ ở Mục 2: `IngestWebhookEventInput`, `EnqueueOutboundIntentInput`, `DispatchOutboundIntentInput`, `ExecuteSafeRemoteFetchInput`, `ReplayConnectionEventsInput`. |
| **Output** | Xem 5 Output JSON Schema đầy đủ ở Mục 2: `InboundIngestAck`, `EnqueueOutboundIntentOutput`, `OutboundDispatchResult`, `RemoteFetchResult`, `ReplayConnectionEventsOutput`. |
| **Errors** | Chuẩn Error Envelope `{code, message, field_errors, correlation_id}`. Mã lỗi chính: `401 INGEST_SIGNATURE_INVALID`; `403 BREAK_GLASS_REQUIRED`; `409 CONNECTION_OWNERSHIP_CONFLICT` (non-disclosure `SEC-U02`), `409 AUTH_PERMISSION_VERSION_STALE` (từ `M14`), `409 IDEMPOTENCY_PAYLOAD_CONFLICT`; `422 CAPABILITY_NOT_VERIFIED`, `422 READ_ONLY_ADAPTER_WRITE_FORBIDDEN`, `422 PROCESSING_RECORD_UNAPPROVED`, `422 EGRESS_SSRF_BLOCKED`, `422 MEDIA_SIZE_OR_MIME_EXCEEDED`, `422 DRY_RUN_REQUIRED`, plus mọi mã chặn từ `M20` (`OUTBOUND_SUPPRESSED_UNSUBSCRIBE | OUTBOUND_SUPPRESSED_CONSENT_REVOKED | OUTBOUND_SUPPRESSED_HARD_BOUNCE | OUTBOUND_SUPPRESSED_SOFT_BOUNCE_COOLDOWN | OUTBOUND_SUPPRESSED_SPAM_COMPLAINT | OUTBOUND_SUPPRESSED_REFUSED_CALLBACK | OUTBOUND_SUPPRESSED_MANUAL_DNC | OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD`); `429 PROVIDER_RATE_LIMITED`; `503 DURABLE_WRITE_UNAVAILABLE` (cấm trả `2xx` ACK khi ghi DB thất bại `ONFR02`). |
| **Concurrency** | **Tuyệt đối không giữ DB lock khi gọi HTTP ra ngoài (`INV-06`).** Áp dụng optimistic locking (`row_version` + CAS `QUEUED -> DISPATCHING`) để chỉ 1 worker được phép thực thi một `Outbound_Intent` tại một thời điểm (`INV-09`). Mạng đọc/timeout sau khi đã gửi POST ra provider $\rightarrow$ chuyển ngay `UNKNOWN_OUTCOME` để đối soát (`INT25`), **không retry mù** (và `allow_auto_retry = false` cho giao dịch tiền/trả phí `Master 2.5 L258`). |
| **Idempotency** | `Inbound_Events`: **`UNIQUE (tenant_id, connection_id, event_key)`** (SQL: `ON CONFLICT (tenant_id, connection_id, event_key) DO NOTHING`; riêng các status-update event của cùng tin nhắn dùng `provider_event_id + receipt_status` riêng biệt per `5.17 L2848`). `Outbound_Intents`: **`UNIQUE (tenant_id, workspace_id, idempotency_key)`** (`OC05`) — cùng key khác payload trả `409`. |
| **Transaction** | `IngestWebhookEvent`: commit `Inbound_Events` + `Internal_Outbox_Events` (`M19.InboundEventPersisted`) xong mới trả `2xx` ACK (`ONFR02`). `EnqueueOutboundIntent`: commit chung 1 DB transaction với bản ghi tin nhắn/lệnh domain nguồn (`INV-06`). `DispatchOutboundIntent`: Pha 1 claim `CAS` và nhả transaction $\rightarrow$ Pha 2 check `M14` + `M20` & gọi mạng $\rightarrow$ Pha 3 mở transaction mới ghi `Send_Attempts` + cập nhật trạng thái `Outbound_Intents` + event kết quả. |
| **Compatibility** | Hỗ trợ đồng thời nhiều version adapter theo từng provider; **tuyệt đối tuân thủ lệnh cấm giả định trong Master `3.12.12` & `Phụ lục G`**: thuật toán xác minh webhook Zalo (`ZALO_OA`) và bộ Meta Message Tags (`FACEBOOK_PAGE`) đánh dấu `UNVERIFIED_UNTIL_POC` (`Fail-Closed` nếu bật cờ live mà chưa có contract xác minh PoC, `GAP-M19-03/04`). |
| **Audit/privacy** | Không lưu token, secret hay PII nội dung tin nhắn thô trong `Send_Attempts` (`5.16 L2826`) và application logs (`NFR11`). Xem raw payload trong `Quarantined_Events` / `Adapter_Dead_Letter_Queue` bắt buộc có `Break-glass` Grant từ `M14`/`M23-F03` (`INV-22`). |
| **Tests** | `M19-AC01..03`, `SEC-U01`, `SEC-U02`, `SEC-U04`, `OC01`, `OC05`, `OC06`, `OC07`, `OC08`, `OC09`, `OC13`, `OC14`, `OC15`, `OC16`, `OC17`, `OC19`, `OC21`, `OC22`, `INT23`, `INT24`, `INT25`, `INT26`, `ONFR01..06`, `OM-G01`, `OM-G02`, `OM-G08`, `P-T17`, `RV15`, `RV17`. Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas Đầy đủ cho 5 Cổng/Lệnh Tích hợp Ngoài (`10 JSON Schemas`)

### 2.1. Trụ cột 1 — `IngestWebhookEventInput` & `InboundIngestAck`

```json
{
  "IngestWebhookEventInput": {
    "provider": "ZALO_OA | FACEBOOK_PAGE | TIKTOK_BM | TELEGRAM | GMAIL | MS_GRAPH | WEB_FORM | VOIP_SIP | PAYMENT_GW | PANCAKE | ERP_MISA | PMS | BIOMETRIC_DEVICE | PAYROLL_BANK",
    "provider_namespace": "string (NN — OA ID / Page ID / Bot ID / Mailbox / Shop ID)",
    "signature_headers": "object (header xác minh theo adapter manifest đã verify; Zalo để adapter_verifier_pending_poc cho tới khi hoàn tất PoC)",
    "raw_body_ref": "string (reference tới payload thô được bảo vệ/mã hóa trước parse sâu)",
    "event_key": "string (NN — canonical provider event key dùng chống trùng)",
    "event_type": "INBOUND_MESSAGE | STATUS_RECEIPT | EMAIL_BOUNCE_OR_COMPLAINT | CALL_CDR | LEAD_FORM | ORDER_SYNC | PAYMENT_CALLBACK | ATTENDANCE_PUNCH | PAYROLL_BATCH_STATUS",
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

> **SQL Bền vững Chuẩn hóa:**  
> `INSERT INTO inbound_events (id, tenant_id, workspace_id, connection_id, event_key, ...) VALUES (...) ON CONFLICT (tenant_id, connection_id, event_key) DO NOTHING;`  
> Nếu là webhook `STATUS_RECEIPT` hoặc `EMAIL_BOUNCE_OR_COMPLAINT`, ghi tách vào `Message_Status_Events` (`UNIQUE (tenant_id, connection_id, provider_event_id, receipt_status)`) / `Email_Delivery_Events` để không bị nuốt do trùng `message_key` gốc (`5.17 L2848`).

### 2.2. Trụ cột 2A — `EnqueueOutboundIntentInput` & `EnqueueOutboundIntentOutput` (Chạy trong Transaction Nghiệp vụ)

```json
{
  "EnqueueOutboundIntentInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "connection_id": "uuid (NN)",
    "actor_id": "uuid (NN)",
    "expected_permission_version": "integer (bigint NN)",
    "idempotency_key": "uuid (NN — UNIQUE (tenant_id, workspace_id, idempotency_key))",
    "message_id": "uuid | null (FK Messages theo Master 5.16 L2825 cho tin nhắn CRM)",
    "source_domain_ref": "string (NN — ví dụ m03_message / m04_step / m12_survey / m09_payment / m22_payout)",
    "channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK (API/ERP/Bank/POS dùng WEBHOOK; VoIP dùng VOICE_CALL)",
    "purpose_code": "string (max 80 chars, khớp Master 5.9)",
    "message_category": "TRANSACTIONAL_TICKET_OR_APPOINTMENT | SERVICE_REPLY | MARKETING_PROMO | SURVEY_VOC | AUTOMATED_JOURNEY",
    "contact_id": "uuid | null",
    "sender_profile_id": "uuid | null",
    "endpoint_lookup_hash": "string (char(64) NN — với API hệ thống ERP/Bank phi cá nhân không gắn contact/người nhận thì truyền canonical system-endpoint HMAC)",
    "risk_class": "STANDARD_MESSAGE | PAID_ZBS_TEMPLATE | PAYMENT_EXECUTION | PAYROLL_DISBURSEMENT | TAX_FILING | IRREVERSIBLE_EXTERNAL_WRITE",
    "allow_auto_retry": "boolean (bắt buộc false khi risk_class <> STANDARD_MESSAGE theo Master 2.5 L258)",
    "queue_lane": "REALTIME_CRITICAL | STANDARD_INTERACTIVE | HEAVY_BATCH_BACKFILL",
    "expires_at": "timestamptz (NN — TTL tối đa theo policy GAP-M19-01)",
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
    "expected_permission_version": "integer (bigint NN — kiểm tra M14 Guarded Execution trước gửi)",
    "idempotency_key": "uuid (NN)",
    "message_id": "uuid | null",
    "channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK",
    "purpose_code": "string (max 80 chars NN)",
    "message_category": "TRANSACTIONAL_TICKET_OR_APPOINTMENT | SERVICE_REPLY | MARKETING_PROMO | SURVEY_VOC | AUTOMATED_JOURNEY",
    "contact_id": "uuid | null",
    "sender_profile_id": "uuid | null",
    "endpoint_lookup_hash": "string (char(64) NN)",
    "risk_class": "STANDARD_MESSAGE | PAID_ZBS_TEMPLATE | PAYMENT_EXECUTION | PAYROLL_DISBURSEMENT | TAX_FILING | IRREVERSIBLE_EXTERNAL_WRITE",
    "allow_auto_retry": "boolean",
    "verified_provider_policy_manifest_version": "string | null (từ Connection_Capabilities, không hardcode Meta tags trước PoC)",
    "payload_ref": "string (NN)",
    "expires_at": "timestamptz (NN)",
    "attempt_no": "integer (NN >= 1)",
    "correlation_id": "uuid (NN)"
  },
  "OutboundDispatchResult": {
    "outbound_intent_id": "uuid",
    "status": "ACCEPTED | RETRY_WAITING | BLOCKED_BY_POLICY | EXPIRED_CANCELLED | UNKNOWN_OUTCOME | FAILED_TERMINAL",
    "provider_message_id": "string | null",
    "block_or_error_code": "string | null (ví dụ AUTH_PERMISSION_VERSION_STALE, OUTBOUND_SUPPRESSED_*, CAPABILITY_NOT_VERIFIED, READ_ONLY_ADAPTER_WRITE_FORBIDDEN)",
    "next_attempt_at": "timestamptz | null",
    "reconcile_due_at": "timestamptz | null (bắt buộc khi status = UNKNOWN_OUTCOME)",
    "dispatched_at": "timestamptz (UTC)"
  }
}
```

> **Quy trình 5 bước của Worker `DispatchOutboundIntent`:**
> 1. **TTL & Connection Gate:** Kiểm `now() < expires_at` (quá hạn $\rightarrow$ `EXPIRED_CANCELLED` `OC08`); kiểm `Channel_Connections.status == 'ACTIVE'`, `Connection_Capabilities` đạt `CAPABILITY_VERIFIED` và chặn cứng nếu connection gắn `READ_ONLY_PARTNER_SYNC` (`P-T17`).
> 2. **`M14` Guarded Authority Check (`ADR-003`):** Gọi `M14.EvaluateAccessDecision` với `execution_mode = 'GUARDED_EXECUTION'` & `expected_permission_version`. Nếu lệch/bị khóa $\rightarrow$ `BLOCKED_BY_POLICY` (`AUTH_PERMISSION_VERSION_STALE` / `AUTH_*`) + audit (`CEO-U18`, `INT23`).
> 3. **`M20` Authoritative Suppression Gate (`ADR-008`):** Gọi `M20.EvaluateOutboundCompliance` (`DISPATCH_AUTHORITATIVE`) với đủ `contact_id`, `sender_profile_id`, `channel`, `purpose_code`, `endpoint_lookup_hash` *(lưu ý: với lệnh `WEBHOOK` hệ thống phi nhắn tin như ERP/Payment/Bank, giữ nguyên Bước 1 [`Deletion_Ledger` + `Endpoint_Suppressions`], Bước 2 [`Processing_Records == ACTIVE` + `EvaluateVendorAndAiTransfer`], và Bước 4 [`Legal_Hold`] của `M20`; chỉ miễn Bước 3 Consent tiếp thị khi thuộc `TRANSACTIONAL_*` kỹ thuật và miễn Bước 5 Sender Profile `EMAIL/SMS/ZALO` theo `C20`)*. Nếu `BLOCK` $\rightarrow$ `BLOCKED_BY_POLICY` (`OC17`, `RV17`).
> 4. **Gọi Adapter Ngoài (Không giữ DB lock `INV-06`):** Dùng secret từ Vault (`ADR-005`). Kiểm kích thước MIME (`+33%` base64 cho Email) & `min(product_limit, provider_limit)`.
> 5. **Xử lý Kết quả & Chống Retry Mù (`INT25`, `Master 2.5 L258`):**
>    - Nếu timeout/mất kết nối sau khi phát POST hoặc `allow_auto_retry = false` gặp lỗi mơ hồ $\rightarrow$ chuyển ngay **`UNKNOWN_OUTCOME`** (đặt `reconcile_due_at`, **tuyệt đối không retry tự động**).
>    - Nếu lỗi định dạng `4xx / 422` xác định thất bại đồng bộ (hoặc `allow_auto_retry = false` bị provider từ chối rõ ràng chưa ghi sổ ngoài) $\rightarrow$ chuyển thẳng **`FAILED_TERMINAL`**.
>    - Nếu `TRANSIENT_ERROR` / `429` và `allow_auto_retry = true` $\rightarrow$ `RETRY_WAITING` theo lịch `[1, 5, 15, 60]` phút + jitter hoặc header `Retry-After` (`GAP-M19-01`).

### 2.4. Trụ cột 4 — `ExecuteSafeRemoteFetchInput` & `RemoteFetchResult` (`SEC04`, `ADR-006`)

```json
{
  "ExecuteSafeRemoteFetchInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "connection_id": "uuid (NN)",
    "inbound_event_id": "uuid | null",
    "source_url": "string (HTTPS URL từ provider payload đã xác minh chữ ký)",
    "expected_mime_types": ["string"],
    "provider_reported_limit_bytes": "integer | null",
    "follow_redirects": "boolean (bắt buộc false)",
    "queue_lane": "HEAVY_BATCH_BACKFILL",
    "correlation_id": "uuid (NN)"
  },
  "RemoteFetchResult": {
    "fetch_log_id": "uuid",
    "decision": "ALLOWED | BLOCKED_SSRF | BLOCKED_ALLOWLIST | BLOCKED_SIZE_OR_MIME | QUARANTINED_INFECTED",
    "effective_max_bytes": "integer (min(26214400, verified_provider_method_limit))",
    "actual_size_bytes": "integer | null",
    "resolved_mime_type": "string | null",
    "content_sha256": "string | null",
    "scan_status": "PENDING | CLEAN | INFECTED | FAILED",
    "asset_id": "uuid | null (chỉ gắn khi scan_status = CLEAN)",
    "quarantined_event_id": "uuid | null",
    "fetched_at": "timestamptz (UTC)"
  }
}
```

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
> - Chạy hoàn toàn trên **`Lane 3 (HEAVY_BATCH_BACKFILL)`**, luôn gắn `source_mode = 'REPLAY'` (không tạo SLA/Journey live `OC09`), đi qua cùng bảng dedup `Inbound_Events` và kiểm lại `M20` trước mọi side-effect (`OC08`, `OC19`).

---

## 3. Domain Events Phát hành & Tiêu thụ (Qua Internal Outbox `M23-F12` — `ADR-005`)

### 3.1. Envelope Chuẩn Mọi Sự kiện `M19` (`schema_version = "1.1"`)

Dùng cấu trúc Envelope thống nhất (`event_id`, `event_type`, `aggregate_type`, `aggregate_id`, `aggregate_version`, `schema_version`, `tenant_id`, `workspace_id`, `occurred_at`, `correlation_id`, `causation_id`, `payload`).

### 3.2. Danh mục Sự kiện Phát hành (`Published Events`)

| Event Name | Payload Trọng yếu | Consumers Bắt buộc | Hành động Phải thực thi |
|---|---|---|---|
| `M19.InboundEventPersisted` | `inbound_event_id`, `connection_id`, `provider`, `event_type`, `source_mode` (`LIVE \| BACKFILL \| REPLAY`), `payload_ref`, `occurred_at` | `M03`, `M01`, `M09`, `M21`, `M22` | `M03` chiếu hội thoại/tin nhắn; nếu `source_mode = BACKFILL` thì chỉ ghi lịch sử, không tính SLA mới hoặc chạy trigger nurture (`OC09`); `M09` đối soát `PAYMENT_GW`; `M21`/`M22` nạp dataset/device/payroll status theo adapter |
| `M19.OutboundDispatchResulted` | `outbound_intent_id`, `message_id`, `channel`, `status` (`ACCEPTED \| BLOCKED_BY_POLICY \| EXPIRED_CANCELLED \| UNKNOWN_OUTCOME \| FAILED_TERMINAL`), `provider_message_id`, `reason_code` | `M03`, `M04`, `M12`, `M09`, `M22` | Cập nhật trạng thái gửi thực tế tại màn hình nguồn; hiển thị cờ chờ đối soát `UNKNOWN_OUTCOME` (`UC19`, `INT25`) hoặc lý do bị chặn `M20`/`M14` |
| `M19.MessageReceiptUpdated` *(Mới — từ `Message_Status_Events` `ENTITY-L2823` & `Email_Delivery_Events` `ENTITY-L2893` do `M19-F04` ingest)* | `message_status_event_id`, `outbound_intent_id`, `message_id`, `connection_id`, `channel`, `purpose_code`, `endpoint_lookup_hash`, `endpoint_masked` *(tùy kênh/payload, nullable)*, `receipt_status` (`ACCEPTED \| SENT \| DELIVERED \| DEFERRED \| READ \| BOUNCED_HARD \| BOUNCED_SOFT \| COMPLAINED \| FAILED`), `occurred_at` | `M03`, `M20`, `M04`, `M12` | `M03` cập nhật trạng thái đọc/nhận/bounce theo thứ tự đơn điệu (`ACCEPTED -> READ`, `ACCEPTED -> FAILED` `OC07`); `M20-F03` tiếp nhận trực tiếp `{channel, endpoint_lookup_hash, purpose_code, endpoint_masked, receipt_status}` từ payload event để ghi/cập nhật `Endpoint_Suppressions` mà **không truy vấn chéo DB `M19`** (`INDEX.md L62`, cấm hồi sinh trước khi gửi kế tiếp; bảng `Email_Delivery_Events` đã do `M19-F04` ingest trước đó) |
| `M19.ConnectionHealthChanged` | `connection_id`, `provider`, `old_status`, `new_status` (`ACTIVE \| DEGRADED \| REAUTHORIZATION_REQUIRED \| PAUSED \| DISCONNECTED`), `health_reason_redacted` | `M03`, `M21`, `M22`, `M23-F08` | Vô hiệu hóa nút gửi/đồng bộ khi mất kết nối, cảnh báo owner có runbook (`ONFR05`), báo `Availability` 2 lớp (`ONFR06`) |
| `M19.SyncCoverageGapReported` | `connection_id`, `checkpoint_id`, `stream_key`, `coverage_from`, `coverage_to`, `coverage_status` (`COMPLETE \| PARTIAL \| UNKNOWN`), `gap_reason` | `M03`, `M18`, `M21`, `M23-F08` | Hiển thị trung thực khoảng dữ liệu lịch sử không lấy lại được trên Monitor/BI (`OC21`, `UC21`, `CMO-U25`) thay vì báo `"100%"` giả |

### 3.3. Danh mục Sự kiện Liên Module `M19` Tiêu thụ (`Subscribed Events`)

| Nguồn & Event | Hành vi Xử lý Tại `M19` |
|---|---|
| **`M14.PermissionVersionBumped`** | Làm mới kiểm tra quyền cho worker dispatch / từ chối các lệnh `DispatchOutboundIntent` hoặc `ReplayConnectionEvents` đang giữ `expected_permission_version` cũ (`409 AUTH_PERMISSION_VERSION_STALE` — `ADR-003`, `CEO-U18`) |
| **`M14.UserOffboardingLocked` / `M14.WorkHandoverAssigned`** | Ngừng phát các `Outbound_Intents` theo lịch gắn `actor_id` cũ (hoặc chuyển `owner/approver` sang Custodian mới sau xác nhận `OC18`); từ chối cấp lại quyền replay/connect cho actor bị khóa |
| **`M14.WorkspaceActivated`** | Cho phép mở quyền đăng ký/kích hoạt `Channel_Connections` trong `workspace_id` vừa kích hoạt (phải kiểm `Processing_Records` ở `M20` trước khi lên `ACTIVE`) |
| **`M20.EndpointSuppressed`** | Hủy ngay toàn bộ `Outbound_Intents` còn ở trạng thái `QUEUED` hoặc `RETRY_WAITING` khớp `(tenant_id, workspace_id, channel, endpoint_lookup_hash)` + `purpose_scope` $\rightarrow$ chuyển sang `BLOCKED_BY_POLICY` (`OC17`, `RV17`) |
| **`M20.SubjectErasureExecuted`** | Hủy toàn bộ `Outbound_Intents` đang xếp hàng liên quan tới `endpoint_hmac_hashes` bị xóa và đánh dấu purge các `payload_ref` raw payload theo chính sách `Retention` |
| **`M20.DataIncidentEscalated`** | Nếu `affected_connection_ids[]` không rỗng: đưa ngay kết nối bị nghi rò rỉ token sang `REAUTHORIZATION_REQUIRED` / `PAUSED` và thu hồi secret cũ khỏi Vault cache (`M20-F08`) |
| **`M23.FeatureFlagUpdated`** (`M23-F09`) | Khi tắt cờ kênh hoặc `M06`/`M21`, áp dụng `Feature Flag Closure` đóng toàn bộ endpoint webhook/outbox của kênh tương ứng (`RV20`) |
