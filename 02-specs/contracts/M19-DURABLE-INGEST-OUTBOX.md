# Contract: M19-DURABLE-INGEST-OUTBOX — Hợp đồng Thu nhận Bền vững, Phát Tin & Phục hồi Kết nối Ngoài

- **Contract ID / Version:** `M19-DURABLE-INGEST-OUTBOX` / `v1.0` (`[PROPOSED]` trên nền `[MASTER]` Mục `2.4`, `2.5`, `2.6`, `2.7`, `3.12`, `4.21`, `5.16`, `7.6`, `9.9–9.15`).
- **Baseline:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`).
- **Provider Owner:** [M19 — Kết nối Bên ngoài, Thu nhận Sự kiện, Phát Sự kiện & Phục hồi](../modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md).
- **Consumers:** `M01` (CDP Identity Intake), `M02` (Lead/Webhook Intake), `M03` (Omnichannel Inbox Receive/Send), `M04` (Journey Dispatch), `M08/M09` (Payment/E-Invoice Gateway), `M12` (Survey Delivery), `M16/M22` (PMS/Timekeeping Sync), `M21` (`API_READ` Partner Sales Adapter `M21-F06`).
- **Source Requirements:** `M19-F01..08`, `M19-AC01..03`, `UC21`, `ONFR01..06`, `SEC01`, `SEC02`, `SEC04`, `SEC-U01`, `SEC-U02`, `SEC-U04`, `FR30`, `FR33`, `FR34`, `FR38`, `FR40`, `INV-06`, `INV-07`, `INV-08`, `INV-23`, `OC01..09`, `OC14..16`, `OC19`, `OC21..23`, `INT01`, `INT11`, `INT24..26`, `RV05`, `RV11`, `RV17`, `OM-G01`, `OM-G02`, `OM-G07`, `OM-G08`, `OM-G09`, `OM-G10`.
- **Status:** `Reviewed` (Đã chốt kiến trúc 3 Trụ cột qua `/grill-me` ngày `16/11/2026`; test ứng dụng `Not Run`).
- **Breaking-Change Policy:** Mọi thay đổi trên envelope `InboundEventEnvelope`, quy tắc khử trùng lặp `(connection_id, external_event_id)`, hợp đồng trạng thái `UNKNOWN_OUTCOME` trên `OutboundDispatchResulted`, hoặc danh sách kiểm tra `RemoteFetchEgressRequest` bắt buộc tăng `major_version`, giữ dual-reader tối thiểu 1 release và chạy lại bộ kiểm thử `M19-AC01..03`, `SEC-U01/02/04`, `ONFR01..06`, `OC01/05/06/08/09`, `INT25`, `OM-G08`.

---

## 1. Bảng 12 Thành phần Hợp đồng (`12 Required Contract Parts`)

| Phần | Nội dung đặc tả chi tiết |
|---|---|
| **Meaning** | `[MASTER]` + `[PROPOSED]` Hợp đồng cổng giao tiếp biên duy nhất giữa CRM và toàn bộ nền tảng bên ngoài (Zalo OA/ZBS, Facebook Page/Lead Ads, TikTok Business Messaging, Gmail/Microsoft 365, Web Form, Tổng đài VoIP, Cổng Thanh toán/Ngân hàng, Hóa đơn điện tử, API Đối tác `M21-F06`), tách bạch hoàn toàn khỏi hàng đợi/DLQ nội bộ do `M23-F12` quản lý (`INV-23`). Hợp đồng gồm **3 giao diện vận hành** (`IngestWebhookEvent`, `DispatchOutboundIntent`, `ExecuteSafeBackfillOrRemoteFetch`) và **4 Domain Events** phát qua Outbox. |
| **Actor/scope** | `[MASTER]` (1) **Webhook Ingress Endpoint:** Không nhận `tenant_id / workspace_id` từ payload bên ngoài; **phải suy xuất `tenant_id` và `workspace_id` độc quyền từ bản ghi ánh xạ server `Channel_Connections` đang giữ quyền sở hữu `(provider, provider_namespace, external_account_id)` (`INV-07`, `SEC02`)**. (2) **Domain Callers (`M03`, `M04`, `M12`, `M21`):** Chỉ được gửi `Outbound_Intents` thuộc `Channel_Connections` ở trạng thái `ACTIVE` trong đúng `workspace_id` và đã kiểm `Connection_Capabilities` ở mức `verified` (`M19-F03`). (3) **Integration Operator (`M19-F07/08`):** Chỉ thao tác vận hành/health/replay trong scope được `M14` cấp; không tự động có quyền đọc nội dung chat/tài chính nếu thiếu `Entity_Team_Grant / Break-glass`. |
| **Preconditions** | `[MASTER]` (1) Với `IngestWebhookEvent`: Adapter phải xác minh chữ ký/secret đúng chuẩn từng kênh (Zalo/Meta signature, Telegram `X-Telegram-Bot-Api-Secret-Token`, Email/Form verification) và kiểm tra kích thước payload trước khi lưu (`3.12.12`). (2) Với `DispatchOutboundIntent`: Phải có `idempotency_key` duy nhất, `capability_code = 'send'` ở trạng thái `verified`, `M14-F04` cho phép actor hiện tại, và `M20-F03` (`DISPATCH_AUTHORITATIVE`) trả về `ALLOW`. (3) Với `RemoteFetch`: URL phải khớp allowlist host đã đăng ký trong manifest của `provider`. |
| **Input** | `[PROPOSED]` Xem chi tiết Schema đầu vào của `IngestWebhookEventInput`, `DispatchOutboundIntentInput` và `ExecuteSafeRemoteFetchInput` tại Mục 2 bên dưới. |
| **Output** | `[PROPOSED]` Xem chi tiết Schema đầu ra `InboundIngestAck`, `OutboundDispatchResult` (`ACCEPTED \| RETRY_SCHEDULED \| UNKNOWN_OUTCOME_RECONCILING \| BLOCKED_BY_POLICY \| FAILED_TERMINAL`) và `RemoteFetchResult` tại Mục 2 bên dưới. Tuyệt đối không lộ raw DB constraint, tên `workspace_id` đang giữ kết nối khác, hay access token ra ngoài (`SEC-U02`). |
| **Errors** | `[MASTER]` + `[PROPOSED]` Chuẩn hóa mã lỗi: `INGEST_SIGNATURE_INVALID` (`401`), `INGEST_QUOTA_OR_SIZE_EXCEEDED` (`413/429`), `INGEST_UNMAPPED_QUARANTINED` (`202 Accepted` vào `Quarantined_Events` nhưng không kích hoạt domain), `CONNECTION_OWNERSHIP_CONFLICT` (`409` — tài khoản đã thuộc owner khác, ẩn thông tin owner `SEC-U02`), `CAPABILITY_NOT_VERIFIED` (`422` — kênh chưa verify tính năng này `M19-F03`), `OUTBOUND_POLICY_BLOCKED` (`403` — chặn tại recheck bởi `M14`/`M20`), `OUTBOUND_WINDOW_OR_BUDGET_EXCEEDED` (`422` — quá cửa sổ 48h/7 ngày Zalo hoặc thiếu budget `OM-G01`), `OUTBOUND_UNKNOWN_OUTCOME` (`202` — khóa retry mù chờ đối soát `INT25`), `EGRESS_SSRF_BLOCKED` (`403` — URL trỏ vào loopback/private/metadata IP hoặc redirect trái phép `SEC-U04`). |
| **Concurrency** | `[MASTER]` (1) **Single Active Connection Lock:** Cưỡng chế bằng Unique Partial Index trên `Channel_Connections(provider, provider_namespace, external_account_id) WHERE status IN ('ACTIVE', 'DEGRADED', 'REAUTHORIZATION_REQUIRED')` để 2 workspace không bao giờ kích hoạt trùng cùng 1 Page/OA/Mailbox (`SEC-U02`). (2) **Token Refresh Mutex:** Worker làm mới OAuth token phải giữ distributed lock / `SELECT ... FOR UPDATE` trên `Channel_Connections` để hai worker không ghi đè mất `refresh_token` của nhau (`M19-F08`, `2.6`). (3) **Non-Blocking Network Call (`INV-06`):** Worker đánh dấu intent sang `DISPATCHING`, **nhả hoàn toàn DB transaction/lock**, thực hiện gọi HTTP ra provider, rồi mới mở transaction ngắn để ghi `Send_Attempts` và cập nhật trạng thái cuối. |
| **Idempotency** | `[MASTER]` (1) **Webhook Ingest:** Dùng khóa duy nhất `(tenant_id, connection_id, event_key)` (`UNIQUE` trong PostgreSQL — `ENTITY-L2824`). Khi cùng một sự kiện webhook đến 10 lần (`OC01`, `ONFR03`), lần 2..10 nhận `200 OK (deduplicated = true)` và không sinh Lead/Message/SLA mới. (2) **Outbound Send:** Dùng `UNIQUE (workspace_id, client_request_id / idempotency_key)` trên `Outbound_Intents` (`OC05`). Double-click cùng payload trả lại intent cũ; khác payload trả `409`. (3) **Backfill vs Realtime (`UC21`):** Dùng chung một pipeline dedup nhưng đánh dấu `source_mode = 'BACKFILL' | 'REPLAY'` để ngăn kích hoạt lại Journey hoặc SLA mới (`OC09`, `OM-G09`). |
| **Transaction** | `[MASTER]` (1) **Durable-Before-ACK (`INV-07`, `ONFR02`):** Webhook chỉ được trả HTTP `2xx` cho nhà cung cấp sau khi `INSERT INTO Inbound_Events` commit thành công trong DB (nếu DB lỗi/timeout $\rightarrow$ trả HTTP `5xx` để đối tác tự gửi lại). (2) **Atomic Domain Projection:** Worker đọc từ `Inbound_Events` cập nhật dữ liệu nghiệp vụ + `Domain Outbox` + cập nhật trạng thái `Inbound_Events.processing_status = 'PROCESSED'` trong cùng 1 transaction. (3) **Page-Atomic Checkpoint (`M19-F06`):** Con trỏ đồng bộ `Sync_Checkpoints` chỉ tiến lên sau khi toàn bộ các bản ghi trong 1 trang (`page`) đã được xử lý và commit bền vững (`2.7` dòng `325`). |
| **Compatibility** | `[MASTER]` + `[PROPOSED]` Hỗ trợ song song Adapter theo đúng `api_version` và bảng `Connection_Capabilities` độc lập cho 9 năng lực (`receive`, `send`, `attachments`, `delivery_receipt`, `read_receipt`, `history_backfill`, `edit`, `delete`, `native_reply_echo`). Năng lực nào ở trạng thái `pending_approval / unsupported / unknown` thì UI và API tự động khóa đúng nút thao tác tương ứng (`OM-G02`, `OC15`). |
| **Audit/privacy** | `[MASTER]` Tuyệt đối không ghi access token, refresh token, secret webhook, hoặc toàn bộ nội dung chat/email PII thô vào log kỹ thuật ứng dụng (`2.5` dòng `260`, `7.6` dòng `3319`). Toàn bộ OAuth token mã hóa trong Vault/Secret Manager; màn hình và DLQ chỉ hiển thị `secret_ref`, trạng thái hết hạn và mã lỗi đã làm sạch (`redacted`). Raw payload trong `Inbound_Events` tuân thủ chính sách xóa định kỳ `Retention_Policies` của `M20-F06` (`6.4`). |
| **Tests** | `[MASTER]` Provider & Consumer test fixtures: `M19-AC01..03`, `SEC-U01`, `SEC-U02`, `SEC-U04`, `ONFR01..06`, `OC01..09`, `OC14..16`, `OC19`, `OC21..23`, `INT01`, `INT11`, `INT24`, `INT25`, `INT26`, `RV05`, `RV11`, `RV17`, `OM-G01`, `OM-G02`, `OM-G07`, `OM-G08`, `OM-G09`, `OM-G10`. Trạng thái thực thi hiện tại: `Not Run`. |

---

## 2. Đặc tả Giao diện & Schema Chi tiết (`3 Pillars of M19 Contract`)

### 2.1. Trụ cột 1: `IngestWebhookEvent` (`Durable-Before-ACK` & Anti-Spoof)

#### Đầu vào chuẩn hóa từ Adapter Webhook (`IngestWebhookEventInput`)
```json
{
  "provider": "ZALO_OA | FACEBOOK_PAGE | TIKTOK_BM | GMAIL | MS_GRAPH | WEB_FORM | VOIP_SIP | PAYMENT_GW",
  "provider_namespace": "string (App ID / Bot ID / Region / Shop Cluster)",
  "external_account_id": "string (OA ID / Page ID / Mailbox / Form ID)",
  "signature_verification": {
    "algorithm": "HMAC_SHA256 | TELEGRAM_SECRET_HEADER | OAUTH_PUSH_JWT | SHARED_TOKEN",
    "verified_by_edge": true,
    "replay_timestamp_utc": "2026-11-16T01:05:00Z"
  },
  "event_key": "string (Ưu tiên provider_event_id; fallback hash phiên bản hóa có kiểm va chạm)",
  "event_type": "INBOUND_MESSAGE | MESSAGE_EDIT | DELIVERY_RECEIPT | READ_RECEIPT | LEAD_AD | PAYMENT_NOTICE | UNSUBSCRIBE",
  "source_mode": "LIVE | BACKFILL | REPLAY",
  "occurred_at_utc": "2026-11-16T01:04:58Z",
  "payload_storage_ref": "s3://crm-quarantine-or-payload/..."
}
```

#### Quy tắc Bảo đảm Bắt buộc
1. **Không bao giờ tin `tenant_id` / `workspace_id` trong payload webhook:** Webhook Ingress tra cứu `Channel_Connections` bằng `(provider, provider_namespace, external_account_id)` đang ở trạng thái nhận được (`ACTIVE | DEGRADED`). Nếu không tìm thấy hoặc chữ ký sai $\rightarrow$ từ chối `401/404` và ghi audit bảo mật. Nếu tìm thấy nhưng cấu trúc payload bất thường $\rightarrow$ lưu vào `Quarantined_Events` rồi mới trả `202` để tránh làm tắc luồng sự kiện hợp lệ kế tiếp (`M19-F04`, `3.12.11`).
2. **Ghi bền trước khi ACK (`ONFR02`):** Thực thi `INSERT INTO Inbound_Events (...) ON CONFLICT (connection_id, event_key) DO NOTHING`. Chỉ trả HTTP `200/202` khi DB đã `COMMIT` thành công (ngân sách nội bộ `p95 <= 1 giây`).
3. **Không lùi trạng thái khi event đến trễ (`OC07`, `OM-G08`):** Khi nhận `DELIVERED` sau `READ` hoặc trạng thái cũ đến muộn, `Delivery_Receipt_Events` lưu append-only toàn bộ lịch sử nhưng bộ giảm trạng thái (`Status Reducer`) giữ trạng thái cao hơn đã đạt (`READ > DELIVERED > ACCEPTED`).

---

### 2.2. Trụ cột 2: `DispatchOutboundIntent` (`Outbox Worker`, `Authoritative Recheck` & `UNKNOWN_OUTCOME`)

#### Đầu vào (`DispatchOutboundIntentInput`)
```json
{
  "tenant_id": "uuid",
  "workspace_id": "uuid",
  "outbound_intent_id": "uuid",
  "connection_id": "uuid",
  "idempotency_key": "uuid",
  "actor_id": "uuid (Actor hoặc Service Principal)",
  "expected_permission_version": 7,
  "channel": "ZALO | FACEBOOK | EMAIL | SMS | TIKTOK | WEBHOOK",
  "purpose_code": "MARKETING_PROMO | SURVEY_VOC | SERVICE_NOTIFICATION | SECURITY_LEGAL",
  "endpoint_lookup_hash": "char(64)",
  "expires_at": "2026-11-16T03:00:00Z",
  "message_ref": "uuid"
}
```

#### Quy tắc Thực thi & Xử lý Timeout (`Decision & Retry Matrix` — Quyết định `/grill-me` #2)
1. **Chốt chặn trước khi gọi mạng (Không dùng cache cũ):**
   - Kiểm tra `now() <= expires_at`: nếu intent đã quá hạn TTL (ví dụ do mất kết nối 2 giờ vừa kết nối lại — `OC08`, `UC21`), **hủy ngay (`EXPIRED_CANCELLED`)**, tuyệt đối không xả hàng loạt tin nhắn cũ cho khách.
   - Gọi đồng bộ `M14-F04` (`EvaluateAccessDecision`) với `expected_permission_version` để đảm bảo người gửi chưa bị thu hồi quyền/nghỉ việc lúc job đang chờ trong hàng đợi (`CEO-U18`, `INT23`).
   - Gọi đồng bộ `M20-F03` (`EvaluateOutboundCompliance` với `check_stage = 'DISPATCH_AUTHORITATIVE'`) để chặn ngay nếu khách vừa rút consent (`U15`, `INT17`, `OC17`).
   - Kiểm tra Cửa sổ gửi & Hạn mức (`Zalo 48h miễn phí vs OpenAPI 7 ngày có phí + budget`, `Meta tag policy` — `OM-G01`, `OC16`).
2. **Nhả khóa DB trước khi gọi Provider (`INV-06`):** Cập nhật `attempt_no`, `started_at`, `OUTBOUND_DISPATCHING` rồi `COMMIT` transaction trước khi mở kết nối HTTPS ra ngoài.
3. **Phân loại kết quả gọi API đối tác (`Retry vs UNKNOWN_OUTCOME`):**
   - `HTTP 2xx`: Lưu `provider_message_id`, chuyển `ACCEPTED` (lưu ý: `ACCEPTED != DELIVERED`, chờ webhook đối chiếu tiếp).
   - `HTTP 429 / 502 / 503` hoặc lỗi từ chối kết nối TCP trước khi gửi dữ liệu: Lên lịch retry theo công thức backoff `1 / 5 / 15 / 60 phút + jitter` (ưu tiên đọc header `Retry-After`).
   - `HTTP 401 / 403` (mất quyền OAuth/Token hết hạn): Dừng gửi trên `Connection`, chuyển trạng thái `Channel_Connections` sang `REAUTHORIZATION_REQUIRED`, giữ nguyên các intent còn TTL và phát cảnh báo cho Connection Owner (`ONFR05`).
   - **Read/Socket Timeout sau khi đã truyền payload sang Provider (`UNKNOWN_OUTCOME` — `INV-08`, `INT25`, `OM-G08`):** **TUYỆT ĐỐI KHÔNG RETRY MÙ**. Đánh dấu `Outbound_Intents.status = 'UNKNOWN_OUTCOME'`, tạo tác vụ đối soát tự động (gọi API tra cứu `message_id/request_ref` nếu provider hỗ trợ) hoặc đẩy vào hàng đợi `Reconciliation Queue` cho Operator xác minh kèm bằng chứng.

---

### 2.3. Trụ cột 3: `ExecuteSafeRemoteFetch` (`SSRF Guard` — `SEC04`, `SEC-U04`) & `Safe Replay`

#### Quy tắc Bảo vệ Tải Media từ URL Đối tác (`Remote Fetch Policy`)
1. **Allowlist & DNS-Rebinding Prevention:** Chỉ tải file từ danh sách domain chính thức thuộc manifest của `provider` (hoặc qua SDK/endpoint xác minh). Worker thực hiện phân giải DNS trước, **từ chối ngay (`EGRESS_SSRF_BLOCKED`) nếu bất kỳ địa chỉ IP kết quả nào thuộc dải `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16` (cloud metadata), `::1`, `fc00::/7`, `fe80::/10`, hoặc IP riêng/reserved**.
2. **Tắt Redirect Tự do & Bảo toàn Credential:** Mặc định `follow_redirects = false`. Nếu một provider đặc thù bắt buộc redirect CDN, mỗi hop chuyển hướng phải qua lại bước kiểm tra IP + Allowlist từ đầu và **tuyệt đối không gửi kèm Header chứa Access Token sang domain thứ hai**.
3. **Giới hạn Kích thước & Quét Mã độc:** Áp đặt `connect_timeout`, `read_timeout`, `max_bytes` (trước khi đọc hết stream), chặn nén bom giải nén (`decompression bomb`), kiểm tra chữ ký MIME thật và quét malware (`scan_status = 'CLEAN'`) trước khi cho phép `Download Gateway` (`SEC03`) hiển thị hoặc tải về (`OC14`).

---

## 3. Các Sự kiện Miền Phát Qua Outbox (`Published Domain Events`)

| Tên Sự kiện (`Event Type`) | Khi nào phát (`Trigger`) | Payload chính | Consumers bắt buộc xử lý |
|---|---|---|---|
| `M19.InboundEventPersisted` | Lưu bền sự kiện webhook/đồng bộ mới hợp lệ (không trùng) | `tenant_id`, `workspace_id`, `connection_id`, `inbound_event_id`, `provider`, `event_type`, `source_mode` (`LIVE \| BACKFILL \| REPLAY`), `occurred_at`, `payload_ref` | `M01/M03` (tiếp nhận hội thoại/identity), `M02` (Lead Ads/Webform), `M09` (biến động thanh toán), `M21` (`API_READ` dataset) |
| `M19.OutboundDispatchResulted` | Outbox Worker hoàn tất một lượt gửi tin hoặc chuyển trạng thái đối soát | `tenant_id`, `workspace_id`, `outbound_intent_id`, `status` (`ACCEPTED \| BLOCKED_BY_POLICY \| EXPIRED_CANCELLED \| UNKNOWN_OUTCOME \| FAILED_TERMINAL`), `provider_message_id`, `block_reason_code` | `M03` (cập nhật trạng thái bong bóng chat), `M04` (ghi nhận kết quả bước Journey), `M11` (xác nhận hoàn tất SLA `response_to`), `M12` (khảo sát) |
| `M19.ConnectionHealthChanged` | Trạng thái kết nối đổi sang `ACTIVE`, `DEGRADED`, `REAUTHORIZATION_REQUIRED`, `PAUSED`, hoặc `DISCONNECTED` | `tenant_id`, `workspace_id`, `connection_id`, `provider`, `old_status`, `new_status`, `capability_summary`, `owner_user_id` | `M03` (hiện badge cảnh báo mất kết nối trên Inbox), `M16` (tạo task khắc phục cho Owner nếu lỗi quyền quá 5 phút `ONFR05`), `M23` (giám sát sức khỏe) |
| `M19.SyncCoverageGapReported` | Đọc lịch sử (`Backfill`) hoàn tất nhưng API không hỗ trợ lấy đủ khoảng mất kết nối (`UC21`, `OC21`) | `tenant_id`, `workspace_id`, `connection_id`, `sync_run_id`, `coverage_from`, `coverage_to`, `gap_reason`, `is_recoverable` | `M03` (hiển thị banner cảnh báo khoảng trống lịch sử trung thực trên timeline), `M18` (đánh dấu chất lượng dữ liệu `Partial/Unknown` — không báo 100%) |
