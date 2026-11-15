# Contract: M14-PRINCIPAL-ACCESS-DECISION — Kiểm tra Quyền Thực thi, Biên dịch Scope & Phát Sự kiện Thu hồi

- **Contract ID / Version:** `M14-PRINCIPAL-ACCESS-DECISION` / `v1.0` (`[PROPOSED]` trên nền `[MASTER]` Mục `3.8.2`, `5.1`, `6.1`, `6.2`, `6.5`, `6.6`, `6.7`, `6.8`).
- **Baseline:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`).
- **Provider Owner:** [M14 — Tổ chức, Nhóm, Quyền & Bàn giao](../modules/M14-ORG-ACCESS-DELEGATION.md).
- **Consumers:** Toàn bộ `M01–M24` (API Gateway, Domain Command Handlers, Search/Count Indexer, Download Gateway `SEC03`, Background Workers `M19/M24`, AI Data Gateway `M06`, BI Engine `M18`).
- **Source Requirements:** `FR21`, `FR08`, `FR35`, `FR37`, `M14-F01..06`, `M14-AC01..03`, `UC12`, `UC14`, `SEC03`, `SEC06`, `SEC-U03`, `SEC-U06`, `U16`, `U17`, `INT23`, `INT29`, `RV10`, `RV15`, `CEO-U17`, `CEO-U18`, `OC20`.
- **Status:** `Reviewed` (Đã chốt kiến trúc Dual-Mode qua `/grill-me` ngày `15/11/2026`; test ứng dụng `Not Run`).
- **Breaking-Change Policy:** Mọi thay đổi trên cấu trúc `AccessDecisionOutput`, thứ tự ưu tiên `Deny-wins`, hoặc payload sự kiện `M14.PermissionVersionBumped` bắt buộc tăng `major_version`, giữ dual-reader tối thiểu 1 release và chạy lại bộ kiểm thử cách ly `U16`, `U17`, `INT23`, `INT29`, `RV15`.

---

## 1. Bảng 12 Thành phần Hợp đồng (`12 Required Contract Parts`)

| Phần | Nội dung đặc tả chi tiết |
|---|---|
| **Meaning** | `[MASTER]` + `[PROPOSED]` Hợp đồng cổng kiểm tra quyền thực thi duy nhất (*Single Source of Truth* — `INV-23`) của toàn hệ thống CRM, gồm **2 giao diện đồng bộ** (`EvaluateAccessDecision` cho lệnh/tài nguyên đơn lẻ/Download Gateway/Worker Job và `CompileScopeFilter` đẩy biểu thức lọc phạm vi + `SET LOCAL` xuống PostgreSQL cho truy vấn danh sách/đếm/tìm kiếm/AI RAG) cùng **4 Domain Events** phát qua Outbox khi thay đổi phiên bản quyền hoặc trạng thái bàn giao nhân sự. |
| **Actor/scope** | `[MASTER]` Tác nhân gọi gồm: `Authenticated User Principal`, `Service Principal / Background Worker`, `Download Gateway`, `Customer Portal Principal`. **`tenant_id` bắt buộc suy xuất từ phiên xác thực phía server (`server-verified session`)**, tuyệt đối không tin `tenant_id` hoặc `actor_id` truyền tự do từ request body (`ENTITY-L2762`, `INV-01`, `INV-13`). |
| **Preconditions** | `[MASTER]` (1) Phiên đăng nhập còn hiệu lực (`Users.status = 'ACTIVE'`, không ở trạng thái `SUSPENDED / OFFBOARDING_LOCKED / OFFBOARDED`); (2) Có đầy đủ ngữ cảnh `tenant_id` và `workspace_id` hợp lệ (`INV-13`: thiếu context phải `fail-closed`); (3) Nếu gọi từ Background Worker hoặc Download Gateway, bắt buộc truyền `principal_id` hiện hành để kiểm tra lại quyền tại thời điểm thực thi (`CEO-U18`, `SEC03`). |
| **Input** | `[PROPOSED]` Xem chi tiết Schema đầu vào của `EvaluateAccessDecisionInput`, `CompileScopeFilterInput` và `BindDbTransactionContextInput` tại Mục 2 bên dưới. |
| **Output** | `[PROPOSED]` Xem chi tiết Schema đầu ra `AccessDecisionOutput` (gồm `decision: ALLOW \| DENY`, `effective_permission_version`, `allowed_fields[]`, `masked_fields[]`, `acting_mode: DIRECT \| DELEGATED \| BREAK_GLASS`, `audit_metadata`) và `CompiledScopeFilterOutput` tại Mục 2 bên dưới. Không bao giờ trả raw DB row hoặc lộ thông tin tài nguyên ngoài quyền. |
| **Errors** | `[MASTER]` + `[PROPOSED]` Chuẩn hóa mã lỗi: `AUTH_MISSING_SCOPE_CONTEXT` (`400/403` — thiếu tenant/workspace, fail-closed), `AUTH_SESSION_REVOKED_OR_OFFBOARDED` (`401` — user đã bị khóa/offboard `U16`), `AUTH_PERMISSION_VERSION_STALE` (`409` — worker/cache cầm `permission_version` cũ), `AUTH_ACCESS_DENIED` (`403` hoặc `404` non-disclosure tùy chính sách từng endpoint để chống dò ID qua workspace khác `U17`, `SEC-U02`). Tuyệt đối không trả raw SQL/FK detail ra client. |
| **Concurrency** | `[MASTER]` Mọi lệnh ghi làm thay đổi quyền (`Grant`, `Revoke`, `Delegate`, `Offboard`) sử dụng khóa lạc quan `expected_version = row_version` (`INV-09`) kết hợp tăng nguyên tử `Principal_Permission_Versions.permission_version = permission_version + 1` trong cùng DB transaction. Khi 2 lệnh cùng sửa 1 grant/user, lệnh đến sau nhận `409 CONFLICT_VERSION`. |
| **Idempotency** | `[MASTER]` + `[PROPOSED]` Các hàm đọc (`EvaluateAccessDecision`, `CompileScopeFilter`) là thuần túy không tạo side-effect (trừ ghi `Access_Deny_Audit` bất đồng bộ khi phát hiện truy cập trái phép hoặc dò ID). Các Domain Events phát ra (`M14.PermissionVersionBumped`, `M14.WorkHandoverAssigned`) đính kèm `event_id` và `(principal_id, permission_version)` tăng đơn điệu để Consumer (`M24-F06`, `M16`, `M03`) xử lý idempotent, bỏ qua sự kiện có version nhỏ hơn version đã áp dụng. |
| **Transaction** | `[MASTER]` (1) **Đường đọc DB (`6.1`):** Mọi kết nối từ connection pool PostgreSQL phải mở `BEGIN` transaction tường minh, gọi `SET LOCAL app.current_tenant_id = ...`, `SET LOCAL app.current_workspace_id = ...`, `SET LOCAL app.current_principal_id = ...`, `SET LOCAL app.permission_version = ...` trước khi chạy query nghiệp vụ; kết thúc transaction tự động xóa context, chống rò rỉ giữa 2 tenant trên cùng pooled connection (`RV15`). (2) **Đường ghi quyền:** Ghi bảng quyền + `Audit_Logs` + tăng `permission_version` + ghi `Outbox` nguyên tử trong 1 transaction (`INV-06`). |
| **Compatibility** | `[PROPOSED]` Hỗ trợ song song chế độ vận hành `SOLO/PILOT` (1 người kiêm nhiệm có cờ audit tường minh) và `TEAM` (`Maker != Checker` bắt buộc cho cấp quyền nhạy cảm/Finance/Privacy/Break-glass theo `INV-22`, `M14-AC02`). Khi nâng cấp từ `SOLO/PILOT` lên `TEAM`, các grant hiện hữu giữ nguyên nhưng mọi lệnh tự cấp/tự gia hạn mới bị chặn ngay lập tức. |
| **Audit/privacy** | `[MASTER]` Mọi quyết định cấp/thu hồi quyền, truy cập qua `Break-glass` (`M23-F03`), hoặc thao tác thay mặt qua `Delegation` (`M14-F05`) bắt buộc ghi nhận đầy đủ `actor_id`, `delegated_from_id` (nếu có), `grant_id`, `correlation_id`, `reason` vào `Audit_Logs` (đã redact PII). Khi trả lỗi `DENY` cho client hoặc AI (`OC20`), ẩn hoàn toàn sự tồn tại, số lượng (`count`) và đoạn trích (`snippet`) của bản ghi thuộc workspace/chi nhánh khác (`U17`, `CX-U01`). |
| **Tests** | `[MASTER]` Provider & Consumer test fixtures: `M14-AC01`, `M14-AC02`, `M14-AC03`, `SEC-U03`, `SEC-U06`, `U16`, `U17`, `INT23`, `INT29`, `RV10`, `RV15`, `CEO-U03`, `CEO-U10`, `CEO-U15`, `CEO-U17`, `CEO-U18`, `CX-U01`, `CX-U21`, `OC18`, `OC20`. Trạng thái thực thi hiện tại: `Not Run`. |

---

## 2. Đặc tả Schema Giao diện (`Runtime Schemas`)

### 2.1. Giao diện 1: `EvaluateAccessDecision` (Kiểm tra đơn lẻ / Command / Download Gateway / Worker Job)

**Input Schema (`EvaluateAccessDecisionInput`):**

```json
{
  "tenant_id": "uuid (required, server-derived)",
  "workspace_id": "uuid (required for scoped resources)",
  "branch_id": "uuid | null",
  "legal_entity_id": "uuid | null",
  "principal_id": "uuid (required)",
  "principal_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
  "expected_permission_version": "bigint | null (required for cached/worker execution)",
  "resource_type": "CONTACT | ACCOUNT | LEAD | DEAL | CONVERSATION | MESSAGE | ATTACHMENT | QUOTE | CONTRACT | PAYMENT | COMMISSION | TICKET | PROJECT | DELIVERABLE | TASK | CAMPAIGN | BUDGET | REPORT | EMPLOYEE | PAYROLL",
  "resource_id": "uuid | null (null for create/collection action)",
  "resource_owner_id": "uuid | null",
  "action": "CREATE | READ | UPDATE | ARCHIVE | DELETE_PRIVACY | APPROVE | EXPORT | IMPORT | SHARE_GRANT | DELEGATE | DOWNLOAD_FILE | AI_RETRIEVE",
  "requested_fields": ["string"],
  "request_context": {
    "correlation_id": "uuid",
    "channel": "WEB_API | WORKER_JOB | DOWNLOAD_GATEWAY | AI_COPILOT | PORTAL",
    "is_range_resume": "boolean (for SEC03 / U16 download gateway)"
  }
}
```

**Thứ tự Ưu tiên Đánh giá Cứng (`Deterministic Evaluation Order — Deny-Wins`):**
1. **`Step 1 — Context & Principal Status Guard` (`INV-01`, `INV-13`, `U16`):**
   - Nếu thiếu `tenant_id` hoặc (`resource_type` là dữ liệu scoped mà thiếu `workspace_id`) $\rightarrow$ trả về `DENY (AUTH_MISSING_SCOPE_CONTEXT)`.
   - Nếu `Users.status != 'ACTIVE'` (đang `INVITED`, `SUSPENDED`, `OFFBOARDING_LOCKED`, `OFFBOARDED`) $\rightarrow$ trả về `DENY (AUTH_SESSION_REVOKED_OR_OFFBOARDED)`.
   - Nếu `expected_permission_version` khác `Principal_Permission_Versions.permission_version` hiện tại $\rightarrow$ bắt buộc nạp lại quyền từ DB gốc (không dùng cache `INV-25`).
2. **`Step 2 — Cross-Tenant & Cross-Workspace Isolation Guard` (`U17`, `RV10`):**
   - Nếu tài nguyên thuộc `tenant_id` khác hoặc `workspace_id` khác mà không có cầu nối hợp lệ còn hiệu lực trong `Workspace_Account_Links` / `Contract_Workspace_Grants` / `Entity_Team_Grants` $\rightarrow$ trả về `DENY (NON_DISCLOSURE_NOT_FOUND)`.
3. **`Step 3 — Explicit Deny Policy Check` (`M14-AC01`, `INT29`):**
   - Kiểm tra mọi `Role_Bindings` và `Entity_Team_Grants` đang hiệu lực (`valid_from <= now() < valid_until` và `revoked_at IS NULL`). Nếu có bất kỳ quy tắc `effect = 'DENY'` nào khớp với `(resource_type, resource_id, action)` hoặc trường dữ liệu $\rightarrow$ **lập tức trả về `DENY` (Quyền Deny luôn thắng Allow)**.
4. **`Step 4 — Specific Grant / Delegation / Break-Glass Evaluation`:**
   - Kiểm tra lần lượt:
     - **4a. `Break-Glass Grant` (`M23-F03` ghi vào `M14`):** Còn trong `ttl_expires_at`, khớp đúng `target_workspace_id` và `incident_ticket_id` (mặc định không mở bảng lương `M22` hoặc ví tài chính trừ khi được chỉ định tường minh).
     - **4b. `Entity_Team_Grants` (`M14-F03`):** Khớp đúng `resource_type`, `resource_id`, `action` và danh sách `allowed_fields` (Grant trên `Account` không tự động mở dữ liệu tài chính agency hay toàn bộ `CLIENT workspace` — `M14-F03`).
     - **4c. `Delegations` (`M14-F05` — Act-On-Behalf):** Nếu `resource_owner_id = delegator_id` và `principal_id = delegatee_id`, kiểm tra bản ghi `Delegations` đang `ACTIVE` (`valid_from <= now() < valid_until`), đồng thời xác minh `delegatee_id` có sẵn `Membership` hợp lệ tại `Branch/Workspace` đó và `action` không thuộc nhóm bị cấm ủy nhiệm tự do (`APPROVE` vượt ngưỡng, `SHARE_GRANT`, `FINANCE_POST`, `PRIVACY_DELETE`).
5. **`Step 5 — Baseline Role Binding & Membership Check` (`M14-F02`, `6.1`):**
   - Đối chiếu `Memberships` + `Role_Bindings` tại `(tenant_id, workspace_id, branch_id, legal_entity_id)`.
   - Tách biệt hoàn toàn quyền `UPDATE` và quyền `APPROVE` (`6.1`). Admin kỹ thuật không có quyền `READ/UPDATE` dữ liệu kinh doanh/tài chính/nhân sự mặc định (`M14-AC02`, `SEC-U06`).
6. **`Step 6 — Field-Level Projection & Masking` (`FR08`, `6.2`):**
   - Phân loại các trường trong `requested_fields` thành 3 tập: `allowed_fields` (trả nguyên vẹn), `masked_fields` (che server-side như SĐT `090***123`, email, giá vốn, CCCD), và `forbidden_fields` (loại bỏ hoàn toàn khỏi DTO trả về).

**Output Schema (`AccessDecisionOutput`):**

```json
{
  "decision": "ALLOW | DENY",
  "http_status_recommendation": 200,
  "internal_reason_code": "ALLOWED_BY_ENTITY_GRANT | DENIED_BY_EXPLICIT_RULE | DENIED_CROSS_WORKSPACE | ...",
  "effective_permission_version": 42,
  "acting_mode": "DIRECT | DELEGATED | BREAK_GLASS",
  "audit_context": {
    "actor_id": "uuid",
    "delegated_from_id": "uuid | null",
    "grant_id": "uuid | null",
    "break_glass_id": "uuid | null"
  },
  "field_policy": {
    "allowed_fields": ["id", "name", "status"],
    "masked_fields": [{"field": "phone", "mask_strategy": "PARTIAL_PHONE"}],
    "forbidden_fields": ["internal_cost_rate", "margin_amount"]
  }
}
```

---

### 2.2. Giao diện 2: `CompileScopeFilter` (Cho List / Search / Count / BI / AI RAG)

Để tuân thủ `INV-02`, `U17`, `CX-U01` và `OC20` (không làm lộ số lượng bản ghi `count`, đoạn trích `snippet` hoặc vector AI ngoài phạm vi quyền), mọi truy vấn tập hợp bắt buộc gọi `CompileScopeFilter` **trước khi chạy câu lệnh SQL/Search**:

- **Input (`CompileScopeFilterInput`):** `(tenant_id, workspace_id, principal_id, resource_type, action: READ | EXPORT | AI_RETRIEVE)`.
- **Output (`CompiledScopeFilterOutput`):**
  - `db_session_bindings`: Tập biến bắt buộc gắn vào transaction PostgreSQL qua `SET LOCAL`:
    - `app.current_tenant_id = '<tenant_id>'`
    - `app.current_workspace_id = '<workspace_id>'`
    - `app.current_principal_id = '<principal_id>'`
    - `app.current_permission_version = '<version>'`
  - `predicate_ast`: Biểu thức lọc tổ hợp:
    ```text
    (tenant_id = :tenant_id)
    AND (workspace_id = :workspace_id OR id IN :bridged_resource_ids)
    AND (
      branch_id IN :allowed_branch_ids
      OR owner_id = :principal_id
      OR owner_id IN :active_delegator_ids_for_resource_type
      OR id IN :explicit_allow_entity_grant_ids
    )
    AND (id NOT IN :explicit_deny_entity_grant_ids)
    ```
  - `field_mask_map`: Danh sách trường phải che ngay tại bước serialize DTO trước khi trả kết quả tìm kiếm/đếm/snippet/AI context.

---

## 3. Danh mục Sự kiện Domain Phát qua Outbox (`Published Domain Events`)

| Event Name | Trigger | Payload chính | Consumers bắt buộc xử lý |
|---|---|---|---|
| `M14.PermissionVersionBumped` | Khi `grant`, `revoke`, `expire-grant`, `delegate`, `suspend`, `offboard` hoặc thu hồi `Break-glass` commit thành công | `{ event_id, tenant_id, principal_id, new_permission_version, reason, occurred_at }` | `M24-F06` (xóa cache quyền/read model tức thì), `Download Gateway` (`SEC03`), `M03/M16/M18` |
| `M14.UserOffboardingLocked` | Khi thực thi Pha 1 của `M14-F06` (`UC12`) tại `effective_at` | `{ event_id, tenant_id, offboarding_case_id, user_id, fallback_custodian_map, effective_at }` | `M23-F02` (cắt toàn bộ session), `M02`, `M03`, `M08`, `M11`, `M13`, `M16`, `M19` (tạm giữ/gán Custodian cho open work) |
| `M14.WorkHandoverAssigned` | Khi người nhận bấm `Accept` hoặc `Queue Manager` chốt nhận bàn giao ở Pha 2 (`M14-F06`) | `{ event_id, tenant_id, workspace_id, offboarding_case_id, item_type, item_id, from_user_id, to_user_id, confirmed_at }` | `M02` (Lead/Deal), `M03` (Conversation), `M11` (Ticket), `M13` (Appointment), `M16` (Task/Template/Review) |
| `M14.WorkspaceActivated` | Khi hoàn tất `UC14` mở `CLIENT workspace` hoặc gói ngành mới | `{ event_id, tenant_id, workspace_id, workspace_type, client_account_id, legal_entity_id, activated_by }` | `M18`, `M19`, `M20`, `M21`, `M23` |
