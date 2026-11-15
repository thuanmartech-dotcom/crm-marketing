# Contract: M20-SUPPRESSION-PRIVACY-GATE — Cổng Kiểm duyệt Chặn Gửi Thời gian thực, Kiểm soát Dữ liệu sang AI/Vendor & Đối soát Sổ Chứng cứ Xóa

- **Contract ID / Version:** `M20-SUPPRESSION-PRIVACY-GATE` / `v1.0` (`[PROPOSED]` trên nền `[MASTER]` Mục `4.11`, `5.13`, `5.18`, `6.2`, `6.3`, `6.4`, `9.5`, `9.9`, `9.10`, `9.13`, `9.14`).
- **Baseline:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`).
- **Provider Owner:** [M20 — Quản trị Dữ liệu Cá nhân, Consent, Suppression & Quyền Chủ thể](../modules/M20-PRIVACY-CONSENT-RETENTION.md).
- **Consumers:** `M01` (CDP Merge/Unmerge), `M03` (Omnichannel Inbox), `M04` (Journey Automation), `M06` (AI Co-Pilot), `M11/M12` (Ticket/VoC Survey), `M14` (CLIENT Workspace Activation `UC14`), `M19` (Integration Outbox Dispatch & Replay), `M21` (Partner Data Retention `M21-F02/F13`), `M22` (HRM Privacy `M22-F27`), `M23` (DLP/Backup Restore), `M24` (Search/Cache/Archive Purge).
- **Source Requirements:** `M20-F01..08`, `M20-AC01..03`, `UC11`, `SEC05`, `SEC-U05`, `FR02`, `FR09`, `FR13`, `FR34`, `FR37`, `U01`, `U15`, `U21`, `INT17`, `INT26`, `RV11`, `RV16`, `RV17`, `OC17`, `OC22`, `CX-U15`, `CX-U20`, `NFR06`.
- **Status:** `Reviewed` (Đã chốt kiến trúc Dual-Gate + HMAC Deletion Ledger qua `/grill-me` ngày `16/11/2026`; test ứng dụng `Not Run`).
- **Breaking-Change Policy:** Mọi thay đổi trên cấu trúc `OutboundComplianceDecision`, ma trận ưu tiên `Endpoint_Suppression` theo mục đích gửi (`purpose`), hoặc định dạng băm `HMAC-SHA256` của `Deletion_Ledger` bắt buộc tăng `major_version`, giữ dual-reader tối thiểu 1 release và chạy lại bộ kiểm thử `M20-AC01..03`, `SEC-U05`, `U15`, `INT17`, `INT26`, `RV17`, `CX-U20`.

---

## 1. Bảng 12 Thành phần Hợp đồng (`12 Required Contract Parts`)

| Phần | Nội dung đặc tả chi tiết |
|---|---|
| **Meaning** | `[MASTER]` + `[PROPOSED]` Hợp đồng cổng tuân thủ quyền riêng tư và chặn gửi bắt buộc (*Single Source of Truth* — `INV-02`, `INV-07`), gồm **3 giao diện đồng bộ**: (1) `EvaluateOutboundCompliance` kiểm tra quyền liên hệ ở cả thời điểm xếp hàng (`Enqueue`) và ngay trước giây phát tin thực tế (`Authoritative Dispatch Recheck`); (2) `EvaluateVendorAndAiTransfer` kiểm duyệt cơ sở xử lý và tự động làm mờ PII (`Pseudonymization/Redaction`) trước khi dữ liệu rời hệ thống sang AI/Vendor; (3) `VerifyPostRestoreComplianceGate` đối soát `Deletion_Ledger` và `Endpoint_Suppressions` trước khi mở cổng truy cập sau khôi phục sao lưu (`INT26`), cùng **4 Domain Events** phát qua Outbox. |
| **Actor/scope** | `[MASTER]` Tác nhân gọi gồm: `Domain Command Handlers` (`M03`, `M04`, `M12`), `Outbox Dispatch Worker` (`M19-F05`), `AI Data Gateway` (`M06-F01/02`), `Workspace Activation Handler` (`M14-F01` / `UC14`), và `Backup Restore Coordinator` (`M23`). Ngữ cảnh `tenant_id` và `workspace_id` bắt buộc lấy từ phiên xác thực server hoặc Outbox envelope đã ký; không bao giờ gộp chung `Consent` hoặc mở rộng `Consent` giữa hai `Workspace` độc lập (`INV-01`, `M20-F02`). |
| **Preconditions** | `[MASTER]` (1) Đối với gửi tin ra ngoài (`EvaluateOutboundCompliance`): phải truyền đủ `workspace_id`, `channel`, `endpoint_lookup_hash` (băm chuẩn hóa của Email/SĐT/Zalo ID), `purpose_code` (`MARKETING_PROMO \| SURVEY_VOC \| SERVICE_NOTIFICATION \| SECURITY_LEGAL`), và `check_stage` (`ENQUEUE \| DISPATCH_AUTHORITATIVE`). (2) Đối với chuyển dữ liệu sang AI/Vendor (`EvaluateVendorAndAiTransfer`): tính năng/connector đích phải có hồ sơ `Processing_Records` và `Vendor_Data_Flows` ở trạng thái `ACTIVE` (`M20-F01`, `M20-F07`). |
| **Input** | `[PROPOSED]` Xem chi tiết Schema đầu vào của `EvaluateOutboundComplianceInput`, `EvaluateVendorAndAiTransferInput` và `VerifyPostRestoreComplianceGateInput` tại Mục 2 bên dưới. |
| **Output** | `[PROPOSED]` Xem chi tiết Schema đầu ra `OutboundComplianceDecision` (`decision: ALLOW \| BLOCK`, `block_reason_code`, `suppression_ref`, `consent_version_ref`, `checked_at`) và `VendorTransferDecision` (`decision: ALLOW_REDACTED \| ALLOW_RAW \| BLOCK`, `sanitized_payload`, `placeholder_map_ref`, `retention_constraint`) tại Mục 2 bên dưới. |
| **Errors** | `[MASTER]` + `[PROPOSED]` Chuẩn hóa mã lỗi: `PRIVACY_PURPOSE_UNAPPROVED` (`422/403` — chưa có `Processing_Records` ở trạng thái `ACTIVE`), `OUTBOUND_SUPPRESSED_UNSUBSCRIBE` (`403` — khách đã hủy đăng ký mục đích này), `OUTBOUND_SUPPRESSED_HARD_BOUNCE` (`403` — endpoint bị lỗi cứng trên kênh này), `OUTBOUND_SUPPRESSED_COMPLAINT_OR_DNC` (`403` — khách khiếu nại spam hoặc từ chối liên hệ lại `CX-U15`), `OUTBOUND_MISSING_CONSENT_EVIDENCE` (`403` — mục đích `MARKETING_PROMO` nhưng chưa có consent hợp lệ `OC22`), `VENDOR_TRANSFER_POLICY_BLOCKED` (`403` — vendor/AI chưa đạt điều kiện vùng lưu trữ/retention `RV17`), `RESTORE_LEDGER_REPLAY_REQUIRED` (`503` — cấm mở hệ thống khi chưa áp lại `Deletion_Ledger` sau restore `INT26`). |
| **Concurrency** | `[MASTER]` Khi khách hàng rút sự đồng ý (`RevokeConsent`), bấm `Unsubscribe`, hoặc phát sinh `Hard-Bounce`, `M20` phải ghi nhận vào `Endpoint_Suppressions` và `Consent_Logs` **nguyên tử trong cùng 1 transaction trước khi trả xác nhận thành công (`M20-F02`, `6.3`)**. Tại thời điểm `M19-F05` chuẩn bị gọi API nhà mạng/kênh ngoài, Worker thực hiện `DISPATCH_AUTHORITATIVE` đọc trực tiếp trạng thái hiện hành của `Endpoint_Suppressions` (không giữ DB lock trong lúc chờ mạng gọi provider — `5.14`, `5.17`). |
| **Idempotency** | `[MASTER]` Các sự kiện webhook từ nhà cung cấp (`Unsubscribe`, `Hard-Bounce`, `Spam-Complaint`) và các lệnh `RecordConsent / RevokeConsent` đi kèm khóa `(tenant_id, workspace_id, channel, endpoint_lookup_hash, provider_event_id / idempotency_key)` để xử lý idempotent tuyệt đối (`ENTITY-L2893`, `SEC-U05`). Gọi lặp cùng một sự kiện hủy đăng ký hoặc bounce không tạo bản ghi trùng và không đảo ngược trạng thái đã chặn. |
| **Transaction** | `[MASTER]` (1) **Đường ghi Consent/Suppression:** Ghi `Consent_Logs` (append-only) + cập nhật `Consent_States` + upsert `Endpoint_Suppressions` + ghi `Audit_Logs` + đẩy `Outbox` (`M20.EndpointSuppressed`) trong cùng 1 DB transaction. (2) **Đường thực thi Xóa/Ẩn danh (`M20-F06`):** Đánh dấu `Legal_Holds` cho phần chứng từ bắt buộc giữ $\rightarrow$ xóa/ẩn danh phần dữ liệu được phép xóa $\rightarrow$ ghi mã băm `HMAC-SHA256` vào `Deletion_Ledger` $\rightarrow$ phát `M20.SubjectErasureExecuted` để các kho phụ (`Search`, `Cache`, `AI Vector`, `File`) dọn dẹp đồng bộ (`6.4`). |
| **Compatibility** | `[MASTER]` + `[PROPOSED]` Hỗ trợ cấu hình `Legal_Policy` theo phiên bản (`Policy_Versions`: `DRAFT -> REVIEWED -> ACTIVE`). Nếu một loại yêu cầu pháp lý chưa được cấu hình công thức tính hạn tự động (`ACTIVE`), hệ thống **không tự bịa một mốc giờ cố định (như 72h chung)** mà chuyển ca về hàng đợi bắt buộc `Privacy Owner` xử lý thủ công có lưu bằng chứng (`M20-F05`, `3149`). |
| **Audit/privacy** | `[MASTER]` Bảng `Consent_Logs`, `Endpoint_Suppressions` và `Deletion_Ledger` là bất biến / có truy vết nguồn gốc (`provenance`). Đặc biệt, **`Deletion_Ledger` tuyệt đối không lưu lại SĐT, Email hay tên thật của người đã yêu cầu xóa**, mà chỉ lưu `endpoint_hmac_sha256` và `subject_hmac_sha256` với khóa bí mật lưu trong Secret Manager (`6.2`, `6.4`). Trong `AI Data Gateway` (`M20-F07`), bảng ánh xạ placeholder (`[PII_PHONE_1]`) có TTL ngắn và kiểm quyền nghiêm ngặt (`6.3` dòng `3174`). |
| **Tests** | `[MASTER]` Provider & Consumer test fixtures: `M20-AC01`, `M20-AC02`, `M20-AC03`, `SEC-U05`, `U01`, `U15`, `U21`, `INT17`, `INT26`, `RV11`, `RV16`, `RV17`, `OC14`, `OC17`, `OC22`, `CX-U15`, `CX-U20`. Trạng thái thực thi hiện tại: `Not Run`. |

---

## 2. Đặc tả Giao diện & Schema Chi tiết (`Dual-Gate & Restore Ledger Schemas`)

### 2.1. Cổng 1: `EvaluateOutboundCompliance` (Kiểm tra Chặn gửi ở `Enqueue` và `Authoritative Dispatch`)

#### Đầu vào (`EvaluateOutboundComplianceInput`)
```json
{
  "tenant_id": "uuid (server-verified)",
  "workspace_id": "uuid (NOT NULL)",
  "check_stage": "ENQUEUE | DISPATCH_AUTHORITATIVE",
  "channel": "EMAIL | SMS | ZALO | FACEBOOK | TELEGRAM | VOICE_CALL | WEBHOOK",
  "endpoint_lookup_hash": "char(64) (HMAC-SHA256 của email/phone/channel_user_id đã chuẩn hóa)",
  "contact_id": "uuid | null",
  "purpose_code": "MARKETING_PROMO | SURVEY_VOC | SERVICE_NOTIFICATION | SECURITY_LEGAL",
  "sender_profile_id": "uuid",
  "outbound_intent_id": "uuid | null"
}
```

#### Quy tắc Đánh giá Tất định (`Deterministic Compliance Matrix` — Quyết định `/grill-me` #1 & #3)
Khi `EvaluateOutboundCompliance` được gọi, `M20-F03` đánh giá theo đúng thứ tự ưu tiên từ `1` đến `5` dưới đây:

1. **Bước 1 — Kiểm tra Trạng thái Xóa / Khóa Pháp lý (`Erasure & Restricted Legal Hold`):**
   - Nếu `endpoint_lookup_hash` hoặc `contact_id` đã nằm trong `Deletion_Ledger` (đã thực thi xóa theo `UC11`), hoặc đang ở chế độ `RESTRICTED_LEGAL_HOLD` và `purpose_code IN ('MARKETING_PROMO', 'SURVEY_VOC')` $\rightarrow$ **`BLOCK` (`OUTBOUND_SUPPRESSED_ERASED_OR_LEGAL_HOLD`)**.
2. **Bước 2 — Kiểm tra Lỗi Kỹ thuật Cứng của Điểm liên hệ (`Hard-Bounce / Invalid Endpoint` — `SEC05`):**
   - Nếu `Endpoint_Suppressions` ghi nhận `reason_code IN ('HARD_BOUNCE', 'INVALID_ENDPOINT', 'PROVIDER_BLOCKED')` đang `ACTIVE` trên `(workspace_id, channel, endpoint_lookup_hash)` $\rightarrow$ **`BLOCK` (`OUTBOUND_SUPPRESSED_HARD_BOUNCE`)** đối với mọi lệnh gửi tự động trên kênh đó cho tới khi điểm liên hệ được xác minh lại bằng bằng chứng mới.
3. **Bước 3 — Kiểm tra Khiếu nại Spam & Từ chối Liên hệ lại (`Complaint / Refused Callback / Manual DNC` — `SEC05`, `CX-U15`):**
   - Nếu `Endpoint_Suppressions` có `reason_code IN ('SPAM_COMPLAINT', 'REFUSED_CALLBACK', 'MANUAL_DNC')`:
     - Chặn tuyệt đối `MARKETING_PROMO` và `SURVEY_VOC` (`M12-AC02`, `CX-U15`).
     - Với `SERVICE_NOTIFICATION`: chỉ cho phép nếu gắn trực tiếp với nghĩa vụ hợp đồng/hóa đơn/ticket đang mở do chính khách hàng yêu cầu xử lý và có cờ `transactional_exempt = true`.
4. **Bước 4 — Kiểm tra Rút sự đồng ý / Hủy đăng ký (`Unsubscribe / Consent Revoked` — `M20-F02`, `OC17`, `U15`):**
   - Nếu `purpose_code IN ('MARKETING_PROMO', 'SURVEY_VOC')`:
     - Tra cứu `Endpoint_Suppressions` theo `(workspace_id, channel, endpoint_lookup_hash, purpose_code)`: nếu có bản ghi `UNSUBSCRIBE` hoặc `CONSENT_REVOKED` đang hiệu lực $\rightarrow$ **`BLOCK` (`OUTBOUND_SUPPRESSED_UNSUBSCRIBE`)** (bất kể `contact_id` vừa được `Merge`, `Undo Merge` hay vừa được `Import` lại từ file Excel — `M20-AC01`, `CX-U20`, `SEC-U05`).
     - Tra cứu `Consent_States`: nếu `purpose_code = 'MARKETING_PROMO'` mà điểm liên hệ đó chưa từng có `Consent_State.status = 'GRANTED'` hợp lệ (ví dụ: form web bị spam hoặc email chưa xác minh — `OC22`, `RV11`) $\rightarrow$ **`BLOCK` (`OUTBOUND_MISSING_CONSENT_EVIDENCE`)**.
   - Nếu `purpose_code = 'SERVICE_NOTIFICATION'` (ví dụ: phản hồi Ticket hỗ trợ đang mở, thông báo nghiệm thu/hóa đơn của hợp đồng đang hiệu lực — `OC17`): việc khách rút `MARKETING_PROMO` **không làm mất hoặc chặn phản hồi dịch vụ hợp lệ**.
5. **Bước 5 — Kiểm tra Xác thực Đầu gửi (`Sender Authentication Gate` — `SEC05`):**
   - Nếu `channel = 'EMAIL'` mà `sender_profile_id` chưa đạt xác thực `SPF/DKIM/DMARC` và chưa cấu hình `List-Unsubscribe` header hợp lệ $\rightarrow$ **`BLOCK` (`SENDER_AUTHENTICATION_NOT_VERIFIED`)**.

#### Đầu ra (`OutboundComplianceDecision`)
```json
{
  "decision": "ALLOW | BLOCK",
  "block_reason_code": "NONE | OUTBOUND_SUPPRESSED_UNSUBSCRIBE | OUTBOUND_SUPPRESSED_HARD_BOUNCE | OUTBOUND_SUPPRESSED_COMPLAINT_OR_DNC | OUTBOUND_MISSING_CONSENT_EVIDENCE | SENDER_AUTHENTICATION_NOT_VERIFIED",
  "suppression_id": "uuid | null",
  "consent_state_version": 12,
  "evaluated_at": "2026-11-16T00:45:00Z"
}
```

---

### 2.2. Cổng 2: `EvaluateVendorAndAiTransfer` (Kiểm duyệt Chuyển Dữ liệu sang AI / Cloud Vendor — `M20-F01`, `M20-F07`, `RV17`)

#### Đầu vào (`EvaluateVendorAndAiTransferInput`)
```json
{
  "tenant_id": "uuid",
  "workspace_id": "uuid",
  "feature_code": "M06_THREAD_SUMMARY | M06_REPLY_DRAFT | M19_EXTERNAL_WEBHOOK | M21_PARTNER_SYNC",
  "vendor_code": "string",
  "purpose_code": "string",
  "data_classes": ["CONTACT_PII", "CONVERSATION_TEXT", "CONTRACT_COMMERCIAL", "NATIONAL_ID_OR_BANK"],
  "raw_payload": {
    "text": "Khách Nguyễn Văn A, SĐT 0901234567, CCCD 079099001122 hỏi về hợp đồng..."
  }
}
```

#### Quy tắc Đánh giá & Làm mờ PII (`AI & Vendor Gate Rules` — Quyết định `/grill-me` #3)
1. **Kiểm tra Hồ sơ Xử lý (`Processing_Records` — `M20-F01`) và Hồ sơ Nhà cung cấp (`Vendor_Data_Flows` — `M20-F07`):**
   - Nếu `(workspace_id, feature_code, purpose_code)` chưa có `Processing_Records.status = 'ACTIVE'` hoặc `vendor_code` chưa có `Vendor_Data_Flows.status = 'APPROVED'` (hoặc vùng lưu trữ `region` / thời hạn lưu log `vendor_retention_days` vượt quá giới hạn cho phép của workspace) $\rightarrow$ **`BLOCK` (`VENDOR_TRANSFER_POLICY_BLOCKED`)**.
   - **Không đánh đồng `No-Train` với `Zero-Data-Retention` (`RV17`):** Cờ `vendor_no_train = true` chỉ có nghĩa là nhà cung cấp AI không dùng dữ liệu để huấn luyện mô hình chung; hệ thống vẫn bắt buộc kiểm tra `vendor_log_retention_days` và chính sách xóa của vendor.
2. **Chặn cứng Nhóm Dữ liệu Cấm Gửi Ra Ngoài (`Prohibited Egress Data Classes`):**
   - Các trường `CCCD/CMND`, `Số tài khoản ngân hàng đầy đủ`, `Mật khẩu/Token`, `Bảng lương cá nhân (M22)` hoặc hồ sơ đang gắn `RESTRICTED_LEGAL_HOLD` **tuyệt đối không được gửi ra AI bên thứ ba**, kể cả khi tính năng AI đang bật (`6.3` dòng `3174`).
3. **Tự động Thay thế PII bằng Placeholder có Kiểm soát (`Deterministic Pseudonymization`):**
   - Trước khi trả `ALLOW_REDACTED` cho `M06`, `M20-F07` thay thế các thông tin định danh cá nhân được phép xử lý trong văn bản bằng token giả lập (`[PII_PHONE_1]`, `[PII_EMAIL_1]`, `[PII_PERSON_1]`) và lưu bảng ánh xạ tạm thời (`Placeholder_Vault` có TTL ngắn, gắn chặt `tenant_id + workspace_id + actor_id`) để chỉ người có quyền mới giải mã ngược được trên giao diện.

---

### 2.3. Cổng 3: `VerifyPostRestoreComplianceGate` (Đối soát Sổ Xóa & Danh sách Chặn sau khi Khôi phục Backup — `M20-F06`, `INT26`)

- **Kích hoạt:** Bắt buộc chạy trước khi mở lại lưu lượng người dùng và trước khi bật lại `M19` Outbox / `M04` Journey sau bất kỳ thao tác khôi phục cơ sở dữ liệu nào (`Restore from Backup`).
- **Hành vi:**
  1. Đọc toàn bộ bản ghi trong kho `Deletion_Ledger` và `Endpoint_Suppressions` (được lưu bền trên nhánh lưu trữ độc lập/append-only tới thời điểm mới nhất trước sự cố).
  2. Tự động quét và xóa/ẩn danh lại toàn bộ các bản ghi khớp `subject_hmac_sha256` / `endpoint_hmac_sha256` vừa bị khôi phục từ bản backup cũ, đồng thời hủy (`CANCELLED_BY_SUPPRESSION`) mọi `Outbound_Intents` và `Journey_Instances` đang chờ gửi tới các điểm liên hệ đã rút consent sau thời điểm backup (`INT26`, `M20-AC03`).
  3. Chỉ khi đối soát đạt `100%` (`pending_reapply_count == 0`), cổng mới trả về `READY_TO_OPEN_TRAFFIC`.

---

## 3. Các Sự kiện Miền Phát Qua Outbox (`Published Domain Events`)

| Tên Sự kiện (`Event Type`) | Khi nào phát (`Trigger`) | Payload chính | Consumers bắt buộc xử lý |
|---|---|---|---|
| `M20.EndpointSuppressed` | Khách rút consent (`Revoke`), bấm `Unsubscribe`, bị `Hard-Bounce`, `Spam-Complaint` hoặc từ chối gọi lại (`Refused Callback`) | `tenant_id`, `workspace_id`, `channel`, `endpoint_lookup_hash`, `purpose_scope[]`, `reason_code`, `effective_at` | `M04` (dừng bước gửi Journey đang chờ — `U15`), `M19` (hủy `Outbound_Intents` đang xếp hàng — `OC17`, `RV17`), `M12` (khóa gọi lại khảo sát — `CX-U15`) |
| `M20.SubjectErasureExecuted` | Thực thi hoàn tất lệnh xóa/ẩn danh theo `Privacy_Request` (`UC11`) hoặc hết hạn `Retention` (`M20-F06`) | `tenant_id`, `workspace_id`, `privacy_request_id`, `subject_hmac_sha256`, `erased_scopes[]`, `retained_legal_hold_scopes[]`, `executed_at` | `M01/M02/M03` (ẩn danh hồ sơ/tin nhắn), `M06` (xóa AI vector/cache), `M24` (xóa chỉ mục tìm kiếm `Search Index` và file export cũ) |
| `M20.LegalHoldChanged` | Đặt mới hoặc gỡ bỏ `Legal_Hold` trên một chủ thể/hợp đồng/hồ sơ (`M20-F06`) | `tenant_id`, `workspace_id`, `target_type`, `target_id`, `hold_status` (`ACTIVE \| RELEASED`), `legal_basis`, `review_due_at` | `M08/M09` (khóa xóa chứng từ), `M14` (áp chế độ chỉ đọc hạn chế `RESTRICTED_LEGAL_HOLD`), `M21/M22` |
| `M20.DataIncidentEscalated` | Phát hiện sự cố rò rỉ dữ liệu cá nhân (`M20-F08`) tại mốc `awareness_at` | `tenant_id`, `workspace_id`, `incident_id`, `awareness_at`, `affected_data_classes[]`, `severity`, `owner_id` | `M11-F07` (điều phối sự cố nghiêm trọng), `M16` (tạo task khắc phục và thông báo theo hạn pháp lý), `M23` (thu hồi token/cô lập kết nối) |
