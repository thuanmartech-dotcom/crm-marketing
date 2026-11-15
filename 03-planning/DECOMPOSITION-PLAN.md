# Kế hoạch Ưu tiên Bóc tách Đặc tả Chi tiết (`M01–M24` & `SL00–SL07`)

> **Trạng thái thực thi:** `Đang thực thi Wave 1 — Đã hoàn tất M14 (1/24), tiếp theo: M20` (cập nhật `15/11/2026`).  
> **Nguồn chuẩn & công cụ:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`), [FUNCTION-CATALOG.md](../02-specs/FUNCTION-CATALOG.md) (`224` chức năng `M01–M24`), [requirements.json](trace/requirements.json), [module-spec-validation.json](evidence/module-spec-validation.json) và skill [crm-ba-spec](../.agents/skills/crm-ba-spec/SKILL.md).

---

## 1. Chiến lược & Nguyên tắc Bóc tách (`Hybrid Hub-First theo Cụm`)

1. **Khóa trục hạ tầng nhiều phụ thuộc nhất trước (`Wave 1`):** Bóc tách và đóng băng hợp đồng quyền (`M14`), chặn gửi/privacy (`M20`), ingest/outbox (`M19`) và lõi công việc (`M16`) ngay đầu để mọi cụm nghiệp vụ đi sau tham chiếu trực tiếp mà không phải sửa ngược.
2. **Bóc tách theo cụm liên kết đôi chặt nhất (`Wave 2` $\rightarrow$ `Wave 5`):** Gom các module thường xuyên trao đổi state/event với nhau thành cùng một Wave.
3. **Khóa `Public Contracts` & Cổng `Verify` cuối mỗi Wave:** Kết thúc một module/Wave phải hoàn thiện đủ 6 mục chuẩn [MODULE-SPEC.md](../02-specs/templates/MODULE-SPEC.md) (EARS + `[MASTER]`/`[PROPOSED]`/`[OPEN-GAP]` + `erDiagram`/`stateDiagram-v2`), tách `public contracts/` vào `02-specs/contracts/` theo mẫu [CONTRACT.md](../02-specs/templates/CONTRACT.md) và vượt qua toàn bộ 4 script ở `05-tools/` trước khi chuyển Wave kế tiếp.
4. **4 Quy ước Nền đã chốt qua `/grill-me` (15/11/2026):**
   - **Truy vết mở rộng (`GAP-03`):** Bao phủ cả 100% ID `owner == Mxx` lẫn các ID liên quan trong nhóm `221 missing_owner` / `PLATFORM` (`U*`, `INT*`, `RV*`, `OC*`, `DB*`, `CEO/CMO/CX/SEC/WF-U*`, `NFR*`, `O*`, `ENTITY-L*`), phân biệt rõ `Primary Owner` vs `Consumer`.
   - **Độ sâu `Per-Function` (`Mxx-Fyy`):** Trong Mục `3. Hành vi` của mỗi file `02-specs/modules/Mxx-*.md`, tách tiểu mục `### 3.x Mxx-Fyy` cho 100% chức năng của module.
   - **Tách bảng gộp (`GAP-04`):** Trong Mục `4. Data/API`, tách rời các khai báo bảng gộp ở Master `5.13/5.18/5.20` thành từng bảng độc lập (kế thừa 10 cột chuẩn Mục `5.1` + gắn mã `ENTITY-Lxxxx`).
   - **Bảng `Policy/Config Parameters` (`Fail-Closed` theo `INV-14`) & Nhịp cuốn chiếu:** Thiết kế tham số mở (`O01–08`, `W-O*`, `GAP-*`) thành bảng cấu hình có `Safe Default (Fail-Closed)` để không chặn spec; chạy cuốn chiếu **từng module một (4 pha/module)** bắt đầu từ `M14`.

---

## 2. Bản đồ Phụ thuộc & Thứ tự 6 Wave

```mermaid
flowchart TB
  subgraph W1["WAVE 1 — Trục Hạ tầng & Công việc Cốt lõi"]
    direction LR
    M14["[DONE] 1. M14 (18/18 IDs) - Quyền & Grants"] --> M20["[NEXT] 2. M20 (14 IDs) - Consent & Privacy"]
    M20 --> M19["3. M19 (24 IDs) - Ingest, Outbox & Adapter"]
    M19 --> M16["4. M16 (96 IDs) - Task Core & Delivery"]
  end

  subgraph W2["WAVE 2 — Cụm Đầu phễu & Hội thoại"]
    direction LR
    M01["5. M01 (15 IDs) - CDP & Định danh"] --> M03["6. M03 (38 IDs) - Omnichannel Inbox"]
    M03 --> M02["7. M02 (18 IDs) - Lead & Deal"]
    M02 --> M13["8. M13 (12 IDs) - Lịch hẹn & Tài nguyên"]
  end

  subgraph W3["WAVE 3 — Cụm Thương mại, Tiền & Ngân sách"]
    direction LR
    M07["9. M07 (14 IDs) - Báo giá"] --> M08["10. M08 (15 IDs) - Hợp đồng & Onboarding"]
    M08 --> M09["11. M09 (21 IDs) - Thu tiền & Phân bổ"]
    M09 --> M10["12. M10 (12 IDs) - Hoa hồng"]
    M09 --> M17["13. M17 (12 IDs) - Ngân sách & Media Funding"]
  end

  subgraph W4["WAVE 4 — Cụm Triển khai Chiến dịch & CSKH"]
    direction LR
    M15["14. M15 (15 IDs) - Brief, IMC & Launch Gate"] --> M11["15. M11 (13 IDs) - Ticket & SLA"]
    M11 --> M12["16. M12 (12 IDs) - VoC & Phục hồi CX"]
  end

  subgraph W5["WAVE 5 — Cụm Tự động hóa, Tăng trưởng, AI & BI"]
    direction LR
    M04["17. M04 (11 IDs) - Journey"] --> M05["18. M05 (12 IDs) - Referral & Loyalty"]
    M05 --> M06["19. M06 (14 IDs) - AI Co-Pilot"]
    M06 --> M18["20. M18 (14 IDs + F08-11) - KPI, BI & Attribution"]
  end

  subgraph W6["WAVE 6 — Chuẩn hóa Mở rộng, Rà chéo & Đóng gói Slice"]
    direction LR
    M2324["21. Nâng chuẩn EARS M23 & M24 (--strict-all)"] --> M2122["22. Rà khớp contract chéo M21 & M22"]
    M2122 --> SLICES["23. Tách spec lát cắt SL00, SL02-SL07"]
  end

  W1 -->|"Khóa 4 contracts nền"| W2
  W1 -->|"Khóa task/auth/outbox"| W3
  W2 -->|"Deal Won & Appointment"| W3
  W3 -->|"Start Auth & Funding Gate"| W4
  W1 -->|"Permission & Suppression"| W4
  W4 -->|"Outcomes, SLA & Feedback"| W5
  W5 -->|"Toàn bộ Metric & BI Facts"| W6
```

---

## 3. Lộ trình Chi tiết 24 Module & Public Contracts từng Wave

| Thứ tự | Wave | Module | Fan-In | Owned IDs | Trạng thái hiện tại | Tệp đặc tả đích (`02-specs/modules/`) | Public Contracts cần khóa cuối Wave (`02-specs/contracts/`) |
|---:|---|---|---:|---:|---|---|---|
| 1 | Wave 1 | `M14` — Tổ chức, Nhóm & Quyền | 17 | 18 | `complete_id_mentions` (`18/18` IDs) | [M14-ORG-ACCESS-DELEGATION.md](../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md) | [M14-PRINCIPAL-ACCESS-DECISION.md](../02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md) |
| 2 | Wave 1 | `M20` — Consent, Suppression & Privacy | 15 | 14 | Chờ lệnh khởi chạy | `M20-PRIVACY-CONSENT-RETENTION.md` | `M20-SUPPRESSION-PRIVACY-GATE.md` |
| 3 | Wave 1 | `M19` — Tích hợp, Ingest & Outbox | 16 | 24 | Chờ lệnh khởi chạy | `M19-INTEGRATION-ADAPTERS-OUTBOX.md` | `M19-DURABLE-INGEST-OUTBOX.md` |
| 4 | Wave 1 | `M16` — Công việc, Dự án & Task Core | 18 | 96 | Chờ lệnh *(có pilot `SL01`)* | `M16-WORK-PROJECTS-TASK-CORE.md` | `M16-TASK-CORE-COMMANDS.md` |
| 5 | Wave 2 | `M01` — CDP & Hồ sơ khách hàng 360 | 12 | 15 | Chờ Wave 1 | `M01-CDP-IDENTITY-MERGE.md` | `M01-IDENTITY-PROFILE-EVENTS.md` |
| 6 | Wave 2 | `M03` — Omnichannel Inbox | 15 | 38 | Chờ Wave 1 | `M03-OMNICHANNEL-INBOX.md` | `M03-INBOX-TRIAGE-HANDOFF.md` |
| 7 | Wave 2 | `M02` — Lead & Deal | 14 | 18 | Chờ Wave 1 | `M02-LEAD-DEAL-PIPELINE.md` | `M02-DEAL-WON-HANDOFF.md` |
| 8 | Wave 2 | `M13` — Lịch hẹn & Tài nguyên | 4 | 12 | Chờ Wave 1 | `M13-APPOINTMENTS-RESOURCES.md` | — |
| 9 | Wave 3 | `M07` — Danh mục & Báo giá | 8 | 14 | Chờ Wave 2 | `M07-CATALOG-QUOTING.md` | `M07-M08-COMMERCIAL-COMMITMENT.md` *(cùng M08)* |
| 10 | Wave 3 | `M08` — Hợp đồng & Onboarding | 13 | 15 | Chờ Wave 2 | `M08-CONTRACTS-ONBOARDING.md` | `M08-START-AUTHORIZATION.md` |
| 11 | Wave 3 | `M09` — Nghĩa vụ thu, Tiền & Đối soát | 13 | 21 | Chờ Wave 2 | `M09-AR-RECEIPTS-RECONCILIATION.md` | `M09-ALLOCATION-REFUND-EVENTS.md` |
| 12 | Wave 3 | `M10` — Hoa hồng & Chi trả | 7 | 12 | Chờ Wave 2 | `M10-COMMISSIONS-PAYOUTS.md` | `M10-COMMISSION-PAYOUT-ROUTE.md` |
| 13 | Wave 3 | `M17` — Ngân sách, Chi phí & Funding | 7 | 12 | Chờ Wave 2 | `M17-BUDGETS-MEDIA-FUNDING.md` | — |
| 14 | Wave 4 | `M15` — Brief, Chiến lược, IMC & Launch | 10 | 15 | Chờ Wave 3 | `M15-BRIEF-IMC-LAUNCH.md` | — |
| 15 | Wave 4 | `M11` — Ticket & SLA | 10 | 13 | Chờ Wave 3 | `M11-TICKETS-SLA.md` | `M11-M12-SLA-CX-FEEDBACK.md` *(cùng M12)* |
| 16 | Wave 4 | `M12` — Voice of Customer & Phục hồi CX | 9 | 12 | Chờ Wave 3 | `M12-VOC-CX-RECOVERY.md` | — |
| 17 | Wave 5 | `M04` — Journey & Nhắc việc | 9 | 11 | Chờ Wave 4 | `M04-JOURNEY-AUTOMATION.md` | — |
| 18 | Wave 5 | `M05` — Referral & Loyalty | 2 | 12 | Chờ Wave 4 | `M05-REFERRAL-LOYALTY.md` | — |
| 19 | Wave 5 | `M06` — AI Co-Pilot có kiểm soát | 5 | 14 | Chờ Wave 4 | `M06-AI-COPILOT-GOVERNED.md` | — |
| 20 | Wave 5 | `M18` — Từ điển KPI, BI & Attribution *(+ F08–11)* | 15 | 14 *(+4)* | Đang có `9/14` IDs | [M18-BI-REPORTING-EXPANSION.md](../02-specs/modules/M18-BI-REPORTING-EXPANSION.md) | `M18-METRIC-FACTS-EXPORT.md` |
| 21 | Wave 6 | `M23` & `M24` — Nâng chuẩn EARS + `--strict-all` | 2 / 2 | 12 / 8 *(đề xuất)* | Đã có bản Draft mở rộng | [M23](../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), [M24](../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md) | — |
| 22 | Wave 6 | `M21` & `M22` — Rà khớp contract chéo | 6 / 8 | 101 / 135 | `complete_id_mentions` | [M21](../02-specs/modules/M21-PARTNER-BUSINESS-RESULTS.md), [M22](../02-specs/modules/M22-HUMAN-RESOURCES.md) | — |
| 23 | Wave 6 | Tách 7 Slice Specs còn thiếu (`02-specs/slices/`) | — | — | Chờ Wave 1–5 | `SL00`, `SL02`, `SL03`, `SL04`, `SL05`, `SL06`, `SL07` | Đồng bộ thêm `SL01`, `SL08`, `SL09–11` |

---

## 4. Definition of Done (DoD) bắt buộc trước khi qua Wave kế tiếp

1. Thực hiện đủ **Pha 1 (Grounding) $\rightarrow$ Pha 2 (Hỏi chặn Tầng 1 qua `ask_question`, ghi `[OPEN-GAP]` Tầng 2 vào [GAPS.md](GAPS.md)) $\rightarrow$ Pha 3 (EARS + Data/API + `contracts/`) $\rightarrow$ Pha 4 (Analyze & Verify)** theo [module-workflow.md](../.agents/skills/crm-ba-spec/references/module-workflow.md).
2. Cập nhật [02-specs/README.md](../02-specs/README.md) và [PROGRESS.md](agent/PROGRESS.md).
3. Chạy đủ 4 lệnh kiểm chứng từ `D:\AI Agent\CRM`:
   ```powershell
   python 05-tools/build_delivery_inventory.py
   python 05-tools/verify_delivery_plan.py
   python 05-tools/verify_hrm_integration.py
   python 05-tools/verify_module_spec.py
   ```
   Yêu cầu mọi module đã bóc tách đạt `complete_id_mentions` (Wave 6 chạy thêm `--strict-all` cho `M18`, `M23`, `M24`), `bad_links: []`, `bad_fences: []`, giữ nguyên `master_unchanged: true` và `application_tests: "Not Run"`.

---

## 5. Nhật ký Kết quả Bóc tách từng Module (`Completed Modules Log`)

### Wave 1

1. **`M14` — Tổ chức, Chi nhánh, Thành viên, Quyền & Bàn giao Nhân sự (Hoàn tất `15/11/2026`):**
   - **Tệp đặc tả Module:** [M14-ORG-ACCESS-DELEGATION.md](../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md) — Đạt `complete_id_mentions` (`18/18` ID sở hữu trực tiếp + `25` ID/thực thể mở rộng từ bể `missing_owner`/`PLATFORM`); đặc tả EARS đầy đủ cho 8 chức năng `M14-F01..08`, tách rời 18 bảng logic từ Master `5.13/5.18`, và khóa bảng `Policy/Config Parameters` (`GAP-M14-01`).
   - **Tệp Hợp đồng Liên Module (`Contract`):** [M14-PRINCIPAL-ACCESS-DECISION.md](../02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md) — Khóa hợp đồng chế độ kép (`EvaluateAccessDecision` + `CompileScopeFilter`) và 4 Domain Events (`M14.PermissionVersionBumped`, `M14.UserOffboardingLocked`, `M14.WorkHandoverAssigned`, `M14.WorkspaceActivated`).
   - **3 Quyết định Kiến trúc đã chốt qua `/grill-me`:**
     1. *Ủy nhiệm Thay ca (`M14-F05`):* Mô hình `Act-On-Behalf` có tiền kiểm `Membership + Role_Binding` nền tại cùng `Workspace/Branch`, giữ nguyên `owner_id` và quyền hưởng hoa hồng lịch sử.
     2. *Bàn giao Nghỉ việc 2 Pha (`M14-F06` & `UC12`):* Pha 1 cắt phiên/quyền nguyên tử tại `effective_at` và gán tạm `Queue Manager` làm `Custodian` cho 8 nhóm open work; Pha 2 yêu cầu người nhận mới bấm `Accept` (hoặc `Reject` có lý do) trước khi đóng ca sang `OFFBOARDED`.
     3. *Cổng Kiểm tra Quyền Thực thi (`M14-F04`):* Hợp đồng kép kết hợp đánh giá bản ghi đơn lẻ/Download Gateway/Worker recheck và đẩy bộ lọc `Predicate AST + SET LOCAL` xuống câu truy vấn gốc cho `List/Search/Count/BI/AI RAG`.
