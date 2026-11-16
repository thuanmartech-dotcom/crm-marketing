# Contract `M14-PRINCIPAL-ACCESS-DECISION` — Cổng Quyết định Quyền Thực thi (`RBAC + ABAC + Legal Hold + Break-Glass`)

- **Contract ID:** `CONTRACT-M14-ACCESS-DECISION-v1.1`
- **Provider Owner:** `M14` (Tổ chức, Thành viên, Quyền & Bàn giao)
- **Consumers:** Toàn bộ domain `M01–M24`, `Download Gateway` (`SEC03`), `Worker Jobs` (`M19`, `M24-F08`), `BI/Search` (`M18`, `M24-F06`), `AI Retrieval` (`M06`, `M20-F07`)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`5.1`, `5.14`, `6.1`, `6.2`, `SEC03`, `SEC06`, `U16`, `U17`, `CEO-U10`, `CEO-U17`, `CEO-U18`, `CX-U01`, `INT23`, `INT29`, `RV10`, `RV15`, `OC20`), [ADR-002](../../01-architecture/decisions/ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-003](../../01-architecture/decisions/ADR-003-PERMISSION-VERSION-CACHE-AND-MODE-GOVERNANCE.md), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](../../01-architecture/decisions/ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-008](../../01-architecture/decisions/ADR-008-OMNICHANNEL-CONTRACTS-RECEIPTS-AND-CROSS-EVENTS.md)
- **Trạng thái:** `Reviewed (CR-20261116-WAVE1-RECONCILIATION Applied)`
- **Chính sách Breaking Change:** Additive-only cho trường mới không bắt buộc; đổi cấu trúc `Output` hoặc mở rộng tập `resource_type`/`action` bắt buộc cập nhật đồng thời `ADR-002`/`ADR-008` và Consumer liên quan (`INDEX.md`).

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | `M14` là **cổng kiểm tra quyền thực thi duy nhất (`INV-23`)** gồm 3 hàm lõi: (1) `EvaluateAccessDecision` cho lệnh ghi/tải file/AI/worker, (2) `CompileScopeFilter` sinh bộ lọc SQL/RLS an toàn cho danh sách/đếm/tìm kiếm/RAG, và (3) `BindDbTransactionContext` gắn ngữ cảnh 5 biến GUC `SET LOCAL` trên PostgreSQL connection pool. Mọi phán quyết tuân thủ tuyệt đối: `Tenant & Workspace Isolation` $\rightarrow$ `Legal Hold` $\rightarrow$ `Role/Entity DENY > ALLOW` (`Deny-Wins`). |
| **Actor/scope** | `principal_id` thuộc 1 trong 3 loại `USER | SERVICE_PRINCIPAL | PORTAL_CLIENT` được xác thực trong `tenant_id` & `workspace_id` đích (suy xuất từ auth session/token, **không nhận `tenant_id` trần từ payload client**). Hỗ trợ `DIRECT`, `DELEGATED`, `BREAK_GLASS` (cấp qua `M23-F03` và ghi runtime tại `M14`), `SYSTEM_WORKER`. |
| **Preconditions** | Principal hợp lệ (`USER.status = 'ACTIVE'`, `SERVICE_PRINCIPAL.key_status = 'ACTIVE'`, `PORTAL_CLIENT.portal_grant_status = 'ACTIVE'`); `Memberships.status = 'ACTIVE'` trong `workspace_id`; `tenant_id` và `workspace_id` tồn tại hợp lệ. Nếu `expected_permission_version` được truyền ở chế độ **Guarded Execution** (`ADR-003`), bắt buộc khớp `M14.Principal_Permission_Versions.permission_version` trên Primary DB. |
| **Input** | Xem 3 JSON Schema tại Mục 2: `BindDbTransactionContextInput`, `EvaluateAccessDecisionInput` (bổ sung đủ `resource_type` cho `M14–M24` & Core, đầy đủ `action` cho `M19`/Privacy/Policy/Audit), và `CompileScopeFilterInput` (có `branch_id`, `legal_entity_id`, `principal_type`, `channel`, `include_legal_hold_records`). |
| **Output** | Xem 3 JSON Schema tại Mục 2: `BindDbTransactionContextOutput`, `AccessDecisionOutput` (`decision`, `http_status_recommendation`, `internal_reason_code`, `effective_permission_version`, `acting_mode`, `field_policy: {allowed_fields, masked_fields, forbidden_fields}`, `audit_context`), và `CompiledScopeFilterOutput` (`predicate_ast`, `bind_params`, `effective_permission_version`, `enforced_visibility_guard`, `enforced_legal_hold_guard`, `correlation_id`). Không trả raw DB row. |
| **Errors** | Chuẩn Error Envelope: `{code, message, field_errors, correlation_id}`. Mã lỗi chính: `401 AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED`; `403 AUTH_RBAC_FORBIDDEN`, `403 AUTH_DENY_POLICY_ACTIVE`, `403 AUTH_PERSONAL_SCOPE_DENIED` (khi đọc bản ghi `PERSONAL` cùng workspace nhưng trái owner/grant), `403 AUTH_LEGAL_ENTITY_MISMATCH`, `403 AUTH_LEGAL_HOLD_RESTRICTED`; `409 AUTH_PERMISSION_VERSION_STALE` (`GUARDED_EXECUTION` Worker/Bulk/`EXPORT`); `404 RESOURCE_NOT_FOUND_OR_DENIED` (**Chính sách Non-Disclosure `U17`/`CX-U01`:** `AUTH_CROSS_WORKSPACE_BLOCKED` là mã lý do ghi `audit_context.internal_reason_code`, còn HTTP trả ra ngoài cho mọi truy vấn ID/search/count khác `workspace_id` không có bridge hợp lệ **bắt buộc là `404 RESOURCE_NOT_FOUND_OR_DENIED`**, không lộ sự tồn tại, tên workspace sở hữu hay `count`). |
| **Concurrency** | Áp dụng 2 chế độ theo `ADR-003`: (A) **Interactive UI Read** (`expected_permission_version = null` hoặc dùng làm `cache_hint`): lệch version thì vô hiệu hóa cache `M24-F06` và nạp đánh giá lại từ **Primary DB**; (B) **Guarded Async / Bulk / Export / Download Gateway** (`execution_mode = 'GUARDED_EXECUTION'` + `expected_permission_version != null` trên cả `EvaluateAccessDecision` lẫn `CompileScopeFilter(action='EXPORT')`): lệch DB version hoặc principal chuyển sang `SUSPENDED/OFFBOARDING_LOCKED/OFFBOARDED` $\rightarrow$ **Fail-Closed tức thì** (`409 AUTH_PERMISSION_VERSION_STALE` cho Worker/Bulk/Export; `401/403` cho Download Gateway). |
| **Idempotency** | Cả 3 hàm đều **thuần đọc / context-binding (side-effect free)** ngoại trừ ghi `Audit_Logs` cảnh báo an ninh khi phát hiện `AUTH_CROSS_WORKSPACE_BLOCKED` hoặc tự nâng quyền (`M23-F08`). Gọi lặp lại không làm thay đổi trạng thái nghiệp vụ. |
| **Transaction** | Mọi DB query/command trên PostgreSQL pool bắt buộc chạy `BindDbTransactionContext` trong transaction (`SET LOCAL app.current_tenant_id`, `app.current_workspace_id`, `app.current_principal_id`, `app.current_permission_version`, `app.current_acting_mode`) dưới `app_runtime_role` không `BYPASSRLS` (`INV-13`, `RV15`). Thiếu GUC $\rightarrow$ RLS trả 0 dòng / raise exception fail-closed. |
| **Compatibility** | Mở rộng enum `resource_type` / `action` theo hướng tương thích tiến: adapter/domain mới phải khai báo rõ `resource_type` vào bảng `Roles.permissions_matrix` trước khi bật Feature Flag (`INV-14`, `M23-F09`). Sự kiện phát ra mang `schema_version = "1.1"`. |
| **Audit/privacy** | Mọi quyết định `DENY` nhạy cảm hoặc sử dụng `BREAK_GLASS` / `DELEGATED` ghi `Audit_Logs` (`M23-F06`) kèm `correlation_id`, `actor_id`, `delegated_from_id`, `break_glass_grant_id`, `internal_reason_code` — đã redact PII (`NFR11`). |
| **Tests** | `M14-AC01`, `M14-AC02`, `U16`, `U17`, `SEC-U03`, `SEC-U06`, `INT23`, `INT29`, `RV10`, `RV15`, `CEO-U10`, `CEO-U17`, `CEO-U18`, `CX-U01`, `OC20`, `H-T04`, `P-T02..06`, `P-T30..31`, `P-T35..36`. Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas & Quy tắc Đánh giá Chuẩn (`ADR-002`, `ADR-003`, `ADR-008`)

### 2.1. `BindDbTransactionContextInput` & `BindDbTransactionContextOutput`

```json
{
  "BindDbTransactionContextInput": {
    "tenant_id": "uuid (NN — lấy từ verified session/job context)",
    "workspace_id": "uuid | null (NULL chỉ hợp lệ cho tenant-catalog transaction được khai báo)",
    "principal_id": "uuid (NN)",
    "permission_version": "integer (bigint > 0, đọc từ Primary DB nếu Guarded)",
    "acting_mode": "DIRECT | DELEGATED | BREAK_GLASS | SYSTEM_WORKER",
    "correlation_id": "uuid (NN)"
  },
  "BindDbTransactionContextOutput": {
    "bound_gucs": {
      "app.current_tenant_id": "string (uuid)",
      "app.current_workspace_id": "string (uuid hoặc rỗng)",
      "app.current_principal_id": "string (uuid)",
      "app.current_permission_version": "string (bigint)",
      "app.current_acting_mode": "DIRECT | DELEGATED | BREAK_GLASS | SYSTEM_WORKER"
    },
    "transaction_isolated": true
  }
}
```

### 2.2. `EvaluateAccessDecisionInput` & `AccessDecisionOutput`

```json
{
  "EvaluateAccessDecisionInput": {
    "principal_id": "uuid (NN)",
    "principal_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "execution_mode": "INTERACTIVE_READ | GUARDED_EXECUTION",
    "expected_permission_version": "integer | null (bắt buộc non-null khi execution_mode = GUARDED_EXECUTION)",
    "resource_type": "TENANT | BRANCH | LEGAL_ENTITY | BUSINESS_LINE | BRAND | BUSINESS_UNIT | WORKSPACE | WORKSPACE_ACCOUNT_LINK | CONTRACT_WORKSPACE_GRANT | DEPARTMENT | USER | TEAM | MEMBERSHIP | ROLE | ROLE_BINDING | ENTITY_TEAM_GRANT | BREAK_GLASS_GRANT | DELEGATION | OFFBOARDING_CASE | CAPACITY_COST_SNAPSHOT | SCORECARD_REVIEW | POLICY_DEFINITION | AUDIT_LOG | EXPORT_REQUEST | CONTACT | ACCOUNT | LEAD | DEAL | CONVERSATION | MESSAGE | ATTACHMENT | ASSET | QUOTE | ORDER | CONTRACT | INVOICE_LINE | PAYMENT | COMMISSION | TICKET | PROJECT | DELIVERABLE | TASK | STRATEGY_BRIEF | IMC_PLAN | JOURNEY | CAMPAIGN | BUDGET | REPORT | REFERRAL | LOYALTY_LEDGER | APPOINTMENT | RESOURCE | FEEDBACK | RECOVERY_CASE | CHANNEL_CONNECTION | CONNECTION_CAPABILITY | OUTBOUND_INTENT | INBOUND_EVENT | QUARANTINED_EVENT | SYNC_RUN | ADAPTER_DLQ | REPLAY_JOB | PROCESSING_RECORD | CONSENT_LOG | CONSENT_STATE | ENDPOINT_SUPPRESSION | PRIVACY_REQUEST | LEGAL_HOLD | LEGAL_DEADLINE_POLICY | RETENTION_POLICY | DELETION_LEDGER | PLACEHOLDER_VAULT | DATA_INCIDENT | VENDOR_DATA_FLOW | PARTNER_DATA_PROFILE | PARTNER_DATASET | PARTNER_REPORT | EMPLOYEE | EMPLOYMENT_CONTRACT | ATTENDANCE | LEAVE_REQUEST | PAYROLL",
    "resource_id": "uuid | null (null khi action = CREATE hoặc list-level check)",
    "action": "CREATE | READ | COMMENT | UPDATE | ARCHIVE | DELETE_PRIVACY | APPROVE | EXPORT | IMPORT | SHARE_GRANT | DELEGATE | DOWNLOAD_FILE | AI_RETRIEVE | CONNECT | VERIFY_CAPABILITY | ACTIVATE | DISPATCH | PAUSE | RESUME | DISCONNECT | TRANSFER | RECONCILE | SYNC | REPLAY | VIEW_QUARANTINE_PAYLOAD | MANAGE_POLICY | VIEW_AUDIT",
    "requested_fields": ["string"],
    "context_flags": {
      "target_workspace_id": "uuid | null",
      "target_branch_id": "uuid | null",
      "target_legal_entity_id": "uuid | null",
      "target_owner_id": "uuid | null",
      "target_account_id": "uuid | null",
      "target_visibility_scope": "PERSONAL | TEAM | WORKSPACE | null",
      "target_legal_hold_status": "NONE | RESTRICTED_LEGAL_HOLD | null",
      "delivery_channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK | null",
      "is_download_range_request": "boolean (default false)",
      "break_glass_grant_id": "uuid | null",
      "delegation_id": "uuid | null"
    },
    "correlation_id": "uuid (NN)"
  }
}
```

**Thứ tự đánh giá 7 bước tất định (`Fail-Closed` & `Deny-Wins`):**
1. **Bước 1 — Kiểm trạng thái Principal theo `principal_type`:**
   - `USER`: bắt buộc `Users.status == 'ACTIVE'` và `Memberships.status == 'ACTIVE'` (trạng thái `OFFBOARDING_LOCKED`, `SUSPENDED`, `OFFBOARDED`, `INVITED`, `CANCELLED` $\rightarrow$ `DENY / 401`).
   - `SERVICE_PRINCIPAL`: bắt buộc service identity active, API key/certificate chưa thu hồi, đúng `tenant_id` & phạm vi `workspace_id`.
   - `PORTAL_CLIENT`: bắt buộc `PORTAL` role chỉ nằm trong `CLIENT workspace` được cấp, không trỏ ngược `AGENCY` (`CEO-U17`).
2. **Bước 2 — Kiểm `expected_permission_version` (`ADR-003`):**
   - Đọc `db_version` từ `M14.Principal_Permission_Versions` (nếu `execution_mode = GUARDED_EXECUTION` hoặc phát hiện cache `M24-F06` cũ hơn DB).
   - Nếu `execution_mode = GUARDED_EXECUTION`: `expected_permission_version != db_version` $\rightarrow$ **`DENY` ngay**: trả `409 AUTH_PERMISSION_VERSION_STALE` (với Worker/Bulk/Export) hoặc `401/403` (với `Download Gateway GET/Range`).
   - Nếu `execution_mode = INTERACTIVE_READ`: xóa cache cũ của principal, nạp toàn bộ Role/Grant/Delegation/Break-Glass/Legal-Hold mới nhất từ Primary DB để đánh giá tiếp.
3. **Bước 3 — Kiểm Cô lập `Workspace`, `Bridge` & `Legal Entity`:**
   - Nếu `target_workspace_id != workspace_id`: bắt buộc có `Workspace_Account_Links` hoặc `Contract_Workspace_Grants` còn hiệu lực (`revoked_at IS NULL AND now() BETWEEN valid_from AND coalesce(valid_until, 'infinity')`) khớp đúng cặp `resource_type` + `allowed_relations`; ngược lại $\rightarrow$ `DENY (404 RESOURCE_NOT_FOUND_OR_DENIED)` + phát cảnh báo `M23-F08`.
   - Nếu `resource_type IN ('CONTRACT', 'ORDER', 'INVOICE_LINE', 'PAYMENT', 'COMMISSION', 'PAYROLL')` hoặc tenant bật `O08 = true`: kiểm khớp `target_legal_entity_id` nằm trong phạm vi pháp nhân được cấp của principal (`CEO-U10`), trái phép $\rightarrow$ `DENY (403 AUTH_LEGAL_ENTITY_MISMATCH)`.
4. **Bước 4 — Bảo vệ `PERSONAL` & `RESTRICTED_LEGAL_HOLD` (`ADR-002`, `ADR-007`):**
   - Nếu `target_visibility_scope = 'PERSONAL'`: chặn hoàn toàn vai trò cấp trên/chi nhánh (`W-O04`, `INV-02`); chỉ tiếp tục nếu `principal_id == target_owner_id` hoặc có `Entity_Team_Grants (ALLOW)` chính danh còn hạn.
   - Nếu `target_legal_hold_status = 'RESTRICTED_LEGAL_HOLD'` (từ `M20.LegalHoldChanged`): chặn ngay mọi vai trò tác nghiệp thường (`SALES`, `MARKETING`, `AM_CSKH`, `DELIVERY`), kể cả `UPDATE`/`DELETE_PRIVACY`/`EXPORT` thường; **chỉ cho phép `READ`/`VIEW_AUDIT` đối với vai trò có thẩm quyền `LEGAL_HOLD_READ` (`FINANCE`, `PRIVACY`, `LEGAL_AUDITOR`)**.
5. **Bước 5 — Kiểm `DENY` Tường minh (`Deny-Wins`, `INT29`):**
   - Kiểm tra cả **Role-level `Role_Bindings (effect = 'DENY')`** trong `(workspace_id, branch_id, legal_entity_id, resource_type)` **VÀ Entity-level `Entity_Team_Grants (effect = 'DENY')`** trên `resource_id` / `target_account_id`. Nếu có bất kỳ `DENY` nào khớp `action` (hoặc wildcard `*`) $\rightarrow$ `DENY (403 AUTH_DENY_POLICY_ACTIVE)` ngay lập tức; `ALLOW` hoặc `Break-Glass` thông thường không tự đè `Entity/Legal DENY`.
6. **Bước 6 — Tổng hợp Nguồn `ALLOW` (`RBAC + ABAC` cùng thỏa):**
   - Phải thỏa quyền thực thi `action` từ `Roles.permissions_matrix` (theo `DIRECT` Role, hoặc `DELEGATED` qua `Delegations` `ACTIVE` đúng `scope_resource_types`/`allowed_actions`, hoặc `BREAK_GLASS` qua `M14.Break_Glass_Grants` `ACTIVE` còn TTL có `incident_ticket_id`).
   - Đồng thời thỏa phạm vi dữ liệu `ABAC`: `data_scope = WORKSPACE`, hoặc `data_scope = BRANCH` (khớp `branch_id`, trừ dữ liệu `PERSONAL/RESTRICTED`), hoặc `owner_id == principal_id`, hoặc `Delegation`, hoặc `Entity_Team_Grants (ALLOW)` (kể cả theo `target_account_id` với `CX-U01`), hoặc `Break_Glass_Grants (ALLOW)`. Thiếu 1 trong 2 lớp $\rightarrow$ `DENY (403 AUTH_RBAC_FORBIDDEN)`.
7. **Bước 7 — Tính `field_policy` (`M01–M24`, `M22` Lương/CCCD, `M20` PII):**
   - Giao cắt các trường cho phép; mọi trường nhạy cảm bị khóa ở vai trò thấp hơn (`M22` lương/CCCD, `standard_cost_rate` đối với non-finance, `TECH_ADMIN` bị cấm đọc dữ liệu kinh doanh/lương) được đẩy vào `masked_fields` hoặc `forbidden_fields` (`forbidden` luôn thắng `masked`, `masked` thắng `allowed`).

```json
{
  "AccessDecisionOutput": {
    "decision": "ALLOW | DENY",
    "http_status_recommendation": 200,
    "internal_reason_code": "ALLOW_DIRECT_ROLE | ALLOW_ENTITY_GRANT | ALLOW_DELEGATED | ALLOW_BREAK_GLASS | AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED | AUTH_PERMISSION_VERSION_STALE | AUTH_CROSS_WORKSPACE_BLOCKED | AUTH_LEGAL_ENTITY_MISMATCH | AUTH_PERSONAL_SCOPE_DENIED | AUTH_LEGAL_HOLD_RESTRICTED | AUTH_DENY_POLICY_ACTIVE | AUTH_RBAC_FORBIDDEN",
    "effective_permission_version": 42,
    "acting_mode": "DIRECT | DELEGATED | BREAK_GLASS | SYSTEM_WORKER",
    "field_policy": {
      "allowed_fields": ["id", "name", "stage"],
      "masked_fields": ["phone_masked", "email_masked"],
      "forbidden_fields": ["bank_account_no", "salary_base", "standard_cost_rate"]
    },
    "audit_context": {
      "delegated_from_id": "uuid | null",
      "break_glass_grant_id": "uuid | null",
      "matched_policy_source": "string"
    }
  }
}
```

### 2.3. `CompileScopeFilterInput` & `CompiledScopeFilterOutput` (`ADR-002`)

```json
{
  "CompileScopeFilterInput": {
    "principal_id": "uuid (NN)",
    "principal_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "execution_mode": "INTERACTIVE_READ | GUARDED_EXECUTION",
    "expected_permission_version": "integer | null (bắt buộc non-null khi execution_mode = GUARDED_EXECUTION hoặc action = EXPORT theo ADR-003)",
    "branch_id": "uuid | null",
    "legal_entity_id": "uuid | null",
    "resource_type": "enum (như EvaluateAccessDecisionInput)",
    "action": "READ | EXPORT | AI_RETRIEVE",
    "delivery_channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK | null",
    "include_legal_hold_records": "boolean (default true; tự động chặn ở AST nếu principal không có legal_hold_read_role)",
    "correlation_id": "uuid (NN)"
  },
  "CompiledScopeFilterOutput": {
    "effective_permission_version": 42,
    "has_any_access": true,
    "scope_mode": "NONE | OWN_AND_GRANTS_ONLY | BRANCH_SCOPED_BY_ROLE | ALL_WORKSPACE_BY_ROLE",
    "enforced_visibility_guard": true,
    "enforced_legal_hold_guard": true,
    "predicate_ast": "string (SQL-safe parameterized AST chuẩn hóa 6 tầng)",
    "bind_params": {
      "tenant_id": "uuid",
      "workspace_id": "uuid",
      "principal_id": "uuid",
      "resource_type": "string (enum từ Input, dùng để khớp verified_bridge_keys)",
      "scope_mode": "NONE | OWN_AND_GRANTS_ONLY | BRANCH_SCOPED_BY_ROLE | ALL_WORKSPACE_BY_ROLE",
      "verified_bridge_keys": ["string"],
      "enforced_legal_entity_ids": "uuid[] | null (NULL khi không giới hạn pháp nhân; cấm truyền [] khi NULL)",
      "allowed_branch_ids": ["uuid"],
      "active_delegator_ids": ["uuid"],
      "granted_account_ids": ["uuid"],
      "explicit_allow_entity_ids": ["uuid"],
      "active_break_glass_ids": ["uuid"],
      "explicit_personal_share_ids": ["uuid"],
      "has_matching_role_deny_in_scope": false,
      "explicit_deny_entity_ids": ["uuid"],
      "explicit_deny_account_ids": ["uuid"],
      "include_legal_hold_records": true,
      "has_legal_hold_read_role": false
    },
    "correlation_id": "uuid"
  }
}
```

**Biểu thức `predicate_ast` chuẩn hóa 6 tầng hội (`AND` — tuyệt đối bỏ `OR branch_id` vô điều kiện):**

```sql
(tenant_id = :tenant_id)
AND (
  workspace_id = :workspace_id
  OR (CONCAT(:resource_type, ':', id::text) = ANY(:verified_bridge_keys))
)
AND (:enforced_legal_entity_ids IS NULL OR legal_entity_id = ANY(:enforced_legal_entity_ids))
AND (
  visibility_scope <> 'PERSONAL'
  OR owner_id = :principal_id
  OR id = ANY(:explicit_personal_share_ids)
)
AND (
  :scope_mode = 'ALL_WORKSPACE_BY_ROLE'
  OR (:scope_mode = 'BRANCH_SCOPED_BY_ROLE' AND branch_id = ANY(:allowed_branch_ids) AND sensitivity_level <> 'RESTRICTED')
  OR owner_id = :principal_id
  OR owner_id = ANY(:active_delegator_ids)
  OR account_id = ANY(:granted_account_ids)
  OR id = ANY(:explicit_allow_entity_ids)
  OR id = ANY(:active_break_glass_ids)
)
AND NOT (:has_matching_role_deny_in_scope)
AND (id <> ALL(:explicit_deny_entity_ids))
AND (account_id IS NULL OR account_id <> ALL(:explicit_deny_account_ids))
AND (legal_hold_status <> 'RESTRICTED_LEGAL_HOLD' OR (:include_legal_hold_records = true AND :has_legal_hold_read_role = true))
```

---

## 3. Domain Events Phát hành & Tiêu thụ (Qua Internal Outbox `M23-F12` — `ADR-005`)

### 3.1. Envelope Chuẩn Mọi Sự kiện `M14` (`schema_version = "1.1"`)

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "aggregate_type": "string",
  "aggregate_id": "uuid",
  "aggregate_version": "integer (bigint)",
  "schema_version": "1.1",
  "tenant_id": "uuid",
  "workspace_id": "uuid | null",
  "occurred_at": "timestamptz (UTC)",
  "correlation_id": "uuid",
  "causation_id": "uuid | null",
  "payload": {}
}
```

### 3.2. Danh mục Sự kiện Phát hành (`Published Events`)

| Event Name | Aggregate & Payload Trọng yếu | Consumers Bắt buộc | Hành động Phải thực thi phía Consumer |
|---|---|---|---|
| `M14.PermissionVersionBumped` | `principal_id`, `new_permission_version`, `reason` (`ROLE_CHANGED \| GRANT_REVOKED \| BREAK_GLASS_EXPIRED \| LEGAL_HOLD \| OFFBOARD`), `revoked_grant_ids[]` | `M24-F06`, `Download Gateway (SEC03)`, `M19`, `M23-F02` | `M24-F06` xóa/làm mới ngay Read-Model Cache (`INV-25`); `M23-F02` thu hồi token/session khi suspend/offboard; `Download Gateway` & `M19` check version mới nhất |
| `M14.UserOffboardingLocked` | `user_id`, `offboarding_case_id`, `case_type` (`OFFBOARD \| BRANCH_TRANSFER \| ROLE_CHANGE`), `from_branch_id`, `to_branch_id`, `default_custodian_id`, `effective_at`, `open_items_count` | `M23-F02`, `M02`, `M03`, `M07`, `M08`, `M11`, `M12`, `M13`, `M15`, `M16`, `M17`, `M19`, `M22` | Ngắt session tức thì; đóng băng quyền tại chi nhánh/role cũ; tạm chuyển mọi open work / scheduled intent / pending approval sang `default_custodian_id` (`UC12`, `OC18`) |
| `M14.WorkHandoverAssigned` | `offboarding_case_id`, `item_category`, `item_id`, `from_user_id`, `to_recipient_id`, `handover_status` (`PENDING_ACCEPT \| CONFIRMED \| CANCELLED_BY_MANAGER`) | `M02`, `M03`, `M07`, `M08`, `M11`, `M12`, `M13`, `M15`, `M16`, `M17`, `M19`, `M22`, `M23` | Cập nhật `owner_id` / `approver_id` cho công việc mới sau khi `CONFIRMED`; giữ nguyên `actor` & người hưởng hoa hồng lịch sử (`INT15`) |
| `M14.WorkspaceActivated` | `workspace_id`, `workspace_type` (`AGENCY \| CLIENT`), `client_account_id`, `processing_scope`, `default_legal_entity_id` | `M20`, `M19`, `M21` | `M20` xác nhận `Processing_Records` + DPA trước khi mở dữ liệu khách cuối (`O06`); `M19` & `M21` cho phép khởi tạo kết nối/profile trong scope đã duyệt |

### 3.3. Danh mục Sự kiện Liên Module mà `M14` Bắt buộc Tiêu thụ (`Subscribed Events`)

| Nguồn & Event | Ý nghĩa & Hành vi Xử lý Tại `M14` |
|---|---|
| **`M20.LegalHoldChanged`** (`ACTIVE` / `RELEASED`, `target_scope_type`, `target_id`) | Ghi nhận trạng thái `RESTRICTED_LEGAL_HOLD` vào bảng/chỉ mục ACL scope của `M14`, bump `Principal_Permission_Versions` cho các principal thuộc workspace liên quan (`ADR-007`) |
| **`M20.DataIncidentEscalated`** (`severity`, `affected_connection_ids[]`, `affected_actor_ids[]`) | Khi sự cố rò rỉ tài khoản (`S1/S2`), tự động gọi luồng khóa khẩn cấp `SuspendUser` / `RevokeAccess` cho `affected_actor_ids[]` và bump `permission_version` (`M20-F08`) |
| **`M22` HR Events** (`hr.employment.changed.v1`, `hr.availability.changed.v1`, `hr.offboarding.effective.v1`) | Tiêu thụ có idempotency + sắp xếp thứ tự theo `effective_at` & `aggregate_version` (xử lý event đến lệch thứ tự từ `M22`); `hr.employment.changed.v1` cập nhật `Departments`/`Branch` hiển thị **không tự mở quyền dữ liệu** (`INV-02`, `H-T04`); `hr.availability.changed.v1` ghi nhận vào `Capacity_Cost_Snapshots` (chỉ trạng thái khả dụng, **không chứa lý do nghỉ phép/lương**); `hr.offboarding.effective.v1` kích hoạt `InitiateOffboarding` (`M22-F22`) |
| **`M23` Ops Events** (`M23.BreakGlassApproved`, `M23.BreakGlassRevoked`, `M23.TenantOperatingModeChanged`) | `ApplyBreakGlassGrant` / `RevokeBreakGlassGrant` vào bảng runtime `Break_Glass_Grants` của `M14` và bump `permission_version`; `SetTenantOperatingMode` cập nhật `Tenants.operating_mode` (`SOLO_PILOT <-> TEAM`, `ADR-003`) |

---

## 4. Compatibility, Privacy & Test Matrix (`MODULE-SPEC` Aligned)

| Test ID | Mục tiêu Kiểm chứng Hợp đồng `C14` | Severity | Applicability | Status | Actual / Build / Fixture |
|---|---|---|---|---|---|
| `M14-AC01` / `INT29` | Xung đột Role/Entity `ALLOW` vs `DENY` & lọc `PERSONAL` trong `CompileScopeFilter` (`OR branch` bị bỏ) | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-ACL-01` |
| `U16` / `SEC-U03` | Token / URL `Download Gateway` (`GET/Range`) mang `expected_permission_version` cũ bị `401/403 Fail-Closed` sau revoke | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-GW-01` |
| `INT23` / `CEO-U18` | Worker `M19` / Bulk `M24-F03` mang `expected_permission_version` cũ bị `409 AUTH_PERMISSION_VERSION_STALE` | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-VER-01` |
| `M20-LEGAL-HOLD-ACL` | Nhận `M20.LegalHoldChanged` bật `RESTRICTED_LEGAL_HOLD`, chặn Sales/CSKH qua cả `EvaluateAccessDecision` & `CompileScopeFilter` | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-LH-01` |
| `U17` / `CX-U01` / `RV10` / `RV15` | Cô lập Cross-Workspace, `Account -> Child`, bridge `Contract_Workspace_Grants`, PG `SET LOCAL` trên pool lỗi/rollback | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-RLS-01` |
| `H-T04` / `P-T02..36` | Điều chuyển `M22` không tự mở quyền cũ/mới; `CLIENT workspace` không đọc chéo agency/partner khác | `P0 Critical` | `SL04/08/09+` | `Not Run` | `Not Run / No Repo / Fixture-XM-01` |
