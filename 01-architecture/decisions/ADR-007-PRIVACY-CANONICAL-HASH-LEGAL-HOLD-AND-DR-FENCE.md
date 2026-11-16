# ADR-007 — Chuẩn hóa `HMAC` & Xoay khóa `Deletion_Ledger`, `RESTRICTED_LEGAL_HOLD` và Hàng rào Phục hồi sau Restore (DR Fence)

**Status:** `Approved (Proposed Extension trong Baseline v1.9)`  
**Phạm vi:** `M20`, `M14`, `M19`, `M23-F12`, `M24-F08`, `M08`, `M09`, `M18`, `M21`, `M22`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`5.9`, `5.18`, `6.3 L3139–3174`, `6.4 L3178`, `7.3 L3294`, `UC11`, `INT26`, `OC03`, `OC19`, `NFR06`, `U21`), [INVARIANTS.md](../INVARIANTS.md) (`INV-15`)

---

## Context

1. `M20` dùng `endpoint_lookup_hash` (`char(64)`) và `Deletion_Ledger.subject_hmac_sha256` nhưng chưa quy định cách chuẩn hóa chuỗi trước khi băm, chưa quản lý vòng đời xoay khóa `hmac_key_version`, và phạm `workspace_id NOT NULL` cho sổ xóa đa workspace (`OC03` / `UC11`).
2. `RESTRICTED_LEGAL_HOLD` do `M20-F06` phát sinh qua `M20.LegalHoldChanged` hiện chưa được `M14` tiêu thụ, khiến quy trình xóa một phần mất hiệu lực cô lập thực thi.
3. Khi Restore DB (`INT26`, `OC19`, `U21 NFR06`), `M20 L433–434` mới bảo vệ PITR cho 2 bảng (`Deletion_Ledger` và `Endpoint_Suppressions`) mà bỏ sót `Consent_Logs`, `Legal_Holds`, `Audit_Logs`; đồng thời thiếu trình tự phối hợp giữa `M23-F12` (Restore Drill), `M20` (`VerifyPostRestoreComplianceGate`), và `M19` (`EXPIRED_CANCELLED` outbox fence) theo `Master 7.3 L3294`.

## Đề nghị

1. **Chuẩn hóa Canonical Endpoint & Xoay khóa `HMAC-SHA256` (`[PROPOSED]` + `[OPEN-GAP]`):**
   - **Canonicalization trước khi băm `endpoint_lookup_hash` / `Deletion_Ledger`:** Mọi chuỗi đầu vào bắt buộc qua bước chuẩn hóa **`Unicode NFKC` trước khi xử lý tiếp** nhằm chặn lách hash bằng ký tự tương đồng/fullwidth:
     - `EMAIL`: `nfkc(raw).trim().lowercase()` + bỏ ký tự điều khiển; giữ nguyên phần local-part chuẩn RFC (chưa tự động gộp dấu `+`/`.` của riêng Gmail trừ khi cấu hình kênh chỉ định rõ để tránh false-positive giữa `OC03`).
     - `PHONE`: `nfkc(raw)` $\rightarrow$ chuẩn hóa sang `E.164` theo mã vùng mặc định Tenant (`+84...` cho VN).
     - `PLATFORM_UID / ZALO_UID / FB_PSID`: `nfkc(raw)` $\rightarrow$ định dạng `<provider>:<provider_namespace>:<canonical_external_id>` (chống trùng ID giữa 2 OA/Page khác nhau — `OC03`).
   - **Phạm vi & Xoay khóa `hmac_key_version`:** Khóa bí mật `HMAC` lưu trong Secret Vault (tách khỏi PostgreSQL backup thông thường), dùng **khóa chung cấp Tenant (`tenant_id + hmac_key_version`) cho `Deletion_Ledger`** (để đối soát được chủ thể bị xóa trên nhiều workspace cùng tenant trong `UC11`), kèm metadata `workspace_id NULL` nếu xóa ở cấp Tenant Controller hoặc `workspace_id` cụ thể nếu xóa phạm vi 1 `CLIENT` workspace. Khi xoay khóa (`v1 -> v2`), **bắt buộc giữ nguyên các khóa `v(n-1)` ở chế độ `VERIFY_ONLY`** cho `Deletion_Ledger` nhằm kiểm tra đối chiếu khi Restore từ backup cũ.
2. **Tích hợp `RESTRICTED_LEGAL_HOLD` Xuyên Module (`M20` $\rightarrow$ `M14` $\rightarrow$ Domain/BI):**
   - Khi `M20-F06` phát `M20.LegalHoldChanged` (`ACTIVE` kèm `target_scope_type`, `target_id`), **`M14` tiêu thụ bắt buộc**, gắn cờ `legal_hold_status = 'RESTRICTED_LEGAL_HOLD'` vào cache/registry ACL phạm vi tài nguyên đó và bump `Principal_Permission_Versions` cho các principal bị ảnh hưởng.
   - Ở trạng thái `RESTRICTED_LEGAL_HOLD`: `M14` (`EvaluateAccessDecision` & `CompileScopeFilter`) chặn toàn bộ vai trò tác nghiệp thường (`SALES`, `MARKETING`, `AM_CSKH`, `DELIVERY`), **chỉ cho phép vai trò có thẩm quyền pháp lý/kiểm toán/tài chính theo policy (`FINANCE`, `PRIVACY`, `LEGAL_AUDITOR`) đọc/đối chiếu** (`M08` Hợp đồng, `M09` Hóa đơn/Chứng từ thu, `M22` Hồ sơ lao động/lương); đồng thời trên báo cáo tổng hợp (`M18`/`M21`), mọi trường danh tính thay bằng nhãn ẩn danh thống nhất `[PROPOSED]` `REDACTED-SUBJECT-#<short_hash>` thay cho PII thật.
3. **Bảo vệ Kho lưu trữ Độc lập (PITR Independence) & Hàng rào Sau Restore (`DR Compliance Fence` — `Master 7.3 L3294`):**
   - **Danh sách 5 bảng/sổ phải nằm trong kho sao lưu liên tục (WAL / immutable append storage độc lập khỏi snapshot DB nghiệp vụ):** `Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`, và `Audit_Logs` (còn `Consent_State` là projection được tái dựng/đối soát tất định từ `Consent_Logs` trong lúc Verify, tránh mất bằng chứng hủy quyền/hold mới phát sinh ngay trước sự cố).
   - **Trình tự Khởi động An toàn Sau Restore (`DR Startup Fence` khớp `Master 7.3 L3294`, `M23-F12` + `M20` + `M19` + `M14`):**
     1. Hệ thống khởi động ở chế độ `MAINTENANCE_COMPLIANCE_LOCK`: **cấm bật Worker gửi tin `M19`** và **cấm mở cổng traffic User**, chỉ mở tài khoản Ops/Recovery có thẩm quyền để khôi phục DB/object/secrets.
     2. Chạy bước đối soát quyền `M14` từ `Audit_Logs` / `Revocation` gần nhất để khóa lại mọi User/Grant đã `OFFBOARDED` / `REVOKED` trước sự cố (`CEO-U26`).
     3. **Replay Outbox có dedup ở trạng thái khóa Worker ngoài (`Master 7.3 L3294` + `OC19`):** Replay `M23-F12` Internal Outbox nội bộ có chống trùng để khôi phục state nội bộ, đồng thời chạy `M19` Outbox reconciliation chuyển toàn bộ `Outbound_Intents` cũ trong backup quá `expires_at` sang `EXPIRED_CANCELLED` và đồng bộ `Sync_Checkpoints` (**Worker phát ra ngoài của `M19` vẫn giữ DỪNG**).
     4. **`M20.VerifyPostRestoreComplianceGate` (`INT26`):** Áp lại 100% lệnh xóa từ `Deletion_Ledger` (kể cả xóa lại phần PII mới hồi sinh trong snapshot cũ), `Endpoint_Suppressions`, `Consent_Logs` (REVOKE + dựng lại `Consent_State`) và `Legal_Holds`, đồng thời hủy nốt mọi `Outbound_Intents` liên quan.
     5. Kiểm toán `pending_reapply_count == 0`, đối soát tiền/số lượng (`U21 NFR06`), chạy smoke test đăng nhập/lead/payment/RLS $\rightarrow$ `M23-F12` ghi `Backup_Drill_Logs` $\rightarrow$ mở khóa hệ thống cho người dùng & bật lại Worker gửi tin `M19`.
4. **Hợp nhất Chính sách `O03/GAP-06` & `O06` (Chốt theo `/grill-me` Bước 5):**
   - `O03/GAP-06` (`privacy_and_steward_role_binding_ids`): Khi `NULL/chưa gán` $\rightarrow$ **Cổng tiếp nhận `Privacy_Requests` (`M20-F04`) LUÔN MỞ** và định tuyến thẳng tới `Owner / CEO` xử lý thủ công có evidence (`Master 6.3 L3149`); ngược lại, mọi tác vụ rủi ro/tự động (`Auto-Purge`, kích hoạt `Processing_Records` / `Vendor_Data_Flows` mới, `Bulk Export PII`, `High-Risk Merge`, `ExecuteErasure` không có chữ ký `Owner/CEO`) **tự động Fail-Closed (`POLICY_UNCONFIGURED_PRIVACY_OWNER`)**.
   - `O06` (`client_workspace_allowed_data_mode`): Thống nhất enum `AGGREGATE_ONLY | SCOPED_PII_WITH_DPA`, mặc định **`AGGREGATE_ONLY`** cho tới khi `M20-F01` duyệt `Processing_Records (PROCESSOR + dpa_contract_ref) = ACTIVE`.
   - **Hủy bỏ cam kết `0 giây` trái Master `6.3 L3172`:** Ghi rõ `DISPATCH_AUTHORITATIVE` recheck thẳng DB tại thời điểm phát; cleanup queue bất đồng bộ có SLA giám sát nội bộ (`[OPEN-GAP]`), **không hứa `0 giây` vật lý**.

## So sánh

- **Chỉ bảo vệ PITR 2 bảng (`Deletion_Ledger` & `Endpoint_Suppressions`):** Nếu khách hàng vừa rút `Consent` (chưa kịp xóa) hoặc Pháp chế vừa đặt `Legal_Hold` mới trước khi DB lỗi 10 phút, bản restore snapshot sẽ hồi sinh `Consent = GRANTED` cũ hoặc làm rớt `Legal_Hold`. Bổ sung `Consent_Logs`, `Legal_Holds`, `Audit_Logs` khép kín lỗ hổng này.

## Hệ quả và điều kiện thay đổi

- Cập nhật [M20](../../02-specs/modules/M20-PRIVACY-CONSENT-RETENTION.md), [C20](../../02-specs/contracts/M20-SUPPRESSION-PRIVACY-GATE.md), [M14](../../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md), [C14](../../02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md), [M19](../../02-specs/modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md), [M23](../../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), và [M24](../../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md).
- Đăng ký `[OPEN-GAP]` về chuẩn hóa HMAC rotation & SLA cleanup queue vào [GAPS.md](../../03-planning/GAPS.md).
