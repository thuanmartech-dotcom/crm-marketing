# ADR-008 — Khóa Hợp đồng Liên Module `M14 <-> M19 <-> M20 <-> M22 <-> M03` và Chuẩn hóa Bảng Trạng thái Omnichannel

**Status:** `Approved (Master Alignment + Contract Stabilization)`  
**Phạm vi:** `C14`, `C19`, `C20`, `M14`, `M19`, `M20`, `M22`, `M03`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`2.5 L268`, `3.12.5 L1333–1335`, `3.12.12 L1419–1420`, `5.1 L2491`, `5.9 L2687–2702`, `5.16 L2816–2829`, `5.17 L2845`, `5.18 L2893`, `6.3 L3143/3159`, `Phụ lục G L4713`, `OC01`, `OC05`, `OC07`, `SEC-U02`), [OMNICHANNEL_AUDIT_RESEARCH_2026-10-16.md](../../04-research/reports/OMNICHANNEL_AUDIT_RESEARCH_2026-10-16.md) (`L308`, `L312`, `L585`)

---

## Context

Đợt rà soát Luồng A xác nhận nhiều điểm gãy trực diện giữa `C14`, `C19`, `C20` và các bảng dữ liệu Master v1.9 (đổi tên bảng cấm ở `5.1`, thiếu `PAUSED`/`tenant_id` trong khóa chống hijack `SEC-U02`, lệch enum `channel`/`provider`/`status`/`resource_type`/`action`, thiếu trường bắt buộc giữa `C19 -> C20`, thiếu 4/6 JSON schema tại `C19`, thiếu 2 schema tại `C20`, thiếu consumer event hai chiều, và khẳng định thuật toán Zalo/Meta bị Master cấm trước PoC).

## Đề nghị

1. **Khôi phục Tên Bảng, Cột & Endpoint Chuẩn Master v1.9 (chấm dứt vi phạm `5.1 L2491`):**
   - **`Message_Status_Events` (`ENTITY-L2823`):** Khôi phục đúng tên canonical trong `M19` thay cho `Delivery_Receipt_Events`; giữ khóa `message_id uuid FK` (`5.16 L2825`) trên `Outbound_Intents` (gỡ tên tự chế `message_ref`). Bổ sung chuyển tiếp `ACCEPTED -> FAILED` (email bounce sau khi MTA đã nhận) và `ACCEPTED -> READ` (`OC07`) trên vòng đời giao vận, đồng thời **tách rõ**: `Outbound_Intents` giữ *trạng thái vận chuyển* (`QUEUED..ACCEPTED..FAILED_TERMINAL`), còn **`Message_Status_Events` + sự kiện đẩy về `M03`** cập nhật trạng thái hiển thị kinh doanh (`DELIVERED`, `READ`, `BOUNCED`, `COMPLAINED`) trên `Messages`.
   - **`Consent_State` (`ENTITY-L2784`):** Thống nhất tên chuẩn số ít theo Master (`Consent_State`, không dùng `Consent_States` gây 2 bộ tên).
   - **`Consent_Logs` (`5.9 L2687–2702`, `ENTITY-L2687`):** Khôi phục đầy đủ các cột Master: `contact_id` (khi chưa rõ liên hệ, luồng `M20-F02` / `5.18 L2895` promote `Channel_Identity` sang bản ghi `Contact` tạm/provisional trong cùng transaction hoặc dùng cơ chế provenance `contact_point_id / source_channel_identity_id / origin_contact_id`), `purpose_code varchar(80) NN` (nâng đồng bộ lên `varchar(80)` ở cả `M20` và `M19`), `action` đủ **`GRANT | REVOKE | EXPIRE`**, `policy_version`, `source`, `evidence_asset_id uuid NULL` (kèm lý do khi NULL), `idempotency_key varchar(255) NN UNIQUE (tenant_id, idempotency_key)`, `supersedes_id uuid NULL`.
   - **`Email_Delivery_Events` (`ENTITY-L2893`):** Khai báo đầy đủ cấu trúc bảng này trong `M19` (`connection_id`, `message_id`, `contact_point_id`, `provider_event_id`, `event_type`, `reason`, `endpoint_lookup_hash`, `occurred_at`, `received_at`) như nguồn sự kiện kỹ thuật bất biến kích hoạt `M20-F03` `Endpoint_Suppressions` (`purpose_scope jsonb/text[]` hoặc bảng chi tiết/hợp đồng mảng khớp `C20 L125`) và cập nhật `M03`.
   - **Endpoint Chuẩn (`CONTRACT-L0268`, `CONTRACT-L2845`):** Khôi phục `POST /v1/consents/revoke` (hỗ trợ `200 OK` hoặc `202 Accepted` nếu còn queue propagation) làm canonical alias/endpoint tại `M20`, và `POST /v1/connections/{id}/replay` tại `M19` (đặt `/v1/integrations/...` nếu có chỉ là alias nội bộ không thay thế đường dẫn Master).
2. **Vá Lỗ hổng Chống Hijack & Khóa Trùng Lặp Dữ liệu tại `M19` (`SEC-U02`, `OC01`, `OC05`):**
   - **`Channel_Connections` Partial Unique Index:** Phải bao gồm cả `tenant_id` lẫn trạng thái `'PAUSED'`:
     `UNIQUE (tenant_id, provider, provider_namespace, external_account_id) WHERE status IN ('ACTIVE', 'DEGRADED', 'REAUTHORIZATION_REQUIRED', 'PAUSED')`.
     Chỉ giải phóng khóa khi đã hoàn tất quy trình `Transfer`/`Disconnect` chuyển về `DISCONNECTED`.
   - **`Inbound_Events`:** Chốt 1 khóa chống trùng duy nhất trên toàn bộ `M19` + `C19` là **`UNIQUE (tenant_id, connection_id, event_key)`**, sửa `INSERT ... ON CONFLICT (tenant_id, connection_id, event_key) DO NOTHING` (và lưu ý theo `5.17 L2848`: status update event không dùng trùng key của message gốc).
   - **`Outbound_Intents`:** Chốt 1 khóa idempotency duy nhất: **`UNIQUE (tenant_id, workspace_id, idempotency_key)`** (`C19` & `M19`).
3. **Đồng bộ Toàn diện Schema, Enum & Events giữa `C14`, `C19`, `C20`, `M22`:**
   - **`C14` (`EvaluateAccessDecisionInput`):** Bổ sung đầy đủ `resource_type` cho Tổ chức (`TENANT`, `BRANCH`, `BRAND`, `BUSINESS_LINE`, `BUSINESS_UNIT`, `LEGAL_ENTITY`, `WORKSPACE`, `WORKSPACE_ACCOUNT_LINK`, `CONTRACT_WORKSPACE_GRANT`, `DEPARTMENT`, `USER`, `MEMBERSHIP`, `TEAM`, `ROLE`, `ROLE_BINDING`, `ENTITY_TEAM_GRANT`, `DELEGATION`, `OFFBOARDING_CASE`, `CAPACITY_COST_SNAPSHOT`, `SCORECARD_REVIEW`, `POLICY_DEFINITION`), `M19` (`CHANNEL_CONNECTION`, `CONNECTION_CAPABILITY`, `OUTBOUND_INTENT`, `INBOUND_EVENT`, `QUARANTINED_EVENT`, `ADAPTER_DLQ`, `SYNC_RUN`, `REPLAY_JOB`), `M20` (`PROCESSING_RECORD`, `CONSENT_LOG`, `CONSENT_STATE`, `ENDPOINT_SUPPRESSION`, `PRIVACY_REQUEST`, `LEGAL_HOLD`, `LEGAL_DEADLINE_POLICY`, `RETENTION_POLICY`, `DELETION_LEDGER`, `DATA_INCIDENT`, `VENDOR_DATA_FLOW`, `PLACEHOLDER_VAULT`), `M21` (`PARTNER_DATA_PROFILE`, `PARTNER_DATASET`, `PARTNER_REPORT`), `M22` (`EMPLOYEE`, `EMPLOYMENT_CONTRACT`, `ATTENDANCE`, `LEAVE_REQUEST`, `PAYROLL`), `M23` (`EXPORT_REQUEST`, `BREAK_GLASS_GRANT`, `AUDIT_LOG`), và toàn bộ Core (`ORDER`, `INVOICE_LINE`, `STRATEGY_BRIEF`, `IMC_PLAN`, `ASSET`, `JOURNEY`, `REFERRAL`, `LOYALTY_LEDGER`, `APPOINTMENT`, `RESOURCE`, `FEEDBACK`, `RECOVERY_CASE`...); bổ sung `action` (`COMMENT`, `CONNECT`, `ACTIVATE`, `VERIFY_CAPABILITY`, `DISPATCH`, `PAUSE`, `RESUME`, `DISCONNECT`, `TRANSFER`, `RECONCILE`, `SYNC`, `REPLAY`, `VIEW_QUARANTINE_PAYLOAD`, `MANAGE_POLICY`, `VIEW_AUDIT`). Hỗ trợ xác thực `principal_type = USER | SERVICE_PRINCIPAL | PORTAL_CLIENT`.
   - **`C19` & `C20`:** Hợp nhất `channel` enum gồm đủ **`EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK`**; `C19.provider` bổ sung **`TELEGRAM | PANCAKE | ERP_MISA | PMS | BIOMETRIC_DEVICE`**; `C19.DispatchOutboundIntentInput` bổ sung bắt buộc **`contact_id` (`uuid | null`)** và **`sender_profile_id` (`uuid | null` tùy kênh Email/SMS/ZNS)**; `C19` bổ sung Public Command **`EnqueueOutboundIntent`** và **`ReplayConnectionEvents`** (đủ 5 trụ cột với 5 cặp Schema Input/Output trong 5 khối JSON), thống nhất tên Trụ cột `ExecuteSafeRemoteFetch` và thống nhất `status` enum (`EXPIRED_CANCELLED`, `UNKNOWN_OUTCOME`, `RETRY_WAITING`).
   - **`Processing_Records` Pre-enable Gate:** `M19` (`RegisterConnection` / `ActivateConnection`) bắt buộc gọi kiểm tra `Processing_Records.status = 'ACTIVE'` từ `M20` trước khi cho phép kết nối chuyển sang `ACTIVE` (`Master 6.3 L3159`).
   - **Ma trận Consumer Events khép kín (kèm Envelope chuẩn `aggregate_id`, `aggregate_version`, `schema_version`, `correlation_id`, `causation_id`, `occurred_at`):**
     - `M14.UserOffboardingLocked` $\rightarrow$ `M23-F02, M02, M03, M07, M08, M11, M12, M13, M15, M16, M17, M19, M22`
     - `M14.WorkHandoverAssigned` $\rightarrow$ `M02, M03, M07, M08, M11, M12, M13, M15, M16, M17, M19, M22, M23`
     - `M14.WorkspaceActivated` $\rightarrow$ `M20, M19, M21` (kèm `processing_scope` khi `CLIENT`)
     - `M20.EndpointSuppressed` $\rightarrow$ `M19` (hủy queued `Outbound_Intents`), `M01`, `M03`, `M04`, `M12`, `M21`
     - `M20.SubjectErasureExecuted` $\rightarrow$ `M01, M02, M03, M06, M11, M12, M16, M18, M19, M21, M22, M24` + `File/Assets`
     - `M20.LegalHoldChanged` $\rightarrow$ `M14` (bắt buộc kích hoạt `RESTRICTED_LEGAL_HOLD`), `M08, M09, M18, M21, M22`
     - `M20.DataIncidentEscalated` $\rightarrow$ `M14, M19, M23-F08, M23-F02`
     - `M19.OutboundDispatchResulted` / `M19.MessageReceiptUpdated` $\rightarrow$ `M03, M04, M12`
     - `M22` Events (`hr.employment.changed.v1`, `hr.availability.changed.v1`, `hr.offboarding.effective.v1`) $\rightarrow$ `M14` (kèm xử lý out-of-order theo `effective_at` & `aggregate_version`, không tự mở quyền dữ liệu `INV-02`).
4. **Tuân thủ Lệnh cấm Tài liệu Chưa Xác minh (`Master 3.12.12 L1419–1420`, `Phụ lục G L4713`):**
   - Xóa bỏ khẳng định Zalo dùng `HMAC-SHA256` ở `M19 L219` và hardcode `"Meta tag policy"` ở `C19 L87`; thay bằng cơ chế `adapter_signature_verifier (Unverified until PoC — Fail-Closed / Feature-Gated)` & `verified_provider_policy_manifest`, ghi thành `[OPEN-GAP]` trong `GAPS.md`.

## So sánh

- **Để mỗi module tự giữ enum & tên bảng riêng:** Gây gãy tích hợp ngay khi bắt đầu code `M16`/`M03` vì `DispatchOutboundIntent` không thể gọi `EvaluateOutboundCompliance`, `LegalHoldChanged` rơi vào khoảng trống, và `Email_Delivery_Events` không ai tạo bảng.

## Hệ quả và điều kiện thay đổi

- Cập nhật toàn diện `C14`, `C19`, `C20` và 3 module specs `M14`, `M19`, `M20` trước khi tái kiểm Fresh-Context Review.
