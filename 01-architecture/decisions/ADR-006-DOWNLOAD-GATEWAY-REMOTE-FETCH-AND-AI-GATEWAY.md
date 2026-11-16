# ADR-006 — Kiến trúc `Download Gateway` (`SEC03`), Zero-Trust `Remote Fetch` (`SEC04`) và `AI Data Gateway` (`M20-F07` $\leftrightarrow$ `M06`)

**Status:** `Approved (Wave 1.5 Hardening — CR-20261116-WAVE1-5-HARDENING)`  
**Phạm vi:** `M14` (`SEC03`), `M19` (`SEC04`, `3.12.11`), `M20` (`M20-F07`, `FR13`), `M22` (`ENTITY-L3031`), `M23` (`Assets` / `Asset_Versions`, `F07`, `Policy_Versions`), `M24-F08` (`Export_Requests`), `M06`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`3.5.3 L737–744`, `3.12.11 L1404–1409`, `5.13 L2783`, `6.2`, `6.3 L3174`, `6.8`, `SEC03 L4687`, `U16`, `U22`, `INT24`, `INT28`, `OC13`, `OC14`, `OC20`, `SEC-U03`, `SEC-U04`), [INVARIANTS.md](../INVARIANTS.md) (`INV-02`, `INV-21`, `INV-24`), [ADR-002](ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-004](ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md)

---

## Context

1. `Master L4687` (`SEC03`) yêu cầu `Download Gateway` bảo vệ mọi lượt tải/Range/Resume tệp nhạy cảm (`Assets` `ENTITY-L2783`, hồ sơ nhân sự `ENTITY-L3031`, `Export_Requests`). Tuy nhiên thiết kế Wave 1 mới chỉ truyền `asset_id` chung mà chưa khóa **`asset_version_id NN`**, chưa kiểm **`Asset_Versions.scan_status == 'CLEAN'`**, và chưa truyền **`owner_resource_type/id`** để `M14` kiểm quyền kép trên cả `ASSET` lẫn thực thể chủ quản.
2. Ở `SEC04` (`Remote Fetch`), hợp đồng cũ hardcode `25MB` (`26.214.400` bytes) thay vì đọc từ `Policy_Versions`, thiếu `total_timeout_ms`, chưa đồng nhất `max_redirects` vs allowlist CDN, chưa chặn đầy đủ CIDR IPv4/IPv6 + IPv4-mapped IPv6 (`::ffff:127.0.0.1`, `::ffff:169.254.169.254`, `fc00::/7`, `fe80::/10`, `100.64.0.0/10`, `0.0.0.0/8`), chưa khóa kiểm magic bytes MIME và trạng thái `asset_version_id (PENDING)` lúc upload, và chưa cấm `WEB_FORM` kích hoạt Remote Fetch.
3. Ở `M20-F07` (`EvaluateVendorAndAiTransfer`), quy tắc chặn cứng `NATIONAL_ID_CCCD`, `BANK_ACCOUNT_OR_PAYMENT`, `HRM_PAYROLL` đang áp chung cho cả `M19_EXTERNAL_WEBHOOK` (gây chặn nhầm tích hợp kế toán/ngân hàng/lương hợp lệ), thiếu server-side DLP scan độc lập với nhãn client, và `Placeholder_Vault` thiếu `(source_resource_type, source_resource_id)` để `M14` tái kiểm quyền khi giải mã ngược.

## Đề nghị

1. **Chuỗi Khép kín `Download Gateway` (`SEC03`, `INV-24`, `U16`, `SEC-U03`):**
   - **Cấm tuyệt đối** trả về raw Object Storage / S3 presigned URL trực tiếp cho trình duyệt khi tệp thuộc nhóm nhạy cảm (`Assets` PII, hợp đồng, chứng từ tài chính, ghi âm cuộc gọi, hồ sơ nhân sự `ENTITY-L3031`, export `M23-F07/M24-F08` thông qua **`Export_Requests.asset_id`** trỏ vào registry `Assets` / `Asset_Versions`).
   - **Tham số Đầu vào Bắt buộc:** `asset_id NN`, **`asset_version_id NN`**, **`owner_resource_type NN`**, **`owner_resource_id NN`** (hoặc `EXPORT_REQUEST` gắn `Export_Requests.asset_id`).
   - Mọi request `GET` hoặc `HTTP Range/Resume` qua Gateway bắt buộc vượt qua 3 chốt theo thứ tự **trước khi stream bất kỳ byte nào**:
     1. **`M14` Live ACL & Session Guard (`EvaluateAccessDecision`):** Kiểm `session/token` còn sống, `Users.status = 'ACTIVE'`, `expected_permission_version`, và kiểm quyền **`M14` lên CẢ hai đích: `ASSET` VÀ `owner_resource` (`owner_resource_type + owner_resource_id`)** — nếu thiếu quyền trên tài nguyên chủ quản hoặc lệch version $\rightarrow$ **`401/403` tức thì, không trả từ CDN/browser cache (`SEC-U03`)**.
     2. **`M20` Asset Version Privacy, Quarantine & Hold Gate (`EvaluateAssetDownloadPrivacyGate`):** Kiểm **`Asset_Versions.scan_status == 'CLEAN'`** trên đúng phiên bản `asset_version_id` (chặn `PENDING/INFECTED/FAILED`), kiểm chưa bị xóa theo `Deletion_Ledger`, kiểm `active_legal_hold_ids` / `RESTRICTED_LEGAL_HOLD` (`M20-F06`), và kiểm quy tắc tệp nhân sự `6.8` (`ENTITY-L3031`).
     3. **`M23-F07` Watermark & Audit Log:** Với tệp Export/bản sao nhạy cảm (`Export_Requests.asset_id`), kiểm `download_expires_at` chưa quá hạn, đính header `Cache-Control: no-store`, đóng watermark và ghi `AssetDownloaded` vào `Audit_Logs` (`M23-F06`).

2. **Zero-Trust `Remote Fetch` & Giới hạn Upload (`SEC04`, `3.12.11 L1404–1409`, `OC13`, `OC14`, `INT24`):**
   - **Cấm `WEB_FORM` kích hoạt Remote Fetch:** Tuyệt đối không cho payload từ `WEB_FORM` công khai (URL tự do từ người dùng ngoài) kích hoạt `ExecuteSafeRemoteFetch`. Chỉ cho phép domain trong allowlist đã verify của `Channel_Connections` qua **Egress Sandbox Proxy**.
   - **Pin DNS, `max_redirects` & Chặn Tuyệt đối CIDR IPv4/IPv6 + IPv4-mapped IPv6:**
     - Mặc định `follow_redirects = false` (`max_redirects = 0`); chỉ khi adapter manifest trong `Connection_Capabilities` yêu cầu CDN redirect đã verify mới cho phép `max_redirects` hữu hạn cấu hình theo policy, **và mọi hop redirect đều phải qua lại đầy đủ Domain Allowlist + Pin DNS + CIDR Block** trước khi mở socket.
     - Chặn toàn diện các dải IP sau khi phân giải DNS (và giải nén IPv4-mapped IPv6 về dạng IPv4 trước khi so sánh):
       - **IPv4:** loopback (`127.0.0.0/8`), private (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local / cloud metadata (`169.254.0.0/16`, `169.254.169.254`), CGNAT (`100.64.0.0/10`), unspecified (`0.0.0.0/8`), multicast/reserved.
       - **IPv6 & IPv4-mapped IPv6:** loopback (`::1/128`), unspecified (`::/128`), ULA (`fc00::/7`), link-local (`fe80::/10`), và **`::ffff:0:0/96`** (cấm tuyệt đối dạng ánh xạ như `::ffff:127.0.0.1`, `::ffff:169.254.169.254`, `::ffff:10.x`, `::ffff:100.64.x`, `::ffff:0.0.0.0`).
   - **Giới hạn Kích thước Động từ `Policy_Versions` & `total_timeout_ms`:**
     - **Bỏ hardcode `25MB` (`26.214.400` bytes);** tham số `remote_fetch_max_bytes` / `upload_max_bytes` đọc từ **`M23.Policy_Versions`** (giá trị `25 MB` chỉ giữ làm đề xuất khởi tạo `[OPEN-GAP: GAP-M19-02]`), kết hợp `effective_max_bytes = min(policy_max_bytes, verified_provider_method_limit)`.
     - Email inbound/outbound **bắt buộc cộng thêm `+33%` MIME base64 overhead** trước khi đối chiếu giới hạn (`3.12.11 L1406`).
     - Bổ sung **`total_timeout_ms`** (tổng ngân sách thời gian toàn phiên từ DNS lookup $\rightarrow$ connect $\rightarrow$ read stream, bổ trợ `connect_timeout_ms` và `read_timeout_ms` để chống slowloris).
   - **Magic Bytes MIME & Quarantine `asset_version_id (PENDING)`:**
     - Mọi file tải về từ Remote Fetch hoặc upload trực tiếp phải **kiểm tra magic bytes thực tế của nội dung stream** để xác minh MIME type (không tin `Content-Type` hay phần mở rộng file), kiểm chống zip/decompression bomb theo byte giải nén thực tế, và **cấp `asset_version_id` ở trạng thái `scan_status = 'PENDING'` ngay lúc upload/ingest** (cấm gắn vào `Deliverable_Asset_Refs` hay tải qua `SEC03` trước khi quét xong chuyển `CLEAN`).
     - Email inbound/outbound HTML: strip script/dangerous tags & invisible tracking pixels trước khi render UI (`OC13`, `INT24`).

3. **`AI Data Gateway` & `Placeholder_Vault` (`M20-F07` $\leftrightarrow$ `M06`, `FR13`, `U22`, `INT28`, `OC20`):**
   - **Cưỡng chế điểm chặn ở tầng Gateway (`M20-F07` Proxy trước LLM SDK của `M06`):** `M06` không được gọi trực tiếp API nhà cung cấp LLM mà không đi qua `EvaluateVendorAndAiTransfer` (`C20`).
   - **Khoanh vùng `PROHIBITED_DATA_CLASS_INCLUDED` riêng cho `feature_code IN ('AI_*')`:**
     - Quy tắc chặn cứng `NATIONAL_ID_CCCD`, `BANK_ACCOUNT_OR_PAYMENT`, `HRM_PAYROLL` (`PROHIBITED_DATA_CLASS_INCLUDED`) **chỉ áp dụng cho `feature_code LIKE 'AI_%'`** (`AI_SUMMARY`, `AI_DRAFT`, `AI_SUGGEST`, `AI_TRANSCRIBE` — cấm đưa vào LLM/index chung `6.8`).
     - Với **`M19_EXTERNAL_WEBHOOK`** (ví dụ đồng bộ ERP MISA, Payment Gateway, chi lương ngân hàng `M22-F28`), **cho phép truyền qua cổng khi đã có `Processing_Records (ACTIVE)` + `Vendor_Data_Flows (APPROVED)`** phù hợp và không vướng `Legal_Hold`, thay vì bị chặn nhầm bởi quy tắc AI.
   - **Server-Side DLP Scan & Chống Prompt Injection (`U22`, `INT28`, `OC20`):**
     - Trước khi đẩy ra ngoài/LLM, `M20-F07` bắt buộc chạy **server-side DLP scan** (regex/classifier phát hiện CCCD, số thẻ/tài khoản ngân hàng, token bí mật, trường lương) bất kể `data_classes[]` client gửi lên khai báo thế nào (`Fail-Closed`).
     - Trước khi truy xuất RAG/Context cho AI: gọi `M14.CompileScopeFilter` (`C14`). Payload khách/tệp đính kèm gắn `untrusted_data_fenced = true` và khóa cứng không cho phép lời nhắc kích hoạt tool đột biến (`U22`, `INT28`); khi feature flag `M06` tắt (`OFF`), tắt sạch mọi tool route.
   - **`Placeholder_Vault`:** Lưu ánh xạ `[PII_<CLASS>_<N>]` $\leftrightarrow$ giá trị gốc đã mã hóa kèm **`(actor_id, source_resource_type, source_resource_id)`**, `session_correlation_id`, và `expires_at` (`[OPEN-GAP: GAP-M20-06]` `<= 24 giờ`); khi `M06` hoặc UI yêu cầu giải mã ngược, bắt buộc gọi `M14.EvaluateAccessDecision` kiểm quyền của đúng `actor_id` lên chính **`(source_resource_type, source_resource_id)`** (`6.3 L3174`, `INV-02`).

## So sánh

- **Giữ `SEC03` chỉ kiểm `asset_id`, hardcode `25MB`, hoặc chặn `BANK/HRM` chung cho mọi `feature_code`:** Dễ làm rò tệp qua `asset_id` giữa các version/chủ sở hữu khác nhau, gây treo worker hoặc SSRF qua IPv4-mapped IPv6/redirect/WEB_FORM, và làm gãy kết nối ngân hàng/ERP/payroll hợp pháp qua `M19`. Thiết kế Wave 1.5 giải quyết toàn diện cả 3 cổng Gateway.

## Hệ quả và điều kiện thay đổi

- Cập nhật [M20-PRIVACY-CONSENT-RETENTION.md](../../02-specs/modules/M20-PRIVACY-CONSENT-RETENTION.md), [M20-SUPPRESSION-PRIVACY-GATE.md](../../02-specs/contracts/M20-SUPPRESSION-PRIVACY-GATE.md), [M19-INTEGRATION-ADAPTERS-OUTBOX.md](../../02-specs/modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md), [M19-DURABLE-INGEST-OUTBOX.md](../../02-specs/contracts/M19-DURABLE-INGEST-OUTBOX.md), [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md) (`Assets` / `Asset_Versions`, `Export_Requests.asset_id`, `Policy_Versions`), `C23`, `C24`, và `M14` (`C14`).
