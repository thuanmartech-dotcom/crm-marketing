# ADR-004 — Phân định SoT Bảng Nền tảng Dùng chung & 3 Biến thể Kế thừa Cột `Master 5.1`

**Status:** `Approved (Baseline v1.9 Clarification + Logical Schema Standard)`  
**Phạm vi:** Toàn bộ `M01–M24` (`ENTITY-L2787`, `ENTITY-L2860`, `ENTITY-L2885`, `5.1`, `Rule 3 / GAP-04`)  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`3.14.1 L1562`, `5.1 L2489–2507`, `5.18 L2860/2885`, `6.2 L3120`, `A.6 L4212`), [module-workflow.md](../../.agents/skills/crm-ba-spec/references/module-workflow.md)

---

## Context

1. Cả `M14`, `M20`, `M19`, `M22`, `M23` đang chồng chéo quyền sở hữu đối với `Policy_Definitions/Versions` (`ENTITY-L2885`), `Audit_Logs` (`ENTITY-L2787`), `Bank_Accounts` (`O04`, `ENTITY-L2860`), `Departments` (`3.14.1 L1562`).
2. `M14`, `M20`, `M19` áp sai quy ước kế thừa cột `Master 5.1`: tất cả đều bỏ sót `business_line_id` (`L2501`), `M19/M20` bỏ sót `branch_id` và `legal_entity_id`, đồng thời áp nhầm `updated_at/updated_by/row_version/archived_at` lên các bảng `Append-only` (`Audit_Logs`, `Consent_Logs`, `Deletion_Ledger`, `Message_Status_Events`), hoặc ép `workspace_id NOT NULL` cho catalog/policy cấp Tenant (trái `Master 5.1 L2491`).
3. `M14` `4.2` vẫn gộp 2 cặp bảng vào 1 dòng (`Brands & Business_Units`, `Policy_Definitions & Policy_Versions`) trái `Rule 3 / GAP-04`, và quên khai báo bảng `Scorecard_Reviews` (`M14-F08`).

## Đề nghị

1. **Khóa phân quyền SSoT cho các bảng nền tảng & giao thoa (Chốt theo `/grill-me` Bước 4):**
   - **`Policy_Definitions` & `Policy_Versions` (`ENTITY-L2885`) — Tách khung Governance khỏi Domain Tables:**
     - **`M23` (Platform Governance Engine)** sở hữu chuẩn hóa lõi `Policy_Definitions` & `Policy_Versions` (máy trạng thái `DRAFT -> REVIEWED -> ACTIVE -> SUPERSEDED`, `owner_role_id`, `effective_from`, Maker-Checker, lịch sử phiên bản `INV-14`) và bảng `Approval_Matrix_Rules` / `Auth_Session_Policies` / `Feature_Flag_Configs`.
     - **Từng Domain Module** khai báo bảng tham số có kiểu hóa riêng (*typed tables*) khi có vòng đời/nghiệp vụ đặc thù (ví dụ `M20` giữ `Legal_Deadline_Policies`, `Retention_Policies`; `M22` giữ `HRPolicyVersion`; `M14` tham chiếu `Policy_Versions` của `M23` cho các cờ `O03/O06/O08/GAP-*` thay vì tự sở hữu `ENTITY-L2885`).
   - **`Audit_Logs` (`ENTITY-L2787`):**
     - **Shared Platform Immutable Ledger (`M23-F06` làm chủ quản trị & điều tra):** Cấm `UPDATE/DELETE` ở cấp DB role ứng dụng và Technical Admin (`Master 6.2 L3120`), áp PII redaction chuẩn trước khi ghi; mọi module (`M14`, `M19`, `M20`...) ghi log qua Shared Audit Port (không mỗi module tạo bảng log riêng); `M20` có quyền gắn tham chiếu `Legal_Hold` để chặn purge sớm mà không sửa bảng `Audit_Logs`.
   - **`Bank_Accounts` (`ENTITY-L2860`, `O04`):**
     - Tài khoản ngân hàng của **Pháp nhân (`Legal_Entities`)** phục vụ thu/chi/đối soát công nợ thuộc về **`M09`** (`M14` giữ `Legal_Entities` liên kết logic sang `M09` và giải tỏa ghi chú mồ côi `M09/M22`).
     - Tài khoản nhận lương cá nhân của **`Employees`** thuộc về **`M22`**.
   - **`Departments` (`Master 3.14.1 L1562`) & `Scorecard_Reviews` (`M14-F08`):**
     - Thuộc **`M14`** (`Departments` là thực thể sơ đồ tổ chức tách rời khỏi cây quyền; `Scorecard_Reviews` bổ sung rõ nhãn `[PROPOSED] P2` kèm flag kiểm soát `GAP`).
2. **Chuẩn hóa 3 Biến thể Kế thừa Cột `Master 5.1` (bắt buộc khai báo đúng biến thể ở đầu Mục `4.2` mỗi module):**
   - **Nhóm A — `Scoped Business Entity`:** Đủ `id`, `tenant_id`, `workspace_id NN`, `branch_id NULL` (hoặc `NN` khi phân nhánh), `legal_entity_id NULL` (hoặc `NN` cho hợp đồng/tài chính), `business_line_id NULL`, `created_at`, `updated_at`, `created_by`, `updated_by`, `row_version`, `archived_at`, kèm `UNIQUE (tenant_id, workspace_id, id)` để FK ghép.
   - **Nhóm B — `Tenant Catalog / Governance Entity`:** Áp ngoại lệ `Master 5.1 L2491`: có `id`, `tenant_id`, `branch_id NULL`, `legal_entity_id NULL`, `business_line_id NULL`, `workspace_id NULL` *(chỉ giữ nếu cho phép override theo workspace, không ép `NN`)*, `created_at`, `updated_at`, `created_by`, `updated_by`, `row_version`, `archived_at`, kèm `UNIQUE (tenant_id, id)`.
   - **Nhóm C — `Append-Only Immutable Ledger / Event` (`Audit_Logs`, `Consent_Logs`, `Deletion_Ledger`, `Message_Status_Events`, `Email_Delivery_Events`, `Send_Attempts`, `Remote_Fetch_Logs`):** Có `id`, `tenant_id`, `workspace_id` (`NN` hoặc `NULL` tùy scope), `branch_id NULL`, `legal_entity_id NULL`, `business_line_id NULL`, `created_at`, `created_by`, `occurred_at`, `received_at`, `correlation_id` — **tuyệt đối KHÔNG có `updated_at`, `updated_by`, `row_version`, `archived_at`** và cấm `UPDATE/DELETE` dưới app role (sửa sai chỉ ghi bản ghi bù trừ qua `supersedes_id`).
3. **Siết `Rule 3 / GAP-04`:** Mọi bảng trong Mục `4.2` phải đứng **1 bảng = 1 dòng** riêng biệt (`Brands` tách khỏi `Business_Units`, `Policy_Definitions` tách khỏi `Policy_Versions`).

## So sánh

- **Dùng 1 mẫu `5.1` cứng cho mọi bảng:** Gây sai sót liên hoàn (`Audit_Logs` có `row_version` và `updated_at`, `Consent_Logs` có `archived_at`, policy cấp tenant bị ép `workspace_id NOT NULL`). Chia 3 biến thể giữ nguyên 100% trường bắt buộc của Master `5.1` đồng thời đảm bảo tính bất biến của các bảng Ledger.

## Hệ quả và điều kiện thay đổi

- `M14`, `M20`, `M19` cập nhật Mục `4.2` phân rõ Bảng Nhóm A / Nhóm B / Nhóm C, bổ sung `business_line_id`, `branch_id`, `legal_entity_id` đầy đủ và gỡ gộp dòng.
- `M23` bổ sung `Policy_Definitions`, `Policy_Versions`, `Audit_Logs` vào phần Entities sở hữu nền tảng (dùng chung toàn hệ thống).
