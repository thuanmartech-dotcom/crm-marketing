# Contract `M23-PLATFORM-GOVERNANCE-OUTBOX` — Cổng Quản trị Nền tảng, Lịch Chuẩn, Phê duyệt Nội bộ, `Assets` & Outbox Nội bộ

- **Contract ID:** `CONTRACT-M23-PLATFORM-GOVERNANCE-v1.0`
- **Provider Owner:** `M23` (Quản trị Hệ thống, Bảo mật Vận hành & Nền tảng Cấu hình — `[PROPOSED]`)
- **Consumers:** Toàn bộ `M01–M24` (đặc biệt `M02`, `M03`, `M04`, `M07`, `M08`, `M09`, `M10`, `M11`, `M13`, `M14`, `M15`, `M16`, `M17`, `M18`, `M19`, `M20`, `M21`, `M22`, `M24`, `Download Gateway SEC03`)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`; Mục `5.1`, `5.13 L2783/2787`, `5.18 L2885`, `6.1`, `6.2`, `7.2–7.5`, `NFR05–12`, `SEC03`, `SEC06`, `CR05`, `U03`, `U21`), [INVARIANTS.md](../../01-architecture/INVARIANTS.md) (`INV-06`, `INV-13`, `INV-14`, `INV-15`, `INV-22..25`), [ADR-002](../../01-architecture/decisions/ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-003](../../01-architecture/decisions/ADR-003-PERMISSION-VERSION-CACHE-AND-MODE-GOVERNANCE.md), [ADR-004](../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-005](../../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](../../01-architecture/decisions/ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-009](../../01-architecture/decisions/ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md), [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md)
- **Trạng thái:** `Reviewed (Wave 1.5 Foundation Hardening — CR-20261116-WAVE1-5-HARDENING Applied & Verified; CR-20261116-SKILL-TEMPLATE-ALIGN Applied; Documentation-Only)`
- **Approved_Scope:** `Wave 1.5 Platform Governance, Internal Outbox, Approvals, Calendars & Asset Gateway Public Contract`
- **Approved_By:** `Chủ dự án`
- **Decision_Ref:** `CR-20261116-SKILL-TEMPLATE-ALIGN`
- **Approved_At:** `2026-11-16`
- **Chính sách Breaking Change:** Additive-only cho trường tùy chọn mới; mọi thay đổi cấu trúc bắt buộc của `Input`/`Output`, tập enum `lane`/`asset_domain`/`state`, hoặc Event Envelope `schema_version = "1.0"` bắt buộc giữ tương thích ngược (upcaster/dual-publish) cho hàng đợi `Internal_Outbox_Events` đang tồn đọng và cập nhật đồng thời toàn bộ Wave 1–5 Consumers (`M14`, `M16`, `M19`, `M20`, `M24`).

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | `M23` là **Cổng Nền tảng Vận hành, Phê duyệt Nội bộ, Lịch Chuẩn, Asset Registry & Outbox Nội bộ Dùng chung (`INV-22`, `INV-23`, `INV-24`)**, cung cấp **6 cổng công khai chính thức (`7` cặp Input/Output trên `6` nhóm JSON Schema tính cả Event Envelope Mục `3.1`)**: (1) `PublishInternalOutboxEvent` (ghi nhận sự kiện miền liên module vào `Internal_Outbox_Events` cùng transaction nghiệp vụ, tách biệt khỏi `M19` External Outbox theo `ADR-005`), (2) `EvaluateApprovalMatrix`, (3) `RecordApprovalDecision` (tính chuỗi thẩm quyền `Approval_Matrix_Rules` và ghi quyết định bất biến vào sổ duyệt dùng chung `Approval_Requests` + `Approval_Decisions` `Nhóm C`, tách khỏi `M16.Acceptances` nghiệm thu khách hàng), (4) `ComputeBusinessCalendarShift` (`AddBusinessMinutes` / `NextShiftStart` / `CheckQuietHours` từ `System_Calendars` cho `CR05`, `U03`, `M04`, `M11`, `M16`, `M22`), (5) `RegisterAssetAndDownloadGateway` (gồm `RegisterAssetVersion` + `DownloadGatewayStep3`: đăng ký `Assets` + `Asset_Versions` `ENTITY-L2783` với `Asset_Versions.scan_status` & `active_legal_hold_ids[]`, và thực thi **Bước 3 `Download Gateway SEC03`** sau khi Bước 1 `M14` & Bước 2 `M20` đều `ALLOW`), và (6) `LookupPolicyVersion` (tra cứu `Policy_Definitions`/`Policy_Versions` `ENTITY-L2885` ở trạng thái `ACTIVE`, fail-closed khi thiếu `INV-14`). |
| **Actor/scope** | `principal_id` thuộc `USER | SERVICE_PRINCIPAL | PORTAL_CLIENT` được xác thực trong `tenant_id`, `workspace_id` & `workspace_type` (`AGENCY \| CLIENT \| SYSTEM`) từ server session/job context (cấm tin `tenant_id` trần từ client payload `INV-01`). `Assets`, `Asset_Versions`, `Approval_Requests`, `Export_Requests` thuộc phạm vi `workspace_id NN` (`Nhóm A`, hỗ trợ `Contract_Workspace_Grants` cho `CLIENT` tải bản publish qua `SEC03`); `System_Calendars`, `Shared_Dictionaries`, `Shared_Templates` thuộc `Nhóm B-Catalog` (đọc chung theo Tenant ở `AGENCY` & `CLIENT`); `Policy_Definitions/Versions`, `Approval_Matrix_Rules`, `Feature_Flag_Configs`, `Break_Glass_Requests` thuộc `Nhóm B-Gov` (`FORCE RLS` ép `app.current_workspace_type IN ('AGENCY', 'SYSTEM')`, chặn `CLIENT` đọc cấu hình/quản trị `workspace_id IS NULL` theo `ADR-002` & `ADR-004`); `Audit_Logs`, `Approval_Decisions`, `Backup_Drill_Logs` là sổ bất biến `Nhóm C`. |
| **Preconditions** | Giao dịch DB phải gọi `M14.BindDbTransactionContext` gắn đủ **bộ `6` GUC Canonical** (`app.current_tenant_id`, `app.current_workspace_id`, `app.current_workspace_type`, `app.current_principal_id`, `app.current_permission_version`, `app.current_acting_mode`) trước mọi truy vấn/ghi (`app_runtime_role` hoặc `worker_runtime_role`, không `BYPASSRLS`). Các thao tác duyệt (`RecordApprovalDecision`, `BreakGlass`, `Export`, `TenantOperatingMode`) phải kiểm `M14.EvaluateAccessDecision` (`GUARDED_EXECUTION` + `expected_permission_version`) và kiểm chế độ `M14.Tenants.operating_mode`: ở `TEAM` (bao gồm cả lệnh hạ cấp **`TEAM -> SOLO_PILOT`** theo `ADR-003`), bắt buộc **`Maker != Checker`** (`INV-22`, tối thiểu 2 người có thẩm quyền độc lập xác nhận, gồm `Owner/CEO` khi hạ cấp); ở `SOLO_PILOT`, gắn cờ `self_approved_in_pilot_mode = true` và phát cảnh báo tức thì về `Owner/CEO`. Tải tệp ở Bước 3 `Download Gateway SEC03` chỉ chạy khi **`Asset_Versions.scan_status == 'CLEAN'`** và Bước 1 (`M14`) + Bước 2 (`M20`) đều trả `ALLOW` (`ADR-006`). |
| **Input** | Xem đủ **7 cặp Input JSON Schema** cho **6 cổng** trên **6 nhóm JSON Schema** (5 tiểu mục Mục 2 + 1 Event Envelope Mục 3.1): `PublishInternalOutboxEventInput`, `EvaluateApprovalMatrixInput`, `RecordApprovalDecisionInput`, `ComputeBusinessCalendarShiftInput`, `RegisterAssetVersionInput`, `DownloadGatewayStep3Input`, `LookupPolicyVersionInput`. Mọi khối JSON hợp lệ chuẩn `json.loads()`. |
| **Output** | Xem đủ **7 cặp Output JSON Schema** cho **6 cổng** ở Mục 2: `PublishInternalOutboxEventOutput`, `EvaluateApprovalMatrixOutput`, `RecordApprovalDecisionOutput`, `ComputeBusinessCalendarShiftOutput`, `RegisterAssetVersionOutput`, `DownloadGatewayStep3Output`, `LookupPolicyVersionOutput`. Không trả raw Storage presigned URL hay raw DB row. |
| **Errors** | Chuẩn Error Envelope `{code, message, field_errors, correlation_id}`. Mã lỗi chính: `401 AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED`; `403 AUTH_RBAC_FORBIDDEN`; `403 SELF_APPROVAL_FORBIDDEN_IN_TEAM_MODE` (`INV-22`); `404 RESOURCE_NOT_FOUND_OR_DENIED` (non-disclosure `U17`); `409 IDEMPOTENCY_PAYLOAD_CONFLICT`; `409 APPROVAL_VERSION_CONFLICT` (lệch `expected_version` hoặc `policy_version_id` đã superseded); `410 EXPORT_LINK_EXPIRED` (Bước 3 `SEC03` khi quá `download_expires_at` hoặc bị `SubjectErasure` thu hồi); `422 POLICY_MISSING_FAIL_CLOSED` (`INV-14`); `422 CALENDAR_NOT_CONFIGURED`; `422 FEATURE_FLAG_DEPENDENCY_UNMET` (`M23-F09`); `422 ASSET_NOT_CLEAN_OR_CHECKSUM_MISMATCH` (`PENDING/INFECTED/FAILED`); `422 ASSET_UNDER_ACTIVE_LEGAL_HOLD`. |
| **Concurrency** | `Approval_Requests`, `Export_Requests`, `Policy_Versions`, `Assets`, `System_Calendars`, `Feature_Flag_Configs` dùng optimistic locking (`row_version = expected_version`). `Internal_Outbox_Events` dùng `SKIP LOCKED` + lease TTL (`lease_owner_id`, `lease_expires_at`) để nhiều worker poll song song không xử lý trùng cùng event (`ADR-005`). `RegisterAssetVersion` bảo vệ thứ tự `version_no` duy nhất theo `(tenant_id, workspace_id, asset_id, version_no)`. |
| **Idempotency** | `PublishInternalOutboxEvent`: `UNIQUE (tenant_id, idempotency_key)` (cùng payload trả `outbox_event_id` hiện hữu; khác payload trả `409 IDEMPOTENCY_PAYLOAD_CONFLICT`). `RecordApprovalDecision`: `UNIQUE (tenant_id, workspace_id, approval_request_id, decision_step_no, idempotency_key)`. `RegisterAssetVersion`: `UNIQUE (tenant_id, workspace_id, asset_id, version_no)` & dedup theo `idempotency_key`. `ComputeBusinessCalendarShift` & `LookupPolicyVersion` là hàm thuần đọc tất định (`deterministic read-only`). |
| **Transaction** | `PublishInternalOutboxEvent` bắt buộc chạy **trong cùng DB transaction** với lệnh đột biến domain nguồn (`INV-06`); tác vụ worker đọc từ `Internal_Outbox_Events` chỉ xảy ra **sau commit**. `RecordApprovalDecision` ghi `Approval_Decisions` (`Nhóm C`) + cập nhật `Approval_Requests` + ghi `Audit_Logs` (`Nhóm C`) + ghi `Internal_Outbox_Events` (`Lane 2`) trong **1 DB transaction nguyên tử**. |
| **Compatibility** | `contract_version = "1.0"`, tách biệt với `envelope_schema_version` (`1.0 \| 1.1 \| 1.2` theo domain nguồn). Trường mới tùy chọn theo quy tắc additive-only; upcaster giữ tương thích ngược cho backlog `Internal_Outbox_Events` & `Internal_Dead_Letter_Queue` khi nâng cấp slice (`SL00 -> SL07`). Cờ `Feature_Flag_Configs` thực thi `Feature Flag Closure` (`OFF` trả `404/422 CAPABILITY_DISABLED`). |
| **Audit/privacy** | Mọi thay đổi chính sách, phê duyệt, Break-glass, Export, tải file qua `SEC03`, và sự cố an ninh đều ghi `Audit_Logs` (`Nhóm C` Append-Only) theo cơ chế **Redact-Before-Insert** (che CCCD, SĐT, số tài khoản, token — `6.2 L3120`, `NFR11`); Technical Admin **không có quyền `DELETE/UPDATE`** trên `Audit_Logs`. `M20.SubjectErasureExecuted` kích hoạt thu hồi `Export_Requests`, xóa/ẩn danh `Assets` không vướng `active_legal_hold_ids`, và **scrub PII trong `Internal_Outbox_Events` / `Internal_Dead_Letter_Queue`**. |
| **Tests** | `S-T01..S-T14`, `U03` (`CR05` calendar), `U16`, `SEC-U03` (`Download Gateway`), `SEC-U06` (`Maker != Checker`), `U21`, `INT26`, `CEO-U26`, `NFR05`, `NFR06`, `NFR07`, `NFR11`, `NFR12`. Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas Đầy đủ cho 6 Cổng Công khai (`7` Cặp Input/Output trên `6` Nhóm JSON Schema Tính cả Mục `3.1`)

> **Quy ước kiểm chứng JSON:** Mọi khối `json` dưới đây tuân thủ cú pháp JSON chuẩn (`json.loads()` hợp lệ, không dùng comment).

### 2.1. Cổng 1 — `PublishInternalOutboxEventInput` & `PublishInternalOutboxEventOutput` (`M23-F12`, `ADR-005`)

```json
{
  "PublishInternalOutboxEventInput": {
    "tenant_id": "uuid (NN — suy xuất từ verified transaction context)",
    "workspace_id": "uuid | null (NULL hợp lệ chỉ cho sự kiện cấp Tenant như M23.TenantOperatingModeChanged hoặc M20.SubjectErasureExecuted scope_tenant_wide)",
    "lane": "REALTIME_CRITICAL | STANDARD_INTERACTIVE | HEAVY_BATCH_BACKFILL",
    "aggregate_type": "string (NN — ví dụ TASK | PROJECT | DELIVERABLE | USER | APPROVAL_REQUEST | EXPORT_REQUEST | POLICY_VERSION | SYSTEM_CALENDAR | INTERNAL_OUTBOX | ASSET | PRIVACY_REQUEST | LEGAL_HOLD | EMPLOYEE)",
    "aggregate_id": "uuid (NN)",
    "aggregate_version": "integer (bigint >= 1)",
    "event_type": "string (NN — chuẩn <Module>.<EventName>, ví dụ M16.TaskCompleted, M14.PermissionVersionBumped, M23.BreakGlassApproved)",
    "envelope_schema_version": "string (NN — 1.0 | 1.1 | 1.2 theo payload domain nguồn)",
    "contract_version": "1.0",
    "payload_json": {
      "note": "object (payload đã redact PII nhạy cảm không cần thiết theo NFR11; chứa subject_hmac_sha256 hoặc ref thay cho PII thô khi phù hợp)"
    },
    "idempotency_key": "string (NN — UNIQUE theo tenant_id)",
    "correlation_id": "uuid (NN)",
    "causation_id": "uuid | null",
    "available_at": "timestamptz | null (UTC — mặc định now())"
  },
  "PublishInternalOutboxEventOutput": {
    "outbox_event_id": "uuid",
    "lane": "REALTIME_CRITICAL | STANDARD_INTERACTIVE | HEAVY_BATCH_BACKFILL",
    "status": "PENDING",
    "idempotent_replay": "boolean",
    "envelope_schema_version": "string (1.0 | 1.1 | 1.2 theo payload domain nguồn)",
    "contract_version": "1.0",
    "correlation_id": "uuid",
    "enqueued_at": "timestamptz (UTC)"
  }
}
```

**Ví dụ (`Example`) `PublishInternalOutboxEventInput` & `PublishInternalOutboxEventOutput`:**

```json
{
  "ExamplePublishInternalOutboxEventInput": {
    "tenant_id": "22222222-2222-4222-8222-222222222222",
    "workspace_id": "33333333-3333-4333-8333-333333333333",
    "lane": "STANDARD_INTERACTIVE",
    "aggregate_type": "TASK",
    "aggregate_id": "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
    "aggregate_version": 2,
    "event_type": "M16.TaskCompleted",
    "envelope_schema_version": "1.0",
    "contract_version": "1.0",
    "payload_json": {
      "task_id": "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
      "status": "DONE"
    },
    "idempotency_key": "m16-task-done-v2-dddddddd",
    "correlation_id": "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
    "causation_id": null,
    "available_at": "2026-11-16T10:05:00Z"
  },
  "ExamplePublishInternalOutboxEventOutput": {
    "outbox_event_id": "ffffffff-ffff-4fff-8fff-ffffffffffff",
    "lane": "STANDARD_INTERACTIVE",
    "status": "PENDING",
    "idempotent_replay": false,
    "envelope_schema_version": "1.0",
    "contract_version": "1.0",
    "correlation_id": "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
    "enqueued_at": "2026-11-16T10:05:00Z"
  }
}
```

### 2.2. Cổng 2 & Cổng 3 — `EvaluateApprovalMatrix` & `RecordApprovalDecision` (`M23-F04`, `ENTITY-L2783`)

```json
{
  "EvaluateApprovalMatrixInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "domain_module": "M06 | M07 | M08 | M10 | M14 | M15 | M16 | M17 | M20 | M22 | M23",
    "action_type": "QUOTE_DISCOUNT_EXCEPTION | CONTRACT_NONSTANDARD_TERM | PROJECT_CHANGE_REQUEST | TASK_SELF_REVIEW_OVERRIDE | BUDGET_OVERRUN | COMMISSION_ADJUSTMENT | BREAK_GLASS_ACCESS | PII_EXPORT_REQUEST | TENANT_MODE_DOWNGRADE | HR_PAYROLL_EXCEPTION | SANITIZED_FALLBACK_APPROVAL | AI_DRAFT_TASK_CONFIRMATION",
    "legal_entity_id": "uuid | null",
    "branch_id": "uuid | null",
    "currency": "string | null (char(3) từ allowlist đã duyệt)",
    "monetary_delta": "string | null (decimal string hữu hạn — cấm float, cấm NaN/Infinity)",
    "schedule_delta_days": "integer | null",
    "requester_id": "uuid (NN)",
    "target_resource_type": "string (NN)",
    "target_resource_id": "uuid (NN)",
    "correlation_id": "uuid (NN)"
  },
  "EvaluateApprovalMatrixOutput": {
    "matched_rule_id": "uuid | null",
    "matched_policy_version_id": "uuid | null",
    "evaluation_status": "RULE_MATCHED | POLICY_MISSING_FAIL_CLOSED",
    "tenant_operating_mode": "SOLO_PILOT | TEAM",
    "requires_dual_control": "boolean (luôn true khi TEAM)",
    "required_steps": [
      {
        "step_no": "integer (>= 1)",
        "approver_role_code": "string",
        "sla_hours": "integer (> 0)"
      }
    ],
    "correlation_id": "uuid",
    "schema_version": "1.0"
  },
  "RecordApprovalDecisionInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "approval_request_id": "uuid (NN)",
    "actor_id": "uuid (NN — người thực hiện phê duyệt/từ chối)",
    "expected_permission_version": "integer (bigint NN — M14 GUARDED_EXECUTION)",
    "expected_request_version": "integer (bigint NN — CAS Approval_Requests.row_version)",
    "decision": "APPROVED | REJECTED | RETURNED_FOR_INFO",
    "reason": "string (NN — 1..1000 chars)",
    "evidence_asset_id": "uuid | null",
    "idempotency_key": "uuid (NN)",
    "correlation_id": "uuid (NN)"
  },
  "RecordApprovalDecisionOutput": {
    "approval_decision_id": "uuid (bản ghi Nhóm C Append-Only)",
    "approval_request_id": "uuid",
    "request_status": "PENDING_APPROVAL | APPROVED | REJECTED | RETURNED_FOR_INFO | CANCELLED | EXPIRED",
    "current_step_no": "integer",
    "self_approved_in_pilot_mode": "boolean (bắt buộc false ở chế độ TEAM)",
    "locked_policy_version_id": "uuid",
    "row_version": "integer (bigint)",
    "idempotent_replay": "boolean",
    "decided_at": "timestamptz (UTC)",
    "correlation_id": "uuid",
    "schema_version": "1.0"
  }
}
```

### 2.3. Cổng 4 — `ComputeBusinessCalendarShiftInput` & `ComputeBusinessCalendarShiftOutput` (`M23-F10`, `CR05`, `U03`, `GAP-16`)

```json
{
  "ComputeBusinessCalendarShiftInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid | null",
    "branch_id": "uuid | null",
    "legal_entity_id": "uuid | null",
    "calendar_id": "uuid | null (null để resolve theo scope branch -> legal_entity -> tenant default)",
    "operation": "ADD_BUSINESS_MINUTES | NEXT_SHIFT_START | CHECK_QUIET_HOURS | GET_WORKING_MINUTES",
    "start_at_utc": "timestamptz (UTC NN)",
    "end_at_utc": "timestamptz | null (bắt buộc cho GET_WORKING_MINUTES)",
    "minutes_delta": "integer | null (bắt buộc >= 0 cho ADD_BUSINESS_MINUTES)",
    "correlation_id": "uuid (NN)"
  },
  "ComputeBusinessCalendarShiftOutput": {
    "calendar_id": "uuid",
    "calendar_version": "integer (bigint >= 1)",
    "timezone": "string (ví dụ Asia/Ho_Chi_Minh)",
    "computed_at_utc": "timestamptz (UTC — mốc hạn sau khi cộng ca làm việc)",
    "next_shift_start_utc": "timestamptz (UTC — mốc đầu ca làm việc kế tiếp cho CR05/U03)",
    "is_within_working_shift": "boolean",
    "is_holiday": "boolean",
    "is_within_quiet_hours": "boolean",
    "working_minutes_between": "integer | null",
    "correlation_id": "uuid",
    "contract_version": "1.0",
    "schema_version": "1.0"
  }
}
```

### 2.4. Cổng 5 — `RegisterAssetAndDownloadGateway` (`M23-F07`, `ENTITY-L2783`, `SEC03`, `ADR-006`)

```json
{
  "RegisterAssetVersionInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "branch_id": "uuid | null",
    "legal_entity_id": "uuid | null",
    "business_line_id": "uuid | null",
    "asset_id": "uuid | null (null khi tạo mới Asset; non-null khi thêm Asset_Version mới)",
    "asset_domain": "CRM_ATTACHMENT | CALL_RECORDING | EXPORT_BUNDLE | HRM_EMPLOYEE_DOCUMENT | CONTRACT_OR_FINANCE_DOC",
    "owner_resource_type": "string (NN — ví dụ TASK | DELIVERABLE | CONTRACT | EMPLOYEE | EXPORT_REQUEST)",
    "owner_resource_id": "uuid (NN)",
    "visibility_scope": "PERSONAL | TEAM | WORKSPACE",
    "account_id": "uuid | null",
    "subject_hmac_sha256": "string | null (char(64) để phục vụ đối soát SubjectErasureExecuted)",
    "object_key": "string (NN — đường dẫn private object storage, cấm public bucket)",
    "content_sha256": "string (char(64) NN — SHA-256 checksum bất biến của tệp)",
    "mime_type": "string (NN — verified magic-byte MIME, cấm tin đuôi tệp thô)",
    "size_bytes": "integer (> 0)",
    "actor_id": "uuid (NN)",
    "idempotency_key": "uuid (NN)",
    "correlation_id": "uuid (NN)"
  },
  "RegisterAssetVersionOutput": {
    "asset_id": "uuid",
    "asset_version_id": "uuid",
    "version_no": "integer (>= 1)",
    "scan_status": "PENDING | CLEAN | INFECTED | FAILED",
    "content_sha256": "string (char(64))",
    "active_legal_hold_ids": ["uuid"],
    "gateway_download_ref": "string (định danh Gateway SEC03 — tuyệt đối không trả raw S3 presigned URL)",
    "idempotent_replay": "boolean",
    "correlation_id": "uuid",
    "schema_version": "1.0"
  },
  "DownloadGatewayStep3Input": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN — workspace ngữ cảnh phiên của actor)",
    "target_workspace_id": "uuid | null (workspace sở hữu Asset khi truy cập qua bridge AGENCY <-> CLIENT)",
    "actor_id": "uuid (NN)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "expected_permission_version": "integer (bigint NN — Bước 1 M14 GUARDED_EXECUTION đã PASS)",
    "asset_id": "uuid (NN)",
    "asset_version_id": "uuid (NN)",
    "asset_domain": "string | null (CRM_ATTACHMENT | CALL_RECORDING | EXPORT_BUNDLE | HRM_EMPLOYEE_DOCUMENT | CONTRACT_OR_FINANCE_DOC — khớp Assets.asset_domain; khi EXPORT_BUNDLE bắt buộc export_request_id NN)",
    "owner_resource_type": "string (NN — khớp C20: EXPORT_REQUEST | DELIVERABLE | TASK | CONTRACT | TICKET | EMPLOYEE | CONVERSATION)",
    "owner_resource_id": "uuid (NN)",
    "export_request_id": "uuid | null (bắt buộc non-null khi asset_domain = EXPORT_BUNDLE)",
    "http_method": "GET | HEAD",
    "range_header": "string | null (hỗ trợ HTTP Range/Resume kiểm quyền từng request SEC-U03)",
    "step1_m14_decision": "ALLOW (bắt buộc Bước 1 M14 đã ALLOW)",
    "step2_m20_decision": "ALLOW (bắt buộc Bước 2 M20 đã ALLOW — đã xác minh active_legal_hold_ids[])",
    "requires_watermark": "boolean",
    "correlation_id": "uuid (NN)"
  },
  "DownloadGatewayStep3Output": {
    "decision": "ALLOW_STREAM | DENY",
    "error_code": "null | EXPORT_LINK_EXPIRED | EXPORT_REVOKED_BY_ERASURE | ASSET_CHECKSUM_MISMATCH | PRECEDING_GATE_NOT_ALLOW",
    "response_headers": {
      "Cache-Control": "no-store, no-cache, must-revalidate, private",
      "Content-Security-Policy": "sandbox",
      "X-Content-Type-Options": "nosniff"
    },
    "watermark_applied": "boolean",
    "watermark_stamp": "string | null (actor_id | request_id | downloaded_at_utc)",
    "audit_log_id": "uuid",
    "correlation_id": "uuid",
    "schema_version": "1.0"
  }
}
```

### 2.5. Cổng 6 — `LookupPolicyVersionInput` & `LookupPolicyVersionOutput` (`M23-F09`, `ENTITY-L2885`, `INV-14`)

```json
{
  "LookupPolicyVersionInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid | null",
    "policy_code": "string (NN — ví dụ M14_DELEGATION_LIMITS | M23_BREAK_GLASS_TTL | M16_REVISION_QUOTA | M23_DLP_THRESHOLDS)",
    "domain_module": "string (NN)",
    "as_of_utc": "timestamptz | null (null lấy phiên bản ACTIVE hiện hành; non-null lấy phiên bản hiệu lực tại thời điểm trình hồ sơ cũ)",
    "correlation_id": "uuid (NN)"
  },
  "LookupPolicyVersionOutput": {
    "policy_definition_id": "uuid | null",
    "policy_version_id": "uuid | null",
    "version_no": "integer | null",
    "status": "ACTIVE | POLICY_MISSING_FAIL_CLOSED",
    "owner_role_id": "uuid | null",
    "effective_from": "timestamptz | null (UTC)",
    "config_payload": "object | null (chỉ trả về khi status == ACTIVE)",
    "fail_closed_reason": "string | null",
    "correlation_id": "uuid",
    "schema_version": "1.0"
  }
}
```

---

## 3. Domain Events Phát hành & Tiêu thụ (Qua `Internal_Outbox_Events` — `ADR-005`)

### 3.1. Envelope Chuẩn Mọi Sự kiện `M23` (`contract_version = "1.0"`, tách `envelope_schema_version`)

```json
{
  "event_id": "uuid",
  "event_type": "M23.BreakGlassApproved | M23.BreakGlassRevoked | M23.TenantOperatingModeChanged | M23.FeatureFlagUpdated | M23.ApprovalDecisionRecorded | M23.AssetScanStatusUpdated",
  "aggregate_type": "BREAK_GLASS_REQUEST | TENANT_OPERATING_MODE | FEATURE_FLAG_CONFIG | ASSET | APPROVAL_REQUEST | EXPORT_REQUEST | POLICY_VERSION | SYSTEM_CALENDAR | INTERNAL_OUTBOX",
  "aggregate_id": "uuid",
  "aggregate_version": "integer (bigint >= 1)",
  "schema_version": "1.0 (của Envelope chuẩn M23; khớp envelope_schema_version theo domain nguồn)",
  "contract_version": "1.0",
  "tenant_id": "uuid",
  "workspace_id": "uuid | null",
  "occurred_at": "timestamptz (UTC)",
  "correlation_id": "uuid",
  "causation_id": "uuid | null",
  "payload": {
    "actor_id": "uuid",
    "detail_note": "Object field-map cụ thể theo từng dòng Sự kiện §3.2"
  }
}
```

### 3.2. Danh mục 6 Sự kiện Phát hành (`6 Published Events`)

| Event Name | Payload Trọng yếu | Consumers Bắt buộc | Hành động Phải thực thi phía Consumer |
|---|---|---|---|
| `M23.BreakGlassApproved` | `approval_request_id`, `break_glass_request_id`, `user_id`, `principal_type` (`USER \| SERVICE_PRINCIPAL`), `workspace_id`, `target_workspace_id`, `target_workspace_ids[]`, `branch_id`, `incident_ticket_id`, `scope_resource_types[]`, `specific_resource_ids[]`, `allowed_actions[]`, `hr_payroll_explicitly_approved`, `operating_mode` (`SOLO_PILOT \| TEAM`), `ttl_minutes`, `ttl_expires_at`, `approved_by`, `self_approved_in_pilot_mode`, `reason` | `M14`, `M23-F08`, `M24-F05` | `M14` thực thi `ApplyBreakGlassGrant` (**fan-out 1 bản ghi/workspace** cho toàn bộ `target_workspace_ids[]` kèm `principal_type`, `branch_id`, `specific_resource_ids`, `hr_payroll_explicitly_approved`, `operating_mode`) ghi bảng runtime `M14.Break_Glass_Grants` (`Nhóm A`) + bump `Principal_Permission_Versions`; `M23-F08` theo dõi sử dụng trong TTL; nếu `self_approved_in_pilot_mode = true` thì `M24-F05` bắn cảnh báo tức thì về `Owner/CEO` (`INV-22`) |
| `M23.BreakGlassRevoked` | `break_glass_request_id`, `user_id`, `workspace_id` (`uuid \| null` — `NULL` để thu hồi đồng loạt mọi dòng fan-out theo `break_glass_request_id`), `revoked_by`, `revoke_reason` (`MANUAL \| TTL_EXPIRED \| OFFBOARD \| SECURITY_INCIDENT`), `revoked_at` | `M14`, `M23-F02`, `M24-F06` | `M14` gọi `RevokeBreakGlassGrant` khóa grant runtime & bump `permission_version`; `M23-F02` hủy session Break-glass tương ứng; `Download Gateway SEC03` chặn ngay `GET/Range` tiếp theo (`U16`) |
| `M23.TenantOperatingModeChanged` | `tenant_id`, `approval_request_id`, `previous_mode` (`SOLO_PILOT \| TEAM`), `new_mode` (`SOLO_PILOT \| TEAM`), `maker_id`, `approver_id`, `approver_count`, `reason`, `effective_at` | `M14`, `M23-F04/F07/F08`, `M24-F06`, `M24-F05` | `M14` gọi `SetTenantOperatingMode` cập nhật `Tenants.operating_mode` (`ADR-003`) & bump `permission_version`; `M23-F04/07` tự động khóa `Maker == Checker` khi chuyển sang `TEAM`; hạ `TEAM -> SOLO_PILOT` bắt buộc `Maker != Checker` (`>= 2` người duyệt độc lập gồm `Owner/CEO`), `M23-F08` + `M24-F05` bắn cảnh báo khẩn cấp tức thì tới `Owner/CEO` |
| `M23.FeatureFlagUpdated` | `flag_key`, `scope_type` (`TENANT \| WORKSPACE`), `scope_id`, `state` (`OFF \| SHADOW \| PILOT \| ON`), `previous_state`, `dependencies_verified[]`, `updated_by`, `reason`, `effective_at` | `M01–M24` (đặc biệt `M14`, `M16`, `M19`, `M20`, `M21`, `M22`, `M24`) | Áp dụng `Feature Flag Closure` (`RV20`): đóng/mở đồng thời cả UI lẫn Backend API & Worker (`404/422 CAPABILITY_DISABLED` khi `OFF`) theo đúng phạm vi `(scope_type, scope_id)` |
| `M23.ApprovalDecisionRecorded` *(bổ trợ)* | `approval_request_id`, `approval_decision_id`, `domain_module`, `action_type`, `target_resource_type`, `target_resource_id`, `request_status`, `decided_by`, `decided_at` | Domain nguồn (`M07`, `M08`, `M10`, `M15`, `M16`, `M17`, `M22`, `M23-F07`) | Domain nguồn mở khóa chuyển trạng thái nghiệp vụ tương ứng (ví dụ `M16.Project_Change_Requests`, `M23.Export_Requests`) sau khi kiểm tra CAS `row_version` |
| `M23.AssetScanStatusUpdated` *(bổ trợ)* | `asset_id`, `asset_version_id`, `scan_status` (`CLEAN \| INFECTED \| FAILED`), `content_sha256`, `scanned_at` | `M16`, `M03`, `M07`, `M08`, `M19`, `M20`, `M22` | Mở điều kiện đính kèm/publish khi `CLEAN` (`M16-F03`); cách ly & chặn tải qua `SEC03` khi `INFECTED/FAILED` (`INT24`) |

### 3.3. Danh mục Sự kiện Liên Module mà `M23` Bắt buộc Tiêu thụ (`Subscribed Events`)

| Nguồn & Event | Ý nghĩa & Hành vi Xử lý Idempotent Tại `M23` |
|---|---|
| **`M14.UserOffboardingLocked`** (`C14`) | (1) `M23-F02` **chỉ thu hồi ngay toàn bộ active sessions & xóa PWA offline cache (`client_operation_id`) khi `case_type = 'OFFBOARD'`** (`BRANCH_TRANSFER`/`ROLE_CHANGE` giữ tài khoản `ACTIVE`); (2) `M23-F03`, `M23-F04`, `M23-F07` chuyển toàn bộ phiếu `Break_Glass_Requests`, `Approval_Requests`, `Export_Requests` đang ở trạng thái **`PENDING_APPROVAL`** gắn `user_id` sang `default_custodian_id` (tuyệt đối không auto-approve); thu hồi quyền tải `Export_Requests` nếu `user_id` là người yêu cầu bị `OFFBOARD`. |
| **`M14.WorkHandoverAssigned`** (`C14`) | `M23-F03`, `M23-F04`, `M23-F07` cập nhật `current_approver_id` trên các phiếu `PENDING_APPROVAL` sang `to_recipient_id` khi `handover_status = 'CONFIRMED'` (giữ nguyên `requested_by` & lịch sử `Approval_Decisions`). |
| **`M14.PermissionVersionBumped`** (`C14`) | `M23-F02` **chỉ thu hồi session & ép xóa PWA offline cache khi `reason IN ('OFFBOARD', 'SUSPEND', 'SECURITY_INCIDENT', 'DR_ACL_EPOCH_JUMP')`** (hoặc thu hồi session Break-glass khi `reason = 'BREAK_GLASS_EXPIRED'`); các lần cấp thêm quyền hoặc đổi grant thường không làm đăng xuất ngang phiên UI đang làm việc. |
| **`M20.SubjectErasureExecuted`** (`C20` — `erased_subject_refs[]`, `endpoint_hmac_hashes_by_version[]`) | `M23-F07` thu hồi lập tức mọi `Export_Requests` còn mở liên quan đến `erased_subject_refs[]` / `subject_hmac_sha256` (`REVOKED_BY_ERASURE`, hết hạn link Gateway); xóa/ẩn danh các `Assets` không có `active_legal_hold_ids` (`erased_at = now()`, xóa object vật lý); **`M23-F12` scrub sạch PII trong `Internal_Outbox_Events` & `Internal_Dead_Letter_Queue`** khớp `erased_subject_refs[]` / `endpoint_hmac_hashes_by_version[]`. |
| **`M20.LegalHoldChanged`** (`C20` — `ACTIVE \| RELEASED`) | Cập nhật mảng **`Assets.active_legal_hold_ids uuid[]`** (`array_append` / `array_remove` nguyên tử theo `legal_hold_id`, hỗ trợ Multi-`Legal_Hold`) và khóa giữ chống xóa `Audit_Logs` liên quan. |
| **`M20.DataIncidentEscalated`** (`C20`) | `M23-F02` thu hồi toàn bộ phiên của `affected_actor_ids[]`; `M23-F08` tạo `Security_Anomaly_Alerts` mức `CRITICAL` và gắn `Audit_Logs` tương ứng. |
| **`M19.ConnectionHealthChanged`** (`C19`) | `M23-F08` / `M23-F12` ghi nhận sự cố kết nối/token hết hạn lên bảng điều khiển sức khỏe và cảnh báo DLP nếu nghi lộ credential. |
| **`M16.ProjectChangeRequestRaised`** (`C16`) | `M23-F04` tự động khởi tạo `Approval_Requests` theo `Approval_Matrix_Rules` đối với thay đổi vượt `committed_due_at` hoặc có `cost_delta <> 0` (`GAP-M16-06`). |

---

## 4. Compatibility, Privacy & Test Matrix (`MODULE-SPEC` Aligned)

| Mã Test | Mục tiêu Kiểm chứng Hợp đồng `C23` | Severity | Applicability | Status | Actual / Build / Fixture |
|---|---|---|---|---|---|
| `S-T01` / `SEC-U06` | `RecordApprovalDecision` chặn `Maker == Checker` tại `TEAM`; `SOLO_PILOT` gắn cờ + cảnh báo Owner; `Approval_Decisions` bất biến (`Nhóm C`) | `P0 Blocker` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M23-APPR-01` |
| `S-T02` | `M14.UserOffboardingLocked` (`OFFBOARD`) & `PermissionVersionBumped` (`OFFBOARD/SUSPEND/SECURITY_INCIDENT`) cắt session + xóa PWA cache; `BRANCH_TRANSFER` giữ session `ACTIVE` và chuyển `PENDING_APPROVAL` sang Custodian | `P0 Blocker` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M23-SESS-02` |
| `S-T03` / `U16` / `SEC-U03` | `RegisterAssetAndDownloadGateway` Bước 3 từ chối `INFECTED`, `EXPORT_LINK_EXPIRED`, `EXPORT_REVOKED_BY_ERASURE`, `active_legal_hold_ids <> '{}'`; chặn `HTTP Range/Resume` sau revoke | `P0 Blocker` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M23-GW-03` |
| `S-T04` / `U03` / `CR05` | `ComputeBusinessCalendarShift`: Lead lúc `18:00` thứ Sáu ngoài ca tính sang đầu ca kế tiếp sau nghỉ lễ theo `System_Calendars`; `Quiet Hours` chặn thông báo ngoài giờ | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M23-CAL-04` |
| `S-T05` / `U21` / `INT26` | `M23-F12` thực thi đủ **5 bước DR Startup Fence đã đảo** (`Lock 3 lanes + M16 schedulers -> Bước 2: M14 PITR #6 + leapfrog acl_epoch + wipe sessions/cache + re-lock incident + time-only expiry -> Bước 3: M20.VerifyPostRestoreComplianceGate kiểm 6 bảng PITR/WAL độc lập & hủy intent/outbox/notification vi phạm compliance -> Bước 4: Replay M23-F12 -> Bước 5: Reconcile + Backup_Drill_Logs`) | `P0 Blocker` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M23-DR-05` |
| `S-T06` / `OC03` | `M20.SubjectErasureExecuted` (`erased_subject_refs[]`) thu hồi `Export_Requests`, xóa `Assets` không Hold, giữ `Assets` có `active_legal_hold_ids`, và scrub PII trên `Internal_Outbox_Events` / `DLQ` | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M23-ERS-06` |
| `S-T07` / `INV-14` / `RV20` | `LookupPolicyVersion` fail-closed khi `DRAFT`/thiếu `owner_role_id`; `FeatureFlagUpdated` kiểm dependency closure & đóng cả UI/API/Worker | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M23-FLG-07` |
| `S-T08` / `NFR11` / `NFR12` | `Audit_Logs` redact-before-insert & chặn Tech Admin xóa/sửa; Portability export `NFR12` xuất kèm dictionary + clean assets + external IDs | `P1 Major` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-M23-AUD-08` |
