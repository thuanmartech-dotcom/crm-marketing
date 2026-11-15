### G.6 PHẦN 6 — PHÁN QUYẾT, SỔ LỖI VÀ BẢN VÁ

#### G.6.1 Điểm đánh giá có tiêu chí

**70/100 cho độ sẵn sàng của tài liệu Master 1.4 để kỹ sư lập trình thống nhất.** Đây là điểm đánh giá chuyên môn theo rubric dưới, không phải “70% module đã đúng”, xác suất thành công hay phần trăm code/test đã hoàn thành. Không dùng điểm này để thay các gate tiền/quyền/consent. Mỗi tiêu chí tối đa5: 0 không có; 1 đề cập; 2 có nguyên tắc nhưng thiếu hợp đồng; 3 có hợp đồng một phần; 4 khá rõ còn điểm phải đồng bộ; 5 rõ/nhất quán/kiểm được ở cấp tài liệu. Rubric là phương pháp của vòng audit, chưa phải chuẩn chấm điểm được doanh nghiệp phê duyệt.

| Trục | Bốn tiêu chí, mỗi tiêu chí tối đa5 | Điểm | Căn cứ chính |
| --- | --- | --- | --- |
| Đồng bộ và truy vết | Rationale/dependency4; FR↔UC4; schema/API3; test applicability3 | 14/20 | 40 FR/22 UC có lý do/liên kết; DB01/WF02/WF04 còn hở |
| Lifecycle và SLA | Phân tách object4; ngoại lệ4; transition3; completion/episode2 | 13/20 | 3.13.4 đã tốt; WF01–03/WF05 chưa đủ hợp đồng |
| Dữ liệu và tài chính | Receipt/invoice4; components/reversal4; close concurrency3; numeric domain3 | 14/20 | 5.10–5.18 có nền tốt; DB01–04 |
| Quyền và tích hợp an toàn | Scope/role4; privacy policy4; connection authority3; file/send boundary3 | 14/20 | 6.1/6.3 đã sửa; SEC01–06 còn thiếu/mâu thuẫn |
| MVP và bàn giao dev | Giới hạn nhỏ5; owners/open decisions4; release manifest3; executable contracts3 | 15/20 | 1.6/5.19/A.6 hợp lý; chưa DDL/OpenAPI/profile/PoC |
| **Tổng** | **20 tiêu chí ×5** | **70/100** | **Đánh giá tài liệu, không có runtime pass** |

**Conditional Go:** discovery, prototype/PoC với fixture đã khử PII, chốt policy và phát triển phần có contract đầy đủ. **No-Go:** đóng băng toàn bộ thành “dev không cần hỏi/đoán”, hoặc ký vận hành tiền/dữ liệu thật trước gate. Không tuyên bố tất cả lỗi đã hết sau khi copy-paste. Bản vá phải được áp vào đúng mục, đồng bộ schema/API/test và kiểm thực thi; nội dung chính sách mới vẫn cần chủ nghiệp vụ quyết định theo A.6.

#### G.6.2 Sổ lỗi và thứ tự khắc phục

15 Major dưới là các khoảng trống/mâu thuẫn của **đặc tả**, không phải15 bug đã tái hiện trên sản phẩm. Chưa xác định Blocker runtime vì không có ứng dụng chạy; điều đó không làm mất No-Go cho baseline freeze của các phần bị ảnh hưởng. Hai Minor là biên tập/fixture. Các ưu tiên dưới phụ thuộc capability thực sự bật, không bắt xây mọi engine trong pilot.

| ID | Mức | Vị trí snapshot1.4 / mã liên quan | Cột hoặc hợp đồng bị ảnh hưởng | Cần hoàn thành trước / chủ trì | Bản vá |
| --- | --- | --- | --- | --- | --- |
| WF01 | Major | 4.1/4.3/5.2 dòng1301; FR04/UC01/03 | Leads.business_model NN B2B/B2C tại intake | Lead thật vào queue; BA/Sales | G.6.3 |
| WF02 | Major | 3.12.7/3.12.10/5.16/5.17; FR36/39, INT04/CX-U23 | Message→subject/episode response binding | Bật SLA nhiều request/thread; CX/Tech | G.6.4 |
| WF03 | Major | 3.2/3.6/3.7/3.12; 5.2/5.5/5.6/5.8/5.13; 9.11 | status/transition/guard/side effects của các object lõi | Freeze lifecycle/API; BA/domain owners | G.6.5 |
| WF04 | Major | 1.6/5.19/9.5/9.12; U19/U20/U23/CEO-U21 | Release scope/dependency/test applicability | Ký phạm vi và test plan; Product/QA | G.6.6 |
| WF05 | Major | 4.3/5.5/5.16; FR04/05/36 | conversion_key, waiting_episode_key, logical unique | Conversion/SLA cạnh tranh; Tech | G.6.7 |
| DB01 | Major | 5.5 dòng1368; 5.12/5.18; FR17/UC07/13 | commission_policy_id → CommissionPolicies chưa rõ vs Policy_Snapshots | Freeze finance schema; Finance/Tech | G.6.8 |
| DB02 | Major | 3.13.4 dòng944; 4.13 dòng1117–18; 5.18 dòng1601 | Available/reservations; UC13 refund dư/allocated | Bật hoàn tiền; Finance/Tech | G.6.9 |
| DB03 | Major | 5.12/5.13 dòng1517/5.14/6.1; U12/CEO-U23 | Finance_Periods scope, cutoff, post/close lock | Khóa kỳ và post; Finance/Tech | G.6.10 |
| DB04 | Major | 5.1/5.10/5.11/5.12; FR16/17 | numeric finite, quantum/scale, supported currency | Nhập/post số tiền; Tech/Finance | G.6.11 |
| SEC01 | Major | 2.6/2.7/3.12.1/5.16 dòng1539; FR30 | OAuth callback actor/session/provider/account binding | Connector OAuth; Integration/Security | G.6.12 |
| SEC02 | Major | 2.7/5.16 dòng1539/UC17 | External namespace ownership và routing connection | Reconnect/nhiều workspace; Integration/Privacy | G.6.13 |
| SEC03 | Major | FR37/4.12/6.2; U16/INT23 | Presigned URL khác current user ACL | Tệp nhạy cảm; Security | G.6.14 |
| SEC04 | Major | 2.7/FR40/5.16/6.2 | Fetch URL/egress/redirect/IP/credential forwarding | Remote fetch; Security/Integration | G.6.15 |
| SEC05 | Major | FR09/34/40, 6.3; consent/suppression | Unsubscribe/bounce/complaint/sender eligibility | Email marketing; CMO/Privacy/Integration | G.6.16 |
| SEC06 | Major | FR21/5.18/6.1 | Grantor/authority/self-escalation trên Role_Bindings/team/grants | Nhiều user/cấp quyền; owner/Security | G.6.17 |
| MN01 | Minor | 5.5 dòng1357 vs5.13; A.3/A.5/E.6 | PipelineStages alias và mô tả lịch sử/version | Xuất dictionary/biên tập; BA | G.6.18 |
| MN02 | Minor | 9.5 U08 vs FR15/4.6 | Fixture thiếu điều kiện ứng trước/credit | Viết UAT; QA/Finance | G.6.18 |

**Cách sử dụng các bản vá bên dưới:** đây là nội dung ready-to-paste phục vụ quyết định và cập nhật đúng vị trí; **chưa tự áp vào phần thân 1.4**, vì người dùng yêu cầu kiểm định/bản vá và một số transition/scope cần quyết định nghiệp vụ. Master hiện hành chứa cả baseline và báo cáo; phụ lục G không ngầm ghi đè mọi quy tắc cũ. Khi chấp nhận một patch, sửa trực tiếp mục được chỉ rõ, cập nhật CR/test/migration và ghi trạng thái quyết định. Không chỉ append thêm bảng khác rồi coi hết mâu thuẫn. Chưa có runtime testing; không đổi trạng thái ca nghiệm thu thành Pass.

