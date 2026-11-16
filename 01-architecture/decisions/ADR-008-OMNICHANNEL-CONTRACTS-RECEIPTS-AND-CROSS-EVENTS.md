# ADR-008 — Khóa Hợp đồng Liên Module `M14 <-> M19 <-> M20 <-> M22 <-> M03 <-> M16` và Chuẩn hóa Bảng Trạng thái Omnichannel

**Status:** `Approved (Wave 1.5 Hardening — CR-20261116-WAVE1-5-HARDENING)`  
**Phạm vi:** `C14`, `C19`, `C20`, `C16`, `M14`, `M19`, `M20`, `M22`, `M23`, `M24`, `M03`, `M16`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`2.5 L268`, `3.12.5 L1333–1335`, `3.12.12 L1419–1420`, `5.1 L2491`, `5.9 L2687–2702`, `5.16 L2816–2829`, `5.17 L2845`, `5.18 L2893`, `6.3 L3143/3159`, `6.4 L3178`, `Phụ lục G L4713`, `OC01`, `OC05`, `OC07`, `SEC-U02`), [OMNICHANNEL_AUDIT_RESEARCH_2026-10-16.md](../../04-research/reports/OMNICHANNEL_AUDIT_RESEARCH_2026-10-16.md) (`L308`, `L312`, `L585`), [ADR-002](ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-007](ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md)

---

## Context

1. Đợt rà soát Luồng A đã khôi phục tên bảng, cột & endpoint chuẩn Master v1.9 (`Message_Status_Events`, `Consent_State`, `Consent_Logs`, `Email_Delivery_Events`, `POST /v1/consents/revoke`, `POST /v1/connections/{id}/replay`), hợp nhất enum & schema `C14/C19/C20`, và khóa lệnh cấm giả định thuật toán Zalo/Meta trước PoC.
2. Đợt re-audit Wave 1.5 phát hiện tiếp **6 lỗ hổng liên kết & vòng đời trạng thái cần vá dứt điểm**:
   - Chỉ mục chống trùng `Channel_Connections` trước đây đặt `tenant_id` lên đầu (`UNIQUE (tenant_id, provider, ...)`), **chỉ chống trùng trong cùng 1 tenant nhưng để lọt cướp webhook xuyên Tenant** nếu Tenant B nối cùng Page/OA ID của Tenant A!
   - Khi Retention (`Master 6.4 L3178`, `GAP-M19-08`) dọn payload raw `Inbound_Events` sau 30 ngày, nếu xóa chung bản ghi hoặc khóa `event_key` sẽ làm mất năng lực chống trùng khi đối tác replay/backfill sau đó.
   - `Channel_Connections` thiếu cờ `requires_reauth`: cho phép chuyển vòng `REAUTHORIZATION_REQUIRED -> PAUSED -> ACTIVE` (`Resume`) mà không đi qua OAuth / nạp token mới lại.
   - `Message_Status_Events` cần hỗ trợ cả chuyển tiếp muộn `DELIVERED/READ -> COMPLAINED/FAILED` **VÀ** không làm rơi webhook receipt đến sớm trước khi `DispatchOutboundIntent` Pha 3 kịp `COMMIT` `provider_message_id`; đồng thời event `M19.MessageReceiptUpdated` thiếu trường **`provider_event_id`**.
   - Ma trận consumer sự kiện còn bỏ sót: `M20.SubjectErasureExecuted -> M14, M23, M24`, `M20.LegalHoldChanged -> M16`, và `M14.WorkspaceActivated -> M16`.

## Đề nghị

1. **Khôi phục Tên Bảng, Cột & Endpoint Chuẩn Master v1.9 (`5.1 L2491`) & Vá `Message_Status_Events`:**
   - **`Message_Status_Events` (`ENTITY-L2823`):** Khôi phục tên canonical trong `M19`; giữ khóa `message_id uuid FK` (`5.16 L2825`) trên `Outbound_Intents`.
     - **Chuyển tiếp trạng thái đơn điệu mở rộng (`OC07`, `3.12.5 L1334`):** Hỗ trợ đầy đủ `ACCEPTED -> DELIVERED -> READ`, `ACCEPTED -> READ`, `ACCEPTED -> FAILED`, **VÀ `DELIVERED / READ -> COMPLAINED | FAILED`** (trường hợp người nhận đã đọc/nhận nhưng sau đó báo cáo spam `COMPLAINED` hoặc relay phía sau trả bounce/lỗi trễ `FAILED`), trong khi vẫn cấm lùi `DELIVERED` về đè `READ`.
     - **Nhận webhook receipt đến sớm trước Phase 3 Commit:** Khi Pha 2 `DispatchOutboundIntent` vừa gọi POST sang provider và webhook `SENT/DELIVERED` bắn về *trước* khi Pha 3 của Worker kịp `COMMIT` `provider_message_id` vào `Outbound_Intents`, `M19-F04` **tuyệt đối không bỏ rơi webhook hay trả `404`**: bắt buộc ghi bền vào `Message_Status_Events` theo `(tenant_id, connection_id, provider_message_id, provider_event_id, receipt_status)` (cho phép `outbound_intent_id` tạm `NULL` lúc ingest và nối khớp khi Phase 3 commit hoặc reconciler đối soát).
   - **`M19.MessageReceiptUpdated` bổ sung `provider_event_id`:** Payload chuẩn bắt buộc có **`provider_event_id`** (cùng `message_status_event_id`, `outbound_intent_id`, `message_id`, `connection_id`, `channel`, `purpose_code`, `endpoint_lookup_hash`, `hmac_key_version`, `endpoint_masked`, `receipt_status`, `occurred_at`) để `M20` và `M03` chống trùng theo sự kiện gốc của provider (`5.17 L2848`).
   - **`Consent_State` (`ENTITY-L2784`), `Consent_Logs` (`ENTITY-L2687`), `Email_Delivery_Events` (`ENTITY-L2893`):** Giữ chuẩn số ít `Consent_State`, `purpose_code varchar(80) NN`, `action (GRANT | REVOKE | EXPIRE)`, `hmac_key_version varchar(30) NN` (`ADR-007`), `idempotency_key UNIQUE (tenant_id, idempotency_key)`, và endpoint `POST /v1/consents/revoke`, `POST /v1/connections/{id}/replay`.

2. **Vá Chống Cướp Webhook Xuyên Tenant, Vòng Đời `requires_reauth` & Bảng `Inbound_Event_Dedup_Keys` (`SEC-U02`, `OC01`, `OC05`):**
   - **`Channel_Connections` Global Anti-Hijack Unique Index:** Thay khóa cục bộ theo tenant bằng **khóa duy nhất TOÀN CỤC**:
     `UNIQUE (provider, provider_namespace, external_account_id) WHERE status IN ('ACTIVE', 'DEGRADED', 'REAUTHORIZATION_REQUIRED', 'PAUSED')`.
     *(Các cột `tenant_id`, `workspace_id` vẫn là scope sở hữu dữ liệu và chịu RLS, nhưng chỉ mục unique toàn cục bảo đảm hai Tenant khác nhau không thể kết nối đồng thời cùng một `external_account_id` để cướp webhook)*. Chỉ giải phóng khi đã hoàn tất quy trình `Transfer`/`Disconnect` chuyển về `DISCONNECTED`.
   - **`webhook_endpoint_token` ngẫu nhiên mật mã:** Mỗi `Channel_Connections` phát sinh `webhook_endpoint_token` ngẫu nhiên (không suy đoán từ `tenant_id`/`connection_id`) làm khóa định tuyến cho **Bootstrap `SECURITY DEFINER` Router (`ADR-002`)** theo bộ ba `(provider, provider_namespace, webhook_endpoint_token)`.
   - **Cờ `requires_reauth boolean NOT NULL DEFAULT false` trên `Channel_Connections`:** Khi kết nối bị chuyển sang `REAUTHORIZATION_REQUIRED` (lỗi `401/403` hoặc sự cố `M20.DataIncidentEscalated`), hệ thống tự động đặt `requires_reauth = true`. Nếu operator tạm đưa sang `PAUSED`, cờ `requires_reauth = true` **vẫn giữ nguyên và chặn cứng chuyển tiếp `PAUSED -> ACTIVE` (`Resume`)** cho tới khi hoàn tất luồng OAuth / nạp token mới vào Vault và reset `requires_reauth = false`.
   - **Tách bảng `Inbound_Event_Dedup_Keys` trước khi Purge Raw 30 Ngày (`GAP-M19-08`, `Master 6.4 L3178`):**
     - Tách bảng nhẹ **`Inbound_Event_Dedup_Keys`** (`tenant_id`, `connection_id`, `event_key`, `event_type`, `received_at`, `retention_until`, `UNIQUE (tenant_id, connection_id, event_key)`) độc lập khỏi bảng payload thô `Inbound_Events`.
     - Khi Retention policy `M20-F06` (tham chiếu 30 ngày) xóa raw payload trong `Inbound_Events`, **`Inbound_Event_Dedup_Keys` vẫn được giữ lại theo cửa sổ chống trùng dài hạn** để bảo đảm replay/backfill sau 30 ngày không phát sinh trùng lặp.
   - **`Outbound_Intents`:** Khóa **`UNIQUE (tenant_id, workspace_id, idempotency_key)`** (`C19` & `M19`) kèm bộ cột lease fencing `lease_owner_id`, `lease_token`, `last_attempted_lease_token`, `lease_expires_at`, `http_attempted_at`, `pre_socket_reclaim_count` (`ADR-005`).

3. **Đồng bộ Toàn diện Schema, Enum & Ma trận Consumer Events (`C14`, `C19`, `C20`, `C16`, `C23`, `C24`):**
   - **`C14` (`EvaluateAccessDecisionInput`):** Đủ `resource_type` cho `M14–M24` & Core (`WORK_QUEUE`, `TASK_TEMPLATE`, `RECURRENCE_RULE`, `TIME_ENTRY`, `RESOURCE_ALLOCATION`, `PARTNER_EXCEPTION_CASE`, `POLICY_DEFINITION`, `APPROVAL_REQUEST`, `ASSET`, v.v.); đủ `action`; hỗ trợ 3 loại `principal_type = USER | SERVICE_PRINCIPAL | PORTAL_CLIENT` (`ADR-002`).
   - **`C19` & `C20`:** Hợp nhất `channel` enum (`EMAIL | SMS | ZALO | FACEBOOK | TIKTOK | TELEGRAM | VOICE_CALL | WEBHOOK`); `C19.provider_category` bổ sung `PMS` & `TASK_SYNC` (`ADR-005`); `C19` giữ đủ 5 trụ cột (10 schemas) và kiểm `Processing_Records.status = 'ACTIVE'` trước khi `ActivateConnection` (`Master 6.3 L3159`).
   - **Ma trận Consumer Events Khép kín Đã Vá Wave 1.5 (qua `M23-F12.Internal_Outbox_Events`):**
     - `M14.UserOffboardingLocked` $\rightarrow$ `M23-F02, M02, M03, M07, M08, M11, M12, M13, M15, M16, M17, M19, M22`
     - `M14.WorkHandoverAssigned` $\rightarrow$ `M02, M03, M07, M08, M11, M12, M13, M15, M16, M17, M19, M22, M23`
     - `M14.WorkspaceActivated` $\rightarrow$ **`M20, M19, M21, M16`** *(bổ sung `M16` nhận cấu hình `client_workspace_id` / `client_account_id` / `default_legal_entity_id`)*
     - `M20.EndpointSuppressed` $\rightarrow$ `M19` (hủy queued `Outbound_Intents`), `M01`, `M03`, `M04`, `M12`, `M21`
     - `M20.SubjectErasureExecuted` *(kèm `erased_subject_refs[]` & `endpoint_hashes_by_version[]`)* $\rightarrow$ **`M01, M02, M03, M06, M11, M12, M14, M16, M18, M19, M21, M22, M23, M24` + `File/Assets`** *(bổ sung `M14` ẩn danh/khóa principal liên quan; `M23` thu hồi `Export_Requests` & `Assets`; `M24` xóa Read Model / Search index / Notifications)*
     - `M20.LegalHoldChanged` *(hỗ trợ thêm `PROJECT | DELIVERABLE | TASK` & `active_legal_hold_ids[]`)* $\rightarrow$ **`M14, M16, M08, M09, M18, M21, M22`** *(bổ sung `M16` khóa xóa/purge `Projects`, `Deliverables`, `Acceptances`, `Task_Submissions`, `Tasks`, `Assets`)*
     - `M20.DataIncidentEscalated` $\rightarrow$ `M14, M19, M23-F08, M23-F02`
     - `M19.OutboundDispatchResulted` / `M19.MessageReceiptUpdated` *(có `provider_event_id`)* $\rightarrow$ `M03, M04, M12, M16` (`PMS`), `M20`
     - `M22` Events (`hr.employment.changed.v1`, `hr.availability.changed.v1`, `hr.offboarding.effective.v1`) $\rightarrow$ `M14` (sắp xếp theo `effective_at` & `aggregate_version`, không tự mở quyền `INV-02`).

4. **Tuân thủ Lệnh cấm Tài liệu Chưa Xác minh (`Master 3.12.12 L1419–1420`, `Phụ lục G L4713`):**
   - Tuyệt đối cấm giả định Zalo dùng `HMAC-SHA256` hoặc hardcode `"Meta tag policy"` trước PoC; giữ cờ `UNVERIFIED_UNTIL_POC` (`Fail-Closed`, `[OPEN-GAP: GAP-M19-03/04]`).

## So sánh

- **Giữ `UNIQUE (tenant_id, ...)` trên `Channel_Connections`, thiếu `Inbound_Event_Dedup_Keys`, thiếu `requires_reauth` và thiếu `M14/M23/M24`/`M16` trên consumer matrix:** Mở lỗ hổng cướp webhook giữa các Tenant, mất khả năng chống trùng khi xóa payload thô 30 ngày, cho phép lách OAuth bằng đường vòng `PAUSED -> ACTIVE`, làm rơi receipt webhook đến sớm trước Phase 3, và để sót dữ liệu xóa/hold tại `M14/M16/M23/M24`.

## Hệ quả và điều kiện thay đổi

- Cập nhật `C14`, `C19`, `C20`, `C16` và các module specs `M14`, `M19`, `M20`, `M16`, `M23`, `M24` theo toàn bộ chỉnh sửa Wave 1.5 này.
