#### G.6.18 Bản vá hai Minor

**MN01 — Thay đích FK `PipelineStages` của `Deals.stage_id` tại Mục5.5 thành `Pipeline_Stages`, thống nhất đúng tên bảng tại5.13.** Khi xuất physical schema sử dụng mapping duy nhất, không tạo hai bảng/alias không được công bố. `CommissionPolicies` đã được xử lý riêng ở DB01, không đếm lại thành lỗi mới.

**Thay câu đầu đoạn giải thích A.3 bằng:**

Bảng A.3–A.4 ghi lịch sử kế thừa tài liệu nguồn. Phạm vi/field/giai đoạn áp dụng lấy từ phần đặc tả hiện hành Chương3/5/9 và các CR đã được chấp thuận; nội dung lịch sử không tự ghi đè baseline. A.5 mô tả phần bổ sung tại vòng hợp nhất ban đầu; số FR/UC hiện hành là40/22, không dùng con số16 luồng trong đoạn lịch sử để cắt phạm vi.

**MN02 — Thay dòng U08 tại Mục9.5 bằng:**

| U08 | UC06 | Won; điều khoản bắt buộc ứng trước; chưa đủ cọc và không có approved credit/start exception | Order có thể tạo; Paid không bật; kickoff pending. Nhánh approved credit/ngoại lệ còn hiệu lực chỉ mở đúng công việc được duyệt, không tự cho chi media. | P0 theo capability |

#### G.6.19 Bàn giao kỹ sư/QA và phương án thực hiện

Thực hiện theo các bước phụ thuộc, chưa gán ngày cam kết khi chưa biết đội triển khai:

1. Chốt release profile và owner policy theo WF04/A.6. Pilot một nguồn/một kênh; loại công việc P1/P2 chưa có business case khỏi cam kết90ngày. Các guard tiền/quyền/consent áp dụng từ ngày đầu của capability tương ứng.
2. Sửa source-of-truth đúng mục theo patch đã chấp thuận; BA kiểm FR→UC→schema/API→RBAC→test và loại alias. WF01/WF03/WF05 chốt trước conversion; DB01/DB04 trước schema tài chính; DB02/DB03 trước hoàn tiền/khóa kỳ; SEC01–06 trước mở luồng bị ảnh hưởng.
3. Xuất dictionary/DDL/OpenAPI versioned của lát cắt đã chọn. Mỗi FK/type/status/unique key có mapping hoặc lý do N/A. Nếu dùng CRM/ERP/ESP native thì ghi field/API/config tương đương và chứng minh bằng PoC, không tạo bảng trùng chỉ để giống tên đặc tả.
4. QA biến WF-U01–05, FA01–06 và SEC-U01–06 thành17 ca bổ sung có fixtures/steps/expected cụ thể, cộng bộ U/OC/INT/CEO/CMO/CX/RV áp dụng. Đây là17 nhóm ca thiết kế, phải tách nhiều test thực khi có nhiều cạnh/race; chưa được tính là17 bài test đã chạy. Với race dùng ít nhất hai connection/session thật và điều khiển thứ tự commit; với connector dùng sandbox/fixtures rồi account được ủy quyền.
5. Gate nghiệm thu ghi build/schema/policy/provider version, người chạy, actual/evidence và defect. Sửa Major ảnh hưởng capability trước ký; test không áp dụng ghi evidence feature-off. Restore phải đối soát tiền và tái áp suppression trước outbound. Triển khai pilot rồi đo nhập liệu/SLA/chi phí trước mở45 tài khoản/hai chi nhánh.

**Vì sao đây là phương án phù hợp dữ kiện hiện có:** lưu lượng100 lead/tháng chưa biện minh cho hạ tầng nhiều dịch vụ hoặc AI dự báo; 50 khách/tháng chưa rõ nghĩa nên không suy conversion50%. Các patch bổ sung ranh giới giao dịch/quyền và semantics cần thiết để không sai tiền/lộ dữ liệu; chúng có thể là cấu hình, quan hệ native và command trong một modular monolith. Không cần15 dịch vụ hay15 phân hệ mới. Mỗi rule có owner, nguồn vào, kết quả ra, quan hệ với chức năng khác và test, thay việc đếm số bảng/số màn hình.

Phương án sản phẩm cụ thể vẫn là quyết định sau PoC cùng fixture và báo giá36tháng. Kiến trúc cấu hình/hybrid nhẹ là khuyến nghị có điều kiện; chưa có căn cứ gọi một hãng là tối ưu tuyệt đối. Các dòng chi phí ở Chương10 vẫn là giả định, không trở thành báo giá sau audit.

**Trạng thái cuối vòng kiểm định:** đã đọc/đối chiếu tài liệu và nguồn, đã viết đủ patch cho15 Major cùng hai Minor, đã kiểm cấu trúc tệp và phản ví dụ số học. Chưa áp toàn bộ patch vào phần thân, chưa chốt các policy thuộc chủ nghiệp vụ, chưa chạy phần mềm/DDL/provider/UAT. Vì vậy baseline freeze và production sign-off vẫn chưa được cấp. Không có điểm100/100 hoặc cam kết “copy-paste là an toàn100%”.

