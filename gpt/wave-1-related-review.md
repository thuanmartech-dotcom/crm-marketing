# Review mở rộng các module liên quan Wave 1

Ngày 16/11/2026. Tiếp nối [review Wave 1](wave-1-review.md). Mọi giải pháp trong báo cáo mang nhãn **[PROPOSED]**, chưa áp dụng vào tài liệu gốc. Test ứng dụng **Not Run**.

## Phạm vi và mức độ kiểm tra

| Nhóm | Phạm vi đã rà | Giới hạn |
|---|---|---|
| M14/M20/M19/M16 | Bốn contract, các đoạn module liên quan quyền, privacy, event, task và capacity | Kế thừa năm phát hiện W1-01..05 ở báo cáo trước |
| M23/M24 | Contract C23/C24, outbox, projection, approval, bulk, notification, export/download và liên kết Wave 1 | Review thiết kế, chưa có thực thi |
| M18 | Nguồn projection, KPI/cost, lịch export và task khắc phục | F01–07 còn khung, F08–11 Draft theo tài liệu |
| M21 | Sharing profile, revoke, import, partner report và task ngoại lệ | Public contract riêng chưa có trong thư mục contracts |
| M22 | HR event, offboarding, availability, quyền/file và liên kết adapter | Chưa có public contract HR riêng được chuẩn hóa theo C14–C24 |
| SL01/SL08/SL09–11 | Dependencies, scope và gate nối foundation | Không đánh giá readiness go-live |
| M01/M02/M03/M04/M05/M06/M07/M08/M09/M10/M11/M12/M13/M15/M17 | Đối chiếu giao diện chung trong Master 3.13, Task Core 3.14, consumer của contract Wave 1 và ownership | Chưa có module spec riêng trong cây hiện tại. Chưa audit sâu từng chức năng |

Các tệp được tra cứu trực tiếp trong `02-specs/`, ADR, INDEX, INVARIANTS và Master hiện hành. Không dùng `99-archive/` làm nguồn.

## Kết quả mở rộng

Ghi nhận **8 điểm bổ sung**, gồm **3 HIGH và 5 MEDIUM**. Tổng hợp với lượt trước có **13 điểm cần xử lý**. Đây là lỗi nhất quán hoặc khoảng trống đặc tả có tình huống tác động cụ thể. Chưa có lỗi runtime được tái hiện.

| Mã | Mức độ | Quan hệ bị ảnh hưởng | Vấn đề |
|---|---|---|---|
| R-01 | HIGH | M16 → M23 → M24 → M18 | Bỏ event version thấp có thể làm mất cập nhật từng phần |
| R-02 | HIGH | M20 → M23/M24 → search/report | Chưa chốt cơ chế ngăn event cũ khôi phục PII đã scrub |
| R-03 | HIGH | M23 → nhiều consumer Wave 1 | Chưa định nghĩa đầy đủ ACK và recovery theo từng consumer |
| R-04 | MEDIUM | M23 ↔ M16/M07/M22 | Chính sách đã supersede vừa được giữ để duyệt vừa bị coi là conflict |
| R-05 | MEDIUM | M24 bulk → M14/M16 | Chưa ràng buộc rõ nội dung COMMIT với DRY_RUN |
| R-06 | MEDIUM | M22 → M14 → M16/M18 | Quỹ giờ thiếu kỳ đo chuẩn và quy tắc xử lý khoảng thời gian chồng lấn |
| R-07 | MEDIUM | M20 ↔ M23 gateway | Test M23 chặn mọi legal hold trái nhánh đọc có thẩm quyền của M20 |
| R-08 | MEDIUM | M22/SL09 → M19/M23 | Tài liệu HR vẫn giao vận chuyển event nội bộ cho M19 |

### R-01 — Giữ version lớn nhất chưa đủ cho sự kiện chỉ chứa phần thay đổi

**Bằng chứng.** M24-F06, dòng 271–282 và bảng `Read_Model_Projections` dòng 369, yêu cầu chỉ nhận `incoming_event_version > source_event_version`. C16 dòng 545–547 công bố payload khác nhau cho đổi hạn/người làm, đổi lifecycle và hoàn tất. Event đổi lifecycle không chứa đầy đủ hạn/người làm như event đổi assignment. [M24](../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md), [C16](../02-specs/contracts/M16-TASK-CORE-COMMANDS.md).

**Tình huống.** Projection đang ở v10. Event v11 đổi assignee A sang B, event v12 đổi trạng thái sang IN_REVIEW. v12 tới trước và cập nhật version lên 12. v11 bị bỏ, projection vẫn hiển thị A dù nguồn chuẩn đã giao cho B. Nếu worker ghi cả payload thay thế, các trường không có trong v12 còn có thể bị mất. M18 đọc projection cũng nhận dữ kiện sai.

**[PROPOSED]** Chốt một cơ chế phù hợp với payload. Có thể dùng snapshot đầy đủ theo version, hoặc phát hiện gap rồi đọc lại snapshot qua public read port có ACL của domain. Nếu tiếp tục dùng delta thì cần xử lý thứ tự/gap và replay theo aggregate. Hai event khác loại cùng aggregate version cần quy tắc riêng, vì điều kiện `>` sẽ loại event thứ hai.

**Nghiệm thu.** Giao v12 trước v11, giao trùng v11, thiếu v11, và hai event khác loại cùng version. Kết quả phải khớp snapshot chuẩn về assignee, hạn, lifecycle và count.

### R-02 — Scrub hiện tại chưa khóa đường tái tạo dữ liệu từ backlog

**Bằng chứng.** C24 mục 3.3 và M24-F08 quy định scrub index/projection khi nhận `M20.SubjectErasureExecuted`. M23-F12 dòng 401–404 scrub payload outbox/DLQ. M24-F06 vẫn nhận cập nhật theo source version, chưa có quy tắc rõ về dấu xóa bền vững hoặc kiểm deletion ledger khi dựng lại projection. [C24](../02-specs/contracts/M24-PRODUCTIVITY-CACHE-QUEUE.md), [M23](../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), [M24](../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md).

**Tình huống suy luận.** Worker đã đọc payload chứa PII vào bộ nhớ nhưng chưa commit projection. Event xóa được xử lý và scrub DB. Worker cũ tiếp tục ghi payload đã đọc, hoặc job rebuild lấy snapshot trước xóa. Việc sửa payload còn nằm trong outbox không thu hồi bản đã đọc. Version của aggregate nghiệp vụ và version yêu cầu privacy cũng chưa được định nghĩa là cùng một thứ tự.

**[PROPOSED]** Đặc tả dấu xóa/phiên bản privacy bền vững theo chủ thể và scope. Mỗi apply/rebuild/import projection phải kiểm dấu này tại thời điểm ghi, hoặc dùng cơ chế đồng bộ tương đương. Phân biệt phần bị xóa và phần cần giữ dưới legal hold. Quy định rõ recovery khi event xóa và event nghiệp vụ đến đảo thứ tự.

**Nghiệm thu.** Dừng worker sau đọc payload, thực hiện xóa, cho worker chạy lại. Làm tương tự với DLQ replay và rebuild. PII đã xóa không xuất hiện lại trong search, snippet, report hoặc cold archive.

Đây là khoảng trống phối hợp concurrency. Chưa kết luận implementation tương lai chắc chắn vi phạm.

### R-03 — Outbox chưa nêu đủ cơ chế giao thành công cho nhiều consumer

**Bằng chứng.** M23-F12 dòng 399 mô tả worker lease event, consumer dedup và DLQ. Bảng `Internal_Outbox_Events` dòng 478 có một trạng thái PUBLISHED cho event. C16/C20 liệt kê nhiều consumer bắt buộc của một event. Các đoạn contract và schema đã rà chưa định nghĩa trạng thái xác nhận riêng từng consumer hoặc cơ chế broker/subscription bền vững thay thế. [M23](../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), [C23](../02-specs/contracts/M23-PLATFORM-GOVERNANCE-OUTBOX.md), [C20](../02-specs/contracts/M20-SUPPRESSION-PRIVACY-GATE.md).

**Tình huống.** M14 xử lý xong SubjectErasureExecuted, M16 lỗi, M24 chưa nhận. Nếu PUBLISHED có nghĩa hoàn tất toàn event thì M16/M24 có thể bị bỏ sót. Nếu replay cả event, mỗi consumer phải dedup nguyên tử với effect của mình. Tài liệu hiện chưa khóa cách quyết định hoàn tất và phục hồi từng phần.

**[PROPOSED]** Định nghĩa rõ PUBLISHED là đã giao bền vững cho bus hay đã xử lý xong. Chọn cơ chế theo dõi giao nhận theo consumer hoặc durable subscription của broker. Khóa dedup theo tenant, consumer và event. Effect nội bộ cùng dấu đã xử lý phải nguyên tử. Replay/DLQ phải nhắm được consumer thất bại, kèm khả năng quan sát các consumer còn thiếu.

**Nghiệm thu.** Ba consumer nhận cùng event, một thành công, một lỗi, một timeout sau commit. Restart/replay phải đưa cả ba tới kết quả đúng, không bỏ sót hoặc nhân effect. Đặc biệt áp dụng cho privacy/offboarding.

### R-04 — Chính sách phê duyệt đang chờ có hai hành vi đối nghịch

**Bằng chứng.** M23-F04 dòng 236/240 khóa `locked_policy_version_id` và cho hồ sơ đang chờ tiếp tục theo luật lúc trình khi admin sửa ma trận. C23 mục Errors lại mô tả `409 APPROVAL_VERSION_CONFLICT` khi `policy_version_id` đã superseded. [M23](../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), [C23](../02-specs/contracts/M23-PLATFORM-GOVERNANCE-OUTBOX.md).

**Tác động.** Cùng một project change request đang chờ duyệt có thể được tiếp tục hoặc bị chặn chỉ vì cập nhật policy. Hai đội triển khai module và contract sẽ chọn kết quả khác nhau.

**[PROPOSED]** Chốt semantics của supersede thông thường, thu hồi khẩn cấp và migration hồ sơ chờ. Phương án phù hợp với mô tả module hiện tại là tiếp tục dùng snapshot policy đã khóa, đồng thời kiểm quyền người duyệt hiện hành qua M14. Policy bị thu hồi khẩn cấp cần cơ chế chặn/migrate riêng có audit. Đây là quyết định cần Owner/BA xác nhận.

**Nghiệm thu.** Trình theo v1, kích hoạt v2, duyệt hồ sơ cũ. Sau đó kiểm riêng trường hợp người duyệt bị offboard và policy bị thu hồi khẩn cấp.

### R-05 — COMMIT có thể thay đổi dữ liệu so với bản preview

**Bằng chứng.** C24 mục 2.1 cho COMMIT truyền lại `items[]`, `command_type`, `command_params` và `dry_run_batch_id`. M24-F03 dòng 204–211 yêu cầu DRY_RUN hợp lệ nhưng chưa nêu điều kiện khớp bất biến các trường trên với batch preview. Bảng `Bulk_Command_Batches` lưu summary, chưa quy định fingerprint toàn bộ nội dung preview. [C24](../02-specs/contracts/M24-PRODUCTIVITY-CACHE-QUEUE.md), [M24](../02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md).

**Tình huống.** Người dùng preview giao 10 task cho A, nhưng COMMIT cùng batch ID gửi 100 task hoặc đổi người nhận thành B. ACL và expected row version có thể đều hợp lệ, trong khi hành động thực thi khác bản đã xem.

**[PROPOSED]** COMMIT thực thi manifest bất biến đã lưu của DRY_RUN, hoặc bắt buộc khớp canonical hash của actor/scope, command, tham số, tập item và expected versions. Chốt TTL, cách vô hiệu preview và idempotency riêng của DRY_RUN/COMMIT. Quyền và trạng thái vẫn kiểm lại tại execution.

**Nghiệm thu.** Thay owner, thêm/bớt item, đổi command hoặc dùng batch của actor/workspace khác. Các trường hợp sai binding phải bị chặn hoặc yêu cầu preview mới.

### R-06 — Capacity thiếu đơn vị kỳ và cách loại trừ giao nhau

**Bằng chứng.** M14-F07 dòng 359 mô tả quỹ giờ theo “tuần/kỳ”, đã trừ nghỉ M22. C14 mục 2.7 nhận `as_of_date`, trả số giờ cùng `effective_from/to`, nhưng chưa khai báo rõ kỳ đo số giờ đó. M14 dòng 360 yêu cầu M16 trừ tiếp ngày lễ, lịch hẹn và resource allocation. M22 BR-H21 truyền unavailable interval và giữ attendance khác timesheet. [M14](../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md), [C14](../02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md), [M22](../02-specs/modules/M22-HUMAN-RESOURCES.md).

**Tình huống.** Một giá trị 32 giờ có thể là tuần hoặc kỳ khác dù cùng ngày hiệu lực. Một lịch hẹn nằm trong buổi đã nghỉ phép, hoặc allocation trùng lịch hẹn, có thể bị trừ hai lần nếu consumer chỉ trừ số tổng. Quy tắc không trừ phép lần hai hiện có chưa giải quyết giao nhau giữa các loại khoảng thời gian.

**[PROPOSED]** Contract cần period start/end, timezone, calendar/version và định nghĩa quỹ giờ gốc. Tính phần bị chiếm bằng hợp các interval trên cùng kỳ, giữ provenance để tránh trừ chồng. Nếu chỉ xuất số tổng, phải kèm bảo đảm rõ về loại thời gian đã được loại trừ và giới hạn phép tính downstream. Thiếu dữ liệu giữ UNKNOWN, theo W-O06.

**Nghiệm thu.** Nghỉ phép trùng lịch hẹn, ngày lễ trùng ca, allocation trùng appointment, kỳ có nhiều calendar version. Kết quả không âm và không tính cùng phút nhiều lần.

### R-07 — Test Download Gateway không thể hiện ngoại lệ đọc legal hold

**Bằng chứng.** C20 mục 2.4 cho actor có `LEGAL_HOLD_READ` đọc tài liệu đang giữ với watermark. C23 test S-T03 lại yêu cầu từ chối `active_legal_hold_ids <> '{}'` mà không nêu ngoại lệ. C23 Step3 nhận kết quả ALLOW từ M14/M20 và `requires_watermark`, nên test này không khớp đường được phép trong chain. [C20](../02-specs/contracts/M20-SUPPRESSION-PRIVACY-GATE.md), [C23](../02-specs/contracts/M23-PLATFORM-GOVERNANCE-OUTBOX.md).

**Tác động.** Nếu dùng test này làm oracle, nhóm pháp chế có thể mất quyền đọc đối chiếu được thiết kế trong M20.

**[PROPOSED]** Tách test đọc thường bị chặn, đọc có LEGAL_HOLD_READ đúng scope được watermark/audit, và xóa/purge luôn bị chặn khi còn hold. Nếu muốn loại asset cụ thể bị cấm tải hoàn toàn thì ghi thành policy tường minh.

**Nghiệm thu.** Hai actor cùng asset giữ pháp lý, một có quyền chuyên biệt và một không có. Kiểm thêm range/resume sau khi thu hồi quyền.

### R-08 — HR vẫn tham chiếu M19 cho event nội bộ

**Bằng chứng.** M22 dòng 28 ghi “M19 vận chuyển sự kiện”, SL09–11 dòng 7 ghi dependency “M19 outbox/import”. M23/C23 và ADR-005 phân công internal domain outbox cho M23, M19 dành cho external adapter. M22 đã có ghi chú bổ sung adapter thiết bị/ngân hàng, nhưng các dòng dependency cũ vẫn chưa phân định rõ hai đường. [M22](../02-specs/modules/M22-HUMAN-RESOURCES.md), [SL09–11](../02-specs/slices/SL09-11-HRM.md), [ADR-005](../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md).

**Tác động.** HR-A chỉ nhập file/thủ công có thể bị gắn phụ thuộc external outbox không cần thiết. Event offboarding/availability có thể bị triển khai vào đường M19 thay vì internal bus phục vụ M14/M16.

**[PROPOSED]** Làm rõ dependency HR domain event qua C23; M19 áp dụng cho device/bank/provider đã bật. Định nghĩa adapter chuẩn hóa tên event `hr.*.v1` sang envelope C23 vốn ghi chuẩn `<Module>.<EventName>`, giữ tương thích ID và không đổi namespace im lặng. Ghi rõ xử lý import file thuộc worker/domain nào.

**Nghiệm thu.** HR-A chạy khi external connector OFF vẫn gửi được offboarding/availability qua internal outbox. Device/bank OFF không nhận/gửi lệnh ngoài. Consumer cũ và mới nhận đúng một effect.

## Các phụ thuộc cần chốt, chưa coi là lỗi mới

| Giao diện | Điều đã có | Phần cần hoàn thiện trước khi bật |
|---|---|---|
| M21 revoke → M14/M19/M20/M16 | BR-P03 bắt buộc kiểm authority hiện hành, PartnerSharingRevoked và task business key đã nêu | Public contract payload, scope mapping, queued job cancellation và lịch sử report sau revoke. Chưa có contract riêng là công việc còn lại theo kế hoạch |
| M18 → M24 → M23 export | Chuỗi duyệt, worker, gateway đã nêu | Cổng submit export, snapshot dữ liệu và audience, tham số metric/version, partial failure. F08–11 còn Draft |
| M22 → M14 availability/offboarding | Tên event, effective_at/version và nguyên tắc không mở quyền từ chức danh đã có | Schema payload, API đọc snapshot có quyền và mapping employee/user chưa được đóng gói thành contract HR riêng |
| M08 → M16 project handoff | Master yêu cầu accepted handoff và start authorization, C16 đã có InitializeProjectFromHandoff | Producer contract M08, expiry/revoke authorization và nghiệm thu consumer khi M08 được bóc tách |
| M02/M03/M04/M11/M12 → M16 | Source business key, Task Done không tự đóng SLA/reach/complaint đã khóa | Contract của các domain nguồn và test end-to-end cho retry/closure |
| M09/M10/M17 → M19/M20/M23 | Unknown phải đối soát, provider call ngoài DB transaction, không tự Paid | Contract tiền, reservation và proof không chi hai lần khi các module tài chính được tách |
| M06 → M16/M20 | Human approval token, draft hash và vendor/privacy gate đã có | Producer contract token, expiry và replay binding khi triển khai M06 |
| M13 → M16/M23 | Calendar/resource scheduling có ownership | Contract availability cùng kỳ/interval để xử lý R-06 |

Các điều kiện chưa hoàn thiện này chặn đúng capability liên quan. Không tự suy rằng toàn bộ foundation phải chờ mọi module tương lai hoàn tất.

## Thứ tự xử lý đề xuất

1. Chốt cơ chế event delivery/projection của R-01..03 cùng W1-02..03 về lease/retry. Đây là nền chung cho task, privacy và offboarding.
2. Chốt privacy theo chủ thể của W1-01 và khả năng đọc legal hold của R-07.
3. Đồng bộ approval policy và DRY_RUN binding ở R-04..05.
4. Hoàn thiện contract capacity R-06 trước bật cân tải theo giờ.
5. Đồng bộ dependencies HR R-08, manifest W1-05 và test rút submission W1-04.
6. Bóc tách các producer contract còn thiếu theo wave/capability được chọn, dùng bảng phụ thuộc trên làm đầu vào review.

Tech Lead phụ trách concurrency/event semantics, Privacy Owner chốt erasure/legal hold, BA/PO chốt policy và kỳ đo, QA chuyển các tình huống thành expected outcomes. Các vai trò này là đề xuất trách nhiệm, chưa phải người đã nhận việc.

## Kiểm chứng và giới hạn

Chạy `verify_module_spec.py --file` cho 10 tệp bổ sung gồm M18/M21/M22/M23/M24, C23/C24 và SL01/SL08/SL09–11. Cả 10 trả `passed = true`. [Kết quả máy](wave-1-related-validation.json).

Các nhánh kiểm legacy/extension của script có mức kiểm khác nhau. `passed` không xác nhận contract đầy đủ, thứ tự event đúng, isolation đúng hoặc module sẵn sàng triển khai. Kết quả này bổ sung cho 8 tệp đã kiểm ở lượt đầu.

Chỉ ghi báo cáo và kết quả kiểm trong `gpt/`. Không chạy chế độ tổng hợp ghi evidence vào dự án. Chưa thực thi software test, provider PoC, DB/RLS hoặc UAT. Báo cáo là rà soát các liên kết đã mô tả, không là chứng nhận an toàn toàn bộ 24 module.
