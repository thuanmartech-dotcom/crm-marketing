# Kiểm kê và khoảng trống

Nguồn hiện hành: Master1.9, hash ở README; số liệu phần “Kết quả ban đầu” bên dưới là snapshot lịch sử1.7; kết quả số lượng lấy từ evidence/inventory-validation.json.


## Cập nhật M21 ngày18/10/2026

Sau tích hợp1.8: 21 module, 735 ID ứng viên; 221 ID cũ chưa có owner giữ nguyên để review. M21 đã có owner domain, feature/UC/rule/test matrix và P-NFR; chưa có code/UAT đã chạy. Findings/evidence hiện hành thay số snapshot dưới cho báo cáo coverage mới.

Các khoảng trống M21 có P-O01–08 trong Master A.8: volume chính xác, authority/scope chia sẻ, sản phẩm/quyền Pancake, metric/tolerance, mapping/precedence, retention/audience, schedule/budget và exception rules. API thiếu chỉ chặn API; không ép đối tác cấp data để dùng nghiệp vụ công ty. Physical DDL/OpenAPI và người phụ trách thực vẫn cần chốt trước enable.

## Kết quả ban đầu — snapshot1.7 ngày16/10/2026

Parser đã quét toàn bộ 4.170 dòng, giữ occurrences và nội dung nguồn cho từng ID nhận diện. Có 20 module; 634 ID ứng viên trong các namespace đã cấu hình, trong đó 623 có vị trí định nghĩa ứng viên. Đây gồm yêu cầu, test, control và open decision, không phải 634 chức năng khác nhau.

Đã kiểm có định nghĩa ứng viên cho FR01–40, UC01–22, NFR01–12, W-F01–14, BR-W01–10, UC-W01–10 và W-T01–40. Đồng thời thu 98 khai báo entity/nhóm entity, 24 khai báo contract/phần contract và 450 đoạn ứng viên quy tắc chưa có ID. Các nhóm entity không tương đương số bảng cần xây.

## Findings cần đọc đúng

| Kết quả máy | Số lượng | Ý nghĩa thực tế |
|---|---:|---|
| Reference-only ID | 11 | Chưa tìm được định nghĩa bằng heuristic; không tự kết luận yêu cầu bị thiếu |
| ID có nhiều definition candidates | 12 | Có thể là bảng trace hoặc phần mô tả mở rộng; không tự là xung đột |
| ID chưa gán owner | 221 | Phần lớn test/control/open item cần phân công semantic; không bịa owner để đạt coverage |
| Mục không phải test chưa trích được test link | 291 | Same-row extraction không đủ phát hiện mọi link ở đoạn khác; cần hoàn thiện trace |
| Dòng shorthand cần review | 47 | Gồm W01/T01, nhiều module và legacy namespace; có cả false positives |

Reference-only hiện tại: WF01, WF06–14, U23. Master 3.14 nói rõ WF01–14 là mã trong báo cáo nguồn, nay dùng W-F01–14; trong khi WF cũng là namespace control khác. Vì vậy không tự alias mọi WFxx sang W-Fxx. U23 đã tách U23-R/U23-L theo capability; giữ việc đối chiếu tham chiếu cũ. Findings có line/text để review từng occurrence.

Các candidate trùng FR25/FR37/FR38 do định nghĩa và ma trận truy vết; UC-W08/09/10 còn có mô tả chi tiết; W-F01 còn xuất hiện trong phụ lục thay đổi. O01–05 còn xuất hiện dưới dạng mã nguồn Odoo ở Phụ lục H: cần phân loại nguồn tham khảo riêng với open decisions ở A.6, không gộp semantics chỉ vì cùng chuỗi. Registry giữ occurrences để phát hiện vấn đề này, chưa là canonical registry đã ký.

## Gap log hành động

| ID | Dữ kiện / gap | Quyết định đề nghị | Owner vai trò | Chặn gì |
|---|---|---|---|---|
| GAP-01 | Đã có AGENTS.md giai đoạn tài liệu (Documentation-Only); chưa có manifest hoặc repo mã nguồn ứng dụng | Giữ nguyên trạng thái chỉ viết tài liệu cho tới khi xong spec; xác nhận build mới/configure/hybrid và lập ADR trước khi scaffold code | Chủ dự án + Tech lead | Code production; không chặn spec |
| GAP-02 | Stack ở 2.8 là tham chiếu, chưa có repo triển khai | Ưu tiên đánh giá TS/React/NestJS/PostgreSQL nếu tự xây; phiên bản chưa pin | Tech lead | Build và test commands thật |
| GAP-03 | 221 ID chưa có owner và shorthand lịch sử | Review theo từng nhóm; mỗi requirement một accountable owner, nhiều consumer | BA + domain owner | Tuyên bố hoàn tất trace toàn hệ thống |
| GAP-04 | Dictionary logical, có grouped names như Task_Submissions / Reviews | Chốt tên bảng, field, constraints, indexes, policy và API schema cho SL01 trước migration | DB lead + BA | SL01 implementation-ready |
| GAP-05 | Team/reviewer/queue manager chưa chỉ định | Fixture giả cho review; trước pilot thật cấu hình W-O01/02 | Ops + Team lead | Giao việc/review live |
| GAP-06 | Visibility/retention/publish, luồng intake `O03` (`Master A.6`), chế độ dữ liệu `CLIENT` (`O06` / `GAP-M14-02`), ngân hàng công ty vs cá nhân (`O04` / `GAP-M14-04`) và mô hình đa chi nhánh/pháp nhân (`O08` / `GAP-M14-03`) chưa cấu hình doanh nghiệp | Giữ private không mở cho cấp trên; giữ intake `O03` định tuyến về `Owner/CEO` và tắt tự động hóa rủi ro (`Fail-Closed`); giữ `CLIENT` ở `AGGREGATE_ONLY` (`M14/M20`); giữ `Retention_Policies` ở `DRAFT`; xác nhận `W-O04` | Owner / CEO + Privacy Owner + Finance Lead | Dữ liệu cá nhân thật, `CLIENT` PII & tự động hóa `SL02+` |
| GAP-07 | Offer timeout, lịch, reminder, review due chưa có policy active | Không bật timer tự động khi thiếu; UI báo chưa cấu hình | Ops | Automation theo lịch |
| GAP-08 | Chưa có kênh/account/API capability được xác minh | SL02 mock trước; live chỉ sau thử tài khoản được phép | Integration owner | Nhận/gửi live |
| GAP-09 | Nơi ghi task có thể đổi nếu dùng PMS | SL01 đề xuất CRM theo A.7; adapter PMS off; không dual-write | PM + Tech lead | Sync PMS |
| GAP-10 | Không có migration/test suite/run logs ứng dụng | Tạo sau ADR và physical contract; mọi ca CRM hiện Not Run | Dev + QA | Merge/enable/release |
| GAP-11 | Baseline P0 lớn hơn SL01 | SL01 là milestone kỹ thuật; giữ W-F08/09 và CRM P0 trong roadmap | PO | Tuyên bố hoàn tất P0 |
| GAP-12 | Ngân sách/nhân lực/hạ tầng/DR chưa chốt O05/O08/W-O07 | Ước tính sau spike, không hứa 90 ngày hoặc SLO đã đạt | Owner + Ops | Lịch go-live/SLA |
| GAP-13 | Endpoint start/block/update/result draft chưa đầy đủ ở 5.20 | Thiết kế command table trước sinh OpenAPI; không dùng PATCH status tự do | M16 BA + Tech | SL01 contract-ready |
| GAP-14 | P0 asset/comment có scan/retention; pilot text-only chỉ là tập con | Upload/comment UI và API off nếu chưa kiểm; giữ các ca tương ứng trong release tiếp | M16 + M20 | Tuyên bố W-F06 hoàn tất |
| GAP-15 | Ngưỡng chuyển `SOLO/PILOT -> TEAM` (`M23-F05`) và TTL Break-glass (`M23-F03`) mới ở mức đề xuất | Chốt số lượng người duyệt tối thiểu (đề xuất $\ge 3$ quản lý) và trần TTL Break-glass (đề xuất 2–4 giờ) trước khi đóng spec `SL00` | Owner/CEO + Security | Đóng spec chi tiết `M23` |
| GAP-16 | Chưa chốt danh mục chuẩn dùng chung (`M23-F11`) và khung `Quiet Hours` mặc định (`M23-F10`) | Chốt bộ lý do Won/Lost/Hold/Cancel, thuế/tiền tệ, mẫu ZNS/Email và lịch nghỉ lễ công ty | Ops Lead + BA | `M23-F10/11` ready |
| GAP-17 | Chưa chốt ngưỡng kích hoạt cảnh báo DLP (`M23-F08`) | Xác định ngưỡng số dòng/lần export/lỗi 403 bất thường trước khi bật cảnh báo tự động ở `SL07` | Security + Tech | Bật `M23-F08` |
| GAP-18 | Chưa chốt công nghệ Read Model/Search/Queue (`M24-F01/06/07/08`) và chu kỳ Archiving | Chọn sau khi hoàn tất ADR stack thật (`GAP-02`), đảm bảo tách 3 làn queue và `permission_version` invalidation | Tech Lead + SRE | Benchmark & code `M24` |
| GAP-M14-01 | Chưa chốt trần số ngày ủy nhiệm tự kích hoạt (`delegation_max_duration_days` tại `M14-F05`) | Áp dụng `Safe Default = 14 ngày` (vượt quá 14 ngày hoặc chứa quyền nhạy cảm bắt buộc `Branch Manager / Owner` duyệt trước khi `ACTIVE`) | Ops Lead + Owner | Chỉ chặn tự kích hoạt ủy nhiệm dài hạn |
| GAP-M20-01 | Chưa phê duyệt bảng công thức hạn pháp lý (`legal_deadline_policy_matrix` tại `M20-F05`) theo từng loại quyền và vai trò `Controller/Processor` | Giữ `Legal_Deadline_Policies` ở trạng thái `DRAFT` (`Fail-Closed`: không tự gán 72h giả định; bắt buộc `Privacy Owner` nhập hạn thủ công có căn cứ trên từng ca cho tới khi duyệt `ACTIVE`) | Privacy Owner / Pháp chế | Bật tính hạn tự động `M20-F05` |
| GAP-M20-02 | Chưa phê duyệt chính thức thời hạn lưu trữ tự động xóa (`default_retention_days_by_domain` tại `M20-F06`) | Lưu đề xuất Master `6.4` (`180 / 90 / 30 / 180` ngày) ở trạng thái `DRAFT`; worker purge định kỳ chỉ chạy trên miền đã được `Privacy Owner` duyệt `ACTIVE` | Privacy Owner + Finance Lead | Bật worker xóa định kỳ `M20-F06` |
| GAP-M19-01 | Chưa chốt cấu hình TTL mặc định và lịch retry Outbox (`outbound_intent_default_ttl_minutes` & `retry_backoff_schedule_minutes` tại `M19-F05/F06`) | Áp dụng `Safe Default`: TTL mặc định `120 phút` cho tin nhắn SLA ngắn/cơ hội hết hạn sau reconnect, backoff `[1, 5, 15, 60]` phút + jitter và tôn trọng header `Retry-After` | Tech Lead + Ops Lead + Integration Owner | Tối ưu SLA gửi tin & chống bão Outbox `M19` |
| GAP-M19-02 | Chưa chốt ngưỡng kích thước tệp tối đa và timeout tải phương tiện từ xa (`remote_fetch_max_bytes` & `connect/read_timeout_ms` tại `M19-F08` & `SEC04`) | Áp dụng `Safe Default Fail-Closed`: tối đa `25 MB` (`26.214.400` bytes), `connect_timeout = 3000ms`, `read_timeout = 15000ms`, `follow_redirects = false`, chặn tuyệt đối dải IP nội bộ/metadata | Security + Tech Lead | Vận hành Zero-Trust Media Fetch `M19-F08` |
| GAP-M14-02 | Chưa chốt chế độ dữ liệu trên `CLIENT workspace` (`O06`: `client_workspace_allowed_data_mode`) | Áp dụng `Safe Default = AGGREGATE_ONLY`: cấm tạo/đồng bộ PII khách cuối vào `CLIENT workspace` khi chưa có `Processing_Records (PROCESSOR)` + DPA `ACTIVE` tại `M20-F01` | Owner / CEO + Privacy Owner | Mở `SCOPED_PII_WITH_DPA` cho `CLIENT` |
| GAP-M14-03 | Chưa chốt mô hình đa chi nhánh & đa pháp nhân (`O08` / `GAP-12`: `multi_branch_and_legal_entity_mode`) | Áp dụng `Safe Default = false` (Pilot đơn chi nhánh/pháp nhân dùng `default_branch_id` & `default_legal_entity_id`); khi bật `true` bắt buộc gán tường minh cặp chi nhánh–pháp nhân (`CEO-U10`) | Owner / CEO + Finance Lead | Bật đa chi nhánh / đa pháp nhân (`ADR-004`) |
| GAP-M14-04 | Xác nhận phân tách ngân hàng Công ty vs Cá nhân (`O04`: `corporate_vs_personal_bank_owner_rule`) | Khóa ranh giới cứng theo `ADR-004`: tài khoản ngân hàng pháp nhân thuộc `M09`, tài khoản nhận lương nhân viên thuộc `M22`, chặn đọc chéo qua `M14-F04` | Owner / CEO + Finance Lead | Rà soát vận hành Tài chính (`M09`) & Lương (`M22`) |
| GAP-M14-05 | Chưa chốt cỡ mẫu tối thiểu đánh giá Scorecard (`scorecard_min_sample_size` tại `M14-F08`) | `Fail-Closed`: thiếu cấu hình hoặc chưa đạt cỡ mẫu đánh dấu `INSUFFICIENT_DATA` và ẩn ranking/đánh giá xếp hạng (`M14-AC03`) | Delivery Lead + Owner | Mở xếp hạng hiệu suất `M14-F08` |
| GAP-M14-06 | Chưa chốt thời hạn cảnh báo hạng mục bàn giao treo ở Người giám hộ (`custodian_aging_alert_hours` tại `M14-F06`) | Áp dụng đề xuất `[PROPOSED] = 24 giờ`: vượt ngưỡng `CUSTODIAN_HOLD` chưa xác nhận `Accept/Reject` gửi cảnh báo nhắc việc `Branch Manager / Ops` | Ops Lead | Cảnh báo SLA bàn giao `M14-F06` |
| GAP-M20-03 | Chưa chốt chuẩn chuẩn hóa dữ liệu & lịch xoay khóa HMAC cho `Deletion_Ledger` (`hmac_normalization_and_key_rotation` tại `M20-F06`) | Dùng Unicode `NFKC` + E.164 / lowercase email (`ADR-007`) với `hmac_key_version` tường minh và hỗ trợ key cũ ở chế độ `VERIFY_ONLY` khi Verify Restore | Security Architect + Privacy Owner | Vận hành xoay khóa & Restore `Deletion_Ledger` |
| GAP-M20-04 | Chưa chốt ngưỡng Soft-Bounce theo từng nhà cung cấp (`soft_bounce_cooldown_and_max_retries` tại `M20-F03`) | Đề xuất `[PROPOSED]` tạm thời `3 lần / 24h` (`SOFT_BOUNCE_COOLDOWN`) cho tới khi chốt cấu hình riêng theo provider (`FR34`) | Ops Lead + Privacy Owner | Tinh chỉnh ngưỡng chặn tạm `Soft-Bounce` |
| GAP-M20-05 | Chưa chốt quy chuẩn chứng từ gỡ chặn endpoint (`endpoint_recovery_evidence_policy` tại `M20-F03`) | Chỉ `Privacy Owner / Data Steward` được gỡ sang `RELEASED_BY_VERIFIED_PROOF` khi có bằng chứng xác thực (`FR34`); cấm `Marketing/Import` tự gỡ | Privacy Owner | Quy trình gỡ chặn có kiểm chứng `M20-F03` |
| GAP-M20-06 | Chưa chốt TTL lưu trữ tạm trong `Placeholder_Vault` (`placeholder_vault_ttl_hours` tại `M20-F07`) | Áp dụng đề xuất `[PROPOSED] <= 24 giờ` (tối thiểu hết phiên làm việc) và buộc gọi `M14.EvaluateAccessDecision` mỗi lần giải mã | Privacy Owner + AI Lead | Tối ưu vòng đời phiên AI RAG/Copilot |
| GAP-M20-07 | Chưa chốt tiêu chí chi tiết chuyển dữ liệu xuyên biên giới (`cross_border_transfer_criteria` tại `M20-F07`) | `Fail-Closed`: thiếu hồ sơ đánh giá tác động/căn cứ hợp lệ theo Luật `91/2025/QH15` $\rightarrow$ chặn `VENDOR_TRANSFER_POLICY_BLOCKED` | Privacy Owner / Pháp chế | Mở chuyển dữ liệu AI/Vendor xuyên biên giới |
| GAP-M20-08 | Chưa chốt kênh & mẫu thông báo sự cố dữ liệu ra bên ngoài (`incident_external_notification_channels` tại `M20-F08`) | Khóa chuyển trạng thái `Data_Incidents = NOTIFIED` cho tới khi hoàn tất checklist thông báo cơ quan chức năng & chủ thể dữ liệu; không reset mốc `awareness_at` | Privacy Owner + Owner | Quy trình báo cáo sự cố chính thức `M20-F08` |
| GAP-M20-09 | Chưa chốt thời gian cảnh báo sớm trước hạn yêu cầu dữ liệu/sự cố (`privacy_due_prealert_hours` tại `M20-F05/F08`) | Áp dụng đề xuất `[PROPOSED] = 24 giờ` trước `response_due_at / action_due_at / notification_due_at` gửi tới `Privacy Owner` & `CEO` | Privacy Owner | Cảnh báo sớm hạn pháp lý `M20` |
| GAP-M20-10 | Chưa chốt SLO dọn hàng đợi bất đồng bộ sau khi có lệnh chặn gửi (`suppression_queue_cleanup_slo_seconds` tại `M20-F03`) | Bảo vệ thực tế bằng đọc thẳng Primary DB tại `DISPATCH_AUTHORITATIVE`; theo dõi thời gian dọn queue bất đồng bộ qua metric SLO (`không hứa 0s vật lý` theo `6.3 L3172`) | Platform Ops + Privacy Owner | Theo dõi SLO dọn hàng đợi `M19/M20` |
| GAP-M19-03 | Chưa xác minh chính thức thuật toán/header xác thực chữ ký webhook Zalo OA (`zalo_webhook_verifier_contract` tại `M19-F04`) | **`UNVERIFIED_UNTIL_POC` (`Fail-Closed`):** Cấm tự giả định `HMAC-SHA256`; khóa webhook Zalo OA live cho tới khi hoàn tất PoC & contract test từ tài liệu chính thức (`Master 3.12.12 L1420`) | Tech Lead + Security Lead | Mở khóa webhook Zalo OA live |
| GAP-M19-04 | Chưa xác minh danh mục Meta Message Tags hợp lệ & hành vi HTTP 429 (`meta_message_tags_and_429_manifest` tại `M19-F03`) | **`UNVERIFIED_UNTIL_POC` (`Fail-Closed`):** Cấm hardcode danh mục Meta Tags hay nút "Tag chung"; khóa gửi ngoài cửa sổ chuẩn cho tới khi verify manifest PoC (`3.12.12 L1419`) | Integration Owner + CX Lead | Mở khóa gửi ngoài cửa sổ Meta/Messenger |
| GAP-M19-05 | Chưa chốt ngưỡng gia hạn sớm Gmail Watch / MS Graph Subscription (`subscription_renewal_lead_minutes` tại `M19-F06`) | Đọc TTL watch/subscription động từ tài liệu/version hiện hành của Google/Microsoft (cấm hardcode TTL chung `2.7 L325`); đặt ngưỡng gia hạn sớm trước hạn | Integration Owner + Tech Lead | Tự động gia hạn Gmail / MS Graph ổn định |
| GAP-M19-06 | Chưa chốt SLA đối soát trạng thái `UNKNOWN_OUTCOME` & cờ duyệt kép (`unknown_outcome_reconcile_sla_minutes` & `manual_override_dual_control`) | Đề xuất `[PROPOSED]`: cảnh báo sau `+15 phút`; với `risk_class <> STANDARD_MESSAGE` (tiền/lương/ZBS phí) bắt buộc `evidence_ref` + duyệt kép `Maker != Checker` | Finance Lead + Ops Lead | Chốt đối soát thủ công `UNKNOWN_OUTCOME` |
| GAP-M19-07 | Chưa chốt thời gian sống của OAuth `state_nonce` dùng một lần (`oauth_state_ttl_minutes` tại `M19-F02`) | Áp dụng đề xuất `[PROPOSED] = 10 phút` cho `OAuth_Authorization_Attempts.expires_at`; hết hạn phải khởi tạo lại luồng OAuth | Security Lead | Tối ưu bảo mật luồng OAuth `SEC01` |
| GAP-M19-08 | Chưa chốt thời hạn xóa tự động raw webhook payload / quarantine / file tạm (`integration_raw_payload_retention_days` tại `M19-F04`) | Lưu tham khảo Master `6.4 L3178` = `30 ngày` ở trạng thái `DRAFT`; worker chỉ purge khi `Privacy Owner` duyệt `ACTIVE` tại `M20-F06` và tôn trọng `Legal_Hold` | Privacy Owner + Ops Lead | Bật purge định kỳ dữ liệu tích hợp thô |
| GAP-M19-09 | Chưa chốt cửa sổ backfill tối đa và ngưỡng mở circuit breaker 429 (`sync_backfill_max_window_days` & `provider_429_circuit_breaker_threshold`) | Áp dụng đề xuất `[PROPOSED]`: mặc định backfill tối đa `30 ngày/lượt` trên `Lane 3`; vượt ngưỡng lỗi liên tiếp chuyển `Channel_Connections = DEGRADED` | Tech Lead + Ops Lead | Bảo vệ rate-limit & cách ly Backfill `Lane 3` |
| GAP-M19-10 | Danh mục & hợp đồng kết nối phi nhắn tin chưa chốt nhà cung cấp (`O04/O06/O08`: `non_messaging_adapter_activation_policy`) | `Fail-Closed`: tắt mặc định nhóm `PARTNER_POS_READ` (`PANCAKE`) và các provider `VOIP_SIP`, `ERP_MISA`, `PMS`, `BIOMETRIC_DEVICE`, `PAYROLL_BANK` cho tới khi chốt nhà cung cấp (`O04`), `dpa_data_mode` (`O06`), `Processing_Records = ACTIVE` và PoC (`H-NFR08`) | Owner / CEO + Tech Lead | Kích hoạt từng adapter ERP/PMS/VoIP/Bank |

## Phạm vi parser và kiểm semantic

Parser mở dải ID cùng prefix và shorthand slash dạng FR01/02; giữ reference và definition candidates riêng. Nó không giải nghĩa mọi bảng trace có W01/T01 hoặc mọi đoạn văn. Không suy “mục không có test link” là “không có test trong Master”. Không lấy consumer co-mention làm dependency chuẩn. Danh sách unnumbered có cả phụ lục lịch sử và Mermaid; review trước promote thành requirement.

NFR/controls xuyên module không bị xóa: owner PLATFORM là trách nhiệm kỹ thuật đề xuất, không phải module M21. Capability hiện chưa enable nên trạng thái test là Not Run; chỉ được ghi N/A khi có release profile và bằng chứng không có đường sử dụng. Hoãn tính năng không hoãn quyền/audit của tính năng đang chạy.

Thứ tự xử lý: SL01 quyền + semantics + physical schema → trace SL01 được review → test fixtures → code. Sau đó chuẩn hóa ownership/test links phần còn lại trước từng slice. Chưa cần chốt chính sách hoa hồng để thiết kế Task Core; thiếu policy hoa hồng vẫn chặn payout.

## Cập nhật HRM1.9

M22 đã có đặc tả28chức năng/16UC/24rules/48UAT/8NFR; các H-O01–10 ở Master A.9 là đầu vào triển khai còn mở. Đã xác nhận hiện trạng Excel, chưa nhận file thật; không giả đã làm sạch/import dữ liệu. Chưa chọn INTERNAL/EXTERNAL payroll, thiết bị hoặc bank adapter. Số liệu kiểm kê hiện hành lấy evidence/inventory-validation.json; snapshot1.8 phía trên là lịch sử.
