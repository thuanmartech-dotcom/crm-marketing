# Mxx — Tên module

Template; không phải module đã đặc tả hoàn chỉnh.

## Manifest

- Baseline path/version/hash + nguồn section/line.
- Status: Draft / Reviewed / Ready / Implemented / Verified (không tự nhảy trạng thái).
- Domain owner, accountable business role và technical reviewer.
- Owned entities/commands/events/projections; consumers và public contract links.
- Core/industry-pack boundary; dependency closure theo capability.
- Read first: invariants + active slice + contracts; read on demand: policies/ADR/tests.
- Allowed write paths: resolve theo repo thực, migration mới cụ thể; thay phạm vi ghi lý do.

## Requirement trace

| ID nguồn | Source anchor/hash | Ý nghĩa | Owner/consumer | Priority | Applicability | Test | Evidence |
|---|---|---|---|---|---|---|---|
| Điền | Điền | Không tự bổ sung không nhãn | Điền | Theo source/profile | Biểu thức capability | ID | Not Run |

## Hành vi

Mục tiêu; actor/scope; trigger; preconditions; input/default/validation; state machine; main flow; exceptions; concurrency; idempotency/retry; side effects; audit; metric. Phân biệt rule nguồn và thiết kế mới đề xuất.

## Data/API

ERD scoped; physical names/types/nullability/keys/indexes; lifecycle/history; runtime schemas; error envelope; auth matrix; version compatibility; producer/consumer tests. Không copy DB row vào public DTO. Thiếu field quyết định ghi GAP, không bịa.

## UI/operations

Screens/actions/empty/loading/error/permission states, accessibility, metric freshness; logs/alerts/runbook/retention/backup/restore; ownership khi integration lỗi.

## Migration và gate

Clean install/upgrade, backfill/reconcile, constraint debt nếu có, flag closure và phục hồi dữ liệu. Test matrix theo release profile: severity, capability priority, applicability, expected/actual/build/fixture/status/evidence. N/A có lý do; Not Run không là Pass. Ghi phạm vi chưa thực thi.
