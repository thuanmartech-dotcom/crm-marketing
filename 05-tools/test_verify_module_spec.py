"""Regression tests for verify_module_spec.py (documentation & traceability validator only)."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_module_spec as vms


def _real_baseline_sha() -> str:
    return hashlib.sha256(vms.MASTER.read_bytes()).hexdigest()


def _valid_module_text(baseline_sha: str) -> str:
    return f"""# M91 — Widget Test Module

## 1. Manifest

- **Baseline nguồn:** `CRM_MASTER_BRD_SRS_HOP_NHAT.md` (v1.9, `SHA-256: {baseline_sha}`)
- **Status:** `Reviewed`
- **Approved_Scope:** Wave 1 Validation Fixture
- **Approved_By:** Chủ dự án
- **Decision_Ref:** CR-TEST-001
- **Approved_At:** 2026-11-16

## 2. Requirement trace

| ID nguồn | Source anchor/line | Ý nghĩa | Owner/consumer | Hành vi / Contract | Priority | Applicability | Test | Evidence |
|---|---|---|---|---|---|---|---|---|
| `FR91` | `L100` | Tạo widget theo scope | `M91` | `### 3.1 M91-F01` | P0 | In Scope | `M91-AC01` | `Not Run` |
| `M91-F01` | `L101` | Create widget | `M91` | `### 3.1 M91-F01` | P0 | In Scope | `M91-AC01` | `Not Run` |
| `M91-F02` | `L105` | Read widget | `M91` | `### 3.2 M91-F02` | P0 | In Scope | `M91-AC02`, `[OPEN-GAP: GAP-01]` | `Not Run` |

## 3. Hành vi

### 3.1. `M91-F01` — Create Widget

- **Mục tiêu & Phạm vi:** Tạo widget gắn scope tenant/workspace (`[MASTER]`).
- **Tác nhân & Kích hoạt:** Actor nội bộ gọi `POST /widgets`.
- **Tiền điều kiện & Đầu vào bắt buộc:** Có `tenant_id`, `workspace_id`, `branch_id`, `legal_entity_id`, `business_line_id` và quyền hợp lệ qua `M14.EvaluateAccessDecision`.
- **Mô tả Nghiệp vụ & Cơ chế Hoạt động Từng bước:** Kiểm quyền rồi chèn `Widget_Items` và ghi `Widget_Audit_Logs`.
- **Đồng thời, Idempotency & Tác động phụ / Outbox:** Dùng `Idempotency-Key` trong bảng outbox cùng transaction.
- **Ngoại lệ & Quy tắc Hành vi (EARS):** `[MASTER]` When thiếu `tenant_id`, system shall reject `401/403` fail-closed. `[OPEN-GAP: GAP-01]`

### 3.2. `M91-F02` — Read Widget

- **Mục tiêu & Phạm vi:** Đọc danh sách widget đúng scope (`[PROPOSED]`).
- **Tác nhân & Kích hoạt:** Actor có grant hợp lệ truy vấn `GET /widgets`.
- **Tiền điều kiện & Đầu vào bắt buộc:** Có `tenant_id`, `workspace_id` và phạm vi RLS đã bind.
- **Mô tả Nghiệp vụ & Cơ chế Hoạt động Từng bước:** Lọc bằng compiled predicate trước khi trả kết quả.
- **Đồng thời, Idempotency & Tác động phụ / Outbox:** Read-only snapshot; không phát side effect ghi.
- **Ngoại lệ & Quy tắc Hành vi (EARS):** `[PROPOSED]` While thiếu grant, system shall deny access and emit `0` rows.

## 4. Data/API

### 4.1. Sơ đồ ERD

```mermaid
erDiagram
  Widget_Items ||--o{{ Widget_Audit_Logs : logs
```

### 4.2. Từ điển bảng

| Tên bảng độc lập | Nguồn truy vết Master | Các cột chuyên biệt & Kiểu dữ liệu | Nhóm kế thừa & Ràng buộc |
|---|---|---|---|
| `Widget_Items` | `[MASTER] L100` | `code varchar(50) NN`, `title text NN`, `branch_id uuid NULL`, `legal_entity_id uuid NULL`, `business_line_id uuid NULL` | `Nhóm A`; `UNIQUE (tenant_id, workspace_id, code)` |
| `Widget_Audit_Logs` | `[PROPOSED] ADR-004` | `event_code varchar(50) NN`, `actor_id uuid NN`, `occurred_at timestamptz NN` | `Nhóm C` (Append-only immutable) |

## 5. UI/operations

Hỗ trợ đủ 4 trạng thái Empty / Loading / Error / Conflict và logging ẩn PII.

## 6. Migration và gate

### 6.2. Ma trận Kiểm thử & Cổng Nghiệm thu

| Mã Test | Yêu cầu / Chức năng | Severity | Kịch bản kiểm thử & Tiêu chí Đậu | Actual | Build | Fixture | Applicability / Slice | Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| `M91-AC01` | `FR91`, `M91-F01` | Blocker | Nạp widget hợp lệ giữ cô lập scope | Not Run / No Repo | N/A (Docs-Only) | Clean Fixture | `SL01` | `Not Run` | `Not Run` |
| `M91-AC02` | `M91-F02` | Critical | Từ chối đọc trái phạm vi tenant/workspace | Not Run / No Repo | N/A (Docs-Only) | Cross-Tenant Fixture | `SL01` | `Not Run` | `Not Run` |
"""


def _valid_contract_text() -> str:
    return """# Contract C91 — Widget Port

## 1. Bảng chuẩn Contract

| Phần | Nội dung |
|---|---|
| `Meaning` | Cổng khởi tạo widget chuẩn hóa theo scope `tenant_id` / `workspace_id`. |
| `Actor/scope` | Internal worker hoặc backend service với 6 GUC scope hợp lệ. |
| `Preconditions` | Principal đã vượt qua cổng `M14.EvaluateAccessDecision`. |
| `Input` | `tenant_id`, `workspace_id`, `widget_code`, `idempotency_key`. |
| `Output` | `widget_id`, `status`, `schema_version`. |
| `Errors` | `401/403` AuthZ fail-closed; `409` idempotency conflict. |
| `Concurrency` | Khóa lạc quan `expected_version` và `UNIQUE (tenant_id, workspace_id, widget_code)`. |
| `Idempotency` | Trùng `idempotency_key` cùng payload trả kết quả cũ; khác payload trả `409`. |
| `Transaction` | Commit nghiệp vụ + outbox trong cùng 1 local DB transaction. |
| `Compatibility` | Additive optional fields trên `schema_version = "1.0"`. |
| `Audit/privacy` | Không đưa PII vào technical error logs; mọi lệnh có `correlation_id`. |
| `Tests` | `M91-AC01` (`Not Run` ở giai đoạn Docs-Only). |

## 2. Schemas Cổng Công khai

### 2.1. `CreateWidgetInput` & `CreateWidgetOutput`

```json
{
  "CreateWidgetInput": {
    "tenant_id": "uuid NN",
    "workspace_id": "uuid NN",
    "widget_code": "string NN (1..50 chars)",
    "idempotency_key": "string NN"
  },
  "CreateWidgetOutput": {
    "widget_id": "uuid NN",
    "status": "enum(ACTIVE|PENDING)",
    "schema_version": "string NN"
  }
}
```

**Ví dụ (`Example`) `CreateWidgetInput`:**

```json
{
  "CreateWidgetInput": {
    "tenant_id": "11111111-1111-4111-8111-111111111111",
    "workspace_id": "22222222-2222-4222-8222-222222222222",
    "widget_code": "WDG-001",
    "idempotency_key": "req-91001"
  }
}
```

## 3. Domain Events (`Published Events` & Envelope)

### 3.1. Envelope Chuẩn

```json
{
  "event_id": "uuid NN",
  "event_type": "string NN",
  "schema_version": "1.0",
  "tenant_id": "uuid NN",
  "occurred_at": "timestamptz UTC NN",
  "correlation_id": "uuid NN",
  "payload": {
    "widget_id": "uuid NN",
    "status": "string NN"
  }
}
```
"""


def _valid_slice_text(baseline_sha: str) -> str:
    return f"""# SL91 — Test Slice

## 1. Manifest

- **Baseline nguồn:** `SHA-256: {baseline_sha}`
- **Status:** `Reviewed`
- **Approved_Scope:** Wave 1 Slice Fixture
- **Approved_By:** Chủ dự án
- **Decision_Ref:** CR-TEST-001
- **Approved_At:** 2026-11-16

## 2. Phạm vi và Ranh giới

Thuộc phạm vi thử nghiệm `[OPEN-GAP: GAP-01]`.

## 3. Luồng Nghiệp vụ Chính

1. Nạp yêu cầu hợp lệ và xác nhận đầu ra bất biến.

## 4. Test Matrix

| ID | Setup/action | Kết quả bắt buộc | Status |
|---|---|---|---|
| `SL91-T01` | Gửi lệnh hợp lệ | Ghi thành công đúng scope | `Not Run` |

## 5. Danh sách Gate & GAP

- Giữ nguyên cổng `Not Run` trong Docs-Only.
"""


class VerifyModuleSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline_sha = _real_baseline_sha()
        cls.owned_map = {'M91': ['FR91', 'M91-F01', 'M91-F02']}
        cls.req_funcs = {'M91': ['M91-F01', 'M91-F02']}
        cls.real_gaps = vms.load_registered_gap_ids()
        cls.real_surface = vms.load_known_contract_surface()

    def _run_module_fixture(self, content: str, filename: str = 'M91-TEST.md') -> dict:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / filename
            p.write_text(content, encoding='utf-8')
            return vms.check_module_file(
                p,
                self.baseline_sha,
                self.owned_map,
                known_surface=self.real_surface,
                required_funcs_map=self.req_funcs,
                registered_gaps=self.real_gaps,
                root=Path(td),
            )

    def _run_contract_fixture(self, content: str, filename: str = 'M91-PORT.md') -> dict:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / filename
            p.write_text(content, encoding='utf-8')
            return vms.check_contract_file(p, registered_gaps=self.real_gaps, root=Path(td))

    def _run_slice_fixture(self, content: str, filename: str = 'SL91-TEST.md') -> dict:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / filename
            p.write_text(content, encoding='utf-8')
            return vms.check_slice_file(p, self.baseline_sha, registered_gaps=self.real_gaps, root=Path(td))

    def test_minimal_valid_fixtures_pass(self) -> None:
        mod_res = self._run_module_fixture(_valid_module_text(self.baseline_sha))
        con_res = self._run_contract_fixture(_valid_contract_text())
        sli_res = self._run_slice_fixture(_valid_slice_text(self.baseline_sha))
        self.assertTrue(mod_res['passed'], mod_res)
        self.assertTrue(con_res['passed'], con_res)
        self.assertTrue(sli_res['passed'], sli_res)

    def test_fake_module_hidden_ids_in_html_comment_wrong_hash_and_empty_tests_fails(self) -> None:
        fake = """# M91 — Fake Empty Module

## 1. Manifest
- **Baseline nguồn:** Master v1.9 (`SHA-256: deadbeef`)
- **Status:** `Reviewed`

## 2. Requirement trace
<!-- `FR91` `M91-F01` `M91-F02` -->
| ID nguồn | Hành vi / Contract | Test |
|---|---|---|

## 3. Hành vi
Chưa tách tiểu mục chức năng.

## 4. Data/API
### 4.2. Từ điển bảng
- Thiếu bảng và thiếu cột scope.

## 5. UI/operations
Tóm tắt ngắn.

## 6. Migration và gate
### 6.2. Ma trận Kiểm thử
| Mã Test | Yêu cầu | Severity | Kịch bản | Actual | Build | Fixture | Slice | Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|
"""
        res = self._run_module_fixture(fake)
        self.assertFalse(res['passed'])
        self.assertFalse(res['has_baseline_ref'])
        self.assertFalse(res['manifest_approval_ok'])
        self.assertFalse(res['trace_ids_complete'])
        self.assertIn('FR91', res['missing_ids_sample'])
        self.assertEqual(set(res['missing_function_subsections']), {'M91-F01', 'M91-F02'})
        self.assertFalse(res['test_matrix_rows_valid'])

    def test_fake_contract_with_12_headers_and_empty_json_blocks_fails(self) -> None:
        fake = """# Contract C91 — Empty

## 1. Metadata
| Phần | Nội dung |
|---|---|
| Meaning | Điền nội dung |
| Actor/scope | TBD |
| Preconditions | ... |
| Input | <input> |
| Output | - |
| Errors | Điền lỗi |
| Concurrency | TBD |
| Idempotency | TBD |
| Transaction | TBD |
| Compatibility | TBD |
| Audit/privacy | TBD |
| Tests | TBD |

## 2. Schemas

### 2.1. `EmptyPortInput`

```json
{}
```

## 3. Events (`Published Events`)

```json
{}
```
"""
        res = self._run_contract_fixture(fake)
        self.assertFalse(res['passed'])
        self.assertTrue(len(res['empty_contract_parts']) >= 1)
        self.assertTrue(len(res['empty_json_nodes']) >= 2)
        self.assertFalse(res['has_port_schema'])
        self.assertFalse(res['has_matching_example'])
        self.assertFalse(res['has_event_envelope_fields'])

    def test_module_missing_one_function_subsection_fails(self) -> None:
        txt = _valid_module_text(self.baseline_sha)
        broken = txt.split('### 3.2. `M91-F02`')[0] + '\n## 4. Data/API' + txt.split('## 4. Data/API')[1]
        res = self._run_module_fixture(broken)
        self.assertFalse(res['passed'])
        self.assertEqual(res['missing_function_subsections'], ['M91-F02'])

    def test_trace_test_id_missing_from_matrix_fails(self) -> None:
        txt = _valid_module_text(self.baseline_sha).replace('`M91-AC02`', '`M91-MISSING-99`', 1)
        res = self._run_module_fixture(txt)
        self.assertFalse(res['passed'])
        self.assertIn('M91-MISSING-99', res['missing_test_matrix_ids'])

    def test_nhom_c_table_with_updated_at_fails(self) -> None:
        txt = _valid_module_text(self.baseline_sha).replace(
            '`occurred_at timestamptz NN`',
            '`occurred_at timestamptz NN`, `updated_at timestamptz NN`',
        )
        res = self._run_module_fixture(txt)
        self.assertFalse(res['passed'])
        self.assertTrue(any('updated_at' in item for item in res['forbidden_immutable_columns']))

    def test_unregistered_open_gap_fails(self) -> None:
        txt = _valid_module_text(self.baseline_sha).replace('[OPEN-GAP: GAP-01]', '[OPEN-GAP: GAP-M99-99]')
        res = self._run_module_fixture(txt)
        self.assertFalse(res['passed'])
        self.assertIn('GAP-M99-99', res['unregistered_open_gaps'])

    def test_unknown_cross_module_contract_ref_fails(self) -> None:
        txt = _valid_module_text(self.baseline_sha).replace(
            '`M14.EvaluateAccessDecision`',
            '`M14.KhongTonTai`',
        )
        res = self._run_module_fixture(txt)
        self.assertFalse(res['passed'])
        self.assertIn('M14.KhongTonTai', res['unknown_cross_module_refs'])

    def test_contract_nested_empty_object_or_mismatched_example_fails(self) -> None:
        bad_nested = _valid_contract_text().replace(
            '"widget_id": "uuid NN",\n    "status": "string NN"',
            '"nested_empty": {}',
        )
        res1 = self._run_contract_fixture(bad_nested)
        self.assertFalse(res1['passed'])
        self.assertTrue(any('nested_empty' in e for e in res1['empty_json_nodes']))

        bad_ex = _valid_contract_text().replace('"tenant_id": "11111111-1111-4111-8111-111111111111",', '').replace(
            '"workspace_id": "22222222-2222-4222-8222-222222222222",', ''
        ).replace('"widget_code": "WDG-001",', '').replace('"idempotency_key": "req-91001"', '"unrelated": true')
        res2 = self._run_contract_fixture(bad_ex)
        self.assertFalse(res2['passed'])
        self.assertFalse(res2['has_matching_example'])

    def test_slice_missing_hash_or_approval_fails(self) -> None:
        bad_sha = _valid_slice_text('deadbeef' * 8)
        res1 = self._run_slice_fixture(bad_sha)
        self.assertFalse(res1['passed'])
        self.assertFalse(res1['has_baseline_ref'])

        no_appr = _valid_slice_text(self.baseline_sha).replace('- **Approved_Scope:** Wave 1 Slice Fixture\n', '')
        res2 = self._run_slice_fixture(no_appr)
        self.assertFalse(res2['passed'])
        self.assertIn('Approved_Scope', res2['missing_approval_fields'])

    def test_inv27_erasure_regression_checks_and_exemptions(self) -> None:
        # 1. Single-shot scrub phrasing in module fixture fails inv27_erasure_issues.
        bad_single_shot = _valid_module_text(self.baseline_sha).replace(
            'Read-only snapshot; không phát side effect ghi.',
            '`privacy_erasure_system_role` chỉ scrub 1 lần `M16.Task_Submissions.privacy_redacted_at`.',
        )
        res_single = self._run_module_fixture(bad_single_shot)
        self.assertFalse(res_single['passed'])
        self.assertTrue(res_single['inv27_erasure_issues'], res_single)

        # 2. Compound WHERE ... privacy_redacted_at IS NULL in module & contract fails.
        bad_mod_null = _valid_module_text(self.baseline_sha).replace(
            'Read-only snapshot; không phát side effect ghi.',
            'Cập nhật `Task_Submissions` `WHERE cardinality(active_legal_hold_ids) = 0 AND privacy_redacted_at IS NULL`.',
        )
        res_mod_null = self._run_module_fixture(bad_mod_null)
        self.assertFalse(res_mod_null['passed'])
        self.assertTrue(res_mod_null['inv27_erasure_issues'], res_mod_null)

        bad_con_null = _valid_contract_text().replace(
            'Không đưa PII vào technical error logs; mọi lệnh có `correlation_id`.',
            'Áp dụng 1-time scrub khi `privacy_redacted_at IS NULL`.',
        )
        res_con_null = self._run_contract_fixture(bad_con_null)
        self.assertFalse(res_con_null['passed'])
        self.assertTrue(res_con_null['inv27_erasure_issues'], res_con_null)

        # 3. Valid prohibition and historical replaced-design phrase in active module pass.
        good_prohibition = _valid_module_text(self.baseline_sha).replace(
            'Read-only snapshot; không phát side effect ghi.',
            '**Cấm dùng** khóa một lần `privacy_redacted_at IS NULL`; thiết kế cũ \'chỉ scrub 1 lần\' đã bị thay thế.',
        )
        res_good = self._run_module_fixture(good_prohibition)
        self.assertTrue(res_good['passed'], res_good)
        self.assertEqual(res_good['inv27_erasure_issues'], [])

        # 4. Mixed clause does NOT get exempted by an earlier unrelated negation.
        mixed_clause = _valid_module_text(self.baseline_sha).replace(
            'Read-only snapshot; không phát side effect ghi.',
            'Cấm admin tự xóa; `privacy_erasure_system_role` chỉ scrub 1 lần `M16.Task_Submissions`.',
        )
        res_mixed = self._run_module_fixture(mixed_clause)
        self.assertFalse(res_mixed['passed'])
        self.assertTrue(res_mixed['inv27_erasure_issues'], res_mixed)

        # 5. Sandbox-mutated M23 restoring historical bug fails check_module_file on inv27_erasure_issues.
        m23_real = (vms.SPECS / 'modules' / 'M23-SYSTEM-ADMIN-SECURITY-OPS.md').read_text(encoding='utf-8')
        m23_mutated_lines = [
            '   - `privacy_erasure_system_role` (chỉ scrub 1 lần `M16.Task_Submissions.privacy_redacted_at` ngoài `Legal_Hold` theo `ADR-004`).'
            if '**`privacy_erasure_system_role`**' in ln
            else ln
            for ln in m23_real.splitlines()
        ]
        m23_mutated = '\n'.join(m23_mutated_lines) + '\n'
        with tempfile.TemporaryDirectory() as td:
            m23_sandbox = Path(td) / 'M23-SYSTEM-ADMIN-SECURITY-OPS.md'
            m23_sandbox.write_text(m23_mutated, encoding='utf-8')
            owned_map = vms.load_owned_ids_by_module()
            req_funcs = vms.load_required_functions_by_module()
            res_m23_bad = vms.check_module_file(
                m23_sandbox,
                self.baseline_sha,
                owned_map,
                known_surface=self.real_surface,
                required_funcs_map=req_funcs,
                registered_gaps=self.real_gaps,
                root=Path(td),
            )
            self.assertFalse(res_m23_bad['passed'])
            self.assertTrue(res_m23_bad['inv27_erasure_issues'], res_m23_bad)

    def test_aligned_wave1_wave15_repo_files_pass(self) -> None:
        owned_map = vms.load_owned_ids_by_module()
        req_funcs = vms.load_required_functions_by_module()
        for mod_name in (
            'M14-ORG-ACCESS-DELEGATION.md',
            'M16-WORK-PROJECTS-TASK-CORE.md',
            'M19-INTEGRATION-ADAPTERS-OUTBOX.md',
            'M20-PRIVACY-CONSENT-RETENTION.md',
            'M23-SYSTEM-ADMIN-SECURITY-OPS.md',
            'M24-PERFORMANCE-AND-PRODUCTIVITY.md',
        ):
            res = vms.check_module_file(
                vms.SPECS / 'modules' / mod_name,
                self.baseline_sha,
                owned_map,
                known_surface=self.real_surface,
                required_funcs_map=req_funcs,
                registered_gaps=self.real_gaps,
            )
            self.assertTrue(res['passed'], res)
        for con_path in sorted((vms.SPECS / 'contracts').glob('*.md')):
            res = vms.check_contract_file(con_path, registered_gaps=self.real_gaps)
            self.assertTrue(res['passed'], res)
        sl01 = vms.check_slice_file(
            vms.SPECS / 'slices' / 'SL01-INTERNAL-WORK.md',
            self.baseline_sha,
            registered_gaps=self.real_gaps,
        )
        self.assertTrue(sl01['passed'], sl01)


if __name__ == '__main__':
    unittest.main()
