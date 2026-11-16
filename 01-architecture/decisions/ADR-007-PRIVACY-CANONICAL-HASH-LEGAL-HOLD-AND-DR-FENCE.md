# ADR-007 — Chuẩn hóa `HMAC` & Xoay khóa Đa Phiên bản, Multi-`Legal_Hold` và Hàng rào Phục hồi sau Restore (`DR Startup Fence`)

**Status:** `Approved (Wave 1.5 Hardening — CR-20261116-WAVE1-5-HARDENING)`  
**Phạm vi:** `M20`, `M14`, `M16`, `M19`, `M23-F12` (`C23`), `M24-F08` (`C24`), `M08`, `M09`, `M18`, `M21`, `M22`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`5.9`, `5.18`, `6.3 L3139–3174`, `6.4 L3178`, `7.3 L3294`, `UC11`, `INT26`, `OC03`, `OC19`, `NFR06`, `U21`), [INVARIANTS.md](../INVARIANTS.md) (`INV-15`), [ADR-002](ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-003](ADR-003-PERMISSION-VERSION-CACHE-AND-MODE-GOVERNANCE.md), [ADR-004](ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md)

---

## Context

1. Đợt rà soát Wave 1.5 phát hiện **lỗ hổng thứ tự nghiêm trọng trong `DR Startup Fence` cũ**: trình tự cũ cho chạy replay `M23-F12` Internal Outbox ở Bước 3 *trước* khi `M20.VerifyPostRestoreComplianceGate` chạy ở Bước 4 — tạo cửa sổ nguy hiểm khiến sự kiện nội bộ/notification/timer của `M16` được replay trên dữ liệu snapshot chưa áp lại lệnh xóa `Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs` và `Legal_Holds`, đồng thời bỏ qua kiểm soát rollback `permission_version` (`ADR-003`).
2. Cơ chế `HMAC` trước đây dùng chung 1 khái niệm khóa cho cả tra cứu hàng ngày lẫn sổ xóa dài hạn `Deletion_Ledger`, và thiếu cột `hmac_key_version` trên `Endpoint_Suppressions`, `Consent_Logs`/`Consent_State`, `Privacy_Requests`, `Outbound_Intents` (chỉ có trên `Deletion_Ledger`), gây đứt tra cứu khi xoay khóa.
3. Mô hình `Legal_Holds` còn thiếu `PROJECT`, `DELIVERABLE`, `TASK` trong `target_scope_type`, còn dùng cờ đơn trị `legal_hold_status` (lỗi khi 1 bản ghi có nhiều hold chồng nhau), và event `M20.SubjectErasureExecuted` thiếu danh sách `erased_subject_refs[]` nội bộ để `M14`/`M16`/`M22`/`M23`/`M24` khóa sạch danh tính không dựa vào email/SĐT.

## Đề nghị

1. **Chuẩn hóa Canonical Endpoint, Tách 2 Khóa `HMAC` & Tra cứu Multi-Version (`ACTIVE + VERIFY_ONLY`):**
   - **Canonicalization (`Unicode NFKC`):** Mọi chuỗi đầu vào qua bước chuẩn hóa `Unicode NFKC` trước khi băm:
     - `EMAIL`: `nfkc(raw).trim().lowercase()` bỏ ký tự điều khiển (giữ nguyên local-part chuẩn RFC).
     - `PHONE`: `nfkc(raw)` $\rightarrow$ `E.164` theo mã vùng mặc định Tenant (`+84...` cho VN).
     - `PLATFORM_UID / ZALO_UID / FB_PSID`: `nfkc(raw)` $\rightarrow$ `<provider>:<provider_namespace>:<canonical_external_id>`.
   - **Tách 2 Khóa Độc lập trong Secret Vault (`GAP-M20-03`):**
     - **`endpoint_lookup_hmac_key`:** Dùng cho tra cứu/chống spam trên **`Endpoint_Suppressions`, `Consent_Logs`, `Consent_State`, `Privacy_Requests`, `Outbound_Intents`**.
     - **`deletion_ledger_hmac_key`:** Dùng riêng cho chứng từ xóa vĩnh viễn **`Deletion_Ledger`** (lưu dài hạn xuyên nhiều chu kỳ backup/restore).
   - **Bổ sung `hmac_key_version varchar(30) NN` & Tra cứu Multi-Version (`ACTIVE + VERIFY_ONLY`):**
     - Bắt buộc lưu cột **`hmac_key_version`** trên tất cả các bảng: **`Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs`, `Consent_State`, `Privacy_Requests`, `Outbound_Intents`**.
     - Khi xoay khóa (`v1 -> v2`), khóa `v1` chuyển sang chế độ **`VERIFY_ONLY`** (cấm dùng để tạo mới, nhưng giữ để đối chiếu đọc/verify). Mọi cổng kiểm tra (`EvaluateOutboundCompliance`, `VerifyPostRestoreComplianceGate`, kiểm tra xóa trùng) bắt buộc thực hiện **tra cứu multi-version (`ACTIVE + VERIFY_ONLY`)** qua tập `endpoint_hashes_by_version[]` (hoặc danh sách version đang hoạt động) để đảm bảo không bao giờ lọt tin cho endpoint đã bị suppress/xóa ở khóa cũ `v1`.

2. **Mở rộng `Legal_Holds` (`PROJECT`, `DELIVERABLE`, `TASK`), Mẫu `active_legal_hold_ids uuid[]` & `erased_subject_refs[]`:**
   - **Mở rộng `Legal_Holds.target_scope_type`:** Bổ sung **`PROJECT | DELIVERABLE | TASK`** vào tập chuẩn (`CONTACT | ACCOUNT | CONTRACT | PAYMENT | TICKET | INCIDENT | EMPLOYEE | AUDIT_LOG | ASSET | PROJECT | DELIVERABLE | TASK`) và cập nhật consumer **`M16`** tiêu thụ bắt buộc `M20.LegalHoldChanged` (`ADR-008`, `ADR-009`).
   - **Chuyển từ cờ đơn trị sang mảng `active_legal_hold_ids uuid[] DEFAULT '{}'` (`ADR-004`):** Mọi thực thể chịu chi phối giữ danh sách ID hold đang hiệu lực; `RESTRICTED_LEGAL_HOLD` kích hoạt khi `cardinality(active_legal_hold_ids) > 0`, chặn vai trò tác nghiệp thường (`SALES`, `MARKETING`, `AM_CSKH`, `DELIVERY`), chỉ mở `READ`/`VIEW_AUDIT` cho vai trò thẩm quyền (`FINANCE`, `PRIVACY`, `LEGAL_AUDITOR`) và thay danh tính trên BI/Partner (`M18`/`M21`) bằng `REDACTED-SUBJECT-#<short_hash>`.
   - **Bổ sung `erased_subject_refs[]` nội bộ:** Trên `Deletion_Ledger` và payload `M20.SubjectErasureExecuted`, bổ sung trường nội bộ **`erased_subject_refs[]`** (mảng cặp `(subject_type, subject_id_or_ref)` đã ẩn danh cho tiêu thụ nội bộ) giúp `M14` (gắn trạng thái khóa/ẩn danh `Portal_Clients`/`Users` liên quan), `M16` (ẩn danh `Tasks`/`Task_Comments`/`Task_Links`), `M22`, `M23` (thu hồi `Export_Requests` & `Assets`), và `M24` (xóa Read Model / Search index / Notifications) xử lý triệt để mà không phụ thuộc đơn độc vào email/SĐT.

3. **Bảo vệ 6 Bảng PITR Độc lập & Đảo Thứ tự Chuẩn 5 Bước `DR Startup Fence` (`Master 7.3 L3294`):**
   - **Danh sách 6 bảng/sổ bắt buộc nằm trong kho sao lưu liên tục độc lập (PITR/WAL tách khỏi snapshot DB nghiệp vụ):**
     1. `M20.Deletion_Ledger`
     2. `M20.Endpoint_Suppressions`
     3. `M20.Consent_Logs` *(tái dựng/đối soát `Consent_State` khi Verify)*
     4. `M20.Legal_Holds`
     5. `M23.Audit_Logs`
     6. **`M14.Security_Revocation_Ledger`** *(PITR #6 — bổ sung theo `ADR-003` để chống rollback `permission_version`)*
   - **Trình tự Khởi động An toàn Sau Restore (`DR Startup Fence` — 5 Bước Bắt buộc, đã đảo thứ tự Verify trước Replay):**
     1. **Bước 1 — `LOCK_ALL` (`MAINTENANCE_COMPLIANCE_LOCK`):** Khóa toàn bộ **3 làn queue (`M24-F07`)**, khóa toàn bộ **`M16` Schedulers** (nhắc việc, recurrence `W-F09`, offer/hold timeout), và khóa toàn bộ cổng traffic / **Sessions người dùng**; chỉ mở phiên Ops/Recovery có thẩm quyền.
     2. **Bước 2 — `M14` Security Reconciliation & Infrastructure Purge (`ADR-003`):** Đọc **`M14.Security_Revocation_Ledger` (PITR #6)** và `M23.Audit_Logs` để áp lại 100% lệnh thu hồi quyền (`OFFBOARDED`, `SUSPENDED`, `GRANT_REVOKED`, `BREAK_GLASS_REVOKED` `CEO-U26`), **nhảy cóc `acl_epoch / permission_version` vượt `pre_crash_max_version`**, **xóa trắng 100% cache `M24-F06` & thu hồi toàn bộ sessions (`M23-F02`)**, đóng băng lại `Vendor_Data_Flows` / `Channel_Connections` từng bị vô hiệu hoặc `REAUTHORIZATION_REQUIRED` trong `RPO`, và **chỉ xử lý hết hạn thời gian đơn thuần (time-only expiry)** đối với timer `M16` (`offer_expires_at`, `hold_expires_at`, `Recurrence = LATEST_ONLY_DEFAULT`) & thông báo nhắc việc quá hạn thời gian (`M24.Internal_Notifications -> EXPIRED_DR_SKIPPED`) mà **chưa** động tới các bản ghi `M19` / `M23-F12` cần Bước 3 đối soát tuân thủ.
     3. **Bước 3 — `M20.VerifyPostRestoreComplianceGate` (`INT26` — BẮT BUỘC CHẠY TRƯỚC REPLAY):** Kết nối kho PITR độc lập (**đủ `6` bảng**: `Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`, `M23.Audit_Logs`, `M14.Security_Revocation_Ledger`), kiểm chứng đủ mọi `hmac_key_version` (`ACTIVE + VERIFY_ONLY` cho cả `endpoint_lookup_hmac_key` & `deletion_ledger_hmac_key`); chạy fan-out theo từng `(tenant_id, workspace_id)` dưới `BindDbTransactionContext` + **`maintenance_compliance_role`** (`ADR-002`/`ADR-005`, tuyệt đối không `BYPASSRLS`) để áp lại idempotent 100% lệnh xóa `Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs` (tái dựng `Consent_State`), `Legal_Holds` (`active_legal_hold_ids[]`); **hủy toàn bộ phần tử quá hạn hoặc vi phạm compliance (`Erasure / Suppression / Revoked Consent / Legal Hold`) trên cả `M19.Outbound_Intents` (`EXPIRED_CANCELLED`), `M23-F12.Internal_Outbox_Events` (`CANCELLED_BY_DR_GATE`), lẫn `M24.Internal_Notifications` (`EXPIRED_DR_SKIPPED`)** để xuất chính xác các bộ đếm `cancelled_*_count`. Chỉ trả `PASSED` khi `pending_reapply_count == 0 && hmac_keys_verified == true`.
     4. **Bước 4 — `CONDITIONAL_REPLAY` (`M23-F12` & `Sync_Checkpoints`):** **CHỈ khi `VerifyPostRestoreComplianceGate` trả `PASSED` với `pending_reapply_count == 0` và `hmac_keys_verified == true`**, mới cho phép replay có dedup **`M23-F12.Internal_Outbox_Events`** và đối soát `M19.Sync_Checkpoints` (`Worker phát ra ngoài của M19` vẫn kiểm `M14`/`M20` trước khi gửi).
     5. **Bước 5 — `AUDIT_SMOKE_AND_UNLOCK`:** Kiểm toán đối soát số lượng/tiền (`Audit counts`, `U21 NFR06`), chạy smoke test đăng nhập, RLS `SET LOCAL`, chống rollback `permission_version`, và payment gate $\rightarrow$ ghi nhận **`M23-F12.Backup_Drill_Logs`** $\rightarrow$ mở khóa từng bước hệ thống.

4. **Hợp nhất Chính sách `O03/GAP-06`, `O06` & Bỏ cam kết `0 giây` (`Master 6.3 L3172`):**
   - `O03/GAP-06`: Khi `NULL` $\rightarrow$ cổng tiếp nhận `Privacy_Requests` luôn mở định tuyến thẳng về `Owner / CEO` (`6.3 L3149`), nhưng chặn tự động hóa rủi ro (`Auto-Purge`, kích hoạt `Processing_Records`/`Vendor_Data_Flows`, `Bulk Export PII`).
   - `O06`: Mặc định `AGGREGATE_ONLY` cho tới khi `Processing_Records (PROCESSOR + dpa_contract_ref) = ACTIVE`.
   - Tuyệt đối không hứa `0 giây` vật lý cho queue cleanup; bảo đảm an toàn thực tế bằng đọc thẳng Primary DB tại `DISPATCH_AUTHORITATIVE`.

## So sánh

- **Replay `M23-F12` trước `VerifyPostRestoreComplianceGate` và dùng chung 1 khóa HMAC không version trên bảng suppression/outbox:** Gây rủi ro phát lại thông báo/task cho dữ liệu đáng lẽ đã xóa hoặc giữ hợp đồng đang `Legal_Hold`, đồng thời khi xoay khóa HMAC sẽ làm mù toàn bộ bản ghi `Endpoint_Suppressions` / `Consent_Logs` tạo dưới khóa cũ. Đảo thứ tự 5 bước và tách 2 khóa kèm `hmac_key_version` + tra cứu `ACTIVE + VERIFY_ONLY` khóa chặt hoàn toàn luồng DR.

## Hệ quả và điều kiện thay đổi

- Cập nhật [M20-PRIVACY-CONSENT-RETENTION.md](../../02-specs/modules/M20-PRIVACY-CONSENT-RETENTION.md), [M20-SUPPRESSION-PRIVACY-GATE.md](../../02-specs/contracts/M20-SUPPRESSION-PRIVACY-GATE.md), [M14-ORG-ACCESS-DELEGATION.md](../../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md), [M19-INTEGRATION-ADAPTERS-OUTBOX.md](../../02-specs/modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md), [M16-WORK-PROJECTS-TASK-CORE.md](../../02-specs/modules/M16-WORK-PROJECTS-TASK-CORE.md), [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), `C23`, `C24`, và [GAPS.md](../../03-planning/GAPS.md).
