# Mxx — Tên module

> Khuôn mẫu đặc tả chuẩn hóa cho `02-specs/modules/Mxx-TEN-MODULE.md` (`Documentation-Only`). Không tự ý nâng `Status` hoặc ghi `Pass` cho kiểm thử ứng dụng CRM.

---

## 1. Manifest

- **Baseline:** `Master v1.9` (`00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md`) — `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c` — Nguồn mục/dòng: `<Mục 3.x L...; 4.x L...; 5.x L...>`
- **Status:** `Draft` *(chỉ nâng lên `Reviewed` hoặc `Ready (Scope: <phạm vi>)` khi có xác nhận và điền đủ 4 trường duyệt bên dưới; giữ nguyên `Documentation-Only`)*
- **Approved_Scope:** `N/A (Draft)` *(khi `Reviewed`/`Ready`: nêu rõ phạm vi đã duyệt)*
- **Approved_By:** `N/A (Draft)` *(vai trò/chủ dự án duyệt)*
- **Decision_Ref:** `N/A (Draft)` *(mã `CR-*` hoặc phiên chốt quyết định; đề xuất `[PROPOSED]` đã duyệt vẫn giữ nguyên nhãn `[PROPOSED]` kèm `decision_ref`, không đổi thành `[MASTER]`)*
- **Approved_At:** `N/A (Draft)` *(`YYYY-MM-DD`)*
- **Domain Owner & Roles:** `<Accountable business role | Technical reviewer>`
- **Owned Entities / Commands / Events / Projections:** `<Liệt kê thực thể sở hữu SSoT, lệnh, domain events và read projections>`
- **Consumers & Public Contract Links:** `<Danh sách module tiêu thụ + link tới 02-specs/contracts/*.md liên quan>`
- **Core / Industry-Pack Boundary & Capability Closure:** `<Core vs Pack P0/P1/P2; điều kiện capability>`
- **Read First / Read On Demand:**
  - *Read first:* `INVARIANTS.md`, `INDEX.md`, `CONTRACTS-REGISTRY.md`, `03-planning/waves/WAVE-x-PLAN.md`, `03-planning/modules/Mxx-COMPLETION-PLAN.md`
  - *Read on demand:* `<Public contracts, ADR-001..009, dải dòng Master v1.9>`
- **Allowed Write Paths:** `Documentation-Only` (`02-specs/modules/Mxx-TEN-MODULE.md`, `02-specs/contracts/Mxx-*.md`; `application_write_scope: null`).

---

## 2. Requirement trace

Bao phủ **100% ID** có `owner == Mxx` trong `03-planning/trace/requirements.json` và các ID liên quan thuộc nhóm `missing_owner`/`PLATFORM` (`GAP-03`) ngay trong các hàng bảng dưới đây (cấm giấu trong HTML comment hoặc đoạn văn rời).

| ID nguồn | Source anchor/line | Ý nghĩa | Owner/consumer | Hành vi / Contract | Priority | Applicability | Test | Evidence |
|---|---|---|---|---|---|---|---|---|
| `<FRxx / UCxx / Mxx-F01>` | `<3.x L123>` | `<Tóm tắt ngắn>` | `Primary Owner: Mxx` / `Consumer: Myy` | `### 3.1 Mxx-F01` / `Cxx` | `P0` | `<Capability/Slice>` | `<Mxx-T01>` *(phải tồn tại ở `## 6.2`)* | `Not Run` |

---

## 3. Hành vi

### 3.0A. Tổng quan Cơ chế Hoạt động của Module

Mô tả luồng nghiệp vụ đầu-cuối của module và vẽ sơ đồ `flowchart TD` nối liền các chức năng `Mxx-Fyy` với cổng nền tảng (`M14`, `M19`, `M20`, `M23`, `M24`).

### 3.0B. Mô hình Máy trạng thái Cốt lõi

Vẽ `stateDiagram-v2` cho các thực thể có $\ge 3$ trạng thái (nêu rõ `N/A (<lý do>)` nếu stateless), kèm bảng chuyển trạng thái hợp lệ/bị cấm và tác nhân có quyền chuyển.

### 3.1. Mxx-F01 — `<Tên chức năng>`

*(Lặp lại đủ 1 tiểu mục `### 3.x Mxx-Fyy` cho 100% chức năng trong `FUNCTION-CATALOG.md`, mỗi chức năng có đủ 6 phần con bên dưới.)*

- **Mục tiêu & Phạm vi:** `<Mục tiêu nghiệp vụ, phạm vi P0/P1/P2 và ranh giới với module khác>`
- **Tác nhân & Kích hoạt:** `<Actor, Trigger command/event/schedule>`
- **Tiền điều kiện & Đầu vào bắt buộc:** `<Quyền M14 / 6 GUC, trạng thái hợp lệ, policy active, input/default>`
- **Mô tả Nghiệp vụ & Cơ chế Hoạt động Từng bước:** `<Từng bước xử lý kèm ví dụ thực tế cụ thể>`
- **Đồng thời, Idempotency & Tác động phụ / Outbox:** `<expected_version/CAS, idempotency_key, lease_token nếu nhả lock theo INV-26, Dual Outbox M19 ngoài vs M23-F12 nội bộ theo ADR-005 — hoặc ghi N/A kèm lý do>`
- **Ngoại lệ & Quy tắc Hành vi (EARS):**
  - `[MASTER] Khi ..., Mxx phải ...` (`R-Mxx-F01-01`, Test: `Mxx-T01`)
  - `[PROPOSED] Nếu ..., Mxx phải ...` (`R-Mxx-F01-02`, Test: `Mxx-T02`)
  - `[OPEN-GAP: GAP-Mxx-01] Nếu thiếu cấu hình ..., Mxx phải ... (Fail-Closed)` (`R-Mxx-F01-03`, Test: `Mxx-T03`)

---

## 4. Data/API

### 4.1. Mô hình Dữ liệu Logic (`ERD Scoped`)

```mermaid
erDiagram
  %% Chỉ khai báo thực thể và quan hệ thuộc phạm vi module
```

### 4.2. Từ điển Thực thể & Phân nhóm Kế thừa (`ADR-004` — `1 bảng = 1 dòng`)

Tuân thủ [ADR-004](../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md): tách mọi bảng gộp thành **1 bảng = 1 dòng**, phân loại rõ `Nhóm A` (`12` cột chuẩn gồm `tenant_id`, `workspace_id NN`, `branch_id`, `legal_entity_id`, `business_line_id`...), `Nhóm B-Catalog`, `Nhóm B-Governance-Sensitive` (`app.current_workspace_type IN ('AGENCY', 'SYSTEM')`), hoặc `Nhóm C` (`Append-Only`: kế thừa `occurred_at`, `received_at`, `correlation_id` — **tuyệt đối cấm `updated_at`, `updated_by`, `row_version`, `archived_at`**). Nếu bảng bất biến cho phép scrub PII, áp dụng `redacted_deletion_ledger_ids uuid[]`, giữ nguyên `content_sha256` gốc và tính riêng `redacted_content_sha256` (`INV-27`).

| Bảng Logic | Mã `ENTITY` | Nhóm Kế thừa (`ADR-004`) | Trường Trọng yếu, Nullability & Ràng buộc | Ghi chú Bất biến / PII / Hold |
|---|---|---|---|---|
| `Example_Table` | `ENTITY-Lxxxx` | `Nhóm A` | `id uuid PK`, `idempotency_key text`, `row_version int`... | `[MASTER]` / `[PROPOSED]` |

### 4.3. Tham số Mở & Chính sách (`7` Trường Phân loại Khớp `03-planning/GAPS.md`)

Mọi `[OPEN-GAP]` trong spec phải đăng ký đủ 7 trường phân loại tại bảng này và đồng bộ 1-1 với [03-planning/GAPS.md](../../03-planning/GAPS.md).

| ID GAP | Tham số / Chính sách Mở | Chặn thiết kế? | Chặn triển khai? | Chặn kích hoạt? | Phạm vi bị chặn | Hành vi khi thiếu cấu hình (`Fail-Closed` / `Safe Default`) | Người quyết định | Điều kiện đóng |
|---|---|---|---|---|---|---|---|---|
| `GAP-Mxx-01` | `<Tên tham số>` | `Không` | `Có/Không` | `Có` | `<Phạm vi/chức năng>` | `Fail-Closed: ...` | `<Vai trò>` | `<Điều kiện chốt>` |

### 4.4. Giao diện Command / Query / Error Envelope & Public Contracts

- **Public Contracts phát hành / tiêu thụ:** `<Link tới 02-specs/contracts/*.md>`
- **Lệnh & Truy vấn nội bộ module:**

| Command / Query | Actor & Quyền (`M14`) | Đầu vào chính | Đầu ra / Trạng thái | Mã lỗi & Non-disclosure | Idempotency & Concurrency |
|---|---|---|---|---|---|
| `<CommandName>` | `<Role / Grant>` | `<Fields>` | `<200/201 Payload>` | `<400/403/404/409/422>` | `<expected_version / idempotency_key>` |

---

## 5. UI/operations

- **Màn hình & Hành động chính:** `<Danh sách màn hình, action, kiểm tra quyền trên UI>`
- **4 Trạng thái UI bắt buộc:** `Empty` (gồm trạng thái chưa cấu hình policy) | `Loading` | `Error` | `Permission Denied` (non-disclosure)
- **Độ tươi dữ liệu, Log, Alert, Runbook & Khôi phục:** `<Metric freshness, retention, backup/restore, ownership khi integration lỗi>`

---

## 6. Migration và gate

### 6.1. Chiến lược Migration, Backfill, Feature Flag Closure & Phục hồi

Mô tả clean install, upgrade không phá vỡ (`INV-15`), backfill/reconcile idempotent, feature flag closure (`M23-F09`) và điều kiện DR (`ADR-007`).

### 6.2. Test Applicability Matrix (`10` Cột Chuẩn — Giữ `Not Run`)

Tách riêng ca thành công (`200 OK`) khỏi ca xung đột (`409`) (`INV-28`). Mọi dòng bắt buộc ghi rõ **Tiền điều kiện & Hành động** và **Kết quả mong đợi quan sát được**; giữ `Build = N/A (Docs-Only)`, `Actual = Not Run / No Repo`, `Status / Evidence = Not Run`.

| Mã Test | Severity | Capability / Priority | Applicability | Tiền điều kiện & Hành động | Kết quả mong đợi quan sát được | Fixture | Build | Actual | Status / Evidence |
|---|---|---|---|---|---|---|---|---|---|
| `Mxx-T01` | `High` | `P0` | `SLxx` | `<Tiền điều kiện cụ thể + hành động gửi lệnh>` | `<HTTP status, DB state, outbox event quan sát được>` | `<Synthetic>` | `N/A (Docs-Only)` | `Not Run / No Repo` | `Not Run` |
