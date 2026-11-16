# Contract `M20-SUPPRESSION-PRIVACY-GATE` — Cổng Kiểm duyệt Gửi tin, Legal Hold, AI/Vendor, File Privacy & Phục hồi

- **Contract ID:** `CONTRACT-M20-PRIVACY-GATE-v1.1`
- **Provider Owner:** `M20` (Consent, Mục đích Xử lý, Suppression, Privacy Requests, Legal Hold, Retention & AI Gateway)
- **Consumers:** `M19` (Outbound Dispatch), `M01` (Merge Consent Guard), `M02` (Lead/Import), `M03` (Inbox Compose), `M04` (Journey Dispatch), `M06` (AI Co-Pilot), `M08`/`M09` (Legal Hold Lock), `M11`/`M12` (Ticket vs Survey/Feedback), `M14` (Legal Hold ACL & Download Gateway `SEC03`), `M16`/`M18`/`M21`/`M22` (Erasure & Reporting/HR Gate), `M23-F12`/`M24-F08` (Restore Drill & Async Export)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`2.5 L268 CONTRACT-L0268`, `3.5.3 FR13`, `5.9`, `5.18`, `6.3 L3132–3174`, `6.4 L3178`, `7.3 L3294`, `SEC03`, `SEC05`, `SEC-U05`, `U15`, `U21`, `U22`, `INT17`, `INT26`, `INT28`, `OC03`, `OC17`, `OC19`, `OC20`, `RV16`, `RV17`, `CX-U15`, `CX-U20`), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](../../01-architecture/decisions/ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-008](../../01-architecture/decisions/ADR-008-OMNICHANNEL-CONTRACTS-RECEIPTS-AND-CROSS-EVENTS.md)
- **Trạng thái:** `Reviewed (CR-20261116-WAVE1-RECONCILIATION Applied)`
- **Chính sách Breaking Change:** Thay đổi rule chặn gửi hoặc schema chuyển AI/Restore bắt buộc giữ chế độ Fail-Closed trong `ADR-006`/`ADR-007` và cập nhật đồng thời `M19`, `M14`, `M06`, `M23-F12`.

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | Cung cấp **4 cổng kiểm duyệt Authoritative** của `M20`: (1) `EvaluateOutboundCompliance` (Cổng Kép chặn gửi tại lúc `Enqueue` và tại thời điểm phát tin `DISPATCH_AUTHORITATIVE`), (2) `EvaluateVendorAndAiTransfer` (Cổng Kiểm soát AI Data Gateway, `Placeholder_Vault` & Chống Prompt Injection `U22`/`INT28`), (3) `VerifyPostRestoreComplianceGate` (Hàng rào áp lại `Deletion_Ledger` + `Endpoint_Suppressions` + `Consent_Logs` + `Legal_Holds` sau Restore `INT26`), và (4) `EvaluateAssetDownloadPrivacyGate` (`SEC03` File/Document Privacy & Hold Check phối hợp `M14`). |
| **Actor/scope** | `tenant_id`, `workspace_id` (lưu ý `Deletion_Ledger` & kiểm soát chủ thể xóa hỗ trợ phạm vi toàn `tenant_id` khi Agency là `Controller` hoặc nhiều `CLIENT workspace` cùng email `OC03`), `actor_id` (required trên Vendor/AI & Asset Gate), `channel` đồng bộ 8 giá trị (`EMAIL \| SMS \| ZALO \| FACEBOOK \| TIKTOK \| TELEGRAM \| VOICE_CALL \| WEBHOOK`). |
| **Preconditions** | Endpoint phải được chuẩn hóa canonical trước khi băm `endpoint_lookup_hash` (`ADR-007`: qua bước `Unicode NFKC` $\rightarrow$ `EMAIL: trim().lowercase()` bỏ ký tự điều khiển; `PHONE: E.164`; `PLATFORM_UID: <provider>:<provider_namespace>:<canonical_external_id>`); `Processing_Records` phải đạt `ACTIVE` (nếu `PROCESSOR` bắt buộc có `dpa_contract_ref`); `Vendor_Data_Flows` phải đạt `APPROVED` và phân tách `training_opt_out` vs `zero_data_retention` (`RV17`). |
| **Input** | Xem 4 cặp JSON Schema đầy đủ ở Mục 2 (`EvaluateOutboundComplianceInput`, `EvaluateVendorAndAiTransferInput`, `VerifyPostRestoreComplianceGateInput`, `EvaluateAssetDownloadPrivacyGateInput`). |
| **Output** | Xem 4 JSON Schema đầy đủ ở Mục 2 (`OutboundComplianceDecision` với đúng tên trường `suppression_id`, `consent_state_version`, `evaluated_at`; `VendorTransferDecision`; `PostRestoreComplianceGateResult`; `AssetPrivacyGateDecision`). |
| **Errors** | Chuẩn Error Envelope `{code, message, field_errors, correlation_id}`. Mã chặn đầy đủ khớp 100% 4 JSON schema bên dưới: `OUTBOUND_SUPPRESSED_UNSUBSCRIBE`, `OUTBOUND_SUPPRESSED_CONSENT_REVOKED`, `OUTBOUND_SUPPRESSED_HARD_BOUNCE`, `OUTBOUND_SUPPRESSED_SOFT_BOUNCE_COOLDOWN`, `OUTBOUND_SUPPRESSED_SPAM_COMPLAINT`, `OUTBOUND_SUPPRESSED_REFUSED_CALLBACK`, `OUTBOUND_SUPPRESSED_MANUAL_DNC`, `OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD`, `PRIVACY_PURPOSE_UNAPPROVED`, `SENDER_PROFILE_UNVERIFIED`, `VENDOR_TRANSFER_POLICY_BLOCKED`, `PROHIBITED_DATA_CLASS_INCLUDED`, `AI_PROMPT_TOOL_POLICY_BLOCKED`, `MISSING_HMAC_KEY_VERSION`, `PENDING_REAPPLY_NONZERO`, `INDEPENDENT_LEDGER_UNREACHABLE`, `ASSET_QUARANTINED_OR_INFECTED`, `ASSET_PRIVACY_HOLD_OR_ERASED`, `ASSET_RETENTION_EXPIRED`, `HRM_CONFIDENTIALITY_BLOCKED`. *(Lưu ý: `EXPORT_LINK_EXPIRED` do `M23-F07` kiểm ở Bước 3 Download Gateway theo `ADR-006`)*. |
| **Concurrency** | `EvaluateOutboundCompliance` đọc thẳng Primary DB (Authoritative State, không chờ cache) tại bước `DISPATCH_AUTHORITATIVE`. **Theo Master `6.3 L3172`: tuyệt đối không hứa `0 giây` vật lý hay thu hồi chắc chắn tin mà provider đã nhận (`in-flight`)**; cleanup hàng đợi bất đồng bộ chạy với `SLA` giám sát riêng (`[OPEN-GAP]`). Giao dịch `REVOKE`/`UNSUBSCRIBE` commit `Endpoint_Suppressions` nguyên tử trước khi trả `200/202` (`CONTRACT-L0268`). |
| **Idempotency** | Các hàm `Evaluate*` không ghi đột biến nghiệp vụ (chỉ ghi audit chặn/tạo phiên `Placeholder_Vault` theo `correlation_id`). `VerifyPostRestoreComplianceGate` chạy idempotent tuyệt đối theo khóa tổng hợp `(restore_run_id, source_table, source_record_id)` (bao phủ `Deletion_Ledger` [`deletion_ledger_id`], `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`) — chạy lặp 100 lần không sai lệch dữ liệu (`NFR08`, `INT26`). `POST /v1/consents/revoke` yêu cầu `idempotency_key` duy nhất theo `tenant_id` (`5.9 L2701`). |
| **Transaction** | Lệnh `POST /v1/consents/revoke` (`CONTRACT-L0268`) hoặc `PublicOneClickUnsubscribe` (`SEC05`) bắt buộc ghi `Consent_Logs` + cập nhật `Consent_State` + ghi `Endpoint_Suppressions` + ghi `Internal_Outbox_Events` (`M20.EndpointSuppressed`) trong **1 DB transaction nguyên tử**; trả `202 Accepted` nếu còn tác vụ lan truyền hủy `Outbound_Intents` ở `M19` chưa hoàn tất đồng bộ tức thì (`200 OK` nếu xong ngay). |
| **Compatibility** | Hỗ trợ đồng thời nhiều `hmac_key_version` ở chế độ `VERIFY_ONLY` cho `Deletion_Ledger` khi xoay khóa (`ADR-007`). `purpose_code` chuẩn hóa `varchar(80)` khớp Master `5.9 L2692`. |
| **Audit/privacy** | Không lộ PII gốc trong log/error; `PublicOneClickUnsubscribe` không lộ hồ sơ khách; giải mã ngược `Placeholder_Vault` kiểm lại `M14.EvaluateAccessDecision` cho đúng `actor_id` (`6.3 L3174`); **5 bảng bảo vệ PITR/WAL độc lập (`ADR-007`)**: `Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`, `M23.Audit_Logs` (đồng thời `Consent_State` được tái dựng/đối soát từ `Consent_Logs` khi Verify). |
| **Tests** | `M20-AC01..03`, `SEC-U05`, `U15`/`INT17`, `U18`, `U21` (backup restore), `U22` (AI prompt injection), `INT24`, `INT26`, `INT28`, `RV11`, `RV16`, `RV17`, `OC03`, `OC17`, `OC19`, `OC20`, `CX-U12`, `CX-U15`, `CX-U20`, `SEC-U03`. Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas Đầy đủ cho 4 Cổng Kiểm duyệt (`ADR-006`, `ADR-007`, `ADR-008`)

### 2.1. `EvaluateOutboundComplianceInput` & `OutboundComplianceDecision`

```json
{
  "EvaluateOutboundComplianceInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "actor_id": "uuid (NN)",
    "check_stage": "ENQUEUE_PREVIEW | DISPATCH_AUTHORITATIVE",
    "channel": "EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK",
    "purpose_code": "string (max 80 chars, varchar(80) theo Master 5.9)",
    "message_category": "TRANSACTIONAL_TICKET_OR_APPOINTMENT | SERVICE_REPLY | MARKETING_PROMO | SURVEY_VOC | AUTOMATED_JOURNEY",
    "contact_id": "uuid | null (có thể null khi mới có channel identity)",
    "endpoint_lookup_hash": "string (char(64) HMAC-SHA256 của chuỗi Unicode NFKC canonical theo ADR-007: EMAIL trim().lowercase(); PHONE E.164; UID <provider>:<namespace>:<id>)",
    "sender_profile_id": "uuid | null (bắt buộc non-null cho EMAIL / SMS / ZALO để kiểm định danh & Opt-out)",
    "connection_id": "uuid (NN)",
    "correlation_id": "uuid (NN)"
  },
  "OutboundComplianceDecision": {
    "decision": "ALLOW | BLOCK",
    "block_reason_code": "null | OUTBOUND_SUPPRESSED_UNSUBSCRIBE | OUTBOUND_SUPPRESSED_CONSENT_REVOKED | OUTBOUND_SUPPRESSED_HARD_BOUNCE | OUTBOUND_SUPPRESSED_SOFT_BOUNCE_COOLDOWN | OUTBOUND_SUPPRESSED_SPAM_COMPLAINT | OUTBOUND_SUPPRESSED_REFUSED_CALLBACK | OUTBOUND_SUPPRESSED_MANUAL_DNC | OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD | PRIVACY_PURPOSE_UNAPPROVED | SENDER_PROFILE_UNVERIFIED",
    "suppression_id": "uuid | null",
    "consent_state_version": "integer | null",
    "evaluated_at": "timestamptz (UTC)",
    "audit_ref": "uuid (NN)"
  }
}
```

**Thứ tự kiểm tra 5 bước (`Fail-Closed`):**
1. **Bước 1 (Erasure & Suppression Cứng):** Nếu `endpoint_lookup_hash` khớp bản ghi xóa ở `Deletion_Ledger` (trừ trường hợp hợp đồng/hồ sơ còn mở giao dịch giao vận pháp lý được miễn trừ theo `Legal_Hold` hợp lệ) $\rightarrow$ `BLOCK (OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD)`. Nếu khớp `Endpoint_Suppressions (status = 'ACTIVE')` trong đúng `channel + purpose_scope` (`OC17`: không chặn `TRANSACTIONAL_TICKET_OR_APPOINTMENT` khi khách chỉ rút `MARKETING_PROMO`) $\rightarrow$ `BLOCK` trả đúng mã tương ứng với `reason_code` (`OUTBOUND_SUPPRESSED_UNSUBSCRIBE | OUTBOUND_SUPPRESSED_CONSENT_REVOKED | OUTBOUND_SUPPRESSED_HARD_BOUNCE | OUTBOUND_SUPPRESSED_SOFT_BOUNCE_COOLDOWN | OUTBOUND_SUPPRESSED_SPAM_COMPLAINT | OUTBOUND_SUPPRESSED_REFUSED_CALLBACK | OUTBOUND_SUPPRESSED_MANUAL_DNC`).
2. **Bước 2 (`Processing_Records` Gate):** Nếu `Processing_Records` cho `purpose_code` trong `workspace_id` chưa đạt `ACTIVE` (hoặc `PROCESSOR` thiếu `dpa_contract_ref` theo `O06`) $\rightarrow$ `BLOCK (PRIVACY_PURPOSE_UNAPPROVED)`.
3. **Bước 3 (`Consent_State` Gate):** Nếu `message_category IN ('MARKETING_PROMO', 'SURVEY_VOC', 'AUTOMATED_JOURNEY')` $\rightarrow$ bắt buộc `Consent_State (channel, endpoint_lookup_hash, purpose_code).status == 'GRANTED'` (trạng thái `REVOKED | EXPIRED | UNKNOWN` $\rightarrow$ `BLOCK (OUTBOUND_SUPPRESSED_CONSENT_REVOKED)`).
4. **Bước 4 (Legal Hold vs Notification Rules):** Nếu `contact_id` đang ở `Legal_Hold`, kiểm xem tin gửi có vi phạm phạm vi tạm dừng tiếp thị/xử lý (`RESTRICT`) hay không (`M20-F04`); nếu vi phạm phạm vi hold/`RESTRICT` $\rightarrow$ `BLOCK (OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD)`.
5. **Bước 5 (Sender Profile Gate cho `EMAIL / SMS / ZALO`):** Với `EMAIL`, kiểm `sender_profile_id` đã verify `SPF / DKIM / DMARC` và nhúng token `List-Unsubscribe` / `PublicOneClickUnsubscribe`; với `SMS`, kiểm Brandname / Sender ID đã đăng ký nhà mạng còn `ACTIVE` và cú pháp từ chối (`Opt-out`); với `ZALO`, kiểm `OA_ID` hợp lệ và mẫu ZBS tương ứng đúng `purpose_code` theo năng lực đã kiểm chứng (`OM-G01` & `M19-F03 Connection_Capabilities.verified_policy_manifest_version`, giữ `GAP-M19-03` fail-closed cho webhook Zalo và tách riêng `GAP-M19-04` cho Meta Tags); thiếu hoặc `NULL` khi bắt buộc $\rightarrow$ `BLOCK (SENDER_PROFILE_UNVERIFIED)`. *(Với `WEBHOOK` hệ thống phi nhắn tin như ERP/Bank: giữ nguyên Bước 1 [`Deletion_Ledger` + `Endpoint_Suppressions`], Bước 2 [`Processing_Records`], và Bước 4 [`Legal_Hold`]; chỉ miễn Bước 3 Consent tiếp thị khi thuộc `TRANSACTIONAL_*` kỹ thuật và miễn Bước 5 Sender Profile `EMAIL/SMS/ZALO`).*

### 2.2. `EvaluateVendorAndAiTransferInput` & `VendorTransferDecision` (`U22`, `INT28`, `OC20`, `RV17`)

```json
{
  "EvaluateVendorAndAiTransferInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "actor_id": "uuid (NN — dùng cho M14 check khi re-identify Placeholder_Vault)",
    "feature_code": "AI_SUMMARY | AI_DRAFT | AI_SUGGEST | AI_TRANSCRIBE | M19_EXTERNAL_WEBHOOK | M21_PARTNER_SYNC | REMOTE_VENDOR_API",
    "vendor_code": "string (NN)",
    "processing_record_id": "uuid (NN)",
    "data_classes": ["PUBLIC_META | INTERNAL_NOTES | CONVERSATION_TEXT | CONTACT_PII_PHONE_EMAIL | NATIONAL_ID_CCCD | BANK_ACCOUNT_OR_PAYMENT | HRM_PAYROLL | CALL_RECORDING_RAW"],
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
> - Nếu `data_classes` chứa `NATIONAL_ID_CCCD`, `BANK_ACCOUNT_OR_PAYMENT`, hoặc `HRM_PAYROLL` (hồ sơ HR/lương không được index vào AI chung `6.8`): trả ngay `BLOCK (PROHIBITED_DATA_CLASS_INCLUDED)`.
> - Nếu `Processing_Records` chưa đạt `ACTIVE` (hoặc `PROCESSOR` thiếu `dpa_contract_ref`): trả ngay `BLOCK (PRIVACY_PURPOSE_UNAPPROVED)` kèm `fallback_manual_mode`.
> - Nếu `Vendor_Data_Flows` chưa ở `APPROVED` (hoặc không đáp ứng `zero_data_retention` / căn cứ xuyên biên giới theo chính sách): trả `BLOCK (VENDOR_TRANSFER_POLICY_BLOCKED)` kèm `fallback_manual_mode`. Không coi `training_opt_out = true` là `zero_data_retention = true` (`RV17`).
> - Nếu `payload_provenance IN ('CUSTOMER_MESSAGE', 'EXTERNAL_ATTACHMENT_TEXT')`: luôn gắn `untrusted_data_fenced = true` và khóa cứng không cho phép lời nhắc trong nội dung khách kích hoạt tool đột biến (`U22`, `INT28`). Trước khi trả placeholder về bản gốc cho UI (`Placeholder_Vault`), gọi `M14.EvaluateAccessDecision` cho đúng `actor_id` hiện tại.

### 2.3. `VerifyPostRestoreComplianceGateInput` & `PostRestoreComplianceGateResult` (`INT26`, `OC19`, `U21`, `ADR-007`)

```json
{
  "VerifyPostRestoreComplianceGateInput": {
    "restore_run_id": "uuid (NN)",
    "tenant_id": "uuid | null (NULL khi verify toàn hệ thống)",
    "backup_point_in_time": "timestamptz (UTC, mốc snapshot DB vừa khôi phục)",
    "dry_run": "boolean (default false)",
    "hmac_key_versions_available": ["string"],
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
    "pending_reapply_count": "integer (0 mới PASSED)",
    "hmac_keys_verified": "boolean",
    "blocked_reason": "null | MISSING_HMAC_KEY_VERSION | PENDING_REAPPLY_NONZERO | INDEPENDENT_LEDGER_UNREACHABLE",
    "verified_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Kiểm duyệt `VerifyPostRestoreComplianceGate` (`INT26`, `OC19`, `ADR-007`):**
> - Trước hết xác minh kết nối tới kho PITR/WAL độc lập (`Deletion_Ledger`, `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`, `M23.Audit_Logs`); nếu không truy cập được $\rightarrow$ `BLOCKED (INDEPENDENT_LEDGER_UNREACHABLE)`.
> - Kiểm mọi `hmac_key_version` xuất hiện trên `Deletion_Ledger` đều hiện diện trong `hmac_key_versions_available[]` (gồm khóa cũ ở chế độ `VERIFY_ONLY`); thiếu bất kỳ phiên bản khóa nào $\rightarrow$ `BLOCKED (MISSING_HMAC_KEY_VERSION)` + `hmac_keys_verified = false`.
> - Nếu `dry_run = true`: chỉ tính số bản ghi chênh lệch so với snapshot vừa restore để Ops thẩm định mà **không ghi đè bảng nghiệp vụ**. Nếu `dry_run = false`: chạy idempotent theo `(restore_run_id, source_table, source_record_id)` (bao phủ `Deletion_Ledger` [`deletion_ledger_id`], `Endpoint_Suppressions`, `Consent_Logs`, `Legal_Holds`) áp lại 100% xóa phân tầng (gồm cả `RESTRICTED_LEGAL_HOLD`), `Endpoint_Suppressions`, `Consent_Logs` (tái dựng `Consent_State`), `Legal_Holds` và hủy các `M19 Outbound_Intents` quá hạn/thuộc đối tượng đã rút/xóa; chỉ trả `PASSED` khi `pending_reapply_count == 0` & `hmac_keys_verified == true`.

### 2.4. `EvaluateAssetDownloadPrivacyGateInput` & `AssetPrivacyGateDecision` (`SEC03`, `ADR-006`)

```json
{
  "EvaluateAssetDownloadPrivacyGateInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "actor_id": "uuid (NN)",
    "asset_id": "uuid (NN)",
    "asset_domain": "CRM_ATTACHMENT | CALL_RECORDING | EXPORT_BUNDLE | HRM_EMPLOYEE_DOCUMENT | CONTRACT_OR_FINANCE_DOC",
    "correlation_id": "uuid (NN)"
  },
  "AssetPrivacyGateDecision": {
    "decision": "ALLOW | BLOCK",
    "block_reason_code": "null | ASSET_QUARANTINED_OR_INFECTED | ASSET_PRIVACY_HOLD_OR_ERASED | ASSET_RETENTION_EXPIRED | HRM_CONFIDENTIALITY_BLOCKED",
    "legal_hold_status": "NONE | RESTRICTED_LEGAL_HOLD",
    "requires_watermark": "boolean",
    "evaluated_at": "timestamptz (UTC)"
  }
}
```

> **Thứ tự Kiểm duyệt & Ranh giới `SEC03` (`ADR-006` Bước 2 vs Bước 3):**
> - **Bước 1 (Quarantine / Malware `INT24`):** Nếu `Assets.scan_status <> 'CLEAN'` $\rightarrow$ `BLOCK (ASSET_QUARANTINED_OR_INFECTED)`.
> - **Bước 2 (Erasure & `Legal_Hold` trên `ASSET`):** Nếu tệp thuộc hồ sơ đã xóa theo `Deletion_Ledger` hoặc bị khóa xuất ngoại lệ bởi `Legal_Holds (target_scope_type = 'ASSET' | ...)` (trừ vai trò `LEGAL_HOLD_READ` được phép xem đối chiếu) $\rightarrow$ `BLOCK (ASSET_PRIVACY_HOLD_OR_ERASED)`; khi đang `RESTRICTED_LEGAL_HOLD` và được phép đọc $\rightarrow$ trả `legal_hold_status = 'RESTRICTED_LEGAL_HOLD'` & `requires_watermark = true`.
> - **Bước 3 (`Retention_Policies`):** Nếu tệp đã quá hạn lưu giữ (`ACTIVE` retention policy) chờ purge $\rightarrow$ `BLOCK (ASSET_RETENTION_EXPIRED)`.
> - **Bước 4 (`Master 6.8` & `ENTITY-L3031` cho `HRM_EMPLOYEE_DOCUMENT`):** Kiểm quy tắc bảo mật hồ sơ nhân sự/CCCD/bảng lương theo `6.8` (cấm AI/tìm kiếm đại trà/role thường truy xuất trái phạm vi) $\rightarrow$ `BLOCK (HRM_CONFIDENTIALITY_BLOCKED)`.
> - **Watermark & Ranh giới Bước 3 (`M23-F07`):** Đặt `requires_watermark = true` với `EXPORT_BUNDLE`, `HRM_EMPLOYEE_DOCUMENT`, `CONTRACT_OR_FINANCE_DOC` hoặc khi `legal_hold_status = 'RESTRICTED_LEGAL_HOLD'`. Kiểm tra hạn link `download_expires_at` (`EXPORT_LINK_EXPIRED`), header `Cache-Control: no-store` và ghi event `AssetDownloaded` thuộc **Bước 3 (`M23-F07`)** sau khi Bước 1 (`M14`) & Bước 2 (`M20`) đều trả `ALLOW` (`ADR-006 L22`).

---

## 3. Domain Events Phát hành & Tiêu thụ (Qua Internal Outbox `M23-F12`)

### 3.1. Envelope Chuẩn Mọi Sự kiện `M20` (`schema_version = "1.1"`)

Dùng chung cấu trúc chuẩn (`event_id`, `event_type`, `aggregate_type`, `aggregate_id`, `aggregate_version`, `schema_version`, `tenant_id`, `workspace_id` [`uuid | null`, `NULL` khi sự kiện phạm vi toàn Tenant như `SubjectErasureExecuted` / `LegalHoldChanged Nhóm B`], `occurred_at`, `correlation_id`, `causation_id`, `payload`).

### 3.2. Danh mục Sự kiện Phát hành (`Published Events`)

| Event Name | Payload Trọng yếu | Consumers Bắt buộc | Hành động Phải thực thi |
|---|---|---|---|
| `M20.EndpointSuppressed` | `suppression_id`, `channel`, `endpoint_lookup_hash`, `purpose_scope[]`, `reason_code`, `effective_at` | `M19`, `M01`, `M03`, `M04`, `M12`, `M21` | `M19` hủy toàn bộ `Outbound_Intents` đang xếp hàng (`QUEUED`/`RETRY_WAITING`) khớp `endpoint_lookup_hash + channel + purpose_scope`; `M04` dừng nhánh Journey tiếp thị; `M01`/`M03`/`M12`/`M21` đồng bộ trạng thái DNC trên UI (`OC17`, `RV17`) |
| `M20.SubjectErasureExecuted` | `privacy_request_id`, `deletion_ledger_id`, `subject_hmac_sha256`, `endpoint_hmac_hashes[]`, `hmac_key_version`, `erased_scopes[]`, `retained_legal_hold_scopes[]`, `scope_tenant_wide` | `M01`, `M02`, `M03`, `M06`, `M11`, `M12`, `M16`, `M18`, `M19`, `M21`, `M22`, `M24`, `File/Assets` | Xóa/ẩn danh dữ liệu cá nhân theo phạm vi đã phê duyệt (`M19` hủy `Outbound_Intents` khớp `endpoint_hmac_hashes[]` + xóa raw payload cache; `M06` xóa `Placeholder_Vault`/vector index; `M18`/`M21`/`M24` cập nhật projection sang `REDACTED-SUBJECT-#...`; `M22-F27` kiểm tra hold lao động) |
| `M20.LegalHoldChanged` | `legal_hold_id`, `target_scope_type`, `target_id`, `status` (`ACTIVE \| RELEASED`), `review_due_at` | `M14`, `M08`, `M09`, `M18`, `M21`, `M22` | `M14` bật/tắt cờ `RESTRICTED_LEGAL_HOLD` trong ACL & bump `permission_version`; `M08`/`M09`/`M22` khóa xóa vật lý; `M18`/`M21` ẩn danh báo cáo ngoài phạm vi audit |
| `M20.DataIncidentEscalated` | `incident_id`, `severity` (`S1 \| S2 \| S3`), `awareness_at`, `notification_due_at`, `affected_connection_ids[]`, `affected_actor_ids[]` | `M14`, `M19`, `M23-F08`, `M23-F02` | `M19` tạm ngắt/thu hồi token kết nối liên quan; `M14` & `M23-F02` thu hồi phiên & khóa user nghi lộ; `M23-F08` bật cảnh báo an ninh khẩn |

### 3.3. Danh mục Sự kiện `M20` Tiêu thụ (`Subscribed Events`)

- **`M14.WorkspaceActivated`:** Kiểm tra & khởi tạo yêu cầu rà soát `Processing_Records` + DPA khi bật `CLIENT workspace` (`O06`).
- **`M19.MessageReceiptUpdated` (`BOUNCED_HARD | BOUNCED_SOFT | COMPLAINED`):** Tiếp nhận sự kiện receipt từ `M19` (đã được `M19-F04` ingest bất biến vào `Email_Delivery_Events`/`Message_Status_Events` và được `M19` làm giàu sẵn `channel`, `purpose_code`, `endpoint_masked | null` trước khi phát) để `M20-F03` ghi/cập nhật **`Endpoint_Suppressions`** (`purpose_scope` lấy theo `purpose_code` hoặc `["ALL"]` khi `BOUNCED_HARD`/`COMPLAINED`; cho phép `endpoint_masked NULL` nếu kênh chỉ trả hash) theo cơ chế đếm `Soft-Bounce` (`[OPEN-GAP: GAP-M20-04]`) hoặc chặn tức thì (`Hard-Bounce`, `Spam Complaint`) mà **không truy vấn chéo DB `M19`** (`INDEX.md L62`).
