<a id="phu-luc-f"></a>

## PHỤ LỤC F CÁC THAY ĐỔI ĐÃ HỢP NHẤT TRONG ĐẶC TẢ BA1.6

Đây là nhật ký thay đổi đã áp dụng vào phần thân, không phải danh sách patch để người dùng tự dán. Snapshot1.5 giữ báo cáo kiểm định cũ ở `docs/archive/research-2026-10-15/CRM_MASTER_BRD_SRS_HOP_NHAT_v1.5.md`. Bản chính thức hiện hành luôn là tệp Master tại thư mục gốc.

| Thay đổi đã thực hiện | Module và vị trí quy định hiện hành | Ca kiểm chấp nhận |
| --- | --- | --- |
| Bổ sung20 hồ sơ module có chức năng/màn hình/dữ liệu/quyền/ngoại lệ/liên kết | Danh mục3.0 và các khối M01–M20 tại phần nghiệp vụ/tích hợp/quyền | Mxx-AC theo từng module; trace FR/UC được giữ |
| Đồng bộ field intake Ticket: queue, request type và triage state; chưa rõ severity vẫn nhận vấn đề | M11;5.8, triage hoàn tất phải đủ severity/impact/urgency | M11-AC và kiểm intake Unknown/Pending có queue |
| WF01 — Lead Unknown được vào queue/SLA; chỉ bắt B2B/B2C trước qualification/convert | M02; UC01/UC03;5.2 | WF-U01 |
| WF02 — Message gắn đúng subject/response episode; reply không dừng mọi SLA | M03/M11;5.17/5.18 | WF-U02 |
| WF03 — Commands, allowed transitions, guard và tác động cho các đối tượng lõi | M02/M07/M08/M09/M10/M11/M16;3.13.5 | WF-U03 |
| WF04 — Release profile và test applicability, tách N/A/Not Run/Deferred/Pass | Mọi module;9.5/9.11 | WF-U04; U19/U23-R/U23-L và nhóm theo profile |
| WF05 — Stable conversion key và logical unique SLA episode | M02/M11;5.5/5.16 | WF-U05 |
| DB01 — Policy pointer tới snapshot có version, không FK sang bảng không định nghĩa | M10;5.5/5.12 | FA01 |
| DB02 — Tách hoàn dư và hoàn allocated; sửa số dư và reservation headroom | M09;3.13.4/UC13/5.18 | FA04/FA05 |
| DB03 — Post và close khóa cùng kỳ; pending không giữ khóa đợi consumer | M09/M10;5.13/5.14 | FA02/FA03 |
| DB04 — Số tiền hữu hạn, currency allowlist/quantum, validate trước cast | M07/M09/M10/M17;5.1 | FA06 |
| SEC01 — Callback OAuth gắn actor/session/provider/account/scope | M19;2.6 | SEC-U01 |
| SEC02 — External account có namespace owner, activate/reconnect chống trùng scope | M19/M03;2.7/5.16 | SEC-U02 |
| SEC03 — Download gateway kiểm quyền hiện tại, thay raw URL cho tệp nhạy cảm | M03/M14/M20;FR37/UC12/5.16/6.2 | SEC-U03/U16 |
| SEC04 — Remote fetch có egress/redirect/IP/credential policy | M19/M03;FR40 | SEC-U04 |
| SEC05 — Email unsubscribe/bounce/complaint và sender activation | M03/M04/M20;FR34/5.18 | SEC-U05 |
| SEC06 — Grant authority và ngăn tự nâng quyền qua role/team/config | M14;5.18/6.1 | SEC-U06 |
| Hai hiệu chỉnh — Pipeline_Stages dùng một tên; U08 nêu đúng cọc/credit exception | M02/M08;5.5/9.5 | Kiểm dictionary/U08 |

**Trạng thái bàn giao:** các sửa đổi trên đã là đặc tả thiết kế hiện hành. Chưa chạy code/DDL/provider/UAT; các điều kiện phê duyệt cấu hình cụ thể vẫn theoA.6. Kỹ sư triển khai field/command/migration và QA thực hiện ca theo release profile; không ghi Pass chỉ vì nội dung đã được viết vào tài liệu.
