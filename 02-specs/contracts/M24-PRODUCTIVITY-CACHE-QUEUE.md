# Contract `M24-PRODUCTIVITY-CACHE-QUEUE` — Cổng Lệnh Hàng loạt, Thông báo Nội bộ, Cache Quyền & Phân làn Hàng đợi

- **Contract ID:** `CONTRACT-M24-PRODUCTIVITY-SCALE-v1.0`
- **Provider Owner:** `M24` (Lớp Tăng Hiệu năng Hệ thống & Hiệu suất Người dùng — `[PROPOSED]`)
- **Consumers:** Toàn bộ `M01–M23` (đặc biệt `M01`, `M02`, `M03`, `M04`, `M06`, `M11`, `M14`, `M16`, `M18`, `M19`, `M20`, `M21`, `M22`, `M23`)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`; Mục `3.3`, `3.10`, `3.14`, `6.1`, `6.2`, `6.4`, `6.6`, `6.8`, `7.1 NFR01–12`, `7.2`, `7.4`, `7.6 ONFR01–04`, `7.7`, `7.8 P-NFR06`, `U24`, `U21`, `INT23`, `INT26`, `CEO-U18`), [INVARIANTS.md](../../01-architecture/INVARIANTS.md) (`INV-02`, `INV-03`, `INV-04`, `INV-05`, `INV-06`, `INV-09`, `INV-23`, `INV-24`, `INV-25`), [ADR-002](../../01-architecture/decisions/ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-003](../../01-architecture/decisions/ADR-003-PERMISSION-VERSION-CACHE-AND-MODE-GOVERNANCE.md), [ADR-004](../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-005](../../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](../../01-architecture/decisions/ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [M24-PERFORMANCE-AND-PRODUCTIVITY.md](../modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md)
- **Trạng thái:** `Reviewed (Wave 1.5 Foundation Hardening — CR-20261116-WAVE1-5-HARDENING Applied & Verified; Documentation-Only)`
- **Chính sách Breaking Change:** Additive-only cho trường mới tùy chọn; mọi thay đổi cấu trúc bắt buộc của `Input`/`Output`, enum `lane_code`, `cache_status`, hoặc Event Envelope `schema_version = "1.0"` bắt buộc cập nhật đồng bộ `M14`, `M16`, `M18`, `M19`, `M20`, `M23` và giữ tương thích ngược cho backlog `M23-F12.Internal_Outbox_Events` & `Internal_Notifications`.

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | `M24` cung cấp **4 cổng hạ tầng hiệu năng & năng suất người dùng (`INV-24`, `INV-25`)** mà **không sở hữu quyền hay logic nghiệp vụ domain gốc (`INV-03`, `INV-04`)**: (1) `ExecuteDryRunAndCommitBulkCommand` (thực thi thao tác hàng loạt 2 bước `DRY_RUN -> COMMIT` kèm `expected_version` và cấm tuyệt đối thao tác tài chính/ký hợp đồng/xóa PII), (2) `EnqueueInternalNotificationDispatch` (điều phối thông báo nội bộ `Internal_Notifications` với lease dedup `SL01-T05`, che PII chat/lương, tôn trọng `M23-F10 Quiet Hours`, và recheck ACL khi mở deep-link), (3) `QueryOrInvalidatePermissionCache` (quản lý bản chiếu `Permission_Cache_Versions` từ SSoT `M14.Principal_Permission_Versions` theo nguyên tắc `MAX(permission_version)` chống out-of-order, **chặn rollback DR `client_version > db_version -> 401` theo `ADR-003`**, fallback Primary DB khi Redis/Cache sập `INV-25`, và xóa trắng 100% khi DR Restore), và (4) `EnqueueQueueLaneTask` (phân luồng việc nền vào đúng 3 làn cô lập `LANE_1_REALTIME_CRITICAL`, `LANE_2_STANDARD_INTERACTIVE`, `LANE_3_HEAVY_BATCH_BACKFILL` có backpressure & circuit breaker `GAP-18`). |
| **Actor/scope** | `principal_id` thuộc `USER | SERVICE_PRINCIPAL | PORTAL_CLIENT` được xác thực trong `tenant_id`, `workspace_id` & `workspace_type` (`AGENCY \| CLIENT \| SYSTEM`) từ server session/job context (không tin `tenant_id` trần từ client `INV-01`). Mọi truy vấn `Command_Palette_Index` / `Read_Model_Projections` bắt buộc qua `M14.CompileScopeFilter` trước khi trả snippet hay count (`NFR07`). `Internal_Notifications` chỉ gửi tới `recipient_id` còn `ACTIVE` và có ACL hợp lệ tại thời điểm mở (`Nhóm B-Gov`: `FORCE RLS` khóa `app.current_workspace_type IN ('AGENCY', 'SYSTEM')` hoặc đúng `recipient_id = current_principal_id` / `worker_runtime_role`). |
| **Preconditions** | Mọi giao dịch DB chạy `M14.BindDbTransactionContext` gắn đủ **bộ `6` GUC Canonical** (`app.current_tenant_id`, `app.current_workspace_id`, `app.current_workspace_type`, `app.current_principal_id`, `app.current_permission_version`, `app.current_acting_mode`). `ExecuteDryRunAndCommitBulkCommand (COMMIT)` bắt buộc có phiếu `DRY_RUN` hợp lệ trước đó, kiểm `M14.EvaluateAccessDecision(execution_mode = 'GUARDED_EXECUTION', expected_permission_version)` và từ chối ngay các hành động nhạy cảm bị cấm (`FINANCIAL_APPROVAL`, `CONTRACT_SIGNING`, `PRIVACY_ERASURE`). `EnqueueInternalNotificationDispatch` bắt buộc kiểm `title_redacted` không chứa PII chat thô hoặc dữ liệu lương `M22`. |
| **Input** | Xem 4 cặp JSON Schema đầy đủ ở Mục 2 (`ExecuteDryRunAndCommitBulkCommandInput`, `EnqueueInternalNotificationDispatchInput`, `QueryOrInvalidatePermissionCacheInput`, `EnqueueQueueLaneTaskInput`). Mọi khối JSON hợp lệ chuẩn `json.loads()`. |
| **Output** | Xem 4 cặp Output JSON Schema đầy đủ ở Mục 2 (`ExecuteDryRunAndCommitBulkCommandOutput`, `EnqueueInternalNotificationDispatchOutput`, `QueryOrInvalidatePermissionCacheOutput`, `EnqueueQueueLaneTaskOutput`). Không trả raw DB row của domain hay bản ghi ngoài ACL. |
| **Errors** | Chuẩn Error Envelope `{code, message, field_errors, correlation_id}`. Mã lỗi chính: `401 AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED`; `403 AUTH_RBAC_FORBIDDEN`; `403 BULK_ACTION_FORBIDDEN_FOR_SENSITIVE_DOMAIN` (`INV-25` chặn tài chính/hợp đồng/erasure); `404 RESOURCE_NOT_FOUND_OR_DENIED` (`U17`); `409 AUTH_PERMISSION_VERSION_STALE` (`GUARDED_EXECUTION`); `409 BULK_ITEM_VERSION_CONFLICT`; `409 IDEMPOTENCY_PAYLOAD_CONFLICT`; `422 DRY_RUN_REQUIRED`; `422 NOTIFICATION_PII_REDACTION_VIOLATION`; `429 QUEUE_LANE_BACKPRESSURE_THROTTLED` / `503 QUEUE_CIRCUIT_OPEN` (`GAP-18`). |
| **Concurrency** | `ExecuteDryRunAndCommitBulkCommand` xử lý từng chunk trong transaction nhỏ với `expected_version` CAS trên từng `Bulk_Command_Items` (mục conflict báo `CONFLICT_409` riêng rẽ, không ghi đè last-write-wins). `Internal_Notifications` dùng lease atomic `(lease_owner_id, lease_expires_at)` + **`UNIQUE NULLS NOT DISTINCT (tenant_id, workspace_id, dedup_key)`** (`SL01-T05`, chống trùng tuyệt đối ngay cả khi `workspace_id IS NULL` thuộc `Nhóm B-Gov`). `Permission_Cache_Versions` cập nhật bằng `WHERE incoming_version > current_version` (`MAX(permission_version)`) và `Read_Model_Projections` kiểm `incoming_event_version > source_event_version` để miễn nhiễm với out-of-order events. |
| **Idempotency** | `ExecuteDryRunAndCommitBulkCommand`: `UNIQUE (tenant_id, workspace_id, actor_id, idempotency_key)` trên `Bulk_Command_Batches`. `EnqueueInternalNotificationDispatch`: **`UNIQUE NULLS NOT DISTINCT (tenant_id, workspace_id, dedup_key)`** trên `Internal_Notifications` (bảo đảm chống chèn trùng kể cả khi `workspace_id IS NULL` thuộc `Nhóm B-Gov`, và worker crash + retry sau hết lease không sinh trùng thông báo `SL01-T05`). `EnqueueQueueLaneTask`: `UNIQUE (tenant_id, lane_code, idempotency_key)`. `QueryOrInvalidatePermissionCache` là thao tác idempotent đơn điệu (`MAX()` hoặc wipe toàn bộ). |
| **Transaction** | `Bulk_Command_Batches` không giữ DB lock kéo dài qua nhiều nghìn bản ghi: chia chunk nhỏ (`<= 100` items/tx), mỗi item gọi domain command chuẩn của module nguồn (`M02/M16`) trong 1 tx nguyên tử cùng `Audit_Logs` (`M23-F06`). `Internal_Notifications` nhận từ `M23-F12.Internal_Outbox_Events` và phát push/email/in-app sau commit (`INV-06`). |
| **Compatibility** | `schema_version = "1.0"`. Trường mới tùy chọn theo quy tắc additive-only; upcaster bỏ qua trường lạ trong payload `Read_Model_Projections`. Khi `Redis / Cache` sập, `QueryOrInvalidatePermissionCache` tự chuyển sang chế độ `REDIS_UNAVAILABLE_DB_FALLBACK` đọc thẳng `M14` Primary DB (`INV-25`, bảo toàn tính đúng bảo mật 100%). |
| **Audit/privacy** | `Bulk_Command_Batches` ghi đầy đủ `actor_id`, `reason`, `correlation_id`, số lượng đạt/lỗi vào `M23.Audit_Logs`. `Internal_Notifications` ẩn tuyệt đối nội dung chat nhạy cảm, SĐT/CCCD và lương/lý do nghỉ `M22` (`6.6`, `6.8`); click deep-link ép recheck ACL `M14`. `M20.SubjectErasureExecuted` (`erased_subject_refs[]`) kích hoạt scrub toàn bộ `Command_Palette_Index`, `Read_Model_Projections`, `Notification_Preferences_Digest`, `Internal_Notifications` và `Cold_Archive_Partitions`; `Cold_Archive_Partitions` tôn trọng `active_legal_hold_ids[]`. |
| **Tests** | `PF-T01..PF-T12`, `NFR01`, `NFR02` (4G mô phỏng RTT/bandwidth), `NFR03`, `NFR07`, `NFR09` (`U24`), `SL01-T05` (`lease dedup`), `INT23` / `CEO-U18` (`GUARDED_EXECUTION`), `U21` / `INT26` (`DR cache wipe & notification expiry`). Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas Đầy đủ cho 4 Cổng Hiệu năng & Năng suất (`C24` JSON Schemas)

> **Quy ước kiểm chứng JSON:** Mọi khối `json` dưới đây tuân thủ cú pháp JSON chuẩn (`json.loads()` hợp lệ, không dùng comment).

### 2.1. Cổng 1 — `ExecuteDryRunAndCommitBulkCommandInput` & `ExecuteDryRunAndCommitBulkCommandOutput` (`M24-F03`, `INV-25`)

```json
{
  "ExecuteDryRunAndCommitBulkCommandInput": {
    "tenant_id": "uuid (NN — suy xuất từ verified session)",
    "workspace_id": "uuid (NN)",
    "actor_id": "uuid (NN)",
    "expected_permission_version": "integer (bigint NN — kiểm tra M14 GUARDED_EXECUTION)",
    "mode": "DRY_RUN | COMMIT",
    "dry_run_batch_id": "uuid | null (bắt buộc non-null khi mode = COMMIT)",
    "domain_module": "M02 | M03 | M11 | M13 | M16",
    "command_type": "ASSIGN_OWNER | ADD_TAG | REMOVE_TAG | CHANGE_DUE_DATE | CLOSE_NON_FINANCIAL | SNOOZE_TASK",
    "items": [
      {
        "resource_type": "LEAD | DEAL | CONVERSATION | TICKET | TASK",
        "resource_id": "uuid (NN)",
        "expected_row_version": "integer (bigint NN — chống ghi đè mù)"
      }
    ],
    "command_params": {
      "target_owner_id": "uuid | null",
      "tag_codes": ["string"],
      "new_due_at": "timestamptz | null (UTC)",
      "reason": "string (NN — 1..1000 chars cho audit)"
    },
    "idempotency_key": "uuid (NN)",
    "correlation_id": "uuid (NN)"
  },
  "ExecuteDryRunAndCommitBulkCommandOutput": {
    "batch_id": "uuid",
    "mode": "DRY_RUN | COMMIT",
    "status": "DRY_RUN_READY | COMPLETED | PARTIAL_COMPLETED | REJECTED_FORBIDDEN_DOMAIN | FAILED",
    "total_items": "integer (>= 0)",
    "eligible_or_succeeded_count": "integer (>= 0)",
    "blocked_or_conflict_count": "integer (>= 0)",
    "item_results": [
      {
        "resource_id": "uuid",
        "item_status": "PREVIEW_ELIGIBLE | PREVIEW_BLOCKED | SUCCEEDED | CONFLICT_409 | FORBIDDEN_403 | FAILED",
        "error_code": "string | null"
      }
    ],
    "audit_log_id": "uuid | null",
    "idempotent_replay": "boolean",
    "processed_at": "timestamptz (UTC)",
    "correlation_id": "uuid",
    "schema_version": "1.0"
  }
}
```

### 2.2. Cổng 2 — `EnqueueInternalNotificationDispatchInput` & `EnqueueInternalNotificationDispatchOutput` (`M24-F05`, `SL01-T05`)

```json
{
  "EnqueueInternalNotificationDispatchInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid | null",
    "recipient_id": "uuid (NN — user nhận thông báo)",
    "source_module": "M01 | M02 | M03 | M04 | M05 | M06 | M07 | M08 | M09 | M10 | M11 | M12 | M13 | M14 | M15 | M16 | M17 | M18 | M19 | M20 | M21 | M22 | M23 | M24",
    "source_event_id": "uuid (NN)",
    "source_resource_type": "string (NN)",
    "source_resource_id": "uuid (NN)",
    "priority_tier": "URGENT | ACTIONABLE | DIGEST",
    "title_redacted": "string (NN — max 180 chars, tuyệt đối không chứa PII chat thô hoặc lương M22)",
    "deep_link_ref": "string (NN — URI nội bộ; bắt buộc recheck M14 ACL khi click)",
    "dedup_key": "string (NN — UNIQUE NULLS NOT DISTINCT (tenant_id, workspace_id, dedup_key) chống trùng kể cả khi workspace_id IS NULL và khi retry/crash SL01-T05)",
    "respect_quiet_hours": "boolean (default true; URGENT có thể đánh thức theo policy M23-F10)",
    "expires_at": "timestamptz (UTC NN — dùng hủy thông báo quá khứ trước T_restore khi DR)",
    "lease_ttl_seconds": "integer (default 60, range 15..300)",
    "correlation_id": "uuid (NN)"
  },
  "EnqueueInternalNotificationDispatchOutput": {
    "notification_id": "uuid",
    "recipient_id": "uuid",
    "status": "PENDING | DEFERRED_QUIET_HOURS | BLOCKED_RECIPIENT_INACTIVE | DUPLICATE_DEDUP_NOOP (ánh xạ chuẩn: BLOCKED_RECIPIENT_INACTIVE -> trạng thái BLOCKED_ACL trong M24.Internal_Notifications)",
    "scheduled_deliver_at": "timestamptz | null (UTC)",
    "requires_acl_recheck_on_open": "boolean (bắt buộc true — luôn ép recheck M14 ACL khi mở deep-link)",
    "idempotent_replay": "boolean",
    "correlation_id": "uuid",
    "schema_version": "1.0"
  }
}
```

### 2.3. Cổng 3 — `QueryOrInvalidatePermissionCacheInput` & `QueryOrInvalidatePermissionCacheOutput` (`M24-F06`, `ADR-003`, `INV-25`)

```json
{
  "QueryOrInvalidatePermissionCacheInput": {
    "tenant_id": "uuid (NN)",
    "operation": "QUERY_VERSION | INVALIDATE_AND_BUMP_MIRROR | WIPE_ALL_DR_RESET",
    "principal_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT | null (null chỉ cho WIPE_ALL_DR_RESET)",
    "principal_id": "uuid | null (null chỉ cho WIPE_ALL_DR_RESET)",
    "client_permission_version": "integer | null (bigint — gửi khi QUERY_VERSION để đối chiếu client_permission_version > db_version; kiểm rollback DR phải dùng authoritative_db_version từ Primary DB M14)",
    "authoritative_db_version": "integer | null (bigint — nhận từ M14.Principal_Permission_Versions Primary DB; nếu null hoặc cache miss / sau DR wipe thì M24 bắt buộc đọc fallback Primary DB M14 trước khi kết luận BLOCK_DR_ROLLBACK_401)",
    "observed_permission_version": "integer | null (bigint — chỉ cập nhật khi observed_permission_version > current MAX)",
    "acl_epoch": "integer | null (bigint — tăng nhảy cóc khi DR Startup Fence)",
    "reason": "string | null",
    "correlation_id": "uuid (NN)"
  },
  "QueryOrInvalidatePermissionCacheOutput": {
    "cache_status": "HIT | MISS_FALLBACK_PRIMARY_DB | STALE_INVALIDATED | MONOTONIC_UPDATED | IGNORED_OUT_OF_ORDER | REDIS_UNAVAILABLE_DB_FALLBACK | DR_CACHE_WIPED | BLOCK_DR_ROLLBACK_401",
    "principal_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT | null",
    "principal_id": "uuid | null",
    "effective_cache_version": "integer | null (bigint — giá trị MAX đang giữ)",
    "effective_acl_epoch": "integer | null (bigint)",
    "requires_primary_db_reload": "boolean (true khi MISS/STALE/REDIS_UNAVAILABLE/DR_CACHE_WIPED; bắt buộc false khi BLOCK_DR_ROLLBACK_401 vì phải fail-closed ngay)",
    "requires_session_revoke_401": "boolean (true khi client_permission_version > authoritative_db_version từ M14.Principal_Permission_Versions Primary DB — buộc M23-F02 cắt phiên & M23-F08 ghi cảnh báo)",
    "wiped_entries_count": "integer | null",
    "evaluated_at": "timestamptz (UTC)",
    "correlation_id": "uuid",
    "schema_version": "1.0"
  }
}
```

> **Quy tắc Rollback Guard `401` (`ADR-003`, `INV-25`):** Với luồng kiểm rollback `client_permission_version > db_version -> BLOCK_DR_ROLLBACK_401`, hệ thống **KHÔNG chỉ đọc bảng cache `M24.Permission_Cache_Versions`** (vốn có thể trống sau DR wipe hoặc bị trễ đồng bộ), mà bắt buộc nhận `authoritative_db_version` từ **`M14.Principal_Permission_Versions` (Primary DB)** — hoặc đọc fallback trực tiếp từ Primary DB `M14` khi cache miss / sau DR wipe — mới quyết định `BLOCK_DR_ROLLBACK_401` (`requires_session_revoke_401 = true`, cắt phiên `M23-F02`).

### 2.4. Cổng 4 — `EnqueueQueueLaneTaskInput` & `EnqueueQueueLaneTaskOutput` (`M24-F07`, `ADR-005`, `GAP-18`)

```json
{
  "EnqueueQueueLaneTaskInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid | null",
    "lane_code": "LANE_1_REALTIME_CRITICAL | LANE_2_STANDARD_INTERACTIVE | LANE_3_HEAVY_BATCH_BACKFILL",
    "task_type": "WEBHOOK_LIVE_INGEST | INBOX_LIVE_REPLY | INTERNAL_OUTBOX_DISPATCH | NOTIFICATION_DISPATCH | READ_MODEL_PROJECT | BULK_COMMAND_CHUNK | BACKFILL_SYNC | REMOTE_MEDIA_FETCH | ASYNC_EXPORT | BI_AGGREGATION | COLD_ARCHIVE_PARTITION",
    "actor_id": "uuid | null",
    "expected_permission_version": "integer | null (bắt buộc non-null cho tác vụ GUARDED_EXECUTION như ASYNC_EXPORT / BULK_COMMAND_CHUNK)",
    "payload_ref": "string (NN — tham chiếu payload, không chứa secret thô)",
    "priority_weight": "integer (default 100, range 1..1000)",
    "idempotency_key": "string (NN)",
    "correlation_id": "uuid (NN)"
  },
  "EnqueueQueueLaneTaskOutput": {
    "queued_job_id": "uuid",
    "assigned_lane": "LANE_1_REALTIME_CRITICAL | LANE_2_STANDARD_INTERACTIVE | LANE_3_HEAVY_BATCH_BACKFILL",
    "backpressure_applied": "ACCEPTED | THROTTLED_DEFERRED | REJECTED_CIRCUIT_OPEN",
    "lane1_oldest_pending_age_ms": "integer (>= 0)",
    "estimated_delay_ms": "integer (>= 0)",
    "idempotent_replay": "boolean",
    "queued_at": "timestamptz (UTC)",
    "correlation_id": "uuid",
    "schema_version": "1.0"
  }
}
```

---

## 3. Domain Events Phát hành & Tiêu thụ (Qua `M23-F12.Internal_Outbox_Events` — `ADR-005`)

### 3.1. Envelope Chuẩn Mọi Sự kiện `M24` (`schema_version = "1.0"`)

```json
{
  "event_id": "uuid",
  "event_type": "M24.BulkCommandBatchCompleted | M24.AsyncExportJobCompleted | M24.QueueBackpressureStateChanged",
  "aggregate_type": "BULK_COMMAND_BATCH | ASYNC_EXPORT_JOB | QUEUE_LANE_CONFIG",
  "aggregate_id": "uuid",
  "aggregate_version": "integer (bigint >= 1)",
  "schema_version": "1.0",
  "tenant_id": "uuid",
  "workspace_id": "uuid | null",
  "occurred_at": "timestamptz (UTC)",
  "correlation_id": "uuid",
  "causation_id": "uuid | null",
  "payload": {}
}
```

### 3.2. Danh mục Sự kiện `M24` Phát hành (`Published Events`)

| Event Name | Payload Trọng yếu | Consumers Bắt buộc | Hành động Phải thực thi phía Consumer |
|---|---|---|---|
| `M24.BulkCommandBatchCompleted` | `batch_id`, `actor_id`, `domain_module`, `command_type`, `total_items`, `succeeded_count`, `conflict_count`, `forbidden_count`, `completed_at` | `M23-F06`, `M24-F05`, `M24-F06` | `M23-F06` chốt bản ghi kiểm toán; `M24-F05` thông báo tổng kết cho `actor_id`; `M24-F06` đồng bộ Read Model bị ảnh hưởng |
| `M24.AsyncExportJobCompleted` | `async_export_job_id`, `export_request_id`, `asset_id`, `asset_version_id`, `status` (`READY \| FAILED \| BLOCKED_STALE_PERMISSION`), `row_count`, `csv_formula_neutralized` | `M23-F07`, `M24-F05`, `M18-F10` | `M23-F07` cập nhật `Export_Requests` và mở link tải ngắn hạn qua `Download Gateway SEC03` (`INV-24`); `M24-F05` gửi thông báo link tải an toàn |
| `M24.QueueBackpressureStateChanged` | `lane_code`, `circuit_breaker_state` (`CLOSED \| OPEN \| HALF_OPEN`), `throttle_ratio`, `lane1_oldest_pending_age_ms`, `changed_at` | `M23-F12`, `M19-F06/08`, `M18` | `M23-F12` hiển thị cảnh báo sức khỏe làn; `M19-F06/08` tự động giãn nhịp Backfill/Replay tại `LANE_3` bảo vệ `LANE_1` |

### 3.3. Danh mục Sự kiện Liên Module mà `M24` Bắt buộc Tiêu thụ (`Subscribed Events`)

| Nguồn & Event | Ý nghĩa & Hành vi Xử lý Idempotent Tại `M24` |
|---|---|
| **`M14.PermissionVersionBumped`** (`C14` — `principal_type`, `principal_id`, `new_permission_version`, `acl_epoch`) | Cập nhật `Permission_Cache_Versions` theo quy tắc **chỉ giữ `MAX(permission_version)`** (`WHERE new_permission_version > permission_version`), xóa cache Redis của principal đó (`M24-F06`), và hủy các `Internal_Notifications` đang chờ gửi chứa thông tin vượt quyền mới. Khi Redis sập, fallback trực tiếp sang Primary DB `M14` (`INV-25`). |
| **`M14.UserOffboardingLocked`** & **`M14.WorkHandoverAssigned`** (`C14`) | Khi `case_type = 'OFFBOARD'`, đánh dấu hết hạn/hủy toàn bộ `Internal_Notifications` chưa giao của `user_id`; điều chỉnh lại notification assignee khi bàn giao `WorkHandoverAssigned`. |
| **`M16.TaskCreated`** (`C16`) | `M24-F06` chiếu vào `Read_Model_Projections` (`My Work` / `Team Board` với `source_event_version` check + ACL); `M24-F05` phát `Internal_Notifications` qua `SL01-T05` lease dedup (ẩn title `PERSONAL`/context cấm). |
| **`M16.TaskDeadlineOrAssignmentChanged`** (`C16`) | `M24-F06` cập nhật projection hạn/người làm (kiểm `source_event_version > current`); `M24-F05` thông báo assignee/reviewer mới sau khi kiểm ACL. |
| **`M16.TaskLifecycleOrStageChanged`** (`C16`) | `M24-F06` cập nhật `Team Board` Kanban count/stage theo `source_event_version` (bao gồm chuyển trạng thái `REOPEN` / `Task_Events.TaskReopened`); `M24-F05` gửi thông báo thay đổi trạng thái quan trọng (`IN_REVIEW`, `REOPEN`, `BLOCKED`) theo tùy chọn Digest/Quiet Hours. |
| **`M16.TaskCompleted`** (`C16`) | `M24-F06` cập nhật trạng thái `DONE` trên `My Work`/`Team Board` và cập nhật chỉ mục tìm kiếm `Command_Palette_Index` (`INV-05`: tuyệt đối không tự đánh dấu Deliverable accepted / Ticket closed / Paid). |
| **`M16.ProjectInitialized`** (`C16`) | `M24-F06` khởi tạo/cập nhật projection danh mục dự án (`Portfolio Load` / `Team Board`) theo `source_event_version` và ACL `AGENCY`/`CLIENT` workspace. |
| **`M16.DeliverablePublishedForReview`** (`C16`) | `M24-F06` cập nhật projection Portal (`CLIENT_REVIEW` sẵn sàng review); `M24-F05` gửi thông báo link an toàn qua `SEC03` tới `PORTAL_CLIENT` thuộc `authorized_client_approvers[]` (ẩn toàn bộ dữ liệu nội bộ `AGENCY`). |
| **`M16.DeliverableReworkRequested`** *(cùng `DeliverableRevisionBatchOpened` `C16`)* | `M24-F06` cập nhật projection trạng thái `REWORK` & `Revision_Batches` (giữ nguyên Task vòng cũ ở `DONE`); `M24-F05` cảnh báo PM / Delivery Lead. |
| **`M16.DeliverableAccepted`** (`C16`) | `M24-F06` cập nhật projection nghiệm thu & độ tin cậy milestone; `M24-F05` thông báo tới PM/AM/Finance theo cấu hình. |
| **`M16.ClientWaitIntervalRecorded`** (`C16`) | `M24-F06` cập nhật projection chỉ báo chờ khách trên `Team Board` / `Portfolio Load` (giữ nguyên `committed_due_at`, tách bạch `Client-Wait` khỏi KPI nội bộ). |
| **`M20.SubjectErasureExecuted`** (`C20` — `erased_subject_refs[]`, `endpoint_hmac_hashes_by_version[]`) | `M24-F08` & `M24-F06` scrub sạch PII và dữ liệu đối tượng bị xóa trên **`Command_Palette_Index`**, **`Read_Model_Projections`**, **`Notification_Preferences_Digest`**, **`Internal_Notifications`** và **`Cold_Archive_Partitions`** khớp `erased_subject_refs[]` / `endpoint_hmac_hashes_by_version[]` (trừ phần có `active_legal_hold_ids` khác rỗng, thay bằng `REDACTED-SUBJECT-#...`). |
| **`M20.LegalHoldChanged`** (`C20`) | Cập nhật mảng **`active_legal_hold_ids uuid[]`** trên `Read_Model_Projections` và `Cold_Archive_Partitions`, chặn cứng job purge của `M24-F08` khi mảng không rỗng. |
| **`M23.FeatureFlagUpdated`** (`C23` — `flag_key`, `scope_type`, `scope_id`, `state`) | Kích hoạt/đóng các tính năng UX/Scale (`Ctrl+K`, `Split-View`, `Bulk`, `Quick Replies`, `Async Export`) đồng bộ cả giao diện lẫn endpoint. |
| **`M23.TenantOperatingModeChanged`**, **`M23.BreakGlassApproved`**, **`M23.BreakGlassRevoked`** (`C23`) | `M24-F05` phát cảnh báo tức thì về `Owner/CEO` khi phát sinh `self_approved_in_pilot_mode = true` hoặc hạ chế độ `TEAM -> SOLO_PILOT`; `M24-F06` làm mới trạng thái cache liên quan qua `M14`. |

---

## 4. Compatibility, Privacy & Test Matrix (`MODULE-SPEC` Aligned)

| Mã Test | Mục tiêu Kiểm chứng Hợp đồng `C24` | Severity | Applicability | Status | Actual / Build / Fixture |
|---|---|---|---|---|---|
| `PF-T03` / `INV-25` | `ExecuteDryRunAndCommitBulkCommand`: chặn `COMMIT` thiếu `DRY_RUN` (`422`), chặn `403 BULK_ACTION_FORBIDDEN_FOR_SENSITIVE_DOMAIN` cho tài chính/hợp đồng/erasure, chia chunk kiểm `expected_row_version` + `expected_permission_version` (`409`) | `P0 Blocker` | `SL03–SL06+` | `Not Run` | `Not Run / No Repo / Fixture-M24-BULK-03` |
| `PF-T05` / `SL01-T05` | `EnqueueInternalNotificationDispatch`: Worker crash sau dispatch trước ACK, hết lease worker khác nhận lại không gửi trùng (`dedup_key`), ẩn PII chat/lương, hoãn ngoài `Quiet Hours`, click deep-link recheck ACL `M14` | `P0 Blocker` | `SL01+` | `Not Run` | `Not Run / No Repo / Fixture-M24-NTF-05` |
| `PF-T06` / `NFR02` / `ADR-003` | `QueryOrInvalidatePermissionCache`: Nhận `M14.PermissionVersionBumped` lệch thứ tự (`v12` trước `v10`) giữ đúng `MAX = 12`; đối chiếu `client_permission_version > authoritative_db_version` (đọc từ `M14.Principal_Permission_Versions` Primary DB — không chỉ đọc bảng cache `Permission_Cache_Versions`, kể cả sau DR wipe/cache miss) trả ngay `401 BLOCK_DR_ROLLBACK_401`; khi Redis sập fallback Primary DB `M14`; Read Model mở danh sách Lead `<= 2s` trên 4G mô phỏng | `P0 Blocker` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M24-CACHE-06` |
| `PF-T07` / `GAP-18` | `EnqueueQueueLaneTask`: Tải bão `LANE_3` (Backfill/Export/AI) kích hoạt backpressure/circuit breaker, bảo vệ độ trễ `LANE_1` (`ONFR02 p95 <= 1s`) và `LANE_2` | `P0 Critical` | `SL00–SL07` | `Not Run` | `Not Run / No Repo / Fixture-M24-LANE-07` |
| `PF-T08` / `U21` / `INT26` | DR Restore xóa trắng 100% `Permission_Cache_Versions` + đánh dấu `EXPIRED_DR_SKIPPED` các `Internal_Notifications` trước `T_restore`; `M20.SubjectErasureExecuted` (`erased_subject_refs[]`) scrub index/projection/digest/cold partition và tôn trọng `active_legal_hold_ids` | `P0 Blocker` | `SL00+` / `SL04+` | `Not Run` | `Not Run / No Repo / Fixture-M24-DR-08` |
