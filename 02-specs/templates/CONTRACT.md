# CONTRACT-Mxx-TEN — Tên Public Contract

> Khuôn mẫu chuẩn cho `02-specs/contracts/<PRODUCER>-<TEN-CONTRACT>.md` (`Documentation-Only`). Định nghĩa hợp đồng dùng chung giữa Producer và các module Consumer; không sao chép nguyên bản ghi DB vào DTO công khai.

---

## 1. Thông tin & Đặc tả Tổng quát (`12` Phần Bắt buộc)

- **Contract ID & Version:** `CONTRACT-Mxx-TEN-v1.0` (`schema_version: "1.0"`)
- **Producer Owner:** `Mxx` (`02-specs/modules/Mxx-TEN-MODULE.md`)
- **Consumers:** `Myy`, `Mzz`
- **Source Requirements:** `<FRxx / UCxx / ADR-xxx>`
- **Status:** `Draft` *(hoặc `Reviewed` / `Ready (Scope: ...)` kèm `Approved_Scope`, `Approved_By`, `Decision_Ref`, `Approved_At`)*
- **Breaking-Change Policy:** Chỉ mở rộng additive trong cùng major version; breaking change phải nâng major version, hỗ trợ dual-consume/upcast hoặc mở `CR-*` cho toàn bộ Consumer chịu ảnh hưởng.

| Phần | Quy chuẩn bắt buộc *(phải điền nội dung thực chất, không để trống hoặc ghi TBD)* |
|---|---|
| `Meaning` | `<Ý nghĩa nghiệp vụ chính xác của command/event; không đặt tên mơ hồ>` |
| `Actor/scope` | `<Principal types, 6 GUC tenant/workspace/branch/legal_entity/business_line, resource grant & trusted source>` |
| `Preconditions` | `<Trạng thái aggregate, policy version ACTIVE, authority M14, capability flag>` |
| `Input` | `<Tóm tắt runtime contract & quy tắc field provenance; chi tiết Compact Field-Map JSON ở Mục 2>` |
| `Output` | `<Trường công bố, version, status; tách biệt khỏi internal DB row>` |
| `Errors` | `<Mã lỗi validation/auth/conflict/dependency (400/401/403/404/409/422/503) & chính sách non-disclosure>` |
| `Concurrency` | `<expected_version / CAS / lease_token fencing và kết quả cho request thua cuộc (409)>` |
| `Idempotency` | `<Scope khóa idempotency, hash body check, same-key-different-body -> 409/422, TTL retention & replay semantics>` |
| `Transaction` | `<Ranh giới atomic domain mutation + history + Dual Outbox M19 / M23-F12; external side-effect chỉ sau commit>` |
| `Compatibility` | `<Xử lý event cũ còn tồn trong outbox/backlog, consumer version pinning & chiến lược upcast>` |
| `Audit/privacy` | `<correlation_id, actor_id, reason, redact PII trước log/payload, retention & recipient ACL>` |
| `Tests` | `<Provider/consumer fixtures, negative/replay/race cases; tất cả giữ Not Run>` |

---

## 2. Giao diện Cổng / Lệnh (`Ports / Commands` — Compact Field-Map JSON + Ví dụ)

Mỗi cổng mô tả bằng **Compact Field-Map JSON** (không để `{}` rỗng; mọi trường ghi rõ `type | nullability | constraints`) **kèm ít nhất 1 khối JSON Ví dụ (`Example`)** khớp trường khai báo.

### 2.1. `<PortCommandName>` (`Command`)

- **Input Schema (Compact Field-Map JSON):**
```json
{
  "tenant_id": "uuid (required, trusted from M14.BindDbTransactionContext)",
  "workspace_id": "uuid (required, AGENCY|CLIENT per M14)",
  "idempotency_key": "string (required, 1..128 chars, scoped per workspace_id)",
  "expected_version": "integer (optional >= 1 for updates)",
  "correlation_id": "uuid (required, propagated end-to-end)"
}
```

- **Output Schema (Compact Field-Map JSON):**
```json
{
  "resource_id": "uuid (required)",
  "status": "string (required, CREATED|APPLIED|CONFLICT)",
  "row_version": "integer (required >= 1)",
  "processed_at": "string (required, ISO-8601 UTC)"
}
```

- **Ví dụ Payload (`Example`):**
```json
{
  "tenant_id": "11111111-1111-4111-8111-111111111111",
  "workspace_id": "22222222-2222-4222-8222-222222222222",
  "idempotency_key": "mxx-cmd-20261116-0001",
  "expected_version": 1,
  "correlation_id": "33333333-3333-4333-8333-333333333333"
}
```

---

## 3. Domain Events (`Published` & `Subscribed`)

### 3.1. Event Envelope Chuẩn (`ADR-005` — Qua `M23-F12` Nội bộ hoặc `M19` Ngoài)

Mọi Published Event bắt buộc có đủ `6` trường envelope: `event_id`, `event_type`, `schema_version`, `tenant_id`, `occurred_at`, `correlation_id`.

```json
{
  "event_id": "uuid (required, unique per emitted event)",
  "event_type": "string (required, e.g. Mxx.ResourceUpdated)",
  "schema_version": "string (required, e.g. 1.0)",
  "tenant_id": "uuid (required)",
  "occurred_at": "string (required, ISO-8601 UTC)",
  "correlation_id": "uuid (required)",
  "payload": {
    "workspace_id": "uuid (required)",
    "resource_id": "uuid (required)"
  }
}
```

- **Ví dụ Event Payload (`Example`):**
```json
{
  "event_id": "44444444-4444-4444-8444-444444444444",
  "event_type": "Mxx.ResourceUpdated",
  "schema_version": "1.0",
  "tenant_id": "11111111-1111-4111-8111-111111111111",
  "occurred_at": "2026-11-16T10:00:00Z",
  "correlation_id": "33333333-3333-4333-8333-333333333333",
  "payload": {
    "workspace_id": "22222222-2222-4222-8222-222222222222",
    "resource_id": "55555555-5555-4555-8555-555555555555"
  }
}
```

### 3.2. Danh sách Published Events

| Event Name | Trigger | Outbox Lane (`ADR-005`) | Payload Trọng yếu | Consumers Bắt buộc |
|---|---|---|---|---|
| `Mxx.ResourceUpdated` | `<Khi nào phát>` | `M23-F12 (Lane 2)` | `workspace_id`, `resource_id` | `Myy`, `Mzz` |

### 3.3. Danh sách Subscribed Events

| Nguồn & Event | Idempotency Key | Hành vi Tiêu thụ Bắt buộc | Lỗi / DLQ |
|---|---|---|---|
| `M20.SubjectErasureExecuted` | `deletion_ledger_id` | `<Xử lý scrub theo INV-27>` | `M23-F12 DLQ` |

---

## 4. Ma trận Kiểm thử Contract (`Not Run`)

| Mã Test | Loại (`Positive / Negative / Replay / Race`) | Tiền điều kiện & Hành động | Kết quả mong đợi quan sát được | Status / Evidence |
|---|---|---|---|---|
| `Cxx-T01` | `Positive` | `<Tiền điều kiện + request hợp lệ>` | `<200 OK + outbox event>` | `Not Run` |
| `Cxx-T02` | `Race` | `<2 request cùng expected_version>` | `<1 request 200 OK, 1 request 409 CONFLICT>` | `Not Run` |
