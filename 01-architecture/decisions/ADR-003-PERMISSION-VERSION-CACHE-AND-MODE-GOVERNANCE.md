# ADR-003 — Hợp đồng `permission_version`, Chống Rollback DR Restore, Cache Mirror `M24`, Chế độ `SOLO_PILOT <-> TEAM` & `Break-Glass` Runtime

**Status:** `Approved (Wave 1.5 Hardening — CR-20261116-WAVE1-5-HARDENING)`  
**Phạm vi:** `M14` (`C14`), `M19` (`C19`), `M23` (`F02/03/05`), `M24` (`F03/06/08`, `C24`)  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`6.1`, `6.2`, `7.3 L3294`, `SEC03`, `U16`, `CEO-U18`, `CEO-U26`, `INT23`), [INVARIANTS.md](../INVARIANTS.md) (`INV-22`, `INV-23`, `INV-24`, `INV-25`), [ADR-002](ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-007](ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md)

---

## Context

1. Có xung đột về `expected_permission_version` giữa `M14` (*Fail-Closed tức thì*), `C14` (*409 AUTH_PERMISSION_VERSION_STALE* vs *nạp lại từ DB gốc*) và `M19` Outbox Worker (`CEO-U18`).
2. Rà soát Wave 1.5 phát hiện lỗ hổng **Rollback `permission_version` khi DR Restore**: nếu DB được khôi phục về snapshot cũ (`db_version = 10`) trong khi trước khi sự cố user đã bị thu hồi quyền ở `version = 11` (hoặc client/JWT đang giữ `version = 11`), chế độ `INTERACTIVE_READ` trước đây sẽ tự động tin DB cũ và tiếp tục đánh giá quyền trên snapshot đã lỗi thời.
3. Cần vá dứt điểm ranh giới SSoT giữa `M14` và `M23-F05`: `M23` trước đây tự nhận bảng `Tenant_Operating_Modes` song song với `M14.Tenants.operating_mode`, đồng thời chưa khóa chặt quy tắc chuyển chế độ hai chiều (`SOLO_PILOT -> TEAM` và `TEAM -> SOLO_PILOT`).

## Đề nghị

1. **Phân tách 2 chế độ kiểm `expected_permission_version` & Chống Rollback Phiên bản (`401`):**
   - **Chế độ A — Interactive Read / UI / Query (`execution_mode = 'INTERACTIVE_READ'`, `expected_permission_version` hoặc `client_version` dùng làm `cache_hint`):**
     - `M24-F06` chỉ dùng `Permission_Cache_Versions` làm Read-Model Cache Mirror đồng bộ từ `M14.Principal_Permission_Versions` (DB Authoritative Source of Truth).
     - **Chặn Rollback DR (`client_version > db_version`):** Nếu `client_version` / `token_permission_version` gửi lên **lớn hơn** `db_version` hiện tại trong Primary DB (`client_version > db_version`), hệ thống **tuyệt đối KHÔNG rơi vào nhánh reload cache**, mà phải **Fail-Closed tức thì trả `401 AUTH_UNAUTHENTICATED_OR_SESSION_REVOKED`** (buộc đăng xuất/xác thực lại) và phát cảnh báo an ninh `M23-F08`.
     - Chỉ khi `client_version < db_version` (hoặc cache miss hợp lệ sau khi cấp thêm quyền): vô hiệu hóa cache của principal đó tại `M24-F06`, nạp quyền trực tiếp từ Primary DB (`M14`), áp `Deny-Wins` + `Legal_Hold`, và đánh giá theo trạng thái hiện hành.
   - **Chế độ B — Guarded Async Execution, Bulk Action & Sensitive Links (`execution_mode = 'GUARDED_EXECUTION'`, `expected_permission_version` bắt buộc non-null):**
     - Áp dụng cho: `M19` `Outbound_Intents` Worker (`DispatchOutboundIntent`), `M24-F03` Bulk Actions, `M24-F08` Async Exports, lệnh chuyển giao/nghiệm thu trọng yếu `M16`, và mọi request `GET / HTTP Range` qua `Download Gateway` (`SEC03`, `U16`).
     - Kiểm trực tiếp `Principal_Permission_Versions.permission_version` + `acl_epoch` trên Primary DB (cấm tin cache `M24-F06`). Nếu `expected_permission_version <> db_version` **HOẶC** `Users.status IN ('SUSPENDED', 'OFFBOARDING_LOCKED', 'OFFBOARDED')` $\rightarrow$ **Fail-Closed tức thì**: trả **`409 AUTH_PERMISSION_VERSION_STALE`** (cho Worker/Bulk/Export hủy job có audit `CEO-U18`, `INT23`) hoặc **`401/403`** (cho `Download Gateway` chặn tải file `U16`).

2. **Vá Rollback `permission_version` khi DR Restore (`PITR #6` + Nhảy cóc `acl_epoch` — phối hợp `ADR-007`):**
   - Bổ sung **bảng thứ 6** trong kho sao lưu liên tục độc lập (PITR/WAL tách khỏi snapshot DB chính): **`M14.Security_Revocation_Ledger`** (lưu append-only mọi sự kiện thu hồi quyền, offboarding, khóa tài khoản, revoke break-glass, thay đổi `acl_epoch`, và `pre_crash_max_version`).
   - Tại **Bước 2 của `DR Startup Fence` (`ADR-007`)** — trước khi chạy đối soát tuân thủ và mở cổng người dùng:
     1. Áp lại 100% các lệnh thu hồi từ **`M14.Security_Revocation_Ledger`** (`OFFBOARDED`, `SUSPENDED`, `GRANT_REVOKED`, `BREAK_GLASS_REVOKED`).
     2. Thực hiện **nhảy cóc `acl_epoch / permission_version` vượt qua `pre_crash_max_version`** (bảo đảm mọi `permission_version` sau khôi phục lớn hơn nghiêm ngặt mọi version từng phát hành trước sự cố).
     3. **Xóa trắng 100% cache `M24-F06`** (`Permission_Cache_Versions` & Read-Model Cache) và **thu hồi toàn bộ active sessions qua `M23-F02`** trước khi mở khóa traffic.

3. **Tách SSoT giữa `M14`, `M23` và `M24`:**
   - **`M14` sở hữu độc quyền:** Bảng `Principal_Permission_Versions` (gồm `acl_epoch` & `permission_version`, tăng nguyên tử `+1` trong cùng transaction khi đổi Role, Entity Grant, Delegation, Break-Glass, Offboarding/Suspend, Legal-Hold), bảng runtime `Break_Glass_Grants`, bảng `Security_Revocation_Ledger` (PITR #6), và **runtime flag `M14.Tenants.operating_mode` (`SOLO_PILOT | TEAM`)**.
   - **`M24-F06`:** Chỉ giữ bảng/lớp cache chiếu (`Permission_Cache_Versions`), tuyệt đối không tự tăng version hay làm nguồn ghi (`INV-25`).
   - **`M23` KHÔNG sở hữu `Tenant_Operating_Modes`:**
     - Khẳng định dứt khoát **`M14.Tenants` là SSoT duy nhất sở hữu runtime flag `operating_mode` (`SOLO_PILOT | TEAM`)**.
     - `M23-F05` chỉ sở hữu quy trình **request/audit chuyển chế độ** (`Mode_Change_Requests` & `Audit_Logs`) và gọi command `M14.SetTenantOperatingMode` để cập nhật `M14.Tenants.operating_mode` kèm bump `permission_version`.
     - **Quy tắc chuyển chế độ hai chiều (`INV-22`, `GAP-15`):**
       - **Nâng cấp `SOLO_PILOT -> TEAM`:** Kiểm điều kiện `>= N` approvers độc lập; mọi thao tác nhạy cảm từng thực hiện tự duyệt trong lúc ở pilot bắt buộc gắn cờ kiểm toán **`self_approved_in_pilot_mode = true`**, không ẩn dấu vết; ngay khi lên `TEAM`, hệ thống khóa hoàn toàn tự duyệt cho Technical Admin và cưỡng chế `Maker != Checker`.
       - **Hạ cấp `TEAM -> SOLO_PILOT`:** **Bắt buộc `Maker != Checker`** (tối thiểu 2 người có thẩm quyền độc lập xác nhận, bao gồm phê duyệt của Owner/CEO, có lý do kiểm toán bắt buộc và bắn cảnh báo khẩn cấp tức thì tới Owner/CEO); nghiêm cấm 1 cá nhân tự hạ cấp hệ thống từ `TEAM` về `SOLO_PILOT`.
   - **`Break_Glass_Grants`:** `M23-F03` giữ quy trình `Break_Glass_Requests` (`Maker != Checker` khi `TEAM`, `incident_ticket_id`, `workspace_ids`, `scope_resource_types[]`, `allowed_actions[]`, `ttl_expires_at` theo `GAP-15`); khi duyệt/thu hồi phát `M23.BreakGlassApproved` / `M23.BreakGlassRevoked` gọi `M14.ApplyBreakGlassGrant` / `RevokeBreakGlassGrant` ghi vào SSoT ACL `M14.Break_Glass_Grants`.

## So sánh

- **Giữ `INTERACTIVE_READ` nạp lại DB khi `client_version > db_version` hoặc để `M23` giữ bảng `Tenant_Operating_Modes` riêng:** Khi DR Restore lùi DB về snapshot cũ, user đã bị thu hồi quyền trước sự cố có thể đọc lọt dữ liệu trên bản snapshot cũ; đồng thời tạo 2 nguồn sự thật cho `operating_mode` và cho phép 1 người tự hạ `TEAM -> SOLO_PILOT`. Vá bằng `Security_Revocation_Ledger` + nhảy cóc `acl_epoch` + chặn `client_version > db_version` (`401`) + khóa SSoT `M14.Tenants` giải quyết triệt để rủi ro bảo mật.

## Hệ quả và điều kiện thay đổi

- Bổ sung `Security_Revocation_Ledger` (PITR #6), `acl_epoch`, quy tắc `client_version > db_version -> 401`, và khẳng định SSoT `M14.Tenants.operating_mode` vào [M14-ORG-ACCESS-DELEGATION.md](../../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md) & [M14-PRINCIPAL-ACCESS-DECISION.md](../../02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md).
- Cập nhật [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), `C23`, [M24-PERFORMANCE-AND-PRODUCTIVITY.md](../../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md) và `C24` theo đúng ranh giới này.
