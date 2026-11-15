# Contract template — command/event/API

ID/version; provider owner; consumers; source requirement; status Proposed/Reviewed; breaking-change policy.

| Phần | Cần điền |
|---|---|
| Meaning | Điều gì được yêu cầu hoặc đã xảy ra; không dùng tên mơ hồ |
| Actor/scope | Principal, tenant/workspace, resource grant; trusted source |
| Preconditions | State, policy version, authority, capability |
| Input | Runtime schema, types/ranges/nullability, field provenance |
| Output | Fields được công bố, version, status; khác DB row |
| Errors | Validation/auth/conflict/dependency; non-disclosure policy |
| Concurrency | expected_version/CAS/lock và kết quả người thua |
| Idempotency | Key scope/hash, same-key-different-body, retention/replay semantics |
| Transaction | Mutation/history/outbox boundary; external effect sau commit |
| Compatibility | Event cũ còn tồn, consumer versions, migration/upcast nếu cần |
| Audit/privacy | Correlation/actor/reason; redact; retention và recipient ACL |
| Tests | Provider/consumer fixtures; negative/replay/race; run evidence |

Chọn một nguồn schema máy đọc được khi triển khai; sinh type/OpenAPI khi phù hợp và kiểm drift. Mock pass không thay capability thật; schema pass không thay semantics pass.
