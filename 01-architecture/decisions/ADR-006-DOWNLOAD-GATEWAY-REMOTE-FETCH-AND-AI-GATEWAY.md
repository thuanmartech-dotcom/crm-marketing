# ADR-006 — Kiến trúc `Download Gateway` (`SEC03`), Zero-Trust `Remote Fetch` (`SEC04`) và `AI Data Gateway` (`M20-F07` $\leftrightarrow$ `M06`)

**Status:** `Approved (Proposed Extension trong Baseline v1.9)`  
**Phạm vi:** `M14` (`SEC03`), `M19` (`SEC04`, `3.12.11`), `M20` (`M20-F07`, `FR13`, `Assets`), `M22` (`ENTITY-L3031`), `M23-F07`, `M24-F08`, `M06`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`3.5.3 L737–744`, `3.12.11 L1404–1409`, `5.13 L2783`, `6.2`, `6.3 L3174`, `6.8`, `SEC03 L4687`, `U16`, `U22`, `INT24`, `INT28`, `OC13`, `OC14`, `OC20`, `SEC-U03`, `SEC-U04`), [INVARIANTS.md](../INVARIANTS.md) (`INV-21`, `INV-24`)

---

## Context

1. `Master L4687` (`SEC03`) và `requirements.json` gán `owner = M14`, `consumers = [M03, M20]` cho `Download Gateway`, `M22 L139` trỏ chứng từ nhân sự sang `File gateway M20`, nhưng `M20` bỏ trống `SEC03`, `Assets` (`ENTITY-L2783`) và `ENTITY-L3031`.
2. `M19-F08` (`GAP-M19-02`) tự ấn định `25 MB` không áp quy tắc `min(product_limit, verified_provider_method_limit)` và bỏ sót chi phí mã hóa MIME (`~+33%`) cho Email (`3.12.11 L1406`).
3. `M20` nhầm `U21` thành AI guard và thiếu rào chống prompt injection (`U22`, `INT28`, `OC20`), cũng như chưa chốt ranh giới `Placeholder_Vault` giữa `M20-F07` và `M06`.

## Đề nghị

1. **Chuỗi Khép kín `Download Gateway` (`SEC03`, `INV-24`, `U16`, `SEC-U03`):**
   - **Cấm tuyệt đối** trả về raw Object Storage / S3 presigned URL trực tiếp cho trình duyệt khi tệp thuộc nhóm nhạy cảm (`Assets` PII, hợp đồng, chứng từ tài chính, ghi âm cuộc gọi, hồ sơ nhân sự `ENTITY-L3031`, export `M23-F07/M24-F08`).
   - Mọi request `GET` hoặc `HTTP Range/Resume` qua Gateway bắt buộc vượt qua 3 chốt theo thứ tự **trước khi stream bất kỳ byte nào**:
     1. **`M14` Live ACL & Session Guard (`EvaluateAccessDecision`):** Kiểm `session/token` còn sống, `Users.status = ACTIVE`, `expected_permission_version` (nếu lệch hoặc bị revoke sau khi mở link $\rightarrow$ **`401/403` tức thì, không trả từ CDN/browser cache `SEC-U03`**).
     2. **`M20` Asset Privacy, Quarantine & Hold Gate:** Kiểm `Assets.scan_status = CLEAN` (chặn `PENDING/INFECTED`), kiểm chưa bị xóa theo `Deletion_Ledger`, kiểm `RESTRICTED_LEGAL_HOLD` (`M20-F06`), và kiểm quy tắc tệp nhân sự `6.8` (`ENTITY-L3031`: ẩn tệp lương/CCCD khỏi vai trò không có thẩm quyền HR/Audit).
     3. **`M23-F07` Watermark & Audit Log:** Với tệp Export/bản sao nhạy cảm, kiểm `download_expires_at` chưa quá hạn, đính header `Cache-Control: no-store`, phát `AssetDownloaded` vào `Audit_Logs` (`M23-F06`).
2. **Zero-Trust `Remote Fetch` & Giới hạn Tệp (`SEC04`, `3.12.11 L1404–1409`, `OC13`, `OC14`, `INT24`):**
   - Chỉ gọi qua **Egress Sandbox Proxy** đọc domain trong allowlist đã verify của `Channel_Connections` (không lấy URL tự do từ người dùng).
   - Pin DNS trước kết nối để chặn DNS rebinding; chặn tuyệt đối IPv4/IPv6 loopback, private (`10/8`, `172.16/12`, `192.168/16`), link-local/cloud metadata (`169.254.169.254`); `follow_redirects = false`.
   - Áp `max_bytes = min(product_safe_default, verified_provider_method_limit)` (trong đó `Safe Default` sản phẩm tạm đặt `[OPEN-GAP]` `25 MB` nhưng luôn tôn trọng giới hạn thực tế thấp hơn của kênh, và Email **bắt buộc tính cả ~33% MIME base64 overhead** trước khi gửi/nhận).
   - Stream check chống decompression/zip bomb theo byte thực tế đọc ra; mọi tệp tải về đi qua Antivirus/Malware Quarantine (`Quarantined_Events` / `Remote_Fetch_Logs`) trước khi gắn `Assets`.
   - Email inbound/outbound HTML: strip script/dangerous tags & invisible tracking pixels trước khi render UI (`OC13`, `INT24`).
3. **`AI Data Gateway` & `Placeholder_Vault` (`M20-F07` $\leftrightarrow$ `M06`, `FR13`, `U22`, `INT28`, `OC20`):**
   - **Cưỡng chế điểm chặn ở tầng Gateway (`M20-F07` Proxy trước LLM SDK của `M06`):** `M06` không được gọi trực tiếp API nhà cung cấp LLM mà không đi qua `EvaluateVendorAndAiTransfer` (`C20`).
   - **Quy tắc chống Bypass & Prompt Injection (`U22`, `INT28`, `OC20`, `Master L744`):**
     - Trước khi truy xuất RAG/Context cho AI: gọi `M14.CompileScopeFilter` (`C14`) để đảm bảo chỉ lấy dữ liệu đúng `workspace_id` và quyền hiện tại của `actor_id` (`OC20`).
     - Chặn cứng các trường nhạy cảm (`prohibited_data_classes`: CCCD, số tài khoản ngân hàng, token, **`HRM_PAYROLL` / dữ liệu HR `6.8` không được index vào AI chung**).
     - Payload văn bản từ khách/tệp đính kèm khi đưa vào prompt phải được đóng khung dữ liệu (*untrusted data fence*) và **Tool Policy của `M06`/`M14` cấm tuyệt đối thực thi tool đột biến quyền, xuất PII hay chuyển tiền từ prompt (`U22`, `INT28`)**; khi feature flag `M06` tắt (`OFF`), tắt sạch mọi tool route (`Feature Flag Closure`).
   - **`Placeholder_Vault`:** Lưu ánh xạ `[PII_<CLASS>_<N>]` $\leftrightarrow$ giá trị gốc đã mã hóa có `actor_id`, `session_correlation_id`, và `expires_at` (`[OPEN-GAP]` Safe Default TTL `<= 24 giờ`); khi `M06` hoặc UI yêu cầu giải mã ngược hiển thị cho người dùng, bắt buộc kiểm tra lại quyền `M14.EvaluateAccessDecision` cho đúng `actor_id` hiện tại (`6.3 L3174`).

## So sánh

- **Để `M06` tự mask PII bằng prompt / regex cục bộ:** Dễ bị prompt injection vượt qua (`U22`), không kiểm tra được `Training Opt-out != ZDR` (`RV17`), và tách rời sổ `Vendor_Data_Flows` của `M20`. Đặt cổng cưỡng chế ở `M20-F07` Gateway bảo vệ thống nhất mọi nhà cung cấp AI/Vendor.

## Hệ quả và điều kiện thay đổi

- Bổ sung tường minh `SEC03`, `SEC-U03`, `U22`, `INT28`, `OC20`, `ENTITY-L2783` (`Assets` integration), `ENTITY-L3031` (`EmployeeDocument` gate) vào [M20](../../02-specs/modules/M20-PRIVACY-CONSENT-RETENTION.md) và [C20](../../02-specs/contracts/M20-SUPPRESSION-PRIVACY-GATE.md).
- Đồng bộ kiểm tra `permission_version` tại `Download Gateway` sang [M14](../../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md) và [M22](../../02-specs/modules/M22-HUMAN-RESOURCES.md) (ghi chú trỏ `Download Gateway SEC03` dùng chung `M14 ACL + M20 Privacy Gate`).
