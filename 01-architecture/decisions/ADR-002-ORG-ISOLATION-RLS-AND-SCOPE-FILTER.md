# ADR-002 — Mô hình Cô lập 4 Trục, PostgreSQL RLS (`SET LOCAL`), Định danh `Principals` và Entity-Mapped `CompileScopeFilter`

**Status:** `Approved (Wave 1.5 Hardening — CR-20261116-WAVE1-5-HARDENING)`  
**Phạm vi:** `M14` (`C14`), `M19` (`Webhook Bootstrap`), `M20` (`RESTRICTED_LEGAL_HOLD`, `Nhóm B-Governance-Sensitive`), `M23` (`Break_Glass`), `M16` (`PORTAL_CLIENT`), và mọi domain module (`M01–M24`)  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`5.1`, `5.14`, `6.1`, `NFR07`, `W-O04`, `CX-U01`, `RV10`, `RV15`, `OC03`, `CEO-U03`, `CEO-U17`), [INVARIANTS.md](../INVARIANTS.md) (`INV-01`, `INV-02`, `INV-13`), [ADR-004](ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-007](ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-009](ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md)

---

## Context

1. Đợt rà soát Luồng A phát hiện AST ban đầu của `CompileScopeFilter` dùng `OR branch_id IN :allowed_branch_ids` vô điều kiện — cho phép mọi user cùng chi nhánh đọc `PERSONAL` task (vi phạm `W-O04`, `INV-02`) hoặc vượt `Account` deny (`6.1 L3108`), đồng thời bỏ sót `Role_Bindings.effect = 'DENY'`, `Break-Glass`, `RESTRICTED_LEGAL_HOLD` và `Account -> Child`.
2. Đợt re-audit Wave 1 tiếp tục chỉ ra **7 lỗ hổng kiến trúc mới cần vá dứt điểm trong Wave 1.5 (`CR-20261116-WAVE1-5-HARDENING`)**:
   - `predicate_ast` trong `C14` hardcode **5 cột ma** (`visibility_scope`, `owner_id`, `account_id`, `sensitivity_level`, `legal_hold_status`) không tồn tại đồng nhất trên mọi bảng (ví dụ `M16.Tasks` dùng `visibility`, `Task_Participants`, `reviewer_id`, `assignee_user_id/requester_id`, `active_legal_hold_ids uuid[]`).
   - Nhánh `(workspace_id = :ws OR verified_bridge_keys)` kết hợp với `OR scope_mode = 'ALL_WORKSPACE_BY_ROLE'` tạo khe hở **leo thang quyền chéo workspace** cho bản ghi có bridge và chưa chặn `branch_id IS NULL` khi `scope_mode = 'BRANCH_SCOPED_BY_ROLE'`.
   - Cấu trúc `Delegations` và `Break-Glass` trong compiler còn sơ khai (`Break-Glass` khớp theo `resource id` đơn lẻ thay vì `workspace_ids + scope_resource_types[]`).
   - Thiếu rule RLS chuẩn cho `PORTAL_CLIENT` trên `Deliverables`/`Acceptances`/`Contract_Workspace_Grants` + Write Port `SECURITY DEFINER`, thiếu Bootstrap `SECURITY DEFINER` Router cho `M19` Webhook trước khi có tenant GUC, và thiếu cơ chế fan-out từng workspace cho `Offboarding` / `VerifyPostRestoreComplianceGate` mà không dùng `BYPASSRLS`.
   - Bảng `Nhóm B` có `workspace_id IS NULL` có thể rò dữ liệu nhạy cảm (`Privacy_Requests`, `Legal_Holds`, `Data_Incidents`) sang `CLIENT workspace` (`OC03`); bảng `M14.Users` thiếu RLS qua `Memberships`; và cần bảng định danh thống nhất cho `USER`, `SERVICE_PRINCIPAL`, `PORTAL_CLIENT`.

## Đề nghị

1. **Tách rõ 4 trục phạm vi & Chuẩn hóa Bảng Định danh `Principals` (`INV-01`, Master `5.1`):**
   - **4 trục phạm vi:** `tenant_id` (tổ chức gốc), `workspace_id` (`AGENCY` vs `CLIENT`), `branch_id` (đơn vị vận hành, không làm `OR` mở đọc toàn chi nhánh), `legal_entity_id` (pháp nhân ký kết/hạch toán `M08/09/10/22`, `CEO-U10`).
   - **Hệ bảng định danh thống nhất `Principals` (`M14`):**
     - `Principals` (`id`, `tenant_id`, `principal_type IN ('USER', 'SERVICE_PRINCIPAL', 'PORTAL_CLIENT')`, `status`): khóa chuẩn chung cho `Principal_Permission_Versions`, `EvaluateAccessDecision`, `CompileScopeFilter`, `Audit_Logs`.
     - `Users`: tài khoản nhân sự nội bộ gắn `principal_id`; **RLS của `M14.Users` bắt buộc lọc theo `Memberships`** thuộc `(tenant_id, workspace_id)` hiện hành (ngăn thành viên ở một workspace/khách hàng truy vấn chéo danh sách user ngoài membership được cấp).
     - `Service_Principals`: định danh dịch vụ/worker/API key nội bộ có scope hẹp (`M19`, `M21`, `M24`), tách khỏi nhân sự `M22`.
     - `Portal_Clients`: định danh khách hàng ngoài cổng Portal, neo cứng vào `CLIENT workspace` + `Contact` / `Contract_Workspace_Grants` (không có membership tại `AGENCY workspace`).

2. **PostgreSQL `FORCE RLS`, Bộ 6 GUC Canonical, `Nhóm B` Phân tầng & `SECURITY DEFINER` Ports (`RV15`, `INV-13`):**
   - **DB Roles & `FORCE RLS`:** `app_runtime_role` và `worker_runtime_role` không có `SUPERUSER` và không `BYPASSRLS`; `migration_owner_role` tách riêng. Mọi bảng scoped bật `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY`.
   - **Mở rộng `BindDbTransactionContext` lên Bộ 6 GUC Canonical (`SET LOCAL`):**
     - `app.current_tenant_id` (`uuid`)
     - `app.current_workspace_id` (`uuid`, `NULL` chỉ hợp lệ cho giao dịch catalog/governance cấp tenant được khai báo)
     - `app.current_workspace_type` (`AGENCY | CLIENT | SYSTEM`)
     - `app.current_principal_id` (`uuid`)
     - `app.current_permission_version` (`bigint`)
     - `app.current_acting_mode` (`DIRECT | DELEGATED | BREAK_GLASS | SYSTEM_WORKER`)
     - Thiếu hoặc rỗng GUC bắt buộc $\rightarrow$ **Fail-Closed** trả 0 dòng hoặc raise exception (`RV15`).
   - **Tách RLS `Nhóm B-Catalog` vs `Nhóm B-Governance-Sensitive` (`OC03`, `ADR-004`):**
     - `Nhóm B-Catalog` (`System_Calendars`, `Shared_Dictionaries`, mẫu công khai): cho phép `workspace_id IS NULL` đọc chung trong `tenant_id` ở cả `AGENCY` và `CLIENT`.
     - `Nhóm B-Governance-Sensitive` (`Privacy_Requests`, `Legal_Holds`, `Data_Incidents`, `Retention_Policies`, `Legal_Deadline_Policies`, `Vendor_Data_Flows`, `Policy_Definitions/Versions`, `Break_Glass_Requests`, `Approval_Matrix_Rules`): chính sách RLS **bắt buộc kiểm `current_setting('app.current_workspace_type', true) IN ('AGENCY', 'SYSTEM')`**, chặn cứng `CLIENT` workspace đọc các bản ghi `workspace_id IS NULL` (`OC03`).
   - **RLS 2 chiều cho `PORTAL_CLIENT` & Write Port `SECURITY DEFINER` (`ADR-009`, `CEO-U03/U17`):**
     - Policy `SELECT` cho `PORTAL_CLIENT` trên `Deliverables`: chỉ mở khi **`published_to_client_workspace_id = nullif(current_setting('app.current_workspace_id', true), '')::uuid AND status IN ('CLIENT_REVIEW', 'REWORK', 'ACCEPTED')`**, **HỘI (`AND`) với RLS 2 chiều trên `Contract_Workspace_Grants`** (grant đang `ACTIVE`, `revoked_at IS NULL`, `now() BETWEEN valid_from AND coalesce(valid_until, 'infinity')`, khớp cặp `agency_workspace_id <-> client_workspace_id`).
     - Mọi thao tác ghi từ phía khách hàng (`RecordClientAcceptance`, gửi phản hồi `REWORK`) không được cấp quyền `INSERT/UPDATE` trực tiếp lên bảng `AGENCY`, mà phải đi qua **Write Port `SECURITY DEFINER`** tối thiểu có kiểm cứng **`actor_id == app.current_principal_id (portal_principal_id)`**, kiểm khớp `authorized_client_approvers[]`, `Contract_Workspace_Grants`, `asset_version_id` và `expected_version`.
   - **Bootstrap `SECURITY DEFINER` Router cho `M19` Webhook (`INV-07`):**
     - Request webhook đến từ bên ngoài chưa có session GUC được tiếp nhận qua hàm `SECURITY DEFINER` chỉ-đọc tối thiểu tra cứu duy nhất theo bộ ba **`(provider, provider_namespace, webhook_endpoint_token [string | null])`** trên `Channel_Connections` để xác định đủ **`(connection_id, tenant_id, workspace_id, workspace_type, connection_status, acting_principal_id, permission_version)`**. Ngay sau bước router này, hệ thống gọi `BindDbTransactionContext` gắn đủ 6 GUC + `correlation_id` trước khi ghi `Inbound_Events` dưới `app_runtime_role`/`worker_runtime_role`.
   - **Fan-out từng Workspace cho Tác vụ Xuyên Workspace (`M14-F06` Offboarding & `M20.VerifyPostRestoreComplianceGate`):**
     - Các tác vụ hệ thống cần xử lý dữ liệu nhiều workspace **cấm dùng `BYPASSRLS`**; thay vào đó thực thi theo mô hình **Fan-out từng `(tenant_id, workspace_id)`**, mở transaction riêng cho từng workspace và gọi `BindDbTransactionContext(acting_mode = 'SYSTEM_WORKER')` để `FORCE RLS` bảo vệ cô lập ở mọi truy vấn.

3. **Entity-Mapped SQL Compiler (`CompileScopeFilter` — `RBAC + ABAC + Deny-Wins + Multi-Hold`):**
   - Thay cho `predicate_ast` hardcode 5 cột ma, `CompileScopeFilter` hoạt động như **Entity-Mapped SQL Compiler**: đọc cấu hình ánh xạ thực tế `Entity_Scope_Metadata[resource_type]` cho từng thực thể:
     - `workspace_col`, `branch_col`, `team_col`, `legal_entity_col`, `sensitivity_col`, `allow_tenant_wide_scope`, `is_catalog_entity`
     - `visibility_col` (ví dụ `Tasks.visibility`, nhận chuẩn `PRIVATE | TEAM | PROJECT | EXPLICIT` hoặc `PERSONAL`, hay `NULL` nếu entity không có trạng thái riêng tư)
     - `owner_cols[]` (ví dụ `Tasks`: `[assignee_user_id, requester_id]`; `Projects`: `[project_owner_id]`; `Deals`: `[owner_id]`)
     - `collaborator_spec` (ví dụ `Task_Participants` + `Tasks.reviewer_id`)
     - `account_col` (ví dụ `account_id`, `client_account_id`, hoặc `NULL`)
     - `legal_hold_col` (chuẩn hóa **`active_legal_hold_ids uuid[] DEFAULT '{}'`** thay cho cờ đơn trị — `ADR-004`/`ADR-007`)
   - **Cấu trúc Logic Biên dịch 6 Tầng Hội (`AND`) Đã Vá:**
     1. **Tenant & Legal Entity:** `(tenant_id = :tenant_id)` `AND` `(:enforced_legal_entity_ids IS NULL OR <legal_entity_col> = ANY(:enforced_legal_entity_ids))`
     2. **Workspace, Cross-Workspace Bridge & Nhánh Tenant-Wide `NULL`:**
        - *Nhánh 1 (Nội bộ Workspace hiện tại):*
          `(<workspace_col> = :workspace_id AND (<Positive Grant Envelope: :scope_mode = 'ALL_WORKSPACE_BY_ROLE' OR (:scope_mode = 'BRANCH_SCOPED_BY_ROLE' AND ((<branch_col> IS NOT NULL AND <branch_col> = ANY(:allowed_branch_ids)) OR (<branch_col> IS NULL AND :allow_unbranched_records = true)) AND (<sensitivity_col> IS NULL OR <sensitivity_col> <> 'RESTRICTED')) OR <owner_cols[] matches :principal_id> OR <reviewer_col = :principal_id> OR <collaborator_exists(:principal_id)> OR <Delegation Match> OR <account_col = ANY(:granted_account_ids)> OR id = ANY(:explicit_allow_entity_ids) OR <Break-Glass Match>>))`
        - *`OR` Nhánh 2 (Cross-Workspace Bridge — Hội chặt với `allowed_relations`, tách hẳn khỏi `ALL_WORKSPACE_BY_ROLE`):*
          `(<workspace_col> <> :workspace_id AND CONCAT(:resource_type, ':', id::text) = ANY(:verified_bridge_keys) AND :requested_relation_or_action = ANY(:verified_bridge_allowed_relations))`
        - *`OR` Nhánh 3 (Bản ghi cấp Tenant `workspace_id IS NULL` — chống bẫy SQL `NULL` khi truy vấn `Nhóm B` & `Audit_Logs`):*
          `(<workspace_col> IS NULL AND :allow_tenant_wide_scope = true AND (:is_catalog_entity = true OR :workspace_type IN ('AGENCY', 'SYSTEM')))`
        - *(Xử lý `BRANCH_SCOPED` khi `branch_id IS NULL`: điều kiện `<branch_col> IS NOT NULL AND <branch_col> = ANY(:allowed_branch_ids)` mặc định **Fail-Closed** chặn các bản ghi `branch_id IS NULL` dưới nhánh Role chi nhánh; bản ghi chưa gán chi nhánh chỉ được đọc nếu thuộc `owner_cols[]` / `collaborator` / `explicit_allow_entity_ids` hoặc chính sách `resource_type` bật tường minh quyền đọc unbranched).*
     3. **Visibility Guard (`PERSONAL` / `PRIVATE` / `EXPLICIT`):** `AND (<visibility_col> IS NULL OR <visibility_col> NOT IN ('PERSONAL', 'PRIVATE', 'EXPLICIT') OR (<owner_cols[] matches :principal_id>) OR (<visibility_col> = 'EXPLICIT' AND (<collaborator_exists(:principal_id)> OR id = ANY(:explicit_personal_share_grant_ids))) OR id = ANY(:explicit_personal_share_grant_ids))` (`W-O04`, `INV-02`, `W-T36`).
     4. **`Delegations` Struct Chuẩn hóa:** Khớp theo mảng `active_delegations[]` mang đủ `{ delegator_id, branch_id, specific_resource_ids[], allowed_actions[] }`: chỉ mở khi `<owner_cols[]>` khớp `delegator_id`, khớp `branch_id` (nếu phiếu giới hạn chi nhánh), thuộc `specific_resource_ids[]` (nếu có giới hạn bản ghi cụ thể), và khớp `allowed_actions[]`.
     5. **`Break-Glass` theo `workspace_ids[]`, `<branch_col>`, `scope_resource_types[]`, `specific_resource_ids[]` & Payroll Flag:** Khớp theo `<break_glass_match(:active_break_glass_scopes, :workspace_id, <branch_col>, :resource_type, id)>` kiểm `{ break_glass_grant_id, workspace_ids[], branch_id, scope_resource_types[], specific_resource_ids[], allowed_actions[], hr_payroll_explicitly_approved }` từ `M14.Break_Glass_Grants` (chặn domain lương `M22`/Payroll khi `hr_payroll_explicitly_approved = false`), vẫn không đè `Entity/Legal DENY`.
     6. **Deny-Wins & Multi-Hold Guard (`M20`):** `AND NOT (:has_matching_role_deny_in_scope) AND (id <> ALL(:explicit_deny_entity_grant_ids)) AND (<account_col> IS NULL OR <account_col> <> ALL(:explicit_deny_account_ids)) AND (cardinality(<legal_hold_col>) = 0 OR :principal_has_legal_hold_read_role = true)`.

4. **Chế độ Che lỗi PG Non-Disclosure (`RV15`, `SEC-U02`):**
   - Không lộ `unique violation` / `FK` chứa ID workspace khác hay `count` ngoài phạm vi ra API response (`404 RESOURCE_NOT_FOUND_OR_DENIED` cho truy vấn ID/count cross-workspace hoặc `403`/`409` non-disclosure envelope).

## So sánh

- **Giữ AST hardcode 5 cột ma và gộp `workspace_id = :ws OR bridge` chung với `ALL_WORKSPACE_BY_ROLE`:** Sinh lỗi SQL runtime trên `Tasks`/`Projects`, làm lộ bản ghi của workspace khác khi một user có `ALL_WORKSPACE_BY_ROLE` tại workspace mình, để lọt `branch_id IS NULL` ở chế độ chi nhánh, và mở lỗ hổng đọc dữ liệu `Nhóm B` cấp tenant trên `CLIENT workspace`.
- **Entity-Mapped Compiler + Tách nhánh Bridge + Bộ 6 GUC + `SECURITY DEFINER` Ports tối thiểu:** Khớp 100% schema thực tế từng bảng, giữ `FORCE RLS` không `BYPASSRLS` cho mọi query/fan-out, đồng thời khóa chặt `PORTAL_CLIENT` và `M19` Webhook Bootstrap.

## Hệ quả và điều kiện thay đổi

- Cập nhật toàn bộ schema `BindDbTransactionContextInput/Output` (6 GUC gồm `app.current_workspace_type`), `Entity_Scope_Metadata` / `CompileScopeFilter`, `Delegations` struct, `Break-Glass` struct, `Principals` (`Users`/`Service_Principals`/`Portal_Clients`) trong [M14-PRINCIPAL-ACCESS-DECISION.md](../../02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md) và [M14-ORG-ACCESS-DELEGATION.md](../../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md).
- Đồng bộ `C23`/`C24` và các module `M16`, `M19`, `M20`, `M23` bảo đảm không sử dụng `BYPASSRLS` trong bất kỳ worker hoặc batch job nào.
