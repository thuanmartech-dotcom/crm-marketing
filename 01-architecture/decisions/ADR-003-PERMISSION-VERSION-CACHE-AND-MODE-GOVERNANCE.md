# ADR-003 — Hợp đồng `permission_version`, Cache Mirror `M24`, Chế độ `SOLO_PILOT <-> TEAM` & `Break-Glass` Runtime

**Status:** `Approved (Proposed Extension trong Baseline v1.9 — Logical PG/Modular Monolith Architecture)`  
**Phạm vi:** `M14` (`C14`), `M19` (`C19`), `M23` (`F02/03/05`), `M24` (`F03/06/08`)  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`6.1`, `6.2`, `SEC03`, `U16`, `CEO-U18`, `INT23`), [INVARIANTS.md](../INVARIANTS.md) (`INV-22`, `INV-23`, `INV-24`, `INV-25`)

---

## Context

1. Có xung đột 3 chiều về `expected_permission_version` giữa `M14 L250` (*Fail-Closed tức thì*), `C14 L22` (*409 AUTH_PERMISSION_VERSION_STALE*), `C14 L64` (*nạp lại từ DB gốc*) và `M19` Outbox Worker (`CEO-U18`).
2. `M14` và `M24` cùng tự nhận sở hữu bảng theo dõi phiên bản cache (`Principal_Permission_Versions` vs `Permission_Cache_Versions`).
3. `M23` tự nhận `Break_Glass_Grants` & `Tenant_Operating_Modes`, còn `M14` đọc chúng lúc runtime nhưng chưa hề có bảng/API nhận ghi từ `M23-F03`/`M23-F05`.

## Đề nghị

1. **Phân tách 2 chế độ kiểm `expected_permission_version` (Chốt theo phiên `/grill-me` Bước 3):**
   - **Chế độ A — Interactive Read / UI / Query (`expected_permission_version = NULL` hoặc dùng làm `cache_hint`):**
     - `M24-F06` chỉ dùng `Permission_Cache_Versions` làm Read-Model Cache Mirror đồng bộ từ `M14.Principal_Permission_Versions` (DB Authoritative Source of Truth).
     - Nếu `cache_version != db_version` (hoặc cache miss): **vô hiệu hóa cache của principal đó ngay lập tức, nạp quyền trực tiếp từ Primary DB** (`M14`), áp `Deny-Wins` + `Legal_Hold`, và trả `ALLOW`/`DENY` theo trạng thái hiện hành (không làm văng `409` khi user vừa được cấp *thêm* quyền hợp lệ).
   - **Chế độ B — Guarded Async Execution, Bulk Action & Sensitive Links (`expected_permission_version` bắt buộc là Guard cứng):**
     - Áp dụng cho: `M19` `Outbound_Intents` Worker (`DispatchOutboundIntent`), `M24-F03` Bulk Actions, `M24-F08` Async Exports, và mọi request `GET / HTTP Range` qua `Download Gateway` (`SEC03`, `U16`) có token/link mang snapshot version.
     - Kiểm trực tiếp `Principal_Permission_Versions.permission_version` trên Primary DB (cấm tin cache `M24-F06`). Nếu `expected_permission_version <> db_version` **HOẶC** `Users.status IN ('SUSPENDED', 'OFFBOARDING_LOCKED', 'OFFBOARDED')` $\rightarrow$ **Fail-Closed tức thì**: trả **`409 AUTH_PERMISSION_VERSION_STALE`** (cho Worker/Bulk/Export hủy job có audit `CEO-U18`, `INT23`) hoặc **`401/403`** (cho `Download Gateway` chặn tải file `U16`, buộc người dùng xác thực phiên mới).
2. **Tách SSoT giữa `M14` và `M24`:**
   - **`M14` sở hữu độc quyền** bảng `Principal_Permission_Versions` (tăng nguyên tử `+1` trong cùng transaction khi thay đổi Role, Entity Grant, Delegation, Break-Glass, Offboarding/Suspend, Legal-Hold Role).
   - **`M24-F06`** chỉ giữ bảng/lớp cache chiếu (`Permission_Cache_Versions`), tuyệt đối không tự tăng version hay làm nguồn ghi (`INV-25`).
3. **Phân định `Break_Glass_Grants` & `Tenant_Operating_Modes` (`M23` Workflow vs `M14` Runtime):**
   - **`Break_Glass_Grants`:** `M23-F03` sở hữu quy trình *Xin $\rightarrow$ Duyệt Maker $\neq$ Checker (khi ở `TEAM`) $\rightarrow$ Phát hành `Break_Glass_Requests` có `incident_ticket_id`, `scope`, `ttl_expires_at` (`GAP-15`)*. Khi duyệt thành công (`M23.BreakGlassApproved`), `M23-F03` gọi command **`ApplyBreakGlassGrant`** (ghi nguyên tử vào SSoT ACL `Break_Glass_Grants` tại `M14`) kèm bump `Principal_Permission_Versions`; khi hết TTL hoặc revoke khẩn cấp (`M23.BreakGlassRevoked` $\rightarrow$ **`RevokeBreakGlassGrant`**), `M14` thu hồi hiệu lực tức thì và bump version lại (`INV-23`).
   - **`Tenant_Operating_Modes`:** `M14.Tenants` giữ cột `operating_mode` (`SOLO_PILOT | TEAM`) làm trạng thái đọc nhanh tại runtime ACL (`M14-F02..F04`); `M23-F05` giữ quy trình quản trị chuyển cấp (`check >= N approvers` theo `GAP-15`, gắn cờ `self_approved_in_pilot_mode` khi còn ở `SOLO_PILOT`, cảnh báo `Owner/CEO`, khóa Maker-Checker khi lên `TEAM`) và gọi command cập nhật `Tenants.operating_mode` tại `M14`.

## So sánh

- **Dùng Authoritative DB Reload cho cả Worker `M19`:** Giảm thiểu rơi job khi user vừa được *thêm* quyền khác, nhưng khiến Worker phải truy vết delta xem version mới tăng là do `GRANT` hay `REVOKE`, làm phức tạp code kiểm chứng và dễ hở logic ở `INT23`/`CEO-U18`. Tách 2 chế độ như trên vừa giữ UX mượt trên UI vừa giữ **Fail-Closed 100% deterministic** cho Worker/Gateway/Bulk.

## Hệ quả và điều kiện thay đổi

- Bổ sung bảng `Break_Glass_Grants` và command nội bộ `ApplyBreakGlassGrant` / `RevokeBreakGlassGrant` / `SetTenantOperatingMode` vào [M14-ORG-ACCESS-DELEGATION.md](../../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md).
- Đồng bộ [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md) và [M24-PERFORMANCE-AND-PRODUCTIVITY.md](../../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md) theo ranh giới này.
