# ADR-002 — Mô hình Cô lập 4 Trục, PostgreSQL RLS `SET LOCAL` và AST `CompileScopeFilter`

**Status:** `Approved (Proposed Extension trong Baseline v1.9 — Logical PG/Modular Monolith Architecture)`  
**Phạm vi:** `M14` (`C14`), `M20` (`RESTRICTED_LEGAL_HOLD`), và mọi domain module (`M01–M24`)  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`5.1`, `5.14`, `6.1`, `NFR07`, `W-O04`, `CX-U01`, `RV10`, `RV15`), [INVARIANTS.md](../INVARIANTS.md) (`INV-01`, `INV-02`, `INV-13`)

---

## Context

1. Đợt rà soát Luồng A phát hiện AST của `CompileScopeFilter` trong [M14-PRINCIPAL-ACCESS-DECISION.md](../../02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md) sử dụng `OR branch_id IN :allowed_branch_ids` vô điều kiện — cho phép mọi user cùng chi nhánh đọc `PERSONAL` task (vi phạm `W-O04`, `INV-02`), hồ sơ riêng tư, hoặc vượt `Account` deny (vi phạm Master `6.1 L3108`).
2. AST cũ bỏ sót `Role_Bindings.effect = 'DENY'`, `Break-Glass`, `RESTRICTED_LEGAL_HOLD` (`M20`), kiểm `resource_type`/`allowed_relations` trên `bridged_resource_ids`, và quan hệ `Account -> Child` (`CX-U01`).
3. Hợp đồng `C14` tự mâu thuẫn tên biến phiên PostgreSQL (`app.permission_version` vs `app.current_permission_version`) và thiếu schema `BindDbTransactionContextInput` + `CompiledScopeFilterOutput`.

## Đề nghị

1. **Tách rõ 4 trục phạm vi (`INV-01`, Master `5.1`):**
   - `tenant_id`: ranh giới tổ chức gốc (bắt buộc mọi query/command).
   - `workspace_id` (`AGENCY` vs `CLIENT`): ranh giới cách ly dữ liệu tác nghiệp và PII.
   - `branch_id`: ranh giới đơn vị vận hành (dùng kết hợp với Role/Team/Grant, **tuyệt đối không** dùng làm nhánh `OR` mở đọc toàn chi nhánh).
   - `legal_entity_id`: ranh giới pháp nhân ký kết/hạch toán (`M08`, `M09`, `M10`, `CEO-U10`).
2. **Thống nhất `BindDbTransactionContext` & tên biến PostgreSQL `SET LOCAL` (`RV15`, `INV-13`):**
   - App/Worker DB role (`app_runtime_role`) không có `SUPERUSER` và không `BYPASSRLS`; migration role tách riêng.
   - Mọi transaction trên connection pool bắt buộc gọi `BindDbTransactionContext` ở đầu transaction (`BEGIN; SELECT set_config(...)` tương đương `SET LOCAL`) với **bộ 5 GUC canonical thống nhất**:
     - `app.current_tenant_id` (`uuid`)
     - `app.current_workspace_id` (`uuid`, NULL nếu là tác vụ tenant-catalog hợp lệ được khai báo)
     - `app.current_principal_id` (`uuid`)
     - `app.current_permission_version` (`bigint`)
     - `app.current_acting_mode` (`DIRECT | DELEGATED | BREAK_GLASS | SYSTEM_WORKER`)
   - Mọi bảng scoped bật `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY`; policy đọc `nullif(current_setting('app.current_tenant_id', true), '')::uuid` — **thiếu context lập tức `Fail-Closed` trả 0 dòng hoặc raise exception** (`RV15`).
3. **Chuẩn hóa AST `CompileScopeFilter` (`RBAC + ABAC + Deny-Wins + Hold`):**
   - Biểu thức lọc bắt buộc tuân theo thứ tự hội (`AND`) không vượt quyền:
     1. **Tenant & Workspace & Cross-Bridge:** `(tenant_id = :tenant_id) AND (workspace_id = :workspace_id OR (resource_scope_key IN :verified_bridge_keys_for_resource_type))`
     2. **Legal Entity (khi domain yêu cầu `M08/09/10`):** `AND (:enforced_legal_entity_ids IS NULL OR legal_entity_id = ANY(:enforced_legal_entity_ids))`
     3. **Visibility Guard (`PERSONAL` / Private Lock):** `AND (visibility_scope <> 'PERSONAL' OR owner_id = :principal_id OR id = ANY(:explicit_personal_share_grant_ids))` (`W-O04`, `INV-02`)
     4. **Positive Grant Envelope (bắt buộc thỏa RBAC cho phép `resource_type + action` VÀ ít nhất 1 phạm vi dữ liệu hợp lệ):**
        `AND (scope_mode = 'ALL_WORKSPACE_BY_ROLE' OR (scope_mode = 'BRANCH_SCOPED_BY_ROLE' AND branch_id = ANY(:allowed_branch_ids) AND sensitivity_level <> 'RESTRICTED') OR owner_id = :principal_id OR owner_id = ANY(:active_delegator_ids_for_resource_type) OR account_id = ANY(:granted_account_ids_for_resource_type) OR id = ANY(:explicit_allow_entity_grant_ids) OR id = ANY(:active_break_glass_grant_ids))`
        *(trong đó `scope_mode` chỉ mở `ALL_WORKSPACE_BY_ROLE` / `BRANCH_SCOPED_BY_ROLE` khi Role thực sự có `data_scope = WORKSPACE | BRANCH`, không bao giờ tự mở cho `OWN_ONLY` hay dữ liệu `PERSONAL`)*
     5. **Deny-Wins tuyệt đối (`Role DENY` + `Entity DENY`):** `AND NOT (:has_matching_role_deny_in_scope) AND (id <> ALL(:explicit_deny_entity_grant_ids)) AND (account_id IS NULL OR account_id <> ALL(:explicit_deny_account_ids))` (`INT29`, `CX-U01`)
     6. **Legal Hold Restriction Guard (`M20`):** `AND (legal_hold_status <> 'RESTRICTED_LEGAL_HOLD' OR :principal_has_legal_hold_read_role = true)`
4. **Chế độ che lỗi PG (`RV15`, `SEC-U02`):** Không lộ lỗi `unique violation` / `FK` chứa ID workspace khác ra API response (`403`/`404`/`409` non-disclosure envelope).

## So sánh

- **Giữ AST `OR branch_id` đơn giản:** Lộ ngay `PERSONAL` task và dữ liệu nhạy cảm cùng chi nhánh, vi phạm `W-O04` & `INV-02`.
- **Áp dụng AST hội 6 tầng chuẩn hóa:** Kiểm soát chặt mọi chiều (`Tenant/Workspace/LegalEntity/Branch/Personal/Deny/Hold`) mà vẫn biên dịch thành tham số SQL chuẩn trên PostgreSQL `>= 15`.

## Hệ quả và điều kiện thay đổi

- Cập nhật toàn bộ schema `BindDbTransactionContextInput`, `CompileScopeFilterInput`, `CompiledScopeFilterOutput` và 6 bước `EvaluateAccessDecision` trong [M14-PRINCIPAL-ACCESS-DECISION.md](../../02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md).
- Mọi module Wave 1–6 (`M16`, `M01–M13`, `M21`, `M22`) phải khai báo `data_scope` trên `Roles`, tách `visibility_scope` (`PERSONAL | TEAM | WORKSPACE`), và đánh dấu cột `legal_hold_status` nếu chịu chi phối của `M20-F06`.
