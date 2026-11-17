# Contract `M20-SUPPRESSION-PRIVACY-GATE` — Cổng Kiểm duyệt Gửi tin, Legal Hold, AI/Vendor, File Privacy & Phục hồi

- **Contract ID:** `CONTRACT-M20-PRIVACY-GATE-v1.1`
- **Provider Owner:** `M20` (Consent, Mục đích Xử lý, Suppression, Privacy Requests, Legal Hold, Retention & AI Gateway)
- **Consumers:** `M19` (Outbound Dispatch), `M01` (Merge Consent Guard), `M02` (Lead/Import), `M03` (Inbox Compose), `M04` (Journey Dispatch), `M06` (AI Co-Pilot), `M08`/`M09` (Legal Hold Lock), `M11`/`M12` (Ticket vs Survey/Feedback), `M14` (Legal Hold ACL, PITR #6 Reconciliation & Download Gateway `SEC03`), `M16`/`M18`/`M21`/`M22` (Erasure, `Legal_Hold` & Reporting/HR Gate), `M23` (`M23-F07` Export/Assets & `M23-F12` Restore Drill), `M24` (`M24-F05/F06/F08` Notifications, Cache & Async Export)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`2.5 L268 CONTRACT-L0268`, `3.5.3 FR13`, `5.9`, `5.18`, `6.3 L3132–3174`, `6.4 L3178`, `6.8 L3257`, `7.3 L3294`, `Phụ lục E.3 L4600 CR12`, `SEC03`, `SEC05`, `SEC-U05`, `U15`, `U21`, `U22`, `INT17`, `INT26`, `INT28`, `OC03`, `OC17`, `OC19`, `OC20`, `RV16`, `RV17`, `CX-U15`, `CX-U20`), [ADR-002](../../01-architecture/decisions/ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-004](../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](../../01-architecture/decisions/ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-008](../../01-architecture/decisions/ADR-008-OMNICHANNEL-CONTRACTS-RECEIPTS-AND-CROSS-EVENTS.md)
- **Trạng thái:** `Reviewed (CR-20261116-WAVE1-5-HARDENING Applied; CR-20261116-WAVE1-REVIEW-FIXES Applied; CR-20261116-SKILL-TEMPLATE-ALIGN Applied)` *(đồng bộ hậu `CR-20261116-WAVE1-RECONCILIATION` theo mã đề xuất `CR-20261116-WAVE1-5-HARDENING` và `CR-20261116-WAVE1-REVIEW-FIXES`)*
- **Approved_Scope:** `Wave 1/1.5 Privacy, Suppression, AI Gateway & DR Gate Public Contract`
- **Approved_By:** `Chủ dự án`
- **Decision_Ref:** `CR-20261116-SKILL-TEMPLATE-ALIGN`
- **Approved_At:** `2026-11-16`
- **Chính sách Breaking Change:** Thay đổi rule chặn gửi hoặc schema chuyển AI/Restore/Download Gate bắt buộc giữ chế độ Fail-Closed trong `ADR-006`/`ADR-007` và cập nhật đồng thời `M19`, `M14`, `M16`, `M06`, `M23`, `M24`.

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | Cung cấp **4 cổng kiểm duyệt Authoritative** của `M20`: (1) `EvaluateOutboundCompliance` (Cổng Kép chặn gửi tại lúc `Enqueue` và tại thời điểm phát tin `DISPATCH_AUTHORITATIVE`, hỗ trợ tra cứu `endpoint_hashes_by_version[]` đa phiên bản `ACTIVE + VERIFY_ONLY`), (2) `EvaluateVendorAndAiTransfer` (Cổng Kiểm soát AI Data Gateway + server-side DLP scanner, `Placeholder_Vault`, chuẩn hóa `provider -> vendor_code`, khoanh vùng chặn `CCCD/BANK/HRM_PAYROLL` riêng cho `AI_*`, & chống Prompt Injection `U22`/`INT28`), (3) `VerifyPostRestoreComplianceGate` (Hàng rào sau khi đã chạy `M14` PITR #6 `Security_Revocation_Ledger` + jump `acl_epoch/permission_version` + xóa cache `M24-F06`, áp lại `Deletion_Ledger` + `Endpoint_Suppressions` + `Consent_Logs` + `Legal_Holds` + hủy `M19`/`M23-F12`/`M24` **TRƯỚC** khi replay `M23-F12`), và (4) `EvaluateAssetDownloadPrivacyGate` (`SEC03` kiểm `Asset_Versions.scan_status`, `Deletion_Ledger`, `active_legal_hold_ids` theo cả `asset` lẫn `(owner_resource_type, owner_resource_id)`). |
| **Actor/scope** | `tenant_id`, `workspace_id` (`target_workspace_id` tùy chọn khi truy xuất bridge `AGENCY <-> CLIENT` tại Download Gate), `actor_id` & **`actor_type` (`USER \| SERVICE_PRINCIPAL \| PORTAL_CLIENT`)** bắt buộc trên các cổng `Evaluate*`. Cô lập chặt RLS `Nhóm B-Catalog` (tham chiếu công khai cùng tenant như `M23.System_Calendars`) vs **`Nhóm B-Governance-Sensitive`** (bao gồm cả **`Legal_Deadline_Policies`**, **`Retention_Policies`** cùng `Processing_Records`, `Vendor_Data_Flows`, `Privacy_Requests`, `Legal_Holds`, `Data_Incidents`: `workspace_id IS NULL` CHỈ mở cho **`app.current_workspace_type IN ('AGENCY', 'SYSTEM')`**, chặn `CLIENT` workspace đọc trực tiếp theo `OC03`, `ADR-002:41` & `ADR-004:35`; `CLIENT` kiểm qua `EvaluateAssetDownloadPrivacyGate` hoặc projection đã duyệt), `Deletion_Ledger` là `Nhóm C` hỗ trợ `scope_tenant_wide = true` tại `AGENCY`, và `Endpoint_Suppressions` fan-out theo phạm vi `Controller` (`UC11/UC14`). `channel` đồng bộ 8 giá trị (`EMAIL \| SMS \| ZALO \| FACEBOOK \| TIKTOK \| TELEGRAM \| VOICE_CALL \| WEBHOOK`). |
| **Preconditions** | Tách 2 khóa HMAC độc lập trong Secret Vault (`endpoint_lookup_hmac_key` cho `Endpoint_Suppressions`/`Consent_Logs`/`Consent_State`/`Privacy_Requests` vs `deletion_ledger_hmac_key` cho `Deletion_Ledger`), mỗi bản ghi lưu rõ `hmac_key_version varchar(30) NN`. Endpoint được chuẩn hóa canonical trước khi băm (`ADR-007`: qua bước `Unicode NFKC` $\rightarrow$ `EMAIL: trim().lowercase()` bỏ ký tự điều khiển; `PHONE: E.164`; `PLATFORM_UID: <provider>:<provider_namespace>:<canonical_external_id>`). `Processing_Records` phải đạt `ACTIVE` (nếu `PROCESSOR` bắt buộc có `dpa_contract_ref`); `Vendor_Data_Flows` đạt `APPROVED` (tách `training_opt_out` vs `zero_data_retention` `RV17`, ánh xạ chuẩn `provider -> vendor_code`). |
| **Input** | Xem 4 cặp JSON Schema đầy đủ ở Mục 2 (`EvaluateOutboundComplianceInput` có `actor_type` & `endpoint_hashes_by_version[]`, `EvaluateVendorAndAiTransferInput` có `actor_type`, `source_provider`, `source_resource_type/id`, `VerifyPostRestoreComplianceGateInput` có `workspace_id` fan-out & `security_reconciliation_completed`, `EvaluateAssetDownloadPrivacyGateInput` có `asset_version_id`, `actor_type`, `target_workspace_id`, `owner_resource_type`, `owner_resource_id`). |
| **Output** | Xem 4 JSON Schema đầy đủ ở Mục 2 (`OutboundComplianceDecision` với `suppression_id`, `matched_hmac_key_version`, `consent_state_version`, `evaluated_at`; `VendorTransferDecision` với `dlp_scanned`; `PostRestoreComplianceGateResult` với đếm hủy `M19` / `M23-F12.Internal_Outbox_Events` / `M24.Internal_Notifications`; `AssetPrivacyGateDecision` với `legal_hold_status` & `active_legal_hold_ids[]`). |
| **Errors** | Chuẩn Error Envelope `{code, message, field_errors, correlation_id}`. Mã chặn đầy đủ khớp 100% 4 JSON schema bên dưới (thống nhất dùng `PRIVACY_PURPOSE_UNAPPROVED`): `OUTBOUND_SUPPRESSED_UNSUBSCRIBE`, `OUTBOUND_SUPPRESSED_CONSENT_REVOKED`, `OUTBOUND_SUPPRESSED_HARD_BOUNCE`, `OUTBOUND_SUPPRESSED_SOFT_BOUNCE_COOLDOWN`, `OUTBOUND_SUPPRESSED_SPAM_COMPLAINT`, `OUTBOUND_SUPPRESSED_REFUSED_CALLBACK`, `OUTBOUND_SUPPRESSED_MANUAL_DNC`, `OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD`, `PRIVACY_PURPOSE_UNAPPROVED`, `SENDER_PROFILE_UNVERIFIED`, `VENDOR_TRANSFER_POLICY_BLOCKED`, `PROHIBITED_DATA_CLASS_INCLUDED`, `AI_PROMPT_TOOL_POLICY_BLOCKED`, `MISSING_HMAC_KEY_VERSION`, `PENDING_REAPPLY_NONZERO`, `INDEPENDENT_LEDGER_UNREACHABLE`, `SECURITY_RECONCILIATION_PENDING`, `ASSET_QUARANTINED_OR_INFECTED`, `ASSET_PRIVACY_HOLD_OR_ERASED`, `ASSET_RETENTION_EXPIRED`, `HRM_CONFIDENTIALITY_BLOCKED`. *(Lưu ý: `EXPORT_LINK_EXPIRED` do `M23-F07` kiểm ở Bước 3 Download Gateway theo `ADR-006`)*. |
| **Concurrency** | `EvaluateOutboundCompliance` đọc thẳng Primary DB (Authoritative State, không chờ cache) tại bước `DISPATCH_AUTHORITATIVE`. **Theo Master `6.3 L3172`: tuyệt đối không hứa `0 giây` vật lý hay thu hồi chắc chắn tin mà provider đã nhận (`in-flight`)**; cleanup hàng đợi bất đồng bộ chạy với `SLA` giám sát riêng (`[OPEN-GAP: GAP-M20-10]`). Giao dịch `REVOKE`/`UNSUBSCRIBE` commit `Endpoint_Suppressions` nguyên tử trước khi trả `200/202` (`CONTRACT-L0268`). |
| **Idempotency** | Các hàm `Evaluate*` không ghi đột biến nghiệp vụ (chỉ ghi audit chặn/tạo phiên `Placeholder_Vault` theo `correlation_id`). `VerifyPostRestoreComplianceGate` chạy idempotent tuyệt đối theo khóa tổng hợp `(restore_run_id, source_table, source_record_id)` (bao phủ `Deletion_Ledger` [`deletion_ledger_id`], `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`, `Data_Incidents`) dưới fan-out `Tenants -> Workspaces` — chạy lặp 100 lần không sai lệch dữ liệu (`NFR08`, `INT26`). `POST /v1/consents/revoke` yêu cầu `idempotency_key` duy nhất theo `tenant_id` (`5.9 L2701`). |
| **Transaction** | Lệnh `POST /v1/consents/revoke` (`CONTRACT-L0268`) hoặc `PublicOneClickUnsubscribe` (`SEC05`) bắt buộc ghi `Consent_Logs` + cập nhật `Consent_State` + ghi `Endpoint_Suppressions` + ghi `Internal_Outbox_Events` (`M20.EndpointSuppressed`) trong **1 DB transaction nguyên tử**; khi `Controller` Agency thu hồi toàn Tenant (`scope_tenant_wide = true`, `UC11/UC14`), thực hiện fan-out tạo suppression cho từng workspace thuộc phạm vi Controller (cô lập tuyệt đối `CLIENT` controller khác theo `OC03`) và trả `202 Accepted` nếu tác vụ fan-out/hủy `Outbound_Intents` ở `M19` còn lan truyền bất đồng bộ (`200 OK` nếu xong ngay). |
| **Compatibility** | Hỗ trợ đồng thời nhiều `hmac_key_version` ở chế độ `ACTIVE + VERIFY_ONLY` trên cả `endpoint_lookup_hmac_key` (qua `endpoint_hashes_by_version[]` của `EvaluateOutboundCompliance`) lẫn `deletion_ledger_hmac_key` (`ADR-007`). `purpose_code` chuẩn hóa `varchar(80)` khớp Master `5.9 L2692`. |
| **Audit/privacy** | Không lộ PII gốc trong log/error; `PublicOneClickUnsubscribe` không lộ hồ sơ khách; giải mã ngược `Placeholder_Vault` (`DetokenizePlaceholderVault`) bắt buộc kiểm `vault.actor_id == caller_id` và gọi `M14.EvaluateAccessDecision` trên đúng `(source_resource_type, source_resource_id)` (`6.3 L3174`); sự kiện `SubjectErasureExecuted` truyền `erased_subject_refs[]` qua Internal Outbox nội bộ không ghi plaintext vào log (`NFR11`); **cụm PITR/WAL độc lập (`ADR-007`)**: 5 bảng `M20/M23` (`Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`, `M23.Audit_Logs` — cộng tái dựng `Consent_State`) phối hợp **PITR #6 `M14.Security_Revocation_Ledger`**. |
| **Tests** | `M20-AC01..03`, `CR12`, `SEC-U05`, `U15`/`INT17`, `U18`, `U21` (backup restore đảo thứ tự DR Fence), `U22` (AI prompt injection & server-side DLP), `INT24`, `INT26`, `INT28`, `RV11`, `RV16`, `RV17`, `OC03`, `OC17`, `OC19`, `OC20`, `CX-U12`, `CX-U15`, `CX-U20`, `SEC-U03`. Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas Đầy đủ cho 4 Cổng Kiểm duyệt (`ADR-006`, `ADR-007`, `ADR-008`)

### 2.1. `EvaluateOutboundComplianceInput` & `OutboundComplianceDecision`

```json
{
  "EvaluateOutboundComplianceInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "actor_id": "uuid (NN)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "check_stage": "ENQUEUE_PREVIEW | DISPATCH_AUTHORITATIVE",
    "channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK",
    "purpose_code": "string (max 80 chars, varchar(80) theo Master 5.9)",
    "message_category": "TRANSACTIONAL_TICKET_OR_APPOINTMENT | SERVICE_REPLY | MARKETING_PROMO | SURVEY_VOC | AUTOMATED_JOURNEY | TASK_SYNC | SYSTEM_SYNC",
    "contact_id": "uuid | null (có thể null khi mới có channel identity hoặc SYSTEM_WEBHOOK)",
    "endpoint_lookup_hash": "string | null (char(64) HMAC-SHA256 của chuỗi Unicode NFKC canonical theo endpoint_lookup_hmac_key ACTIVE; giữ tương thích đơn phiên bản)",
    "hmac_key_version": "string | null (phiên bản của endpoint_lookup_hash đơn lẻ)",
    "endpoint_hashes_by_version": [
      {
        "hmac_key_version": "string (NN — toàn bộ phiên bản ACTIVE + VERIFY_ONLY của endpoint_lookup_hmac_key trong cửa sổ xoay khóa)",
        "hash": "string (char(64) NN — HMAC-SHA256 của chuỗi Unicode NFKC canonical theo ADR-007: EMAIL trim().lowercase(); PHONE E.164; UID <provider>:<namespace>:<id>)"
      }
    ],
    "sender_profile_id": "uuid | null (bắt buộc non-null cho EMAIL / SMS / ZALO để kiểm định danh & Opt-out)",
    "connection_id": "uuid (NN)",
    "correlation_id": "uuid (NN)"
  },
  "OutboundComplianceDecision": {
    "decision": "ALLOW | BLOCK",
    "block_reason_code": "null | OUTBOUND_SUPPRESSED_UNSUBSCRIBE | OUTBOUND_SUPPRESSED_CONSENT_REVOKED | OUTBOUND_SUPPRESSED_HARD_BOUNCE | OUTBOUND_SUPPRESSED_SOFT_BOUNCE_COOLDOWN | OUTBOUND_SUPPRESSED_SPAM_COMPLAINT | OUTBOUND_SUPPRESSED_REFUSED_CALLBACK | OUTBOUND_SUPPRESSED_MANUAL_DNC | OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD | PRIVACY_PURPOSE_UNAPPROVED | SENDER_PROFILE_UNVERIFIED | MISSING_HMAC_KEY_VERSION",
    "suppression_id": "uuid | null",
    "matched_hmac_key_version": "string | null",
    "consent_state_version": "integer | null",
    "evaluated_at": "timestamptz (UTC)",
    "audit_ref": "uuid (NN)"
  }
}
```

**Ví dụ (`Example`) `EvaluateOutboundComplianceInput` & `OutboundComplianceDecision`:**

```json
{
  "ExampleEvaluateOutboundComplianceInput": {
    "tenant_id": "22222222-2222-4222-8222-222222222222",
    "workspace_id": "33333333-3333-4333-8333-333333333333",
    "actor_id": "11111111-1111-4111-8111-111111111111",
    "actor_type": "SERVICE_PRINCIPAL",
    "check_stage": "DISPATCH_AUTHORITATIVE",
    "channel": "EMAIL",
    "purpose_code": "MARKETING_NEWSLETTER",
    "message_category": "MARKETING_PROMO",
    "contact_id": "88888888-8888-4888-8888-888888888888",
    "endpoint_lookup_hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "hmac_key_version": "kv-2026-11-active",
    "endpoint_hashes_by_version": [
      {
        "hmac_key_version": "kv-2026-11-active",
        "hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
      }
    ],
    "sender_profile_id": "99999999-9999-4999-8999-999999999999",
    "connection_id": "77777777-7777-4777-8777-777777777777",
    "correlation_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
  },
  "ExampleOutboundComplianceDecision": {
    "decision": "BLOCK",
    "block_reason_code": "OUTBOUND_SUPPRESSED_CONSENT_REVOKED",
    "suppression_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    "matched_hmac_key_version": "kv-2026-11-active",
    "consent_state_version": 3,
    "evaluated_at": "2026-11-16T10:00:00Z",
    "audit_ref": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
  }
}
```

**Thứ tự kiểm tra 5 bước (`Fail-Closed`):**
1. **Bước 1 (Erasure & Suppression Cứng Đa Phiên bản HMAC):** Bắt buộc `endpoint_hashes_by_version[]` bao phủ đủ toàn bộ các phiên bản `ACTIVE + VERIFY_ONLY` của `endpoint_lookup_hmac_key` hiện có cho Tenant (nếu đang xoay khóa mà thiếu phiên bản `ACTIVE` hoặc `VERIFY_ONLY` $\rightarrow$ `BLOCK (MISSING_HMAC_KEY_VERSION)`). Đối khớp đồng thời toàn bộ cặp `(hmac_key_version, hash)` trong `endpoint_hashes_by_version[]` (kèm tương thích ngược `endpoint_lookup_hash` đơn lẻ khi chỉ có 1 phiên bản) trên:
   - **`Deletion_Ledger`**: nếu khớp bản ghi xóa trong `workspace_id` hoặc bản ghi `scope_tenant_wide = true` thuộc phạm vi `AGENCY` Controller (kiểm tra an toàn qua hàm predicate không lộ dữ liệu workspace khác theo `OC03`, trừ giao dịch hợp đồng pháp lý được miễn trừ theo `Legal_Holds` hợp lệ) $\rightarrow$ `BLOCK (OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD)`.
   - **`Endpoint_Suppressions (status = 'ACTIVE')`**: nếu khớp bất kỳ phiên bản khóa nào (`ACTIVE` lẫn `VERIFY_ONLY`) trong đúng `channel + purpose_scope` (`OC17`: không chặn `TRANSACTIONAL_TICKET_OR_APPOINTMENT` khi khách chỉ rút `MARKETING_PROMO`) $\rightarrow$ `BLOCK` trả đúng mã tương ứng với `reason_code` (`OUTBOUND_SUPPRESSED_UNSUBSCRIBE | OUTBOUND_SUPPRESSED_CONSENT_REVOKED | OUTBOUND_SUPPRESSED_HARD_BOUNCE | OUTBOUND_SUPPRESSED_SOFT_BOUNCE_COOLDOWN | OUTBOUND_SUPPRESSED_SPAM_COMPLAINT | OUTBOUND_SUPPRESSED_REFUSED_CALLBACK | OUTBOUND_SUPPRESSED_MANUAL_DNC`) kèm `matched_hmac_key_version`, bảo đảm không bao giờ bỏ lọt `UNSUBSCRIBE`/`HARD_BOUNCE` cũ khi xoay khóa (`CRITICAL-04`).
2. **Bước 2 (`Processing_Records` Gate):** Nếu `Processing_Records` cho `purpose_code` trong `workspace_id` (hoặc `workspace_id IS NULL` đối với luồng Agency/Worker dùng chung khi `workspace_type IN ('AGENCY', 'SYSTEM')`) chưa đạt `ACTIVE` (hoặc `PROCESSOR` thiếu `dpa_contract_ref` theo `O06`) $\rightarrow$ `BLOCK (PRIVACY_PURPOSE_UNAPPROVED)`.
3. **Bước 3 (`Consent_State` Gate):** Nếu `message_category IN ('MARKETING_PROMO', 'SURVEY_VOC', 'AUTOMATED_JOURNEY')` $\rightarrow$ đối khớp `(hmac_key_version, endpoint_lookup_hash)` theo `endpoint_hashes_by_version[]`; bắt buộc bản ghi hiệu lực mới nhất của `Consent_State (channel, hmac_key_version, endpoint_lookup_hash, purpose_code).status == 'GRANTED'` (nếu `REVOKED | EXPIRED | UNKNOWN` hoặc từng có `REVOKE` chưa được cấp lại hợp lệ ở phiên bản mới $\rightarrow$ `BLOCK (OUTBOUND_SUPPRESSED_CONSENT_REVOKED)`). *(Miễn Bước 3 Consent tiếp thị cho `channel = 'WEBHOOK'` có `message_category IN ('TRANSACTIONAL_TICKET_OR_APPOINTMENT', 'TASK_SYNC', 'SYSTEM_SYNC')` không mang PII marketing).*
4. **Bước 4 (Legal Hold vs Notification Rules):** Nếu `contact_id` có `cardinality(active_legal_hold_ids) > 0` / đang trong `Legal_Holds (status = 'ACTIVE')`, kiểm xem tin gửi có vi phạm phạm vi tạm dừng tiếp thị/xử lý (`RESTRICT`) hay không (`M20-F04`); nếu vi phạm phạm vi hold/`RESTRICT` $\rightarrow$ `BLOCK (OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD)`.
5. **Bước 5 (Sender Profile Gate cho `EMAIL / SMS / ZALO`):** Với `EMAIL`, kiểm `sender_profile_id` đã verify `SPF / DKIM / DMARC` và nhúng token `List-Unsubscribe` / `PublicOneClickUnsubscribe`; với `SMS`, kiểm Brandname / Sender ID đã đăng ký nhà mạng còn `ACTIVE` và cú pháp từ chối (`Opt-out`); với `ZALO`, kiểm `OA_ID` hợp lệ và mẫu ZBS tương ứng đúng `purpose_code` theo năng lực đã kiểm chứng (`OM-G01` & `M19-F03 Connection_Capabilities.verified_policy_manifest_version`, giữ `GAP-M19-03` fail-closed cho webhook Zalo và tách riêng `GAP-M19-04` cho Meta Tags); thiếu hoặc `NULL` khi bắt buộc $\rightarrow$ `BLOCK (SENDER_PROFILE_UNVERIFIED)`. *(Với `channel = 'WEBHOOK'` có `message_category IN ('TRANSACTIONAL_TICKET_OR_APPOINTMENT', 'TASK_SYNC', 'SYSTEM_SYNC')` không mang PII marketing như ERP/Bank/PMS: giữ nguyên Bước 1 [`Deletion_Ledger` + `Endpoint_Suppressions`], Bước 2 [`Processing_Records`], và Bước 4 [`Legal_Hold`]; miễn Bước 3 Consent tiếp thị & Bước 5 Sender Profile `EMAIL/SMS/ZALO`).*

### 2.2. `EvaluateVendorAndAiTransferInput` & `VendorTransferDecision` (`U22`, `INT28`, `OC20`, `RV17`)

```json
{
  "EvaluateVendorAndAiTransferInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "actor_id": "uuid (NN — dùng cho kiểm tra vault.actor_id == caller_id & M14 check khi DetokenizePlaceholderVault)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "feature_code": "AI_SUMMARY | AI_DRAFT | AI_SUGGEST | AI_TRANSCRIBE | M19_EXTERNAL_WEBHOOK | M21_PARTNER_SYNC | REMOTE_VENDOR_API",
    "source_provider": "string | null (mã provider nguồn từ M19/M06 để đối chiếu bảng chuẩn hóa provider -> vendor_code)",
    "vendor_code": "string (NN — chuẩn hóa theo mapping provider -> vendor_code, ví dụ PAYMENT_GW, ERP_MISA, PAYROLL_BANK, OPENAI, GOOGLE_GEMINI)",
    "processing_record_id": "uuid (NN)",
    "source_resource_type": "string | null (khớp tập resource_type trong C14; bắt buộc NN khi tạo Placeholder_Vault cho AI_*)",
    "source_resource_id": "uuid | null (bắt buộc NN khi tạo Placeholder_Vault cho AI_*)",
    "data_classes": [
      "PUBLIC_META | INTERNAL_NOTES | CONVERSATION_TEXT | CONTACT_PII_PHONE_EMAIL | NATIONAL_ID_CCCD | BANK_ACCOUNT_OR_PAYMENT | HRM_PAYROLL | CALL_RECORDING_RAW"
    ],
    "payload_text_or_ref": "string (NN)",
    "payload_provenance": "INTERNAL_SYSTEM | CUSTOMER_MESSAGE | EXTERNAL_ATTACHMENT_TEXT",
    "allow_placeholder_pseudonymization": "boolean (default true)",
    "correlation_id": "uuid (NN)"
  },
  "VendorTransferDecision": {
    "decision": "ALLOW | ALLOW_WITH_REDACTION | BLOCK",
    "reason_code": "null | PRIVACY_PURPOSE_UNAPPROVED | VENDOR_TRANSFER_POLICY_BLOCKED | PROHIBITED_DATA_CLASS_INCLUDED | AI_PROMPT_TOOL_POLICY_BLOCKED",
    "vendor_flow_id": "uuid | null",
    "vendor_flow_version_no": "integer | null",
    "dlp_scanned": "boolean",
    "training_opt_out": "boolean",
    "zero_data_retention": "boolean",
    "vendor_log_retention_days": "integer",
    "redacted_payload_text_or_ref": "string | null",
    "placeholder_session_correlation_id": "uuid | null",
    "untrusted_data_fenced": "boolean",
    "placeholder_ttl_expires_at": "timestamptz | null",
    "fallback_manual_mode": "string | null",
    "evaluated_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Cứng `FR13` / `6.3 L3174` / `6.8 L3257` / `U22` / `INT28` / `OC20`:**
> - **Phân tách `AI_*` vs Tích hợp Nghiệp vụ (`M19_EXTERNAL_WEBHOOK` / `REMOTE_VENDOR_API`):**
>   - Rule trả ngay `BLOCK (PROHIBITED_DATA_CLASS_INCLUDED)` đối với `NATIONAL_ID_CCCD | BANK_ACCOUNT_OR_PAYMENT | HRM_PAYROLL` **CHỈ áp dụng cho nhóm AI chung `feature_code IN ('AI_SUMMARY', 'AI_DRAFT', 'AI_SUGGEST', 'AI_TRANSCRIBE')`** (`Master 6.8`: cấm đưa hồ sơ nhân sự/lương/CCCD/ngân hàng vào AI chung).
>   - Với `feature_code IN ('AI_SUMMARY', 'AI_DRAFT', 'AI_SUGGEST', 'AI_TRANSCRIBE')`: **BẮT BUỘC chạy server-side DLP scanner** quét `payload_text_or_ref` trước khi gửi (không tin thuần túy mảng `data_classes[]` do client tự khai báo — `Master 6.3 L3174`); nếu bộ quét DLP phát hiện mẫu CCCD/tài khoản ngân hàng/bảng lương thô $\rightarrow$ trả ngay `BLOCK (PROHIBITED_DATA_CLASS_INCLUDED)`.
>   - Ngược lại, với **`feature_code IN ('M19_EXTERNAL_WEBHOOK', 'M21_PARTNER_SYNC', 'REMOTE_VENDOR_API')`** (các luồng thanh toán/kế toán/chi lương chính danh như `M09 Payment/ERP_MISA` hay `M22-F28 PAYROLL_BANK`): cho phép đi qua chuỗi đánh giá đầy đủ: (1) `Processing_Records == ACTIVE` (nếu `PROCESSOR` bắt buộc `dpa_contract_ref`), (2) `Vendor_Data_Flows == APPROVED` khớp mapping chuẩn hóa `provider -> vendor_code`, có **`dpa_signed_ref IS NOT NULL`**, và (3) **toàn bộ `data_classes[]` nằm trong whitelist `Vendor_Data_Flows.allowed_data_classes`** (không chạm `prohibited_data_classes`).
> - Nếu `Processing_Records` chưa đạt `ACTIVE` (hoặc `PROCESSOR` thiếu `dpa_contract_ref`): trả ngay `BLOCK (PRIVACY_PURPOSE_UNAPPROVED)` kèm `fallback_manual_mode`.
> - Nếu `Vendor_Data_Flows` chưa ở `APPROVED`, lệch chuẩn mapping `provider -> vendor_code`, thiếu `dpa_signed_ref` khi truyền dữ liệu nhạy cảm, vi phạm whitelist `allowed_data_classes`, hoặc không đáp ứng `zero_data_retention` / căn cứ xuyên biên giới theo chính sách: trả `BLOCK (VENDOR_TRANSFER_POLICY_BLOCKED)` (hoặc `PROHIBITED_DATA_CLASS_INCLUDED` khi vượt danh mục `allowed_data_classes`) kèm `fallback_manual_mode`. Không coi `training_opt_out = true` là `zero_data_retention = true` (`RV17`).
> - Nếu `payload_provenance IN ('CUSTOMER_MESSAGE', 'EXTERNAL_ATTACHMENT_TEXT')`: luôn gắn `untrusted_data_fenced = true` và khóa cứng không cho phép lời nhắc trong nội dung khách kích hoạt tool đột biến (`U22`, `INT28`). Khi tạo token che danh tính ở `Placeholder_Vault`, bắt buộc lưu đủ `actor_id`, `source_resource_type`, `source_resource_id`, `UNIQUE (tenant_id, workspace_id, session_correlation_id, placeholder_token)`; khi gọi `DetokenizePlaceholderVault` bắt buộc kiểm **`vault.actor_id == caller_id`** (đúng `tenant_id`, `workspace_id`, `expires_at > now()`) **VÀ** gọi `M14.EvaluateAccessDecision` cho đúng `caller_id` lên **`(vault.source_resource_type, vault.source_resource_id)`**.

### 2.3. `VerifyPostRestoreComplianceGateInput` & `PostRestoreComplianceGateResult` (`INT26`, `OC19`, `U21`, `ADR-007`)

```json
{
  "VerifyPostRestoreComplianceGateInput": {
    "restore_run_id": "uuid (NN)",
    "tenant_id": "uuid | null (NULL khi điều phối fan-out toàn bộ Tenants -> Workspaces dưới BindDbTransactionContext)",
    "workspace_id": "uuid | null (chỉ định từng workspace trong đợt fan-out; NULL chỉ dùng cho bảng cấp Tenant dưới maintenance_compliance_role — DB role chuyên biệt NOBYPASSRLS / NOSUPERUSER đã khóa phạm vi trong ADR-005 / ADR-007 chỉ chạy fan-out DR Gate cho bảng workspace_id IS NULL dưới BindDbTransactionContext)",
    "backup_point_in_time": "timestamptz (UTC, mốc snapshot DB vừa khôi phục)",
    "dry_run": "boolean (default false)",
    "hmac_key_versions_available": [
      "string (đầy đủ phiên bản ACTIVE + VERIFY_ONLY của cả deletion_ledger_hmac_key và endpoint_lookup_hmac_key)"
    ],
    "security_reconciliation_completed": "boolean (bắt buộc true — xác nhận đã hoàn tất Bước 1 LOCK_ALL + Bước 2 M14 PITR #6 Security_Revocation_Ledger, leapfrog acl_epoch/permission_version, thu hồi 100% sessions M23-F02, xóa 100% cache M24-F06, xử lý timer hết hạn thời gian đơn thuần M16 offer/hold timeout & thông báo quá hạn sang EXPIRED_DR_SKIPPED, và re-lock Vendor_Data_Flows/Channel_Connections dính Data_Incident trong RPO)",
    "initiated_by": "uuid (NN)",
    "correlation_id": "uuid (NN)"
  },
  "PostRestoreComplianceGateResult": {
    "restore_run_id": "uuid",
    "gate_status": "PASSED | BLOCKED",
    "reapplied_erasure_count": "integer (>= 0)",
    "reapplied_suppression_count": "integer (>= 0)",
    "reapplied_consent_revokes_count": "integer (>= 0)",
    "reapplied_legal_holds_count": "integer (>= 0)",
    "reapplied_vendor_freezes_count": "integer (>= 0)",
    "cancelled_outbound_intents_count": "integer (>= 0)",
    "cancelled_internal_outbox_count": "integer (>= 0)",
    "cancelled_internal_notifications_count": "integer (>= 0)",
    "pending_reapply_count": "integer (0 mới PASSED — bắt buộc kiểm TRƯỚC khi replay M23-F12)",
    "hmac_keys_verified": "boolean",
    "blocked_reason": "null | MISSING_HMAC_KEY_VERSION | PENDING_REAPPLY_NONZERO | INDEPENDENT_LEDGER_UNREACHABLE | SECURITY_RECONCILIATION_PENDING",
    "verified_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Kiểm duyệt `VerifyPostRestoreComplianceGate` — Phân tách Bước 2 vs Bước 3 trong `DR Startup Fence` (`INT26`, `OC19`, `ADR-005`, `ADR-007`):**
> 1. **Bước 2 (`M14` + Hạ tầng — Kiểm điều kiện `SECURITY_RECONCILIATION_PENDING`):** Bắt buộc **`security_reconciliation_completed == true`** xác nhận trước khi gọi Bước 3 hệ thống đã: (a) khóa 3 làn Worker (`M19`, `M23-F12`, `M24-F05/F06/F08`) + `M16` Schedulers ở Bước 1, (b) chạy `M14` PITR #6 **`M14.Security_Revocation_Ledger`** + leapfrog `acl_epoch / permission_version` vượt mốc trước sự cố, (c) thu hồi 100% active sessions qua `M23-F02` & xóa 100% cache `M24-F06`, (d) chỉ xử lý **timer hết hạn thời gian đơn thuần** (`M16` offer/hold timeout, thông báo nhắc việc quá hạn thời gian sang `EXPIRED_DR_SKIPPED` — chưa chạm mục cần đối soát compliance), và (e) re-lock `Vendor_Data_Flows`/`Channel_Connections` dính `Data_Incident` trong `RPO`; nếu Bước 2 chưa hoàn tất $\rightarrow$ `BLOCKED (SECURITY_RECONCILIATION_PENDING)`.
> 2. **Bước 3 (`VerifyPostRestoreComplianceGate` — Kiểm đủ `6` bảng PITR/WAL & Đa khóa HMAC):** Kết nối kho PITR/WAL độc lập kiểm đủ **`6` bảng PITR/WAL** (**`5` bảng `M20/M23`**: `Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`, `M23.Audit_Logs` + **`1` bảng `M14.Security_Revocation_Ledger`**); nếu không truy cập được $\rightarrow$ `BLOCKED (INDEPENDENT_LEDGER_UNREACHABLE)`. Kiểm mọi `hmac_key_version` trên `Deletion_Ledger` (`deletion_ledger_hmac_key`) và `Endpoint_Suppressions`/`Consent_Logs`/`Consent_State`/`Privacy_Requests`/`M19.Outbound_Intents` (`endpoint_lookup_hmac_key`) đều hiện diện trong `hmac_key_versions_available[]` (gồm cả `ACTIVE` lẫn `VERIFY_ONLY`); thiếu bất kỳ phiên bản nào $\rightarrow$ `BLOCKED (MISSING_HMAC_KEY_VERSION)` + `hmac_keys_verified = false`.
> 3. **Bước 3 (Fan-out dưới `maintenance_compliance_role` & Hủy Phần tử Vi phạm Compliance TRƯỚC Bước 4 Replay `M23-F12`):** Chạy fan-out theo danh sách **`Tenants -> Workspaces`** dưới `BindDbTransactionContext`, sử dụng **`maintenance_compliance_role`** (DB role chuyên biệt **`NOBYPASSRLS / NOSUPERUSER / NOINHERIT`** đã khóa phạm vi trong `ADR-005`/`ADR-007` — chỉ chạy fan-out DR Gate cho bảng cấp Tenant `workspace_id IS NULL` dưới `BindDbTransactionContext(workspace_type = 'SYSTEM', acting_mode = 'SYSTEM_WORKER')`, tuyệt đối không cấp `BYPASSRLS`).
>    - Nếu `dry_run = true`: chỉ tính số bản ghi chênh lệch so với snapshot vừa restore mà **không ghi đè bảng nghiệp vụ**.
>    - Nếu `dry_run = false`: chạy idempotent theo `(restore_run_id, source_table, source_record_id)` áp lại 100% erasure (`Deletion_Ledger`), suppression (`Endpoint_Suppressions`), consent-revokes (`Consent_Logs` tái dựng `Consent_State`), `active_legal_hold_ids[]` (`Legal_Holds`), và vendor freezes (`Data_Incidents`); đồng thời **hủy toàn bộ phần tử vi phạm compliance (erasure / suppression / revoked consent / legal hold)** trên **`M19.Outbound_Intents` (`cancelled_outbound_intents_count`)**, **`M23-F12.Internal_Outbox_Events` (`cancelled_internal_outbox_count`)**, và **`M24.Internal_Notifications` (`cancelled_internal_notifications_count`)**.
>    - **Chỉ trả `PASSED` khi `pending_reapply_count == 0` & `hmac_keys_verified == true`** — **SAU ĐÓ mới chuyển sang Bước 4 replay `M23-F12.Internal_Outbox_Events`** hợp lệ còn lại và mở lại Worker ở Bước 5.

### 2.4. `EvaluateAssetDownloadPrivacyGateInput` & `AssetPrivacyGateDecision` (`SEC03`, `ADR-006`)

```json
{
  "EvaluateAssetDownloadPrivacyGateInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN — workspace ngữ cảnh phiên của actor)",
    "target_workspace_id": "uuid | null (workspace sở hữu thực tế khi truy cập qua bridge AGENCY <-> CLIENT)",
    "actor_id": "uuid (NN)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT",
    "asset_id": "uuid (NN)",
    "asset_version_id": "uuid (NN — phiên bản cụ thể đang yêu cầu tải trong Shared Asset_Versions)",
    "asset_domain": "CRM_ATTACHMENT | CALL_RECORDING | EXPORT_BUNDLE | HRM_EMPLOYEE_DOCUMENT | CONTRACT_OR_FINANCE_DOC",
    "owner_resource_type": "string (NN — khớp resource_type trong C14, ví dụ EXPORT_REQUEST | DELIVERABLE | TASK | CONTRACT | TICKET | EMPLOYEE | CONVERSATION)",
    "owner_resource_id": "uuid (NN — với EXPORT_BUNDLE trỏ Export_Requests.id hoặc đối ứng Export_Requests.asset_id)",
    "correlation_id": "uuid (NN)"
  },
  "AssetPrivacyGateDecision": {
    "decision": "ALLOW | BLOCK",
    "block_reason_code": "null | ASSET_QUARANTINED_OR_INFECTED | ASSET_PRIVACY_HOLD_OR_ERASED | ASSET_RETENTION_EXPIRED | HRM_CONFIDENTIALITY_BLOCKED",
    "legal_hold_status": "NONE | RESTRICTED_LEGAL_HOLD",
    "active_legal_hold_ids": ["uuid"],
    "requires_watermark": "boolean",
    "evaluated_at": "timestamptz (UTC)"
  }
}
```

> **Thứ tự Kiểm duyệt & Ranh giới `SEC03` (`ADR-006` Bước 2 vs Bước 3):**
> - **Bước 1 (Quarantine / Malware theo Phiên bản `INT24`):** Kiểm tra trực tiếp tại **`Asset_Versions.scan_status`** của đúng `asset_version_id` thuộc `asset_id` (Shared Platform Asset Registry tại `M23`): nếu **`Asset_Versions.scan_status <> 'CLEAN'`** $\rightarrow$ `BLOCK (ASSET_QUARANTINED_OR_INFECTED)`.
> - **Bước 2 (Erasure & `active_legal_hold_ids` trên CẢ `Asset` lẫn `Owner Resource`):**
>   - Kiểm tra `Deletion_Ledger` theo **cả** `asset_id`/`asset_version_id` **lẫn** `(owner_resource_type, owner_resource_id)` trong phạm vi `coalesce(target_workspace_id, workspace_id)` (hoặc `scope_tenant_wide = true` tại `AGENCY`); riêng `EXPORT_BUNDLE` kiểm đối chiếu `Export_Requests` (gắn `Export_Requests.asset_id == asset_id`) xem yêu cầu export đã bị thu hồi sau `SubjectErasureExecuted` hay chưa. Nếu đã bị xóa/thu hồi $\rightarrow$ `BLOCK (ASSET_PRIVACY_HOLD_OR_ERASED)`.
>   - Kiểm tra `Legal_Holds (status = 'ACTIVE')` và mảng **`active_legal_hold_ids uuid[]`** trên **cả** `ASSET` (`target_id = asset_id`) **lẫn** `(owner_resource_type, owner_resource_id)` (`PROJECT`, `DELIVERABLE`, `TASK`, `CONTRACT`, `PAYMENT`, `TICKET`, `INCIDENT`, `EMPLOYEE`, v.v.). Nếu `cardinality(active_legal_hold_ids) > 0`: vai trò ngoài nhóm `LEGAL_HOLD_READ` $\rightarrow$ `BLOCK (ASSET_PRIVACY_HOLD_OR_ERASED)`; nếu được phép đọc đối chiếu $\rightarrow$ trả `legal_hold_status = 'RESTRICTED_LEGAL_HOLD'`, `active_legal_hold_ids = [...]` & `requires_watermark = true`.
> - **Bước 3 (`Retention_Policies`):** Nếu tệp đã quá hạn lưu giữ (`ACTIVE` retention policy cho `asset_domain` tương ứng, gồm `WORK_TASK_ARTIFACTS`, `CALL_RECORDING`, `CONTRACT_ACCOUNTING`, `HRM_RECORD`) chờ purge $\rightarrow$ `BLOCK (ASSET_RETENTION_EXPIRED)`.
> - **Bước 4 (`Master 6.8`, `ENTITY-L3031` & Cross-Workspace `AGENCY <-> CLIENT` Guard):** Kiểm quy tắc bảo mật hồ sơ nhân sự/CCCD/bảng lương theo `6.8` (cấm AI/tìm kiếm đại trà/role thường truy xuất trái phạm vi) và chặn `actor_type = 'PORTAL_CLIENT'` nếu `target_workspace_id` / `(owner_resource_type, owner_resource_id)` không thuộc phạm vi `CLIENT` hợp lệ $\rightarrow$ `BLOCK (HRM_CONFIDENTIALITY_BLOCKED)`.
> - **Watermark & Ranh giới Bước 3 (`M23-F07`):** Đặt `requires_watermark = true` với `EXPORT_BUNDLE`, `HRM_EMPLOYEE_DOCUMENT`, `CONTRACT_OR_FINANCE_DOC` hoặc khi `legal_hold_status = 'RESTRICTED_LEGAL_HOLD'`. Kiểm tra hạn link `download_expires_at` (`EXPORT_LINK_EXPIRED`), header `Cache-Control: no-store` và ghi event `AssetDownloaded` thuộc **Bước 3 (`M23-F07`)** sau khi Bước 1 (`M14`) & Bước 2 (`M20`) đều trả `ALLOW` (`ADR-006 L22`).

---

## 3. Domain Events Phát hành & Tiêu thụ (Qua Internal Outbox `M23-F12`)

### 3.1. Envelope Chuẩn Mọi Sự kiện `M20` (`schema_version = "1.1"`)

Dùng chung cấu trúc chuẩn (`event_id`, `event_type`, `aggregate_type`, `aggregate_id`, `aggregate_version`, `schema_version`, `tenant_id`, `workspace_id` [`uuid | null`, `NULL` khi sự kiện phạm vi toàn Tenant như `SubjectErasureExecuted` / `LegalHoldChanged Nhóm B-Governance-Sensitive`], `occurred_at`, `correlation_id`, `causation_id`, `payload`).

```json
{
  "event_id": "uuid (NN)",
  "event_type": "M20.EndpointSuppressed | M20.SubjectErasureExecuted | M20.LegalHoldChanged | M20.DataIncidentEscalated",
  "aggregate_type": "ENDPOINT_SUPPRESSION | PRIVACY_REQUEST | LEGAL_HOLD | DATA_INCIDENT",
  "aggregate_id": "uuid (NN)",
  "aggregate_version": "integer (bigint >= 1)",
  "schema_version": "1.1",
  "tenant_id": "uuid (NN)",
  "workspace_id": "uuid | null",
  "occurred_at": "timestamptz (UTC NN)",
  "correlation_id": "uuid (NN)",
  "causation_id": "uuid | null",
  "payload": {
    "scope_tenant_wide": "boolean",
    "detail_note": "Object field-map cụ thể theo từng dòng Sự kiện §3.2"
  }
}
```

### 3.2. Danh mục Sự kiện Phát hành (`Published Events`)

| Event Name | Payload Trọng yếu | Consumers Bắt buộc | Hành động Phải thực thi |
|---|---|---|---|
| `M20.EndpointSuppressed` | `suppression_id`, `parent_suppression_group_id`, `scope_tenant_wide`, `channel`, `endpoint_lookup_hash`, `hmac_key_version`, `purpose_scope[]`, `reason_code`, `effective_at` | `M19`, `M01`, `M03`, `M04`, `M12`, `M21` | `M19` hủy toàn bộ `Outbound_Intents` đang xếp hàng (`QUEUED`/`RETRY_WAITING`) khớp `endpoint_lookup_hash + hmac_key_version + channel + purpose_scope`; `M04` dừng nhánh Journey tiếp thị; `M01`/`M03`/`M12`/`M21` đồng bộ trạng thái DNC trên UI (`OC17`, `RV17`); trường hợp fan-out `Controller` phát đủ cho từng workspace thuộc phạm vi `Controller` |
| `M20.SubjectErasureExecuted` | `privacy_request_id`, `deletion_ledger_id`, `subject_hmac_sha256`, **`erased_subject_refs` (`[{"subject_type": "...", "subject_id": "uuid", "workspace_id": "uuid \| null"}]`)**, **`endpoint_hmac_hashes_by_version[]` (`[{"hmac_key_version": "...", "hash": "..."}]`)**, `hmac_key_version`, `erased_scopes[]`, `retained_legal_hold_scopes[]`, `scope_tenant_wide` | `M01`, `M02`, `M03`, `M06`, `M11`, `M12`, **`M14`**, `M16`, `M18`, `M19`, `M21`, `M22`, **`M23`**, **`M24`** | Truyền an toàn `erased_subject_refs[]` qua Internal Outbox nội bộ (không ghi plaintext ra log `NFR11`). `M19` hủy `Outbound_Intents` khớp `endpoint_hmac_hashes_by_version[]` + xóa raw payload cache; `M06` xóa `Placeholder_Vault`/vector index; **`M14`** thu hồi grants/bridges liên quan & bump `permission_version`; **`M16`** truy tìm đủ chủ thể qua `Task_Links`/`subject_hmac_sha256`/nội dung để ẩn danh comment & scrub PII **đa lần có kiểm soát theo từng `deletion_ledger_id`** trên `Task_Submissions` (`redacted_deletion_ledger_ids[]`, tăng `privacy_redaction_count`, cập nhật `privacy_redacted_at` & `redacted_content_sha256`, giữ nguyên `content_sha256` gốc khi `cardinality(active_legal_hold_ids) = 0` — `W1-01`); **`M23`** thu hồi `Export_Requests` chứa dữ liệu chủ thể & xóa/ẩn danh `Assets`/`Asset_Versions` ngoài hold; **`M18`/`M21`/`M24`** cập nhật projection sang `REDACTED-SUBJECT-#...` và xóa cache read-model `M24-F06`; `M22-F27` kiểm tra hold lao động |
| `M20.LegalHoldChanged` | `legal_hold_id`, `hold_code`, `target_scope_type` (`... \| PROJECT \| DELIVERABLE \| TASK`), `target_id`, `status` (`ACTIVE \| RELEASED`), `review_due_at` | `M14`, `M08`, `M09`, **`M16`**, `M18`, `M21`, `M22` | Consumers cập nhật mảng **`active_legal_hold_ids uuid[]`** (`ACTIVE` thêm `legal_hold_id`, `RELEASED` gỡ `legal_hold_id`, chỉ thoát `RESTRICTED_LEGAL_HOLD` khi mảng rỗng); `M14` bật/tắt cờ `RESTRICTED_LEGAL_HOLD` trong ACL & bump `permission_version`; `M08`/`M09`/`M16`/`M22` khóa xóa vật lý/scrub trên thực thể (gồm `Projects/Deliverables/Tasks`); `M18`/`M21` ẩn danh báo cáo ngoài phạm vi audit |
| `M20.DataIncidentEscalated` | `incident_id`, `severity` (`S1 \| S2 \| S3`), `awareness_at`, `notification_due_at`, `affected_connection_ids[]`, `affected_vendor_flow_ids[]`, `affected_actor_ids[]` | `M14`, `M19`, `M23-F08`, `M23-F02` | `M19` tạm ngắt/thu hồi token kết nối liên quan; `M20-F07` đóng băng `Vendor_Data_Flows` liên quan; `M14` & `M23-F02` thu hồi phiên & khóa user nghi lộ; `M23-F08` bật cảnh báo an ninh khẩn |

### 3.3. Danh mục Sự kiện `M20` Tiêu thụ (`Subscribed Events`)

- **`M14.WorkspaceActivated`:** Kiểm tra & khởi tạo yêu cầu rà soát `Processing_Records` + DPA khi bật `CLIENT workspace` (`O06`).
- **`M19.MessageReceiptUpdated` (`BOUNCED_HARD | BOUNCED_SOFT | COMPLAINED`):** Tiếp nhận sự kiện receipt từ `M19` (đã được `M19-F04` ingest bất biến vào `Email_Delivery_Events`/`Message_Status_Events` và được `M19` làm giàu sẵn `channel`, `purpose_code`, `hmac_key_version`, `endpoint_masked | null` trước khi phát) để `M20-F03` ghi/cập nhật **`Endpoint_Suppressions`** (`purpose_scope` lấy theo `purpose_code` hoặc `["ALL"]` khi `BOUNCED_HARD`/`COMPLAINED`; cho phép `endpoint_masked NULL` nếu kênh chỉ trả hash) theo cơ chế đếm `Soft-Bounce` (`[OPEN-GAP: GAP-M20-04]`) hoặc chặn tức thì (`Hard-Bounce`, `Spam Complaint`) mà **không truy vấn chéo DB `M19`** (`INDEX.md L62`).
