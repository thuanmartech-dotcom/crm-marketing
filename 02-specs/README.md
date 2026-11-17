# Danh mục Đặc tả Module & Slice (`02-specs/`)

Tài liệu theo dõi trạng thái phân rã từ [Master v1.9](../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md).  
Mục tiêu giai đoạn hiện tại là hoàn thiện đặc tả chi tiết cho toàn bộ module và slice trước khi giao cho AI Agent lập trình.

- **Danh mục 200 chức năng chi tiết & Sơ đồ luồng chức năng (`M01–M22`):** [FUNCTION-CATALOG.md](FUNCTION-CATALOG.md)
- **Sổ tra cứu bề mặt Hợp đồng, Sự kiện, Bảng SSoT & ADR (`Wave 2–6`):** [CONTRACTS-REGISTRY.md](CONTRACTS-REGISTRY.md) *(tự sinh từ `05-tools/build_module_context.py --build-registry`)*

---

## 1. Khuôn mẫu chuẩn (`templates/`)

- [MODULE-SPEC.md](templates/MODULE-SPEC.md) — Khuôn mẫu đặc tả cho từng module (`M01–M22`).
- [CONTRACT.md](templates/CONTRACT.md) — Khuôn mẫu đặc tả contract command / event / API.
- [PARTNER-DATA-PROFILE.md](templates/PARTNER-DATA-PROFILE.md) — Mẫu phiếu cấu hình chia sẻ dữ liệu đối tác (`M21`).
- [PARTNER-REPORT.md](templates/PARTNER-REPORT.md) — Mẫu báo cáo dịch vụ và kết quả đối tác (`M21`).

### Hợp đồng Liên Module (`contracts/` — `C14`, `C16`, `C19`, `C20`, `C23`, `C24`: `Reviewed` sau Wave 1.5)

- [M14-PRINCIPAL-ACCESS-DECISION.md](contracts/M14-PRINCIPAL-ACCESS-DECISION.md) (`C14`) — Hợp đồng `BindDbTransactionContext` (6 GUCs), `ResolveConnectionScopeByWebhookEndpoint` (`M19` Bootstrap `SECURITY DEFINER`), `PORTAL_CLIENT` Write Port, `EvaluateAccessDecision`, `Entity-Mapped CompileScopeFilter`, `ApplyBreakGlassGrant`/`RevokeBreakGlassGrant`, `SetTenantOperatingMode`, `InitiateOffboardingOrTransfer`, `GetCapacityCostSnapshots`, 4 Published Events & `6` Subscribed Streams.
- [M20-SUPPRESSION-PRIVACY-GATE.md](contracts/M20-SUPPRESSION-PRIVACY-GATE.md) (`C20`) — Hợp đồng 4 cổng kiểm duyệt (`EvaluateOutboundCompliance` đa phiên bản HMAC + `endpoint_hashes_by_version[]`, `EvaluateVendorAndAiTransfer` DLP scanner + tách `AI_*` vs `M19_EXTERNAL_WEBHOOK`, `VerifyPostRestoreComplianceGate` DR Fence đảo thứ tự & hủy `M19`/`M23-F12`/`M24`, `EvaluateAssetDownloadPrivacyGate` + `active_legal_hold_ids[]`) và 4 Domain Events (`erased_subject_refs[]`, `redacted_deletion_ledger_ids[]` đa lần trên `Task_Submissions`).
- [M19-DURABLE-INGEST-OUTBOX.md](contracts/M19-DURABLE-INGEST-OUTBOX.md) (`C19`) — Hợp đồng 5 trụ cột Ingest bền vững (`IngestWebhookEvent` + Bootstrap `C14`), Outbox gửi tin (`EnqueueOutboundIntent` + `DispatchOutboundIntent` với `lease_token` fencing CAS, Bảng Reaper 8 nhánh, `CONFLICT` & `PMS`/`TASK_SYNC`), tải media Zero-Trust (`ExecuteSafeRemoteFetch`), Replay an toàn (`ReplayConnectionEvents`), `ListOpenIntentsForPrincipal`, 5 Domain Events phát hành và các sự kiện tiêu thụ (`M14/M20/M23`).
- [M16-TASK-CORE-COMMANDS.md](contracts/M16-TASK-CORE-COMMANDS.md) (`C16`) — Hợp đồng 3 trụ cột (`CreateTaskByBusinessKey` + `TaskLifecycleCommandNote` gồm `WithdrawSubmission` & `Work_Queues.queue_manager_user_id NOT NULL`; `InitializeProjectFromHandoff` + `PublishDeliverableForClientReview` / `RecordClientAcceptance` qua `PORTAL_CLIENT SECURITY DEFINER` Write Port; `ListOpenWorkForPrincipal` + `TransferWorkOwnership`), `11` Domain Events nội bộ qua `M23-F12` (`Lane 2`) và các Subscribed Events của `M16`.
- [M23-PLATFORM-GOVERNANCE-OUTBOX.md](contracts/M23-PLATFORM-GOVERNANCE-OUTBOX.md) (`C23`) — Hợp đồng `6` cổng Nền tảng (`EvaluateApprovalMatrix`, `RecordApprovalDecision` + `Approval_Decisions` `Nhóm C`, `LookupPolicyVersion`, `ComputeBusinessCalendarShift`, `RegisterAssetAndDownloadGateway`, `PublishInternalOutboxEvent` 3-Lane + DR Fence) kèm `6` Published Events & `8` Subscribed Events.
- [M24-PRODUCTIVITY-CACHE-QUEUE.md](contracts/M24-PRODUCTIVITY-CACHE-QUEUE.md) (`C24`) — Hợp đồng `4` cổng Năng suất & Hệ thống (`ExecuteDryRunAndCommitBulkCommand`, `EnqueueInternalNotificationDispatch`, `QueryOrInvalidatePermissionCache` kèm `acl_epoch` leapfrog & DR Wipe, `EnqueueQueueLaneTask` 3-Lane + Backpressure), Published/Subscribed Events (`M14`/`M20`/`M23`/`M16`).

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
| M14 | Tổ chức, chi nhánh, thành viên, quyền và bàn giao nhân sự | `Principals/Membership/role binding/grants/revocation PITR #6` | `Reviewed` (`18/18` IDs — Wave 1.5 Fresh-Context Verified) | [M14-ORG-ACCESS-DELEGATION.md](modules/M14-ORG-ACCESS-DELEGATION.md) |
| M15 | Brief, chiến lược, kế hoạch IMC và phê duyệt launch | `Brief/approved plan/campaign/launch/learning` | Chờ phân tích & tách file | — |
| M16 | Quản lý công việc cá nhân, đội nhóm, tổ chức, dự án và nguồn lực | `Task/queue/submission/review/recurrence/project/deliverable/acceptance` | `Reviewed` (`96/96` IDs — Wave 1.5 Verified; giữ Fail-Closed `W-O01..07`) | [M16-WORK-PROJECTS-TASK-CORE.md](modules/M16-WORK-PROJECTS-TASK-CORE.md) |
| M17 | Ngân sách, chi phí, nguồn tiền media và rủi ro hiệu quả | `Budget/commitment/cost/funding authorization` | Chờ phân tích & tách file | — |
| M18 | Từ điển chỉ số, báo cáo điều hành và attribution *(kèm đề xuất F08–11)* | `KPI definition/metric facts/report snapshot/P&L/ad-hoc` | Đủ truy vết tối thiểu (`14/14` IDs `[MASTER]`); **chưa đủ đặc tả triển khai** — giữ hoàn thiện chi tiết Wave 5–6 *(kèm đề xuất mở rộng F08–11 `Draft`)* | [M18-BI-REPORTING-EXPANSION.md](modules/M18-BI-REPORTING-EXPANSION.md) |
| M19 | Kết nối bên ngoài, nhận/phát sự kiện và phục hồi | `Connection/capability/inbox/outbox/checkpoint` | `Reviewed` (`24/24` IDs — Wave 1.5 Fresh-Context Verified) | [M19-INTEGRATION-ADAPTERS-OUTBOX.md](modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md) |
| M20 | Consent, yêu cầu dữ liệu, retention và quản trị mục đích | `Processing/consent/suppression/privacy/legal hold/retention` | `Reviewed` (`14/14` IDs — Wave 1.5 Fresh-Context Verified) | [M20-PRIVACY-CONSENT-RETENTION.md](modules/M20-PRIVACY-CONSENT-RETENTION.md) |
| M21 | Kết quả kinh doanh đối tác và chia sẻ dữ liệu theo mức | `Sharing profile/source binding/dataset/import/reconciliation/report/exception` | Đã tách & rà soát thiết kế | [M21-PARTNER-BUSINESS-RESULTS.md](modules/M21-PARTNER-BUSINESS-RESULTS.md) |
| M22 | Quản trị nhân sự, công và lương | `Employee/employment/contract/leave/attendance/payroll/import` | Đã tách & rà soát thiết kế | [M22-HUMAN-RESOURCES.md](modules/M22-HUMAN-RESOURCES.md) |

---

## 3. Trạng thái Lát cắt Triển khai (`slices/`)

Nguồn lộ trình: [03-planning/ROADMAP.md](../03-planning/ROADMAP.md).

| Slice | Kết quả chính | Module chính | Trạng thái đặc tả | Tệp đặc tả |
|---|---|---|---|---|
| SL00 | Foundation: Login, Tenant/Workspace, Grants, Audit, Outbox nền *(+ M23/M24 nền)* | M14, M19, M20, M23 *(đề xuất)*, M24 *(đề xuất)* | Chờ tách spec slice | — |
| SL01 | Pilot Work: Giao việc nội bộ, My Work, nộp, rút & duyệt kết quả | M16, M14, M20, M23-F12, M24-F05/06 *(Wave 1.5 `--strict-all`)* | **`Reviewed`** *(Wave 1.5 Upgraded — `--strict-all`; Tests `Not Run`)* | [SL01-INTERNAL-WORK.md](slices/SL01-INTERNAL-WORK.md) |
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
| M23 *(F01–12)* | Quản trị Hệ thống, Bảo mật Vận hành & Nền tảng Cấu hình | MFA/Session/Break-glass TTL, Approval Matrix & `Approval_Decisions`, `Assets/Asset_Versions` + Download `SEC03`, DLP, Feature Flags, Lịch chuẩn/Quiet Hours, Danh mục & Outbox/DLQ nội bộ | **`Reviewed`** *(Wave 1.5 Upgraded `--strict-all` + `C23` + `CR-20261117-M23-ERASURE-ALIGNMENT`; mở `GAP-15..17`)* | [M23-SYSTEM-ADMIN-SECURITY-OPS.md](modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md) |
| M24 *(F01–08)* | Lớp Tăng Hiệu năng Hệ thống & Hiệu suất Người dùng | UX (`Ctrl+K`, Split-View, Bulk dry-run, Quick Replies, Smart Notification `Internal_Notifications`) & System Scale (`Permission_Cache_Versions` + `acl_epoch`, Search ACL, Queue 3 làn, Async Export/Archiving) | **`Reviewed`** *(Wave 1.5 Upgraded `--strict-all` + `C24`; mở `GAP-02/18`)* | [M24-PERFORMANCE-AND-PRODUCTIVITY.md](modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md) |

> Nạp ngữ cảnh protocol v2: tuân thủ [AGENTS.md](../AGENTS.md) Mục 4; registry là chỉ mục có dấu vân tay nguồn, không thay thế contract/ADR. Trạng thái module/slice không đổi.
