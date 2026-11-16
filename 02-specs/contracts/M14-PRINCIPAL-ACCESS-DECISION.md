# Contract `M14-PRINCIPAL-ACCESS-DECISION` — Cổng Quyết định Quyền Thực thi (`RBAC + ABAC + Legal Hold + Break-Glass`)

- **Contract ID:** `CONTRACT-M14-ACCESS-DECISION-v1.1`
- **Provider Owner:** `M14` (Tổ chức, Thành viên, Quyền & Bàn giao)
- **Consumers:** Toàn bộ domain `M01–M24`, `Download Gateway` (`SEC03`), `Worker Jobs` (`M19`, `M24-F08`), `BI/Search` (`M18`, `M24-F06`), `AI Retrieval` (`M06`, `M20-F07`)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`5.1`, `5.14`, `6.1`, `6.2`, `SEC03`, `SEC06`, `U16`, `U17`, `CEO-U10`, `CEO-U17`, `CEO-U18`, `CX-U01`, `INT23`, `INT29`, `RV10`, `RV15`, `OC20`), [ADR-002](../../01-architecture/decisions/ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-003](../../01-architecture/decisions/ADR-003-PERMISSION-VERSION-CACHE-AND-MODE-GOVERNANCE.md), [ADR-004](../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](../../01-architecture/decisions/ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-008](../../01-architecture/decisions/ADR-008-OMNICHANNEL-CONTRACTS-RECEIPTS-AND-CROSS-EVENTS.md), [ADR-009](../../01-architecture/decisions/ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md)
- **Trạng thái:** `Reviewed (CR-20261116-WAVE1-RECONCILIATION; CR-20261116-M16-ALIGNMENT; CR-20261116-WAVE1-5-HARDENING Applied)`
- **Chính sách Breaking Change:** Additive-only cho trường mới không bắt buộc; đổi cấu trúc `Output` hoặc mở rộng tập `resource_type`/`action` bắt buộc cập nhật đồng thời `ADR-002`/`ADR-003`/`ADR-008`/`ADR-009`, Change Proposal liên quan ([CR-20261116-M16-ALIGNMENT.md](../changes/archive/CR-20261116-M16-ALIGNMENT.md), `CR-20261116-WAVE1-5-HARDENING`) và Consumer liên quan (`INDEX.md`).

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | `M14` là **cổng kiểm tra quyền thực thi duy nhất (`INV-23`)** gồm: (1) `EvaluateAccessDecision` cho lệnh ghi/tải file/AI/worker, (2) `CompileScopeFilter` (`Entity-Mapped SQL Scope Compiler`) sinh bộ lọc SQL/RLS an toàn dựa trên bảng ánh xạ cột thực thể, (3) `BindDbTransactionContext` gắn ngữ cảnh **6 biến GUC `SET LOCAL`** trên PostgreSQL pool, (4) `ResolveConnectionScopeByWebhookEndpoint` (`SECURITY DEFINER` Bootstrap Port cho Webhook `M19`) + `PORTAL_CLIENT` Write Port (`SECURITY DEFINER`), và (5) các cổng quản trị runtime (`ApplyBreakGlassGrant`, `RevokeBreakGlassGrant`, `SetTenantOperatingMode`, `InitiateOffboardingOrTransfer`, `GetCapacityCostSnapshots`). Tuân thủ tuyệt đối: `Tenant & Workspace Isolation` $\rightarrow$ `Legal Hold` $\rightarrow$ `Role/Entity DENY > ALLOW` (`Deny-Wins`). |
| **Actor/scope** | `principal_id` thuộc 1 trong 3 loại `USER | SERVICE_PRINCIPAL | PORTAL_CLIENT` qua cha thống nhất `M14.Principals` (tương ứng `Users`, `Service_Principals`, `Portal_Clients`), được xác thực trong `tenant_id` & `workspace_id` (`workspace_type = AGENCY | CLIENT | SYSTEM`) — **không nhận `tenant_id` trần từ payload client**. `Users` áp Membership RLS theo `Memberships.workspace_id` chống `PORTAL_CLIENT` (`M21-F13`). |
| **Preconditions** | Principal hợp lệ (`Users.status = 'ACTIVE'`, `Service_Principals.key_status = 'ACTIVE'`, `Portal_Clients.portal_grant_status = 'ACTIVE'`); `Memberships.status = 'ACTIVE'`; mọi `Role_Bindings` đang hiệu lực phải thỏa runtime **`now() BETWEEN valid_from AND coalesce(valid_until, 'infinity') AND revoked_at IS NULL`**. Nếu `client_version > db_version` $\rightarrow$ từ chối ngay **`401 AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED`** (dấu hiệu rollback/DR leapfrog, cấm reload cache); ở `GUARDED_EXECUTION`, `expected_permission_version` bắt buộc khớp `Principal_Permission_Versions`. |
| **Input** | Xem các JSON Schema tại Mục `2.1–2.7`: `BindDbTransactionContextInput` (6 GUC), `ResolveConnectionScopeByWebhookEndpointInput`, `EvaluateAccessDecisionInput` (bổ sung đủ `resource_type` cho `M14–M24`, `M16`, `M19`, `M20`), `CompileScopeFilterInput`, `ApplyBreakGlassGrantInput`, `RevokeBreakGlassGrantInput`, `SetTenantOperatingModeInput`, `InitiateOffboardingOrTransferInput`, `GetCapacityCostSnapshotsInput`. |
| **Output** | Xem các JSON Schema tại Mục `2.1–2.7`: `BindDbTransactionContextOutput` (6 GUC), `ResolveConnectionScopeByWebhookEndpointOutput`, `AccessDecisionOutput` (`decision`, `http_status_recommendation` gồm `401/403` cho `DOWNLOAD_FILE`, `field_policy`, `audit_context`), `CompiledScopeFilterOutput` (`Entity_Scope_Metadata`, `predicate_ast`, `bind_params` với `active_delegations[]` và `active_break_glass_scopes[]`), và Output của các cổng `2.4–2.7`. Không trả raw DB row. |
| **Errors** | Chuẩn Error Envelope: `{code, message, field_errors, correlation_id}`. Mã lỗi chính: `401 AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED` (kể cả khi **`client_version > db_version`** hoặc session đã cắt, hoặc `DOWNLOAD_FILE` mất phiên); `403 AUTH_RBAC_FORBIDDEN`, `403 AUTH_PERMISSION_VERSION_STALE_DOWNLOAD` (`DOWNLOAD_FILE` lệch version trả `401/403`, không trả `409`), `403 AUTH_SELF_APPROVAL_BLOCKED` (`Maker == Checker` hoặc `COALESCE(delegated_from_id, approver_id) = maker_id`), `403 AUTH_DENY_POLICY_ACTIVE`, `403 AUTH_PERSONAL_SCOPE_DENIED`, `403 AUTH_LEGAL_ENTITY_MISMATCH`, `403 AUTH_LEGAL_HOLD_RESTRICTED`; `409 AUTH_PERMISSION_VERSION_STALE` (`GUARDED_EXECUTION` Worker/Bulk/`EXPORT`); `404 RESOURCE_NOT_FOUND_OR_DENIED` (Non-Disclosure `U17`/`CX-U01`). |
| **Concurrency** | Áp dụng 3 nguyên tắc theo `ADR-003`: (A) **Rollback Guard:** `client_version > db_version` $\rightarrow$ **`401` Fail-Closed ngay**; (B) **Interactive UI Read** (`client_version < db_version`): xóa cache `M24-F06`, nạp lại từ Primary DB; (C) **Guarded Async / Bulk / Export / Download Gateway** (`GUARDED_EXECUTION`): lệch `expected_permission_version != db_version` hoặc `OFFBOARDING_LOCKED/SUSPENDED` $\rightarrow$ **Fail-Closed tức thì** (`401/403` cho `DOWNLOAD_FILE`, `409 AUTH_PERMISSION_VERSION_STALE` cho Worker/Bulk/Export). |
| **Idempotency** | Các cổng quyết định & lọc (`2.1–2.3`, `2.7`) thuần đọc / context-binding (ngoại trừ ghi `Audit_Logs` cảnh báo an ninh); các cổng lệnh (`2.4–2.6`) bắt buộc `idempotency_key` + `correlation_id` xử lý idempotent, ghi `Security_Revocation_Ledger` & bump `permission_version`. |
| **Transaction** | Mọi DB query/command trên PostgreSQL pool bắt buộc chạy `BindDbTransactionContext` trong transaction (**6 GUC `SET LOCAL`**: thêm `app.current_workspace_type`) dưới `app_runtime_role` không `BYPASSRLS` (`INV-13`, `RV15`). Chỉ `ResolveConnectionScopeByWebhookEndpoint` (`M19`) và `PORTAL_CLIENT` Write Port dùng `SECURITY DEFINER` phạm vi tối thiểu; `Offboarding` & `VerifyRestore` chạy **fan-out theo từng `workspace_id`** (tuyệt đối không bật `BYPASSRLS`). |
| **Compatibility** | Mở rộng additive-only theo `ADR-002`/`ADR-008`/`ADR-009` (`CR-20261116-WAVE1-5-HARDENING`); `Entity-Mapped SQL Scope Compiler` ánh xạ rõ cột thực tế trên từng bảng tránh phụ thuộc 5 cột giả định chung. |
| **Audit/privacy** | Mọi quyết định `DENY` nhạy cảm hoặc sử dụng `BREAK_GLASS` / `DELEGATED` ghi `Audit_Logs` (`M23-F06`) kèm `correlation_id`, `actor_id`, `delegated_from_id`, `break_glass_grant_id`, `internal_reason_code` — đã `Redact-Before-Insert` (`NFR11`, `ADR-004`). |
| **Tests** | `M14-AC01`, `M14-AC02`, `U16`, `U17`, `SEC-U03`, `SEC-U06`, `INT23`, `INT29`, `RV10`, `RV15`, `CEO-U10`, `CEO-U17`, `CEO-U18`, `CX-U01`, `OC20`, `H-T04`, `P-T02..06`, `P-T30..31`, `P-T35..36`, `C14-W15-01..03`. Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas & Quy tắc Đánh giá Chuẩn (`ADR-002`, `ADR-003`, `ADR-008`)

### 2.1. `BindDbTransactionContext` (6 GUC), Bootstrap Port `ResolveConnectionScopeByWebhookEndpoint` & `PORTAL_CLIENT` Write Port

```json
{
  "BindDbTransactionContextInput": {
    "tenant_id": "uuid (NN — lấy từ verified session/job/bootstrap context)",
    "workspace_id": "uuid | null (NULL chỉ hợp lệ cho tenant-catalog Nhóm B-Catalog được khai báo)",
    "workspace_type": "AGENCY | CLIENT | SYSTEM (NN — bắt buộc phân biệt lane Portal vs Agency)",
    "principal_id": "uuid (NN — tham chiếu M14.Principals)",
    "permission_version": "integer (bigint > 0, đọc từ Primary DB nếu Guarded)",
    "acting_mode": "DIRECT | DELEGATED | BREAK_GLASS | SYSTEM_WORKER",
    "correlation_id": "uuid (NN)"
  },
  "BindDbTransactionContextOutput": {
    "bound_gucs": {
      "app.current_tenant_id": "string (uuid)",
      "app.current_workspace_id": "string (uuid hoặc rỗng)",
      "app.current_workspace_type": "AGENCY | CLIENT | SYSTEM",
      "app.current_principal_id": "string (uuid)",
      "app.current_permission_version": "string (bigint)",
      "app.current_acting_mode": "DIRECT | DELEGATED | BREAK_GLASS | SYSTEM_WORKER"
    },
    "transaction_isolated": "boolean (true)"
  }
}
```

**Cổng Bootstrap & Write Port phạm vi tối thiểu (`SECURITY DEFINER` — cấm `BYPASSRLS` trên `app_runtime_role`):**
- **Bootstrap Resolution Port `ResolveConnectionScopeByWebhookEndpoint` (`M19` Inbound Webhook):** Trước khi có JWT/Session, Webhook Ingress không thể gắn trước 6 GUC. Chỉ duy nhất hàm/stored procedure `SECURITY DEFINER` này (khóa `SET search_path = pg_catalog, public`) được phép tra bảng định tuyến tối thiểu để phân giải `(tenant_id, workspace_id, workspace_type, acting_principal_id)` và trả về ngay cho Worker `M19` gắn **6 GUC `SET LOCAL`** vào transaction chính.
- **Tác vụ Quét Đa Workspace (`Offboarding` & `VerifyPostRestoreComplianceGate`):** Tuyệt đối **không dùng `BYPASSRLS`**; hệ thống liệt kê danh sách `workspace_id` hợp lệ trong tenant và thực thi **fan-out tuần tự/song song theo từng `workspace_id`** với đủ 6 GUC `SET LOCAL` trên mỗi transaction con.
- **`PORTAL_CLIENT` Write Port (`SECURITY DEFINER` — `ADR-002`):** `PORTAL_CLIENT` có RLS `SELECT` 2 chiều có điều kiện qua `Contract_Workspace_Grants` (trên `DELIVERABLE`, `ACCEPTANCE`, `ASSET`); mọi thao tác ghi phản hồi từ Portal (`ACCEPT_OFFER`, `DECLINE_OFFER`, `PUBLISH_REVIEW` / duyệt nghiệm thu hoặc `COMMENT` trên `CLIENT_REVIEW`/`REWORK`/`ACCEPTED`) bắt buộc đi qua `SECURITY DEFINER` Write Port kiểm tra trước `EvaluateAccessDecision`, thay vì mở RLS `UPDATE` chéo workspace.

```json
{
  "ResolveConnectionScopeByWebhookEndpointInput": {
    "provider": "ZALO_OA | FACEBOOK_PAGE | TIKTOK_BM | TELEGRAM | GMAIL | MS_GRAPH | WEB_FORM | VOIP_SIP | PAYMENT_GW | PANCAKE | ERP_MISA | PMS | BIOMETRIC_DEVICE | PAYROLL_BANK",
    "provider_namespace": "string (NN — external app/page/oa identifier)",
    "webhook_endpoint_token": "string | null (NN trừ khi provider dùng app-level webhook giải qua provider + provider_namespace + chữ ký)",
    "correlation_id": "uuid (NN)"
  },
  "ResolveConnectionScopeByWebhookEndpointOutput": {
    "connection_id": "uuid",
    "tenant_id": "uuid",
    "workspace_id": "uuid",
    "workspace_type": "AGENCY | CLIENT",
    "connection_status": "PENDING_AUTHORIZATION | ACTIVE | DEGRADED | REAUTHORIZATION_REQUIRED | PAUSED | DISCONNECTED",
    "acting_principal_id": "uuid (SERVICE_PRINCIPAL id trong M14.Principals)",
    "permission_version": 1,
    "resolved_via": "SECURITY_DEFINER_BOOTSTRAP_PORT",
    "correlation_id": "uuid"
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
    "workspace_type": "AGENCY | CLIENT | SYSTEM",
    "execution_mode": "INTERACTIVE_READ | GUARDED_EXECUTION",
    "expected_permission_version": "integer | null (bắt buộc non-null khi execution_mode = GUARDED_EXECUTION; nếu > db_version trả 401 ngay)",
    "resource_type": "TENANT | BRANCH | LEGAL_ENTITY | BUSINESS_LINE | BRAND | BUSINESS_UNIT | DEPARTMENT | WORKSPACE | WORKSPACE_ACCOUNT_LINK | CONTRACT_WORKSPACE_GRANT | PRINCIPAL | USER | SERVICE_PRINCIPAL | PORTAL_CLIENT | TEAM | MEMBERSHIP | ROLE | ROLE_BINDING | ENTITY_TEAM_GRANT | BREAK_GLASS_GRANT | DELEGATION | LEGAL_HOLD_SCOPE_REGISTRY | SECURITY_REVOCATION_LEDGER | OFFBOARDING_CASE | OFFBOARDING_CHECKLIST_ITEM | CAPACITY_COST_SNAPSHOT | SCORECARD_REVIEW | POLICY_DEFINITION | POLICY_VERSION | APPROVAL_MATRIX_RULE | AUTH_SESSION_POLICY | USER_SESSION | BREAK_GLASS_REQUEST | SECURITY_ANOMALY_ALERT | FEATURE_FLAG_CONFIG | SYSTEM_CALENDAR | SHARED_DICTIONARY | SHARED_TEMPLATE | AUDIT_LOG | INTERNAL_OUTBOX_EVENT | INTERNAL_DEAD_LETTER_QUEUE | BACKUP_DRILL_LOG | EXPORT_REQUEST | APPROVAL_REQUEST | APPROVAL_DECISION | COMMAND_PALETTE_INDEX | SPLIT_VIEW_CONFIG | BULK_COMMAND_BATCH | BULK_COMMAND_ITEM | QUICK_REPLY_PRESET | NOTIFICATION_PREFERENCES_DIGEST | INTERNAL_NOTIFICATION | PERMISSION_CACHE_VERSION | READ_MODEL_PROJECTION | QUEUE_LANE_CONFIG | ASYNC_EXPORT_JOB | COLD_ARCHIVE_PARTITION | CONTACT | ACCOUNT | LEAD | DEAL | CONVERSATION | MESSAGE | ATTACHMENT | ASSET | ASSET_VERSION | DELIVERABLE_ASSET_REF | QUOTE | ORDER | CONTRACT | INVOICE_LINE | PAYMENT | COMMISSION | TICKET | PROJECT | PROJECT_MILESTONE | PROJECT_CHANGE_REQUEST | DELIVERABLE | REVISION_BATCH | REVISION_ITEM | ACCEPTANCE | CLIENT_WAIT_INTERVAL | TASK | TASK_SUBMISSION | TASK_REVIEW | TASK_LINK | TASK_ASSET | TASK_BOARD_STAGE | TASK_CHANGE_REQUEST | TASK_COMMENT | TASK_BLOCKER | WORK_QUEUE | TASK_TEMPLATE | RECURRENCE_RULE | TIME_ENTRY | RESOURCE_ALLOCATION | STRATEGY_BRIEF | IMC_PLAN | JOURNEY | CAMPAIGN | BUDGET | REPORT | REFERRAL | LOYALTY_LEDGER | APPOINTMENT | RESOURCE | FEEDBACK | RECOVERY_CASE | CHANNEL_CONNECTION | CONNECTOR_MAPPING | CONNECTION_CAPABILITY | OUTBOUND_INTENT | INBOUND_EVENT | QUARANTINED_EVENT | SYNC_RUN | ADAPTER_DLQ | REPLAY_JOB | PROCESSING_RECORD | CONSENT_LOG | CONSENT_STATE | ENDPOINT_SUPPRESSION | PRIVACY_REQUEST | LEGAL_HOLD | LEGAL_DEADLINE_POLICY | RETENTION_POLICY | DELETION_LEDGER | PLACEHOLDER_VAULT | DATA_INCIDENT | VENDOR_DATA_FLOW | DPA_CONTRACT | PARTNER_DATA_PROFILE | PARTNER_DATASET | PARTNER_REPORT | PARTNER_EXCEPTION_CASE | EMPLOYEE | EMPLOYMENT_CONTRACT | ATTENDANCE | LEAVE_REQUEST | PAYROLL",
    "resource_id": "uuid | null (null khi action = CREATE hoặc list-level check)",
    "action": "CREATE | READ | COMMENT | UPDATE | ARCHIVE | DELETE_PRIVACY | APPROVE | CLAIM | ACCEPT_OFFER | DECLINE_OFFER | SUBMIT_RESULT | PUBLISH_REVIEW | REOPEN | WAIVE_DEPENDENCY | EXPORT | IMPORT | SHARE_GRANT | DELEGATE | DOWNLOAD_FILE | AI_RETRIEVE | CONNECT | VERIFY_CAPABILITY | ACTIVATE | DISPATCH | PAUSE | RESUME | DISCONNECT | TRANSFER | RECONCILE | SYNC | REPLAY | VIEW_QUARANTINE_PAYLOAD | MANAGE_POLICY | VIEW_AUDIT",
    "requested_fields": ["string"],
    "context_flags": {
      "target_workspace_id": "uuid | null",
      "target_branch_id": "uuid | null",
      "target_legal_entity_id": "uuid | null",
      "target_owner_id": "uuid | null",
      "target_account_id": "uuid | null",
      "target_team_id": "uuid | null",
      "target_project_id": "uuid | null",
      "target_visibility_scope": "PERSONAL | TEAM | WORKSPACE | null",
      "target_active_legal_hold_ids": ["uuid"],
      "target_legal_hold_status": "NONE | RESTRICTED_LEGAL_HOLD | null",
      "target_deliverable_status": "string | null",
      "target_published_to_client_workspace_id": "uuid | null",
      "maker_id": "uuid | null (kiểm tra Maker != Checker cho APPROVE / APPROVAL_DECISION)",
      "delegated_from_id": "uuid | null",
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
1. **Bước 1 — Kiểm trạng thái `Principals` theo `principal_type` & hiệu lực `Role_Bindings` tại runtime:**
   - `USER`: bắt buộc `Users.status == 'ACTIVE'` và `Memberships.status == 'ACTIVE'` (trạng thái `OFFBOARDING_LOCKED`, `SUSPENDED`, `OFFBOARDED`, `INVITED`, `CANCELLED` $\rightarrow$ `DENY / 401`). Không cho `PORTAL_CLIENT` đọc `Users` Agency (`Memberships` RLS `M21-F13`).
   - `SERVICE_PRINCIPAL`: bắt buộc `Service_Principals.key_status == 'ACTIVE'`, API key/certificate chưa thu hồi, đúng `tenant_id` & phạm vi `workspace_id`.
   - `PORTAL_CLIENT`: bắt buộc `Portal_Clients.portal_grant_status == 'ACTIVE'`, `workspace_type == 'CLIENT'`, không trỏ ngược `AGENCY` (`CEO-U17`).
   - Mọi `Role_Bindings` được xét ở các bước sau **bắt buộc thỏa tại runtime**: `revoked_at IS NULL AND now() BETWEEN valid_from AND coalesce(valid_until, 'infinity')` (`[MASTER]` & `ADR-002`).
2. **Bước 2 — Kiểm `expected_permission_version` & Rollback Detection (`ADR-003`):**
   - Đọc `db_version` (`acl_epoch`) từ `M14.Principal_Permission_Versions` trên Primary DB.
   - **Phát hiện Rollback (`client_version > db_version`):** Nếu `expected_permission_version != null && expected_permission_version > db_version` (xảy ra khi dùng lại token từ snapshot trước DR leapfrog hoặc giả mạo version) $\rightarrow$ **`DENY` ngay với `401 AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED`** (**tuyệt đối không reload cache**).
   - Nếu `execution_mode = GUARDED_EXECUTION` và `expected_permission_version != db_version`:
     - Với **`action == 'DOWNLOAD_FILE'`** (`GET`, `HTTP Range/resume`): trả **`401 AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED`** hoặc **`403 AUTH_PERMISSION_VERSION_STALE_DOWNLOAD`** (tùy trạng thái phiên — **bắt buộc nằm trong `{401, 403}` trong `AccessDecisionOutput`**, tuyệt đối không trả `200`/`409`).
     - Với Worker / Bulk / Export: trả `409 AUTH_PERMISSION_VERSION_STALE`.
   - Nếu `execution_mode = INTERACTIVE_READ` và `expected_permission_version < db_version`: xóa cache `M24-F06` của principal và nạp lại từ Primary DB để đánh giá tiếp.
3. **Bước 3 — Kiểm Cô lập `Workspace`, `Bridge` & `Legal Entity`:**
   - Nếu `target_workspace_id != workspace_id`: bắt buộc có `Workspace_Account_Links` hoặc `Contract_Workspace_Grants` còn hiệu lực (`revoked_at IS NULL AND now() BETWEEN valid_from AND coalesce(valid_until, 'infinity')`) khớp `resource_type` + `allowed_relations` (đã mở rộng gồm `ASSET` (`CLIENT_PUBLISHED` `Deliverable_Asset_Refs`) & `ACCEPTANCE`).
   - Với `principal_type == 'PORTAL_CLIENT'` đọc/tương tác `DELIVERABLE | ACCEPTANCE | ASSET | DELIVERABLE_ASSET_REF`: bắt buộc `target_published_to_client_workspace_id == workspace_id` và `target_deliverable_status IN ('CLIENT_REVIEW', 'REWORK', 'ACCEPTED')` (các trạng thái nháp nội bộ Agency bị chặn `404`).
   - Khi đọc qua cầu nối hợp lệ ở `BRANCH_SCOPED`, bản ghi cross-workspace có `target_branch_id IS NULL` **vẫn được phép đi qua nhánh Bridge** (không bị lọc rớt nhầm bởi điều kiện branch nội bộ).
   - Nếu `resource_type IN ('CONTRACT', 'ORDER', 'INVOICE_LINE', 'PAYMENT', 'COMMISSION', 'PAYROLL')` hoặc tenant bật `O08 = true`: kiểm khớp `target_legal_entity_id` nằm trong phạm vi pháp nhân được cấp của principal (`CEO-U10`), trái phép $\rightarrow$ `DENY (403 AUTH_LEGAL_ENTITY_MISMATCH)`.
4. **Bước 4 — Bảo vệ `PERSONAL` & `Legal Hold` (`cardinality(active_legal_hold_ids) > 0`, `ADR-002`, `ADR-007`):**
   - Nếu `target_visibility_scope = 'PERSONAL'`: chặn hoàn toàn vai trò cấp trên/chi nhánh (`W-O04`, `INV-02`); chỉ tiếp tục nếu `principal_id == target_owner_id` hoặc có `Entity_Team_Grants (ALLOW)` chính danh còn hạn.
   - Nếu **`cardinality(target_active_legal_hold_ids) > 0`** (hoặc `target_legal_hold_status = 'RESTRICTED_LEGAL_HOLD'` đối chiếu qua `Legal_Hold_Scope_Registry` từ `M20.LegalHoldChanged`): chặn ngay mọi vai trò tác nghiệp thường (`SALES`, `MARKETING`, `AM_CSKH`, `DELIVERY`), kể cả `UPDATE`/`DELETE_PRIVACY`/`EXPORT` thường; **chỉ cho phép `READ`/`VIEW_AUDIT` đối với vai trò có thẩm quyền `LEGAL_HOLD_READ` (`FINANCE`, `PRIVACY`, `LEGAL_AUDITOR`)**.
5. **Bước 5 — Kiểm `DENY` Tường minh & `Maker != Checker` (`Deny-Wins`, `INT29`):**
   - Kiểm tra cả **Role-level `Role_Bindings (effect = 'DENY')`** hợp lệ theo `now()` trong `(workspace_id, branch_id, legal_entity_id, resource_type)` **VÀ Entity-level `Entity_Team_Grants (effect = 'DENY')`** trên `resource_id` / `target_account_id`. Có bất kỳ `DENY` nào khớp $\rightarrow$ `DENY (403 AUTH_DENY_POLICY_ACTIVE)` ngay tức thì.
   - Với các action phê duyệt (`APPROVE` trên `APPROVAL_DECISION`, duyệt `Entity_Team_Grants`, duyệt `Delegations`, duyệt `Break_Glass` khi `TEAM`, hạ `TEAM -> SOLO_PILOT`): bắt buộc **`COALESCE(delegated_from_id, principal_id) <> maker_id`** (nếu vi phạm $\rightarrow$ `403 AUTH_SELF_APPROVAL_BLOCKED`).
6. **Bước 6 — Tổng hợp Nguồn `ALLOW` (`RBAC + ABAC` cùng thỏa):**
   - Phải thỏa quyền thực thi `action` từ `Roles.permissions_matrix` (theo `DIRECT` Role còn hạn, hoặc `DELEGATED` qua `Delegations` `ACTIVE` đúng `branch_id`, `specific_resource_ids`, `allowed_actions` — lưu ý `Delegations` bị thu hồi ngay khi `SuspendUser`/`BRANCH_TRANSFER`/`ROLE_CHANGE`, hoặc `BREAK_GLASS` qua `M14.Break_Glass_Grants` `ACTIVE` còn TTL khớp `branch_id`, `specific_resource_ids`, và nếu đụng HR/Payroll phải có **`hr_payroll_explicitly_approved = true`**).
   - Đồng thời thỏa phạm vi dữ liệu `ABAC`: `data_scope = WORKSPACE`, hoặc `data_scope = BRANCH` (khớp `target_branch_id`, trừ `PERSONAL/RESTRICTED`), hoặc `owner_id == principal_id`, hoặc **thành viên `TEAM`/`PROJECT`** (`Memberships.team_id == target_team_id` / `Task_Participants` trên `target_project_id`/`resource_id`), hoặc `Delegation`, hoặc `Entity_Team_Grants (ALLOW)` (kể cả `target_account_id`), hoặc `Break_Glass_Grants (ALLOW)`. Thiếu 1 trong 2 lớp $\rightarrow$ `DENY (403 AUTH_RBAC_FORBIDDEN)`.
7. **Bước 7 — Tính `field_policy` (`M01–M24`, `M22` Lương/CCCD, `M20` PII):**
   - Giao cắt các trường cho phép; mọi trường nhạy cảm bị khóa ở vai trò thấp hơn (`M22` lương/CCCD, `standard_cost_rate` đối với non-finance, `TECH_ADMIN` bị cấm đọc dữ liệu kinh doanh/lương) được đẩy vào `masked_fields` hoặc `forbidden_fields` (`forbidden` luôn thắng `masked`, `masked` thắng `allowed`).

```json
{
  "AccessDecisionOutput": {
    "decision": "ALLOW | DENY",
    "http_status_recommendation": "integer (200 | 401 | 403 | 404 | 409 — voi DOWNLOAD_FILE bi tu choi chi tra 401 hoac 403)",
    "internal_reason_code": "ALLOW_DIRECT_ROLE | ALLOW_ENTITY_GRANT | ALLOW_TEAM_OR_PROJECT_MEMBER | ALLOW_DELEGATED | ALLOW_BREAK_GLASS | AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED | AUTH_PERMISSION_VERSION_STALE | AUTH_PERMISSION_VERSION_STALE_DOWNLOAD | AUTH_CROSS_WORKSPACE_BLOCKED | AUTH_LEGAL_ENTITY_MISMATCH | AUTH_PERSONAL_SCOPE_DENIED | AUTH_LEGAL_HOLD_RESTRICTED | AUTH_DENY_POLICY_ACTIVE | AUTH_SELF_APPROVAL_BLOCKED | AUTH_RBAC_FORBIDDEN",
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

### 2.3. `CompileScopeFilterInput` & `CompiledScopeFilterOutput` (`Entity-Mapped SQL Scope Compiler` — `ADR-002`)

```json
{
  "CompileScopeFilterInput": {
    "principal_id": "uuid (NN)",
    "principal_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "workspace_type": "AGENCY | CLIENT | SYSTEM",
    "execution_mode": "INTERACTIVE_READ | GUARDED_EXECUTION",
    "expected_permission_version": "integer | null (bắt buộc non-null khi execution_mode = GUARDED_EXECUTION hoặc action = EXPORT theo ADR-003)",
    "branch_id": "uuid | null",
    "legal_entity_id": "uuid | null",
    "resource_type": "enum (như EvaluateAccessDecisionInput)",
    "action": "READ | EXPORT | AI_RETRIEVE",
    "requested_relation_or_action": "string (NN — ánh xạ từ action/query dùng để kiểm Contract_Workspace_Grants.allowed_relations)",
    "delivery_channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK | null",
    "include_legal_hold_records": "boolean (default true; tự động chặn ở AST nếu principal không có legal_hold_read_role)",
    "correlation_id": "uuid (NN)"
  },
  "CompiledScopeFilterOutput": {
    "effective_permission_version": 42,
    "acl_epoch": 1,
    "has_any_access": "boolean",
    "scope_mode": "NONE | OWN_AND_GRANTS_ONLY | BRANCH_SCOPED_BY_ROLE | ALL_WORKSPACE_BY_ROLE",
    "entity_scope_metadata": {
      "resource_type": "TASK | PROJECT | DELIVERABLE | ACCEPTANCE | DEAL | CONTACT | ACCOUNT | ...",
      "workspace_col": "workspace_id",
      "branch_col": "branch_id | null",
      "team_col": "team_id | null",
      "legal_entity_col": "legal_entity_id | null",
      "sensitivity_col": "sensitivity_level | null",
      "visibility_col": "visibility (vd M16.Tasks: PRIVATE | TEAM | PROJECT | EXPLICIT; hoặc PERSONAL) | null",
      "owner_cols": ["assignee_user_id", "requester_id"],
      "reviewer_col": "reviewer_id | null",
      "collaborator_exists_sql": "EXISTS (SELECT 1 FROM task_participants tp WHERE tp.task_id = t.id AND tp.user_id = :principal_id) | null",
      "account_col": "account_id | client_account_id | null",
      "legal_hold_col": "active_legal_hold_ids",
      "allow_unbranched_records": "boolean (default false)",
      "allow_tenant_wide_scope": "boolean (true cho Nhóm B & Audit_Logs có workspace_id IS NULL)",
      "is_catalog_entity": "boolean"
    },
    "enforced_visibility_guard": "boolean",
    "enforced_legal_hold_guard": "boolean",
    "predicate_ast": "string (SQL-safe parameterized AST chuẩn hóa 6 tầng biên dịch theo entity_scope_metadata)",
    "bind_params": {
      "tenant_id": "uuid",
      "workspace_id": "uuid",
      "workspace_type": "AGENCY | CLIENT | SYSTEM",
      "principal_id": "uuid",
      "resource_type": "string (enum từ Input, dùng khớp verified_bridge_keys)",
      "requested_relation_or_action": "string",
      "scope_mode": "NONE | OWN_AND_GRANTS_ONLY | BRANCH_SCOPED_BY_ROLE | ALL_WORKSPACE_BY_ROLE",
      "allow_unbranched_records": "boolean (default false)",
      "allow_tenant_wide_scope": "boolean",
      "is_catalog_entity": "boolean",
      "verified_bridge_keys": ["string (RESOURCE_TYPE:uuid)"],
      "verified_bridge_allowed_relations": ["string"],
      "enforced_legal_entity_ids": "uuid[] | null (NULL khi không giới hạn pháp nhân; cấm truyền [] khi NULL)",
      "allowed_branch_ids": ["uuid"],
      "active_delegations": [
        {
          "delegator_id": "uuid",
          "branch_id": "uuid | null",
          "specific_resource_ids": ["uuid"],
          "allowed_actions": ["string"]
        }
      ],
      "active_break_glass_scopes": [
        {
          "break_glass_grant_id": "uuid",
          "workspace_ids": ["uuid"],
          "branch_id": "uuid | null",
          "scope_resource_types": ["string"],
          "specific_resource_ids": ["uuid"],
          "allowed_actions": ["string"],
          "hr_payroll_explicitly_approved": "boolean (default false)"
        }
      ],
      "granted_account_ids": ["uuid"],
      "explicit_allow_entity_ids": ["uuid"],
      "explicit_personal_share_grant_ids": ["uuid"],
      "has_matching_role_deny_in_scope": "boolean",
      "explicit_deny_entity_grant_ids": ["uuid"],
      "explicit_deny_account_ids": ["uuid"],
      "include_legal_hold_records": "boolean (default true)",
      "principal_has_legal_hold_read_role": "boolean"
    },
    "correlation_id": "uuid"
  }
}
```

**Mẫu `predicate_ast` 6 tầng hội đã vá (`Entity-Mapped SQL Scope Compiler` — tách Nhánh Cross-Workspace Bridge, bổ sung Nhánh 3 Tenant-Wide `NULL`, đồng bộ `M16.Tasks.visibility`, và truyền đủ tham số `Break-Glass`):**

```sql
(tenant_id = :tenant_id)
AND (
  :enforced_legal_entity_ids IS NULL
  OR <legal_entity_col> = ANY(:enforced_legal_entity_ids)
)
AND (
  /* Nhánh 1: Dữ liệu nội bộ trong chính :workspace_id */
  (
    <workspace_col> = :workspace_id
    AND (
      :scope_mode = 'ALL_WORKSPACE_BY_ROLE'
      OR (
        :scope_mode = 'BRANCH_SCOPED_BY_ROLE'
        AND (
          (<branch_col> IS NOT NULL AND <branch_col> = ANY(:allowed_branch_ids))
          OR (<branch_col> IS NULL AND :allow_unbranched_records = true)
        )
        AND (<sensitivity_col> IS NULL OR <sensitivity_col> <> 'RESTRICTED')
      )
      OR (<owner_cols[] matches :principal_id>)
      OR (<reviewer_col> IS NOT NULL AND <reviewer_col> = :principal_id)
      OR (<collaborator_exists(:principal_id)>)
      OR (<delegation_match(:active_delegations)>)
      OR (<account_col> IS NOT NULL AND <account_col> = ANY(:granted_account_ids))
      OR id = ANY(:explicit_allow_entity_ids)
      OR (<break_glass_match(:active_break_glass_scopes, :workspace_id, <branch_col>, :resource_type, id)>)
    )
  )
  /* Nhánh 2: Cầu nối Cross-Workspace (tách biệt khỏi ALL_WORKSPACE_BY_ROLE; hỗ trợ DELIVERABLE/ACCEPTANCE/ASSET có branch_id NULL) */
  OR (
    <workspace_col> <> :workspace_id
    AND CONCAT(:resource_type, ':', id::text) = ANY(:verified_bridge_keys)
    AND :requested_relation_or_action = ANY(:verified_bridge_allowed_relations)
  )
  /* Nhánh 3: Bản ghi cấp Tenant (workspace_id IS NULL — vá bẫy SQL NULL cho Nhóm B & Audit_Logs) */
  OR (
    <workspace_col> IS NULL
    AND :allow_tenant_wide_scope = true
    AND (:is_catalog_entity = true OR :workspace_type IN ('AGENCY', 'SYSTEM'))
  )
)
AND (
  <visibility_col> IS NULL
  OR <visibility_col> NOT IN ('PERSONAL', 'PRIVATE', 'EXPLICIT')
  OR (<owner_cols[] matches :principal_id>)
  OR (
    <visibility_col> = 'EXPLICIT'
    AND (<collaborator_exists(:principal_id)> OR id = ANY(:explicit_personal_share_grant_ids))
  )
  OR id = ANY(:explicit_personal_share_grant_ids)
)
AND NOT (:has_matching_role_deny_in_scope)
AND (id <> ALL(:explicit_deny_entity_grant_ids))
AND (<account_col> IS NULL OR <account_col> <> ALL(:explicit_deny_account_ids))
AND (
  cardinality(<legal_hold_col>) = 0
  OR (:include_legal_hold_records = true AND :principal_has_legal_hold_read_role = true)
)
```

> **Chú giải Biên dịch An toàn (`ADR-002`, `W-O04`, `INV-02`):**
> - **Ánh xạ `M16.Tasks.visibility (PRIVATE | TEAM | PROJECT | EXPLICIT)`:** `PRIVATE` (tương ứng tác vụ `PERSONAL` trên `M16`) bị chặn hoàn toàn ở nhánh chung và chỉ mở cho chính `owner_cols[]` (`assignee_user_id`, `requester_id`) hoặc `explicit_personal_share_grant_ids`; `EXPLICIT` chỉ mở cho `owner_cols[]`, người cộng tác tường minh trong `Task_Participants` (`collaborator_exists`), hoặc `explicit_personal_share_grant_ids` (không tự mở cho quản lý chi nhánh/team nếu không được mời); `TEAM` và `PROJECT` đi qua nhánh kiểm tra Team/Project/Workspace thông thường.
> - **Ràng buộc `Break-Glass` (`<break_glass_match(:active_break_glass_scopes, :workspace_id, <branch_col>, :resource_type, id)>`):** Phải khớp `workspace_id`, khớp `<branch_col>` nếu grant có `branch_id IS NOT NULL` (chặn tràn sang chi nhánh khác), khớp `specific_resource_ids` nếu mảng không rỗng, và chặn cứng các domain lương/nhân sự nhạy cảm (`HRM_PAYROLL`, `EMPLOYEE`, `EMPLOYMENT_CONTRACT`, `ATTENDANCE`, `LEAVE_REQUEST`, `PAYROLL`) khi `hr_payroll_explicitly_approved = false`.
> - **Nhánh 3 Tenant-Wide (`workspace_id IS NULL`):** Chỉ kích hoạt khi `allow_tenant_wide_scope = true`; bảng `Nhóm B-Catalog` (`is_catalog_entity = true`) mở cho mọi `workspace_type` cùng tenant, còn `Nhóm B-Governance-Sensitive` & `Audit_Logs` (`is_catalog_entity = false`) chỉ mở khi `:workspace_type IN ('AGENCY', 'SYSTEM')` (chặn tuyệt đối `CLIENT` đọc trực tiếp).

### 2.4. `ApplyBreakGlassGrant` & `RevokeBreakGlassGrant` (`M23-F03` $\rightarrow$ `M14` Runtime Store, `ADR-003`)

```json
{
  "ApplyBreakGlassGrantInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid | null (gửi 1 workspace_id cụ thể; nếu M23 cấp đa workspace theo target_workspace_ids[], caller hoặc handler M14 thực thi fan-out 1 bản ghi/workspace)",
    "target_workspace_ids": ["uuid (optional — khi M23 gửi mảng đa workspace để fan-out từng workspace dưới BindDbTransactionContext)"],
    "approval_request_id": "uuid (NN — từ M23-F03)",
    "break_glass_request_id": "uuid (NN)",
    "user_id": "uuid (NN — Principal ID nhận quyền khẩn cấp)",
    "principal_type": "USER | SERVICE_PRINCIPAL",
    "branch_id": "uuid | null (giới hạn phạm vi chi nhánh nếu có)",
    "incident_ticket_id": "string (NN)",
    "scope_resource_types": ["string"],
    "specific_resource_ids": "uuid[] | null (mảng UUID giới hạn cụ thể hoặc null khi mở theo resource_type)",
    "allowed_actions": ["READ | EXPORT | UPDATE | RECONCILE"],
    "hr_payroll_explicitly_approved": "boolean (default false — bắt buộc true mới chạm HRM_PAYROLL/M22)",
    "operating_mode": "SOLO_PILOT | TEAM",
    "self_approved_in_pilot_mode": "boolean",
    "approved_by": "uuid (NN — TEAM bắt buộc approved_by <> user_id)",
    "ttl_expires_at": "timestamptz (UTC, > now())",
    "reason": "string (NN)",
    "idempotency_key": "string (NN)",
    "correlation_id": "uuid (NN)"
  },
  "RevokeBreakGlassGrantInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid | null (NULL để thu hồi đồng loạt toàn bộ các dòng Break_Glass_Grants đã fan-out theo break_glass_request_id)",
    "break_glass_request_id": "uuid (NN)",
    "revoked_by": "uuid (NN)",
    "revoke_reason": "MANUAL | TTL_EXPIRED | OFFBOARD | SECURITY_INCIDENT",
    "expected_version": "integer (bigint NN)",
    "idempotency_key": "string (NN)",
    "correlation_id": "uuid (NN)"
  },
  "BreakGlassGrantRuntimeOutput": {
    "break_glass_grant_id": "uuid",
    "status": "ACTIVE | REVOKED | EXPIRED",
    "new_permission_version": "integer (bigint)",
    "acl_epoch": "integer (bigint)",
    "revocation_ledger_id": "uuid | null",
    "correlation_id": "uuid"
  }
}
```

### 2.5. `SetTenantOperatingModeInput` & `SetTenantOperatingModeOutput` (`M23-F05` $\rightarrow$ `M14.Tenants`, `ADR-003`)

```json
{
  "SetTenantOperatingModeInput": {
    "tenant_id": "uuid (NN)",
    "approval_request_id": "uuid | null (bắt buộc non-null khi hạ TEAM -> SOLO_PILOT)",
    "target_operating_mode": "SOLO_PILOT | TEAM",
    "maker_id": "uuid (NN)",
    "approver_ids": ["uuid (hạ TEAM -> SOLO_PILOT bắt buộc >= 2 approver độc lập != maker_id gồm Owner/CEO)"],
    "delegated_from_ids": ["uuid | null"],
    "reason": "string (NN)",
    "expected_version": "integer (bigint NN)",
    "idempotency_key": "string (NN)",
    "correlation_id": "uuid (NN)"
  },
  "SetTenantOperatingModeOutput": {
    "tenant_id": "uuid",
    "previous_operating_mode": "SOLO_PILOT | TEAM",
    "current_operating_mode": "SOLO_PILOT | TEAM",
    "self_approved_grants_flagged_count": "integer (>= 0)",
    "row_version": "integer (bigint)",
    "correlation_id": "uuid"
  }
}
```

### 2.6. `InitiateOffboardingOrTransfer` & `CancelScheduledOffboarding` (`M14-F06`, `UC12`, `ADR-002`)

```json
{
  "InitiateOffboardingOrTransferInput": {
    "tenant_id": "uuid (NN)",
    "user_id": "uuid (NN)",
    "case_type": "OFFBOARD | BRANCH_TRANSFER | ROLE_CHANGE",
    "from_workspace_id": "uuid | null",
    "to_workspace_id": "uuid | null",
    "from_branch_id": "uuid | null",
    "to_branch_id": "uuid | null",
    "to_role_ids": ["uuid"],
    "default_custodian_id": "uuid (NN — fallback Branch Manager / Queue Manager / Owner)",
    "effective_at": "timestamptz (UTC — > now() tạo SCHEDULED; <= now() khóa ngay Pha 1)",
    "reason": "string (NN)",
    "expected_user_version": "integer (bigint NN)",
    "idempotency_key": "string (NN)",
    "correlation_id": "uuid (NN)"
  },
  "InitiateOffboardingOrTransferOutput": {
    "offboarding_case_id": "uuid",
    "case_status": "SCHEDULED | LOCKED_IN_HANDOVER | COMPLETED | CANCELLED",
    "user_status": "ACTIVE | OFFBOARDING_LOCKED | OFFBOARDED",
    "scanned_workspace_ids": ["uuid (fan-out từng workspace_id dưới BindDbTransactionContext, cấm BYPASSRLS)"],
    "open_items_by_category": {
      "LEAD": 0,
      "DEAL": 0,
      "CONVERSATION": 0,
      "TICKET": 0,
      "PROMISE": 0,
      "APPOINTMENT": 0,
      "TASK": 0,
      "TASK_OFFER": 0,
      "TASK_REVIEW": 0,
      "RECURRING_TEMPLATE": 0,
      "QUEUE_MANAGER": 0,
      "SCHEDULED_INTENT": 0,
      "PENDING_APPROVAL": 0
    },
    "new_permission_version": "integer (bigint)",
    "revocation_ledger_id": "uuid | null",
    "correlation_id": "uuid"
  },
  "CancelScheduledOffboardingInput": {
    "tenant_id": "uuid (NN)",
    "offboarding_case_id": "uuid (NN — chỉ hợp lệ khi status == SCHEDULED trước effective_at)",
    "cancelled_by": "uuid (NN)",
    "reason": "string (NN)",
    "expected_case_version": "integer (bigint NN)",
    "idempotency_key": "string (NN)",
    "correlation_id": "uuid (NN)"
  }
}
```

**Bảng Ánh xạ Rollup Chính thức (`C16` 9 Subtypes & `C19` 3 Subtypes $\rightarrow$ 13 `item_category` của `M14`):**
Nhằm bảo toàn đủ chi tiết bàn giao khi Offboarding/Transfer mà không làm lệch tổng đếm `total_open_items` giữa `C14`, `C16` (`ListOpenWorkForPrincipal`), và `C19` (`ListOpenIntentsForPrincipal`), mỗi item lưu giữ `source_subtype` gốc khi ánh xạ vào 13 bucket chuẩn của `open_items_by_category`:

| Nguồn & Subtype Gốc | Bucket `M14.open_items_by_category` | Ghi chú Bảo toàn Chi tiết & Ownership |
|---|---|---|
| `C16.TASK`, `C16.TASK_OFFER`, `C16.TASK_REVIEW`, `C16.RECURRING_TEMPLATE`, `C16.QUEUE_MANAGER` | Giữ nguyên (`TASK`, `TASK_OFFER`, `TASK_REVIEW`, `RECURRING_TEMPLATE`, `QUEUE_MANAGER`) | Ánh xạ 1:1 vào `Offboarding_Checklist_Items.item_category` |
| `C16.PROJECT_OWNER` | `TASK` *(kèm cờ dự án / `source_subtype = 'PROJECT_OWNER'`)* | Đếm vào nhóm `TASK` và giữ metadata dự án/deliverable để chuyển giao `Projects.owner_id` / `Deliverables.owner_id` |
| `C16.QA_REVIEWER` | `TASK_REVIEW` | Đếm vào `TASK_REVIEW`, giữ `source_subtype = 'QA_REVIEWER'` (`Deliverables.qa_reviewer_id`) |
| `C16.TASK_CHANGE_APPROVER`, `C16.PROJECT_CHANGE_APPROVER` | `PENDING_APPROVAL` | Đếm vào `PENDING_APPROVAL`, giữ `source_subtype` để định tuyến đúng `Task_Change_Requests` / `Project_Change_Requests` |
| `C19.SCHEDULED_INTENT` | `SCHEDULED_INTENT` | Ánh xạ 1:1; bàn giao `owner_user_id`, giữ `actor_id` gốc bất biến (`INT15`) |
| `C19.CHANNEL_CONNECTION_OWNER`, `C19.ADAPTER_DLQ_OWNER` | `QUEUE_MANAGER` | Rollup cứng vào bucket chuẩn **`QUEUE_MANAGER`** *(Custodian Ops/Integration; giữ `source_subtype` & `original_actor_id` bất biến `INT15` để không rớt item hoặc chia đôi số đếm)* |

### 2.7. `GetCapacityCostSnapshotsInput` & `CapacityCostSnapshotOutput` (`M14-F07` $\rightarrow$ `M16-F07 / M07 / M17 / M18`, `ADR-009`)

```json
{
  "GetCapacityCostSnapshotsInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "user_ids": ["uuid"],
    "role_ids": ["uuid"],
    "as_of_date": "date (ISO-8601)",
    "include_cost_rate": "boolean (chỉ trả số tiền khi caller có quyền FINANCIAL_COST_READ; mặc định che theo field_policy)",
    "correlation_id": "uuid (NN)"
  },
  "CapacityCostSnapshotOutput": {
    "snapshots": [
      {
        "snapshot_id": "uuid",
        "user_id": "uuid | null",
        "role_id": "uuid | null",
        "gross_available_hours_after_hr_leave": "number | null (quỹ giờ đã trừ sẵn phép/nghỉ từ M22 — M16-F07 KHÔNG trừ lại phép M22 lần 2)",
        "availability_status": "CONFIGURED | UNKNOWN",
        "standard_cost_rate": "number | null (NULL nếu thiếu cấu hình CEO-U01 — cấm mặc định 0 làm lãi ảo 100%)",
        "rate_unit": "HOURLY | DAILY",
        "currency": "string (VND | USD | ...)",
        "rate_status": "CONFIGURED | UNKNOWN",
        "effective_from": "date",
        "effective_to": "date | null"
      }
    ],
    "correlation_id": "uuid"
  }
}
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
| `M14.PermissionVersionBumped` | `principal_type`, `principal_id`, `acl_epoch`, `new_permission_version`, `reason` (`ROLE_CHANGED \| GRANT_CREATED \| GRANT_EXPIRED \| GRANT_REVOKED \| DELEGATION_CHANGED \| DELEGATION_EXPIRED \| BREAK_GLASS_GRANTED \| BREAK_GLASS_REVOKED \| BREAK_GLASS_EXPIRED \| TENANT_MODE_CHANGED \| LEGAL_HOLD \| OFFBOARD \| SUSPEND \| SECURITY_INCIDENT \| DR_ACL_EPOCH_JUMP`), `revoked_grant_ids[]` | `M24-F06`, `Download Gateway (SEC03)`, `M19`, `M23-F02` | `M24-F06` xóa/làm mới ngay Read-Model Cache (`INV-25`); `M23-F02` **chỉ thu hồi session & PWA offline cache** khi `reason IN ('OFFBOARD', 'SUSPEND', 'SECURITY_INCIDENT', 'DR_ACL_EPOCH_JUMP')` hoặc hủy session Break-glass khi `reason = 'BREAK_GLASS_EXPIRED'`; `Download Gateway` & `M19` kiểm version mới nhất |
| `M14.UserOffboardingLocked` | `user_id`, `offboarding_case_id`, `case_type` (`OFFBOARD \| BRANCH_TRANSFER \| ROLE_CHANGE`), `from_workspace_id`, `to_workspace_id`, `from_branch_id`, `to_branch_id`, `default_custodian_id`, `system_orchestrator_actor_id`, `effective_at`, `open_items_count` | `M23-F02/03/04/07`, `M02`, `M03`, `M07`, `M08`, `M11`, `M12`, `M13`, `M15`, `M16`, `M17`, `M19`, `M22`, `M24` | Khi `case_type = 'OFFBOARD'`: `M23-F02` cắt session & xóa PWA cache tức thì; `BRANCH_TRANSFER`/`ROLE_CHANGE` giữ `Users = ACTIVE` nhưng khóa quyền cũ; tạm chuyển đủ 13 nhóm `open_items` (gồm `M16` Tasks/Offers/Reviews/Templates/Work_Queues, `M19` Intents, `M23` Approvals) sang `default_custodian_id` (`UC12`, `OC18`) |
| `M14.WorkHandoverAssigned` | `offboarding_case_id`, `workspace_id`, `item_category`, `item_id`, `from_user_id`, `to_recipient_id`, `handover_status` (`PENDING_ACCEPT \| CONFIRMED \| CANCELLED_BY_MANAGER`) | `M02`, `M03`, `M07`, `M08`, `M11`, `M12`, `M13`, `M15`, `M16`, `M17`, `M19`, `M22`, `M23` | Cập nhật `owner_id` / `approver_id` / `queue_manager_user_id` cho công việc mới sau khi `CONFIRMED`; giữ nguyên `actor` & người hưởng hoa hồng lịch sử (`INT15`) |
| `M14.WorkspaceActivated` | `workspace_id`, `workspace_type` (`AGENCY \| CLIENT`), `client_account_id`, `processing_scope`, `default_legal_entity_id` | `M20`, `M19`, `M21`, `M16` | `M20` xác nhận `Processing_Records` + DPA trước khi mở dữ liệu khách cuối (`O06`); `M19`, `M21`, `M16` cho phép khởi tạo kết nối/profile/dự án trong scope đã duyệt |

### 3.3. Danh mục Sự kiện Liên Module mà `M14` Bắt buộc Tiêu thụ (`Subscribed Events`)

| Nguồn & Event | Ý nghĩa & Hành vi Xử lý Tại `M14` |
|---|---|
| **`M20.LegalHoldChanged`** (`ACTIVE \| RELEASED`, `legal_hold_id`, `target_scope_type`, `target_id`) | Đồng bộ mảng **`active_legal_hold_ids uuid[]`** trong `M14.Legal_Hold_Scope_Registry` (`ACTIVE` append, `RELEASED` remove; hỗ trợ `PROJECT \| DELIVERABLE \| TASK`) và bump `Principal_Permission_Versions` cho các principal thuộc workspace liên quan (`ADR-007`) |
| **`M20.SubjectErasureExecuted`** (`erased_subject_refs[]`, `endpoint_hmac_hashes_by_version[]`, `scope_tenant_wide`) | Kiểm tra `Legal_Hold_Scope_Registry` (`cardinality(active_legal_hold_ids) = 0`): nếu không vướng hold, ẩn danh/xóa PII trên `Users` (`full_name`, `email`, giữ `id`), `Portal_Clients` (`display_name`, `email_masked`), trường `reason`/`rejection_reason` trên grants/delegations/offboarding và `Scorecard_Reviews.employee_rebuttal_note` (`ADR-007`) |
| **`M20.DataIncidentEscalated`** (`severity`, `affected_connection_ids[]`, `affected_actor_ids[]`) | Khi sự cố rò rỉ tài khoản (`S1/S2`), tự động gọi luồng khóa khẩn cấp `SuspendUser` / `RevokeAccess` cho `affected_actor_ids[]`, ghi `Security_Revocation_Ledger` và bump `permission_version` (`M20-F08`) |
| **`M22` HR Events** (`hr.employment.changed.v1`, `hr.availability.changed.v1`, `hr.offboarding.effective.v1`) | Tiêu thụ có idempotency + sắp xếp thứ tự theo `(effective_at, aggregate_version)` (xử lý event đến lệch thứ tự từ `M22`); `hr.employment.changed.v1` cập nhật `Departments`/`Branch` hiển thị **không tự mở quyền dữ liệu** (`INV-02`, `H-T04`); `hr.availability.changed.v1` ghi nhận **`gross_available_hours_after_hr_leave` & `availability_status`** vào `Capacity_Cost_Snapshots` (không chứa lý do nghỉ phép/lương); `hr.offboarding.effective.v1` kích hoạt `InitiateOffboardingOrTransfer` (`M22-F22`) |
| **`M23` Ops Events** (`M23.BreakGlassApproved`, `M23.BreakGlassRevoked`, `M23.TenantOperatingModeChanged`) | `ApplyBreakGlassGrant` / `RevokeBreakGlassGrant` vào `M14.Break_Glass_Grants` và bump `permission_version`; `SetTenantOperatingMode` cập nhật `M14.Tenants.operating_mode` (`SOLO_PILOT <-> TEAM`, gắn cờ `self_approved_in_pilot_mode` khi nâng lên `TEAM`, `ADR-003`) |
| **`M16` & `M18` Scorecard Events** (`M16.DeliverableRevisionBatchOpened`, `M16.ClientWaitIntervalRecorded`, `M18` KPI Facts) | `M14-F08` tiêu thụ idempotent theo `event_id` cập nhật `Scorecard_Reviews.context_metrics` (`defect_vs_change_request`, `client_wait_intervals`, `project_mix`) và dấu mốc `last_computed_at` (chỉ hiển thị khi `ENABLE_M14_SCORECARD_P2 = true`) |

---

## 4. Compatibility, Privacy & Test Matrix (`MODULE-SPEC` Aligned)

| Test ID | Mục tiêu Kiểm chứng Hợp đồng `C14` | Severity | Applicability | Status | Actual / Build / Fixture |
|---|---|---|---|---|---|
| `M14-AC01` / `INT29` | Xung đột Role/Entity `ALLOW` vs `DENY` & lọc `PERSONAL` trong `Entity-Mapped CompileScopeFilter` (`OR branch` bị bỏ) | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-ACL-01` |
| `U16` / `SEC-U03` | Token / URL `Download Gateway` (`GET/Range`) mang `expected_permission_version` cũ bị `401/403 Fail-Closed`; rollback `client_version > db_version` trả `401` | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-GW-01` |
| `INT23` / `CEO-U18` | Worker `M19` / Bulk `M24-F03` / Export `M24-F08` mang `expected_permission_version` cũ bị `409 AUTH_PERMISSION_VERSION_STALE` | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-VER-01` |
| `M20-LEGAL-HOLD-ACL` | Nhận `M20.LegalHoldChanged` cập nhật `active_legal_hold_ids[]` & bật `RESTRICTED_LEGAL_HOLD`, chặn Sales/CSKH qua cả `EvaluateAccessDecision` & `CompileScopeFilter` | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-LH-01` |
| `U17` / `CX-U01` / `RV10` / `RV15` | Cô lập Cross-Workspace, `Account -> Child`, bridge `Contract_Workspace_Grants`, 6 GUC `SET LOCAL` trên PG pool lỗi/rollback, khóa `CLIENT` đọc `Nhóm B-Governance-Sensitive` (`OC03`) | `P0 Critical` | `SL00+` | `Not Run` | `Not Run / No Repo / Fixture-RLS-01` |
| `H-T04` / `P-T02..36` | Điều chuyển `M22` không tự mở quyền cũ/mới; `Users` Membership RLS chặn `PORTAL_CLIENT`; `PORTAL_CLIENT` Write Port kiểm `actor_id == portal_principal_id` | `P0 Critical` | `SL04/08/09+` | `Not Run` | `Not Run / No Repo / Fixture-XM-01` |
| `C14-W15-01` | Bootstrap Port `ResolveConnectionScopeByWebhookEndpoint` (`M19` Webhook) & `Entity-Mapped CompileScopeFilter` đọc đúng `Tasks.visibility`/`Task_Participants`/tách nhánh Bridge | `P0 Blocker` | `SL00/02+` | `Not Run` | `Not Run / No Repo / Fixture-W15-01` |
| `C14-W15-02` | Runtime check `Role_Bindings.valid_from/until`, `Break_Glass` `branch_id` + `hr_payroll_explicitly_approved`, `CancelScheduledOffboarding` (`SCHEDULED -> CANCELLED`), `M14-F07` `gross_available_hours_after_hr_leave` | `P0 Critical` | `SL00/04+` | `Not Run` | `Not Run / No Repo / Fixture-W15-02` |
| `C14-W15-03` | `M20.SubjectErasureExecuted` (`erased_subject_refs[]`) & `M16.DeliverableRevisionBatchOpened` / `ClientWaitIntervalRecorded` cập nhật `Scorecard_Reviews.last_computed_at` | `P0 Critical` | `SL04/07+` | `Not Run` | `Not Run / No Repo / Fixture-W15-03` |
