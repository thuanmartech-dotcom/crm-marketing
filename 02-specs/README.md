# Danh mục Đặc tả Module & Slice (`02-specs/`)

Tài liệu theo dõi trạng thái phân rã từ [Master v1.9](../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md).  
Mục tiêu giai đoạn hiện tại là hoàn thiện đặc tả chi tiết cho toàn bộ module và slice trước khi giao cho AI Agent lập trình.

- **Danh mục 200 chức năng chi tiết & Sơ đồ luồng chức năng (`M01–M22`):** [FUNCTION-CATALOG.md](FUNCTION-CATALOG.md)

---

## 1. Khuôn mẫu chuẩn (`templates/`)

- [MODULE-SPEC.md](templates/MODULE-SPEC.md) — Khuôn mẫu đặc tả cho từng module (`M01–M22`).
- [CONTRACT.md](templates/CONTRACT.md) — Khuôn mẫu đặc tả contract command / event / API.
- [PARTNER-DATA-PROFILE.md](templates/PARTNER-DATA-PROFILE.md) — Mẫu phiếu cấu hình chia sẻ dữ liệu đối tác (`M21`).
- [PARTNER-REPORT.md](templates/PARTNER-REPORT.md) — Mẫu báo cáo dịch vụ và kết quả đối tác (`M21`).

### Hợp đồng Liên Module Đã Khóa (`contracts/`)

- [M14-PRINCIPAL-ACCESS-DECISION.md](contracts/M14-PRINCIPAL-ACCESS-DECISION.md) — Hợp đồng Kép kiểm tra quyền thực thi (`EvaluateAccessDecision` + `CompileScopeFilter`) và 4 Domain Events thu hồi/bàn giao của `M14`.
- [M20-SUPPRESSION-PRIVACY-GATE.md](contracts/M20-SUPPRESSION-PRIVACY-GATE.md) — Hợp đồng Kép kiểm duyệt chặn gửi thời gian thực (`EvaluateOutboundCompliance`), kiểm soát chuyển dữ liệu sang AI/Vendor (`EvaluateVendorAndAiTransfer`), đối soát sổ xóa sau Restore (`VerifyPostRestoreComplianceGate`) và 4 Domain Events của `M20`.
- [M19-DURABLE-INGEST-OUTBOX.md](contracts/M19-DURABLE-INGEST-OUTBOX.md) — Hợp đồng 3 trụ cột Ingest bền vững trước ACK (`Durable-Before-ACK`), Backfill/Replay an toàn TTL (`Safe Backfill & Replay`), tải media Zero-Trust (`SEC04`) và 4 Domain Events của `M19`.

---

## 2. Trạng thái 22 Module nghiệp vụ (`modules/`)

Nguồn định nghĩa: [Master 3.0](../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) và [modules.json](../03-planning/trace/modules.json).

| Mã | Tên module | Phạm vi dữ liệu sở hữu | Trạng thái spec riêng | Tệp đặc tả |
|---|---|---|---|---|
| M01 | Hồ sơ khách hàng, doanh nghiệp, định danh và hợp nhất | `Contacts/Accounts/Contact_Points/roles/merge` | Chờ phân tích & tách file | — |
| M02 | Tiếp nhận nhu cầu, phân lead, cơ hội và hoạt động bán hàng | `Leads/Deals/assignment/stage history/Activities` | Chờ phân tích & tách file | — |
| M03 | Hộp thư hợp nhất, trả lời và điều phối hội thoại | `Conversations/Messages/response links/assignment` | Chờ phân tích & tách file | — |
| M04 | Chăm sóc tự động và nhắc việc theo hành trình | `Journey definition/instance/send schedule` | Chờ phân tích & tách file | — |
| M05 | Giới thiệu khách hàng và tích điểm | `Referral/reward; loyalty ledger khi bật` | Chờ phân tích & tách file | — |
| M06 | Trợ lý AI: tóm tắt, gợi ý, soạn nháp | `AI draft/evaluation/model/prompt evidence` | Chờ phân tích & tách file | — |
| M07 | Danh mục dịch vụ, báo giá, SOW và phê duyệt chào bán | `Catalog/Quote_Lines/quote revision/approval` | Chờ phân tích & tách file | — |
| M08 | Hợp đồng, đơn dịch vụ, onboarding và gia hạn | `Contract/SOW/order/service period/handoff` | Chờ phân tích & tách file | — |
| M09 | Nghĩa vụ thu, nhận tiền, phân bổ, hoàn tiền và đối soát | `Receipt/evidence/obligation/allocation/refund/period` | Chờ phân tích & tách file | — |
| M10 | Hoa hồng và chi thưởng bán hàng | `Policy snapshot/pool/commission/payout/adjustment` | Chờ phân tích & tách file | — |
| M11 | Tiếp nhận hỗ trợ, khiếu nại, SLA và khắc phục sự cố | `Ticket/entitlement/SLA/promise/resolution` | Chờ phân tích & tách file | — |
| M12 | Phản hồi, CSAT/NPS và phục hồi trải nghiệm | `Feedback/survey/recovery/corrective action` | Chờ phân tích & tách file | — |
| M13 | Lịch hẹn và đặt tài nguyên | `Appointment/resource/booking/reminder` | Chờ phân tích & tách file | — |
| M14 | Tổ chức, chi nhánh, thành viên, quyền và bàn giao nhân sự | `Membership/role binding/team grant/delegation` | Đã tách & chốt thiết kế (`Reviewed` — `18/18` IDs) | [M14-ORG-ACCESS-DELEGATION.md](modules/M14-ORG-ACCESS-DELEGATION.md) |
| M15 | Brief, chiến lược, kế hoạch IMC và phê duyệt launch | `Brief/approved plan/campaign/launch/learning` | Chờ phân tích & tách file | — |
| M16 | Quản lý công việc cá nhân, đội nhóm, tổ chức, dự án và nguồn lực | `Task/assignment/review/recurrence/project/deliverable/acceptance` | Chờ tách file module *(đã có pilot SL01)* | — |
| M17 | Ngân sách, chi phí, nguồn tiền media và rủi ro hiệu quả | `Budget/commitment/cost/funding authorization` | Chờ phân tích & tách file | — |
| M18 | Từ điển chỉ số, báo cáo điều hành và attribution *(kèm đề xuất F08–11)* | `KPI definition/metric facts/report snapshot/P&L/ad-hoc` | Baseline v1.9 chờ tách đầy đủ *(đã có đề xuất mở rộng F08–11)* | [M18-BI-REPORTING-EXPANSION.md](modules/M18-BI-REPORTING-EXPANSION.md) |
| M19 | Kết nối bên ngoài, nhận/phát sự kiện và phục hồi | `Connection/capability/inbox/outbox/checkpoint` | Đã tách & chốt thiết kế (`Reviewed` — `24/24` IDs) | [M19-INTEGRATION-ADAPTERS-OUTBOX.md](modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md) |
| M20 | Consent, yêu cầu dữ liệu, retention và quản trị mục đích | `Processing/consent/suppression/privacy/retention` | Đã tách & chốt thiết kế (`Reviewed` — `14/14` IDs) | [M20-PRIVACY-CONSENT-RETENTION.md](modules/M20-PRIVACY-CONSENT-RETENTION.md) |
| M21 | Kết quả kinh doanh đối tác và chia sẻ dữ liệu theo mức | `Sharing profile/source binding/dataset/import/reconciliation/report/exception` | Đã tách & rà soát thiết kế | [M21-PARTNER-BUSINESS-RESULTS.md](modules/M21-PARTNER-BUSINESS-RESULTS.md) |
| M22 | Quản trị nhân sự, công và lương | `Employee/employment/contract/leave/attendance/payroll/import` | Đã tách & rà soát thiết kế | [M22-HUMAN-RESOURCES.md](modules/M22-HUMAN-RESOURCES.md) |

---

## 3. Trạng thái Lát cắt Triển khai (`slices/`)

Nguồn lộ trình: [03-planning/ROADMAP.md](../03-planning/ROADMAP.md).

| Slice | Kết quả chính | Module chính | Trạng thái đặc tả | Tệp đặc tả |
|---|---|---|---|---|
| SL00 | Foundation: Login, Tenant/Workspace, Grants, Audit, Outbox nền *(+ M23/M24 nền)* | M14, M19, M20, M23 *(đề xuất)*, M24 *(đề xuất)* | Chờ tách spec slice | — |
| SL01 | Pilot Work: Giao việc nội bộ, My Work, nộp & duyệt kết quả | M16, M14, M19, M20, M23/M24 *(đề xuất)* | Đã có spec pilot để review | [SL01-INTERNAL-WORK.md](slices/SL01-INTERNAL-WORK.md) |
| SL02 | Omnichannel Intake & Inbox tối thiểu (1 nguồn, 1 kênh) | M01, M03, M19, M23/M24 *(đề xuất)* | Chờ tách spec slice | — |
| SL03 | Lead/Deal, Follow-up & Lịch hẹn đơn giản | M02, M13, M18 *(F11)*, M24 | Chờ tách spec slice | — |
| SL04 | Quote/SOW → Contract → Delivery → Acceptance / Ticket | M07, M08, M11, M12, M15, M16, M23 *(F04/07)*, M24 | Chờ tách spec slice | — |
| SL05 | Finance: Receipt → Allocation → Reconcile & Commission có điều kiện | M09, M10, M17, M18 *(F08)*, M23 *(F04/07)* | Chờ tách spec slice | — |
| SL06 | Hoàn thiện Work P0 (`W-F01–09`) & Automation cơ bản | M04, M13, M16, M18 *(F11)*, M24 | Chờ tách spec slice | — |
| SL07 | Mở rộng có căn cứ (Capacity, thêm kênh, BI nâng cao, AI, Referral) | M05, M06, M15, M18 *(F08–10)*, M23 *(F08)*, M24 *(F08)* | Chờ tách spec slice | — |
| SL08 | Kết quả đối tác `NONE / SUMMARY / FILE` trước `API_READ` | M21, M14, M16, M18, M19, M20 | Đã có spec để review | [SL08-PARTNER-RESULTS.md](slices/SL08-PARTNER-RESULTS.md) |
| SL09–11 | HRM theo giai đoạn (`HR-A` → `HR-B` → `HR-C`) | M22, M14, M10, M09 | Đã có spec lộ trình HRM | [SL09-11-HRM.md](slices/SL09-11-HRM.md) |

---

## 4. Đặc tả Đề xuất Mở rộng sau Master v1.9 (`modules/` — Chờ chốt phạm vi chính thức)

> Tổng cộng **24 chức năng đề xuất mở rộng** (ngoài 200 chức năng Baseline v1.9), đã chuẩn hóa ranh giới *Single Source of Truth* tại [INDEX.md](../01-architecture/INDEX.md) và [INVARIANTS.md](../01-architecture/INVARIANTS.md).

| Mã | Tên phần mở rộng | Nội dung chính | Trạng thái | Tệp đặc tả |
|---|---|---|---|---|
| M18 *(mở rộng F08–11)* | Báo cáo Tổng hợp Nâng cao (`M18-F08–11`) | P&L & Dòng tiền hợp nhất (`M09+M17+M10+M22`), Ad-hoc Report Builder, Scheduled Report Delivery, Cockpit Data Quality | Bản đề xuất sau `/grill-me` (15/11/2026) | [M18-BI-REPORTING-EXPANSION.md](modules/M18-BI-REPORTING-EXPANSION.md) |
| M23 *(F01–12)* | Quản trị Hệ thống, Bảo mật Vận hành & Nền tảng Cấu hình | MFA/Session/Break-glass TTL, Approval Matrix & Pilot/Team Maker–Checker, Audit Log bất biến, Export 2 lớp/Watermark, DLP, Feature Flags, Lịch chuẩn/Quiet Hours, Danh mục & Outbox/DLQ nội bộ | Bản đề xuất sau `/grill-me` (15/11/2026) | [M23-SYSTEM-ADMIN-SECURITY-OPS.md](modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md) |
| M24 *(F01–08)* | Lớp Tăng Hiệu năng Hệ thống & Hiệu suất Người dùng | UX (`Ctrl+K`, Split-View, Bulk dry-run, Quick Replies, Smart Notification) & System Scale (Read Model/Permission Cache, Queue Priority Isolation 3 làn, Async Export/Archiving) | Bản đề xuất sau `/grill-me` (15/11/2026) | [M24-PERFORMANCE-AND-PRODUCTIVITY.md](modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md) |
