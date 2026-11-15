# Phân tích phản biện báo cáo kiểm toán CRM và phương án đề xuất

Ngày đánh giá: 15/10/2026. Phạm vi: thẩm định tài liệu và thiết kế, chưa kiểm thử phần mềm chạy thật.

## 1. Kết luận để ra quyết định

**Báo cáo `gemini-code-1792004600780.md` có giá trị phát hiện rủi ro, nhưng chưa đủ chính xác để dùng nguyên văn làm yêu cầu sửa hệ thống.** Một số vấn đề được phát hiện đúng; một số là đặc tả chưa đủ chi tiết, bị diễn đạt thành lỗi chắc chắn; một số phương án sửa có thể gây mất an toàn hoặc làm sai số liệu.

Phương án phù hợp nhất với dữ kiện hiện có: **CRM có sẵn được cấu hình hoặc hybrid nhẹ, triển khai theo lát cắt nghiệp vụ từ tiếp nhận nhu cầu đến thu tiền và bàn giao; chỉ tự xây phần khác biệt đã được chứng minh qua PoC.** Nếu mục tiêu còn là sở hữu sản phẩm phần mềm để kinh doanh, cần đánh giá riêng; lưu lượng vận hành hiện tại chưa đủ để biện minh cho việc tự xây toàn bộ nền tảng.

Nếu quyết định tự xây đã được xác lập bởi mục tiêu khác, kiến trúc modular monolith + PostgreSQL + worker của SRS là nền tảng hợp lý. Không cần thay bằng microservices; cũng không nên gộp dữ liệu chỉ để giảm số bảng.

Giữ thiết kế đích đến trong Master SRS, nhưng tách ra một baseline MVP có từng FR, bảng dữ liệu, màn hình, tích hợp và UAT rõ ràng. Hoãn năng lực chưa cần thay vì xóa vĩnh viễn khỏi tầm nhìn đa ngành.

### Cơ sở đối chiếu

- [Báo cáo cần đánh giá](<D:/AI Agent/CRM/gemini-code-1792004600780.md>), đọc toàn bộ.
- [Master BRD/SRS phiên bản 1.2](<D:/AI Agent/CRM/CRM_MASTER_BRD_SRS_HOP_NHAT.md>), đối chiếu các FR/UC, schema, quyền, KPI, phạm vi và lộ trình liên quan.
- [Bản ghi cập nhật 1.2](<D:/AI Agent/CRM/CRM_CAP_NHAT_V1_2.md>), đối chiếu mục tiêu và giới hạn nghiên cứu.
- Nguồn chính thức về hóa đơn và lao động được dẫn tại các nhận định tương ứng bên dưới.

Các mệnh lệnh “xóa”, “bắt buộc sửa”, “loại bỏ” trong báo cáo được xem là đề xuất cần thẩm định. Không có thay đổi nào được áp dụng vào hai tài liệu gốc trong lần đánh giá này.

Không chấm điểm kiểu 6,5/10 hoặc quy đổi thành “đúng 80%”: chưa có rubric, trọng số, dữ liệu vận hành hay PoC để những con số đó mang ý nghĩa đo lường.

## 2. Những phần báo cáo làm tốt

1. **Tách service, production và media thu hộ** để tính hoa hồng và báo cáo quản trị đúng cơ sở. Tuy nhiên loại dòng hàng không tự quyết định cách ghi nhận doanh thu kế toán; phải theo bản chất hợp đồng và nguồn kế toán có thẩm quyền.
2. **Tách dữ liệu Agency và dữ liệu xử lý cho từng khách hàng**, giữ ranh giới tenant/workspace ở cả truy vấn, tệp, tìm kiếm, tích hợp và xuất dữ liệu.
3. **Tách B2B/B2C**, không tạo công ty giả cho người mua cá nhân; cho phép một contact đại diện nhiều account.
4. **Giữ bằng chứng thanh toán và bút toán đảo**, không lấy ảnh chuyển khoản làm xác nhận tiền; giữ idempotency, outbox và kiểm soát cạnh tranh.
5. **Nhìn thấy rủi ro nhập liệu trùng** giữa CRM, công cụ dự án và tài liệu chiến lược; đúng khi yêu cầu một nơi ghi dữ liệu chính cho mỗi nghiệp vụ.
6. **Bổ sung các tình huống thực tế**: tiền về trước dữ liệu hóa đơn, khách quay lại, chấm dứt hợp đồng sớm, vòng sửa, chờ khách duyệt, chia sẻ hồ sơ giữa Sales/AM và điều chỉnh hoa hồng.

Đây là những nội dung nên chuyển thành quyết định thiết kế và UAT cụ thể.

## 3. Các nhận định cần sửa trước khi sử dụng

### 3.1 Không thể lấy số bảng làm bằng chứng hệ thống quá tải

Báo cáo cộng 11 bảng lõi, khoảng 29 mục mở rộng và 15 bảng omnichannel để suy ra khoảng 55 bảng. Nhưng nhiều dòng mục 5.13 gộp nhiều bảng, đồng thời có tên xuất hiện lại ở 5.16. Đây chưa phải phép đếm các bảng vật lý duy nhất.

Quan trọng hơn, mục 1.6 của SRS đã giới hạn MVP; đoạn đầu 5.13 nói rõ không phải mọi phần mở rộng đều bắt buộc cho pilot; mục 9.1 không cam kết xây toàn bộ trong 90 ngày. FR10 đã để loyalty ở P2. Vì vậy, nhận định “phải xây hết hơn 55 bảng ngay” không phản ánh đúng tài liệu.

**Khoảng trống thật:** thiếu bản đồ triển khai đủ chi tiết giữa FR → bảng → API → UAT → giai đoạn; vẫn có năng lực strategy/IMC gọn trong lịch 90 ngày cần làm rõ. Chi phí phụ thuộc workflow, tích hợp, quyền và vận hành nhiều hơn số bảng đơn thuần.

**Quyết định:** giảm phạm vi chức năng và nhập liệu, không đặt chỉ tiêu “xóa ít nhất 20 bảng” hoặc hứa “giảm ít nhất 40% chi phí” khi chưa ước lượng công việc.

### 3.2 Một số nội dung bị báo cáo là “không có” thực tế đã có

| Nhận định trong báo cáo | Nội dung SRS gốc | Kết luận chính xác hơn |
| --- | --- | --- |
| Undo merge chỉ dựa snapshot, bỏ quên dữ liệu sau merge | Mục 3.12 yêu cầu xử lý cả thay đổi phát sinh sau merge | Nguyên tắc đã có; schema/provenance và thuật toán chưa đủ cụ thể |
| Buying group phải đầy đủ ngay khi qualified | FR04 cho phép người duyệt Unknown | UC03 cần làm rõ mức tối thiểu; chưa có căn cứ nói bắt buộc đầy đủ approver/billing |
| Tất cả gói dịch vụ phải theo quy trình chiến lược 9 tầng cứng | FR22 cho phép form gọn và scope_template; không ép gói thiết kế đơn lẻ nghiên cứu đầy đủ | Cần giảm nhập lại và định nghĩa gate theo gói, không phủ nhận toàn bộ thiết kế |
| Đổi owner chắc chắn làm Sales hoặc AM mất quyền | Mục 6.1 có team và hồ sơ chia sẻ có hạn; FR21 cho phép chia sẻ account | Thiếu mô hình chia sẻ cụ thể, chưa phải chứng minh mất quyền chắc chắn |
| Time entry đồng nghĩa phải xây lại PMS/HRM | FR25 yêu cầu một nguồn ghi task khi tích hợp; FR27 loại payroll/chấm công nhân sự khỏi Customer 360 | Cần quyết định ai sở hữu task và chi phí, không bắt buộc bỏ dữ liệu chi phí delivery |
| Deal Lost làm mất lịch sử báo giá | Không có quy tắc xóa quote khi Lost | Cần bổ sung re-engagement; trạng thái Lost tự nó không làm mất lịch sử |

Các trích dẫn `[cite: 1]` lặp lại không đủ truy vết từng khẳng định, đặc biệt những khẳng định về thị trường hoặc pháp luật. Nên thay bằng mục/đoạn cụ thể và nguồn bên ngoài phù hợp.

### 3.3 Lập luận về hóa đơn khi nhận tiền trước có sai sót quan trọng

Báo cáo nói “90% trường hợp” chưa xuất hóa đơn cho khoản cọc và hóa đơn chỉ xuất khi nghiệm thu “theo quy định thuế”. Tỷ lệ 90% không có bằng chứng; quy tắc hóa đơn không thể suy ra từ tên gọi “đặt cọc”.

Khoản 2 Điều 9 được sửa tại Nghị định 70/2025/NĐ-CP quy định nguyên tắc: dịch vụ thu tiền trước hoặc trong khi cung cấp thì lập hóa đơn tại thời điểm thu tiền, với ngoại lệ đặt cọc/tạm ứng cho một danh mục dịch vụ cụ thể. Không thể mặc định mọi hợp đồng marketing thuộc ngoại lệ. Cần phân loại bản chất khoản thu và dịch vụ, đối chiếu văn bản áp dụng khi triển khai. [Nguồn Chính phủ](https://xaydungchinhsach.chinhphu.vn/nghi-dinh-70-2025-nd-cp-sua-doi-bo-sung-quy-dinh-ve-hoa-don-chung-tu-11925032321512617.htm).

**Phát hiện kỹ thuật vẫn có giá trị:** tiền có thể đã về nhưng dữ liệu hóa đơn chưa đồng bộ, hoặc giao dịch đang được phân loại. CRM phải lưu được tiền thật và khoản chưa phân bổ, đồng thời theo dõi nghĩa vụ hóa đơn. Không để hệ thống coi dữ liệu ERP đến chậm là chưa thu tiền.

Chỉ đổi `invoice_line_id` thành nullable là chưa đủ; phải có đích phân bổ và quy tắc chống đếm tiền hai lần. Chi tiết ở mục 5.

### 3.4 Không dừng tất cả SLA vì có một hoạt động trên cùng contact

Một người có thể đại diện hai công ty, có nhiều nhu cầu hoặc nhiều ticket. Cuộc gọi về báo giá A không hoàn thành SLA khiếu nại B. Cuộc gọi không nghe máy chỉ chứng minh nỗ lực, không chứng minh đã phản hồi thành công.

**Quyết định:** có một cơ chế tính SLA dùng chung, nhưng giữ nhiều nghĩa vụ độc lập. Mỗi sự kiện chỉ hoàn thành episode mà nó liên quan, theo policy có phiên bản. Liên kết bằng lead/conversation/ticket/request và mục đích công việc; `contact_id` chỉ là điều kiện phụ.

Không lấy ngưỡng đổ chuông 15 giây làm bằng chứng đủ: busy/rejected có thể kết thúc sớm hợp lệ; ringing dài vẫn có thể là thao tác đối phó. Dùng outcome từ provider và quy tắc đánh giá nỗ lực, tách biệt với kết nối thành công.

### 3.5 Sticky assignment không được đứng trước ranh giới truy cập

Hash điện thoại trùng có thể do hotline dùng chung hoặc thông tin chưa xác minh. Nó là tín hiệu nghi trùng, không phải danh tính đã được xác nhận. SRS 3.12 và 5.3 đã nêu rõ điều này.

**Thứ tự đề xuất:** lọc tenant/workspace và quyền → phạm vi phục vụ/kỹ năng bắt buộc → ưu tiên owner hợp lệ → kiểm sự sẵn sàng hoặc chuyển người trực dự phòng → cân bằng tải trong nhóm đủ điều kiện. Các giới hạn capacity có thể phân thành ngưỡng mềm/cứng theo policy; không gạt hết bằng “sticky số 1”.

Hai hồ sơ nghi trùng trong cùng phạm vi được gắn cảnh báo và điều phối một người xử lý nếu người đó có quyền với cả hai. Không tự chia sẻ nội dung, gộp danh tính hoặc trao quyền chỉ vì trùng số.

### 3.6 Thu gọn IMC không có nghĩa bỏ kiểm soát phê duyệt

CRM không cần bắt nhập lại toàn bộ slide chiến lược. Nhưng một URL tài liệu có thể bị sửa sau phê duyệt, nên URL đơn lẻ không đủ làm bằng chứng.

Giữ brief, phạm vi, ngân sách, phiên bản tài liệu/asset, người duyệt, thời điểm và nội dung được duyệt. Chi tiết message house, nghiên cứu và nội dung làm ở công cụ chuyên môn. Campaign launch chỉ kiểm các điều kiện thực sự áp dụng theo gói; thay đổi trong phạm vi tối ưu đã duyệt không cần xin lại từng lần.

### 3.7 Trạng thái vận hành không được thay thế sự thật tài chính

- `Order Completed` không có nghĩa đã thanh toán đủ.
- `Terminated` không có nghĩa công nợ đã được giải quyết.
- Tổng giá trị order không tự trở thành doanh thu kế toán.
- `Lost` không được xóa lịch sử quote; `OnHold` không được dùng để làm đẹp win rate.
- Write-off khoản thiếu không phải tiền mặt thực thu và không tự là phí ngân hàng.

Giữ riêng trạng thái hợp đồng, giao hàng, lập hóa đơn, đối soát và thanh toán. Báo cáo phải phân biệt giá trị ký, giá trị đang có hiệu lực, giá trị đã nghiệm thu, đã lập hóa đơn, thực thu và doanh thu được kế toán ghi nhận.

## 4. Đối chiếu toàn bộ 15 mục trong Action Plan của báo cáo

Mức ưu tiên dưới đây là ưu tiên thiết kế/triển khai đề xuất, không phải kết luận đã có lỗi production.

| STT báo cáo | Đánh giá | Cách xử lý đề xuất |
| --- | --- | --- |
| 1. Tiền trước hóa đơn | Đúng về khoảng trống mô hình, sai/thiếu căn cứ về thuế và “90%” | P0: ghi nhận cash receipt độc lập; phân bổ vào nghĩa vụ/kỳ/dòng hợp đồng; liên kết hóa đơn riêng, theo dõi hóa đơn cần xử lý |
| 2. Schema trùng | Xác nhận được việc đặc tả chồng lấn ở 5.13/5.16; chưa phải lỗi migration đã chạy | P0: một từ điển dữ liệu chuẩn, mapping tên cũ→mới; bảo toàn trường/constraint cần thiết thay vì xóa mù |
| 3. Contact và consent | Có bất nhất ERD/nullability; không tự suy ra mọi intake đều crash | P0: lưu sự kiện và bằng chứng bền vững trước; tạo contact tạm trước khi insert consent cần FK, trong transaction; hoặc dùng mô hình subject riêng nếu thực sự cần |
| 4. Phạm vi quá rộng | Đúng về nguy cơ, quá lời về bắt buộc xây toàn bộ | P0: chốt baseline MVP; hoãn loyalty/HR scorecard/experiment/IMC chi tiết. Không xóa cả FR10 vì còn referral |
| 5. SLA | Cần làm rõ, nhưng sửa “dừng cả hai theo contact” không chấp nhận | P0: tách nhận việc, nỗ lực đầu, phản hồi người thật và giải quyết; completion theo episode/ngữ cảnh |
| 6. Identity và routing | Có nguy cơ liên hệ trùng; hash không đủ xác minh | P0: hard scope trước, continuity sau; cảnh báo nghi trùng và điều phối có quyền; có người dự phòng |
| 7. Vòng sửa và chờ duyệt | Hợp lý nhưng điều kiện chặn quá cứng | P0 cho delivery: đếm vòng phản hồi hợp lệ; lỗi do agency không tự tiêu hao quota sửa của khách; giữ lịch cam kết và lịch dự kiến riêng |
| 8. Ngoại lệ tạm ứng | Hợp lý về thời hạn và giới hạn rủi ro | P0: người duyệt, hạn, mức exposure, việc được phép. Chặn chi tiêu mới theo rule; không tự dừng mọi dịch vụ đang chạy nếu chưa có điều khoản phù hợp |
| 9. Quyền chia sẻ/chi nhánh | Đúng về cần cụ thể hóa; giải pháp blanket NOT NULL chưa tốt | P0: membership có vai trò, scope, hiệu lực; account dùng chung được chia sẻ có chủ ý; branch bắt buộc ở giao dịch được phân nhánh, không ép mọi dữ liệu dùng chung |
| 10. Lead/deal/deferred | Tách Lead/Deal đúng; clone mọi deal để làm ngắn sales cycle là sai mục tiêu | P0: lịch sử trạng thái; OnHold có lý do/hẹn lại; giữ tổng thời gian và active time; nhu cầu mới mới tạo deal mới có lineage |
| 11. Unmatched/dung sai | Cần có quy trình; tự coi thiếu tiền là bank fee không đúng | P0: Sales đề xuất, kế toán xác nhận; thiếu tiền/fee/write-off có loại và bằng chứng riêng; thiếu cơ sở phân bổ thì pending |
| 12. Masking | Hợp lý khi giảm ma sát cho người có trách nhiệm | P0: quyền đọc liên hệ theo assignment/mục đích; còn hiệu lực, đúng scope; audit/rate-limit bổ sung, không thay quyền backend |
| 13. Undo merge | Rủi ro đúng nhưng SRS đã nêu nguyên tắc xử lý phát sinh sau merge | P0 nếu bật merge: provenance, preview tác động, trạng thái kiểm tra; dữ liệu tài chính đã chốt không tự chuyển theo contact |
| 14. Renewal | Cần cấu hình theo hợp đồng; lỗi “vừa ký là nhắc” chưa chắc vì chưa biết cách trigger | P1: sinh lịch tại các mốc tương lai phù hợp; không catch-up hàng loạt mốc trước ngày ký; khóa chống trùng theo hợp đồng/kỳ/mốc |
| 15. Ticket/CSAT | Hướng cải thiện tốt, không áp ngưỡng cứng toàn bộ | P1 cho tối ưu; P0 cho ticket thiết yếu: priority riêng, timeout có ngoại lệ, không tự đóng sự cố nghiêm trọng; survey có cooldown và ghi lý do không gửi |

### Các điểm phụ trong báo cáo cũng cần chỉnh

- **SLA B2B 30 phút hay 60 phút:** phần đầu đề xuất 30, phần quy trình và bảng tổng hợp dùng 60. Đây là mâu thuẫn nội bộ. Cả hai chỉ là giả thuyết pilot, không phải chuẩn bắt buộc.
- **Gia hạn 60% hay 70% thời lượng:** nội dung chi tiết và bảng tổng hợp không thống nhất; điều kiện 60% còn có thể chặn mốc 45 ngày của hợp đồng 90 ngày. Nên dùng policy tạo mốc cụ thể.
- **Re-inquiry sau 14 ngày:** ngưỡng tùy ý không thể thay việc xác định nhu cầu mới/cũ. Tin hỗ trợ sau mua không được tự thành lead mới; không gắn toàn bộ hoạt động đang mở vào deal vừa tạo.
- **Auto-approve khi không giảm giá:** giá chuẩn vẫn có thể đi kèm điều khoản thanh toán, số vòng sửa, quyền sở hữu, giới hạn trách nhiệm hoặc scope bất lợi. Chỉ auto-approve khi toàn bộ điều kiện trong hạn mức, không chỉ discount = 0.
- **Sửa lịch thanh toán “không ảnh hưởng margin”:** vẫn có thể tăng nhu cầu vốn và rủi ro tín dụng. Approval cần xác định các chiều bị tác động, không chỉ margin.
- **Tự cộng ngày khách chậm vào Project.end_date:** có thể phá lịch sự kiện cố định; các công việc chờ song song không được cộng trùng. Lưu waiting intervals và đề xuất rebaseline có duyệt khi thay đổi cam kết.
- **Bắt decision maker trước Negotiation:** quá cứng với khách không công khai người quyết định. Cho bằng chứng/ngoại lệ, yêu cầu xác thực thẩm quyền ký đúng lúc ký hợp đồng.
- **Cho CMO nghe toàn bộ recording để kiểm lead:** recording/chat cũng có dữ liệu cá nhân. Cấp quyền kiểm tra mẫu có mục đích và giới hạn; ưu tiên transcript đã che thông tin không cần thiết. Không suy quyền nghe từ chức danh.
- **Tách bonus chất lượng:** hợp lý. Nhưng không biến `PENALTY_ADJUSTMENT` thành phạt tiền/cắt lương tự động. Điều 127 Bộ luật Lao động 2019 cấm dùng phạt tiền/cắt lương thay xử lý kỷ luật; cần phân biệt điều kiện thưởng, clawback hợp lệ và kỷ luật. [Văn bản chính thức](https://datafiles.chinhphu.vn/cpp/files/vbpq/2019/12/45.signed.pdf).

## 5. Thiết kế nghiệp vụ đề xuất

### 5.1 Tiền, phân bổ và hoa hồng

Luồng đề xuất:

`Giao dịch xác thực → ghi nhận tiền → xác định khách/hợp đồng → phân bổ vào nghĩa vụ → đối chiếu hóa đơn → preview hoa hồng → duyệt đủ điều kiện → chi trả`.

**Trạng thái xác thực tiền và trạng thái khớp nghiệp vụ phải riêng.** Giao dịch ngân hàng đã xác thực nhưng chưa biết khách vẫn là tiền có thật, ở trạng thái chưa khớp; không nên mất thông tin xác thực chỉ vì `Payments.status = Unmatched`.

Các đối tượng cần có, hoặc ánh xạ sang năng lực tương đương của phần mềm được chọn:

- `Order_Lines`: loại dòng, giá trị net/tax/gross, tiền tệ, version đã duyệt; không sao chép động từ bảng giá đang thay đổi.
- `Payment_Schedules` và chi tiết kỳ: hạn, số tiền, thành phần dịch vụ/media/thuế được thu; tổng phải khớp nghĩa vụ còn hiệu lực.
- `Payments`: nguồn xác thực, tài khoản nhận, transaction ID, số tiền, chiều thu/hoàn và liên kết gốc.
- `Payment_Allocations`: đích phân bổ rõ ràng đến nghĩa vụ/dòng kỳ; ghi tăng/đảo. Không cho bản ghi không có đích chỉ vì invoice nullable.
- Liên kết đối chiếu giữa phần đã phân bổ và `Invoice_Lines`: hỗ trợ phân bổ một phần; bổ sung liên kết không tạo thêm thực thu hoặc hoa hồng. Nếu dùng lịch sử bất biến, thêm sự kiện liên kết thay vì sửa dòng tiền cũ.
- `Commission_Entries`: tham chiếu allocation, base đủ điều kiện, tỷ lệ, người hưởng và phiên bản chính sách. Tách giá trị bút toán bất biến khỏi lịch sử phê duyệt/chi trả.

**Thứ tự phân bổ:** điều khoản/kỳ thanh toán đã duyệt → chỉ định hợp lệ được kế toán xác nhận → quy tắc fallback đã phê duyệt. Khi không đủ cơ sở, pending. Pro-rata là một policy được chọn, không phải mặc định luôn đúng.

Ví dụ minh họa, bỏ qua thuế chỉ để dễ thấy phép tính: hợp đồng 20 triệu service + 80 triệu media, nhận 50 triệu. Nếu policy pro-rata đã duyệt, service thực thu là 10 triệu; rate 5% thì preview hoa hồng 500.000 đồng trước phân chia. Nếu kỳ đầu chỉ thu media, cơ sở service bằng 0. Khi có thuế thực tế, phải phân bổ theo thành phần net/tax của nghĩa vụ, không dùng tỷ lệ minh họa này trên tổng tiền gồm thuế một cách máy móc.

Các bất biến bắt buộc:

1. Không phân bổ quá số dư khả dụng; không phân bổ vượt nghĩa vụ hợp lệ; khóa và kiểm tra trong transaction.
2. Không phân bổ chéo tenant/workspace hoặc tiền tệ không qua nghiệp vụ được phê duyệt.
3. Reversal liên kết chính xác phần gốc; không đảo/hoàn cùng một phần nhiều lần.
4. Credit dư chưa phân bổ không tự tính service revenue hay commission.
5. Một payment được nhập từ sao kê rồi xuất hiện ở API vẫn chỉ là một khoản thu: cần cơ chế đối chiếu xuyên nguồn, không chỉ unique theo connector.
6. Write-off không tạo cash receipt; base “thực thu” không tăng bằng phần xóa nợ. Bank fee có chứng từ phải xử lý theo bản chất khác.
7. Kỳ đã khóa không sửa số cũ; điều chỉnh vào kỳ cho phép và giữ truy vết.
8. Preview không phải quyền hưởng đã chốt. Điều kiện chất lượng chưa có thì pending phần liên quan hoặc tách bonus theo policy, không tự suy chất lượng bằng 1 để chi ngay.

### 5.2 Danh tính, consent và phân vùng

**Khoảng trống quan trọng báo cáo bỏ sót:** mục 5.1 dùng `client_workspace_id` nullable cho dữ liệu agency, trong khi 5.16 dùng `workspace_id NOT NULL`. Chưa có ánh xạ thống nhất cho FK và policy giữa hai miền. Đây là điểm cần giải quyết trước migration.

Đề xuất cho triển khai mới: `workspace_id NOT NULL` cho dữ liệu có phạm vi; mỗi tenant có workspace loại `AGENCY`, các workspace loại `CLIENT` có `client_account_id`. Những danh mục thực sự dùng chung cấp tenant phải được định nghĩa riêng. Không dùng NULL với nhiều nghĩa “dùng chung/chưa phân loại/không áp dụng”.

Đây là quyết định thiết kế đề xuất, không phải khẳng định schema nullable luôn sai. Nếu giữ schema hiện tại thì phải quy định mapping và các ràng buộc NULL rõ ràng; không chạy hai mô hình scope song song thiếu cầu nối.

Với MVP, intake hợp lệ cần consent/contact có thể tạo **contact tạm** trong cùng transaction trước khi lưu `Consent_Logs`. Tách trạng thái xác minh `identity_status` khỏi `lifecycle_stage`: “chưa xác minh” khác “lead/customer”. Event thô được giữ bền vững, có retention và quyền truy cập; sự kiện lỗi vào hàng chờ xử lý. Không ép tạo contact cho mọi webhook status, spam hay dữ liệu chưa xác định tenant.

Merge nên giữ identity và nguồn bất biến, thêm mapping canonical có lịch sử. Unmerge có preview dữ liệu trước/sau, phân loại phần đủ bằng chứng và phần cần xét thủ công; không tự thay người mua trên hợp đồng đã ký hoặc chủ thể chứng từ tài chính. Trước outbound phải kiểm quyền/consent hiện hành; không lấy hợp consent nhiều hồ sơ để mở rộng quyền gửi.

### 5.3 Routing và SLA

| Đồng hồ | Sự kiện có thể hoàn thành | Không được coi là hoàn thành |
| --- | --- | --- |
| Nhận việc | Claim có quyền hoặc hành động xử lý hợp lệ theo policy | Chỉ nhìn danh sách |
| Nỗ lực tiếp cận đầu | Call outcome được xác thực; gửi phù hợp qua kênh được phép | Ghi chú “đã gọi” không có chứng cứ |
| Phản hồi người thật | Phản hồi hữu ích cho yêu cầu cụ thể; cuộc gọi kết nối đúng yêu cầu nếu policy chấp nhận | Autoack, NoAnswer, cuộc gọi cho nhu cầu khác |
| Giải quyết | Đủ kết quả/bằng chứng theo loại yêu cầu | Chỉ chuyển assignee, gửi lời chào |

Có một thư viện/service SLA dùng lịch làm việc và phiên bản policy; các trường deadline trên Lead/Inbox là projection hoặc có trách nhiệm rõ, không hai nơi tự sửa deadline độc lập. Reassignment không làm mới thời điểm bắt đầu nghĩa vụ khách hàng; timer nhận việc của assignee mới có thể là episode khác.

Ngưỡng pilot đề xuất, chưa phải cam kết SLA: inquiry có người trực được phản hồi người thật sớm trong ca; B2B tách xác nhận nhu cầu/hẹn tư vấn khỏi buổi discovery sâu. Có thể thử mục tiêu 15–30 phút cho phản hồi đầu ở kênh trực và 2–4 giờ làm việc cho bước tư vấn phù hợp; đo baseline rồi điều chỉnh. Nếu cá nhân đang họp, dùng lịch khả dụng, nhắc việc và người dự phòng khi có; không giả lập đội trực bằng vòng thu hồi.

### 5.4 Pipeline và lịch sử

- Lead quản lý một nhu cầu/đợt tiếp nhận: New → Assigned → Contacting → Qualified → Converted; có Nurture, Dormant, Disqualified với lý do và điều kiện thoát rõ.
- Deal B2B: Discovery → Proposal → Negotiation → Won/Lost. Tình trạng OnHold là thuộc tính/trạng thái có lý do, review date và quy tắc forecast; không xóa thời gian trước đó.
- Khách quay lại cùng nhu cầu được nối đúng lịch sử; nhu cầu mới tạo lead/deal mới với `previous_id` hoặc lineage. Không dùng ngày thứ 14 làm ranh giới duy nhất.
- Chỉ gắn những activity/conversation thuộc nhu cầu đó vào deal. Một contact nhiều vai trò không làm toàn bộ hội thoại thuộc cùng deal.
- Báo cáo giữ số lead episode và số contact duy nhất riêng; đo sales cycle tổng, active time và hold time. Nếu mở deal mới, vẫn giữ thời gian toàn hành trình qua lineage, tránh làm đẹp chỉ số bằng clone.
- Kiểm trùng cơ hội phải có scope quyền, khách B2B hoặc buyer B2C, nhu cầu/campaign/dịch vụ. Cảnh báo mềm cho nhu cầu giống nhau; không áp unique “một account chỉ có một deal mở”.

### 5.5 Hợp đồng, triển khai và nghiệm thu

Giữ quote revision và approval snapshot. Hợp đồng khung có thể có SOW/phụ lục, order và kỳ dịch vụ; quote bổ sung có thể gắn hợp đồng gốc. Các liên kết phải tường minh và cùng scope.

Loại văn bản (`MSA`, hợp đồng, phụ lục) và mô hình dịch vụ (`RETAINER`, `ONE_OFF`) là hai thuộc tính khác nhau. Không dùng cùng `contract_type` cho cả hai như các đoạn đề xuất của báo cáo.

Ngày ký/chấp thuận không tự đủ điều kiện Active trong mọi trường hợp: vẫn cần thẩm quyền người ký và điều kiện hiệu lực. `Won`, hiệu lực hợp đồng, kickoff, được phép chi media và đã thu đủ tiền là các mốc khác nhau.

MVP chỉ cần deliverable, phiên bản asset, phản hồi, acceptance, change request và milestone. Các task sản xuất chi tiết ở công cụ dự án; CRM nhận trạng thái/mốc hoặc cập nhật thủ công có bằng chứng. Muốn đo lợi nhuận phải có chi phí trực tiếp đáng tin cậy từ kế toán/PMS hoặc tổng hợp có kiểm tra; bỏ time entry không có nghĩa được bỏ toàn bộ cost.

Quota sửa lấy từ SOW đã duyệt, không mặc định mọi hợp đồng là hai vòng. Một vòng là tập phản hồi được chốt, không phải một comment. Lỗi không đạt SOW của agency phải xử lý theo nghĩa vụ khắc phục; không tự ép khách trả thêm vì đã hết quota đổi ý.

Khi chờ khách, lưu khoảng chờ và trách nhiệm; có deadline nội bộ, lịch dự kiến và lịch cam kết riêng. Khi thanh lý sớm, chốt phần đã làm, phần nghĩa vụ hủy/điều chỉnh, phí chấm dứt nếu có và công nợ còn lại; ERP xử lý chứng từ cần điều chỉnh. Chỉ ghi “settled” khi thực sự hoàn tất nghĩa vụ thanh toán.

### 5.6 Quyền truy cập và dùng chung hồ sơ

Một người phụ trách chính vẫn cần tồn tại. Bổ sung team membership hoặc grant theo Account/Project/Deal/Contact, có vai trò và hạn hiệu lực. Không chỉ có `Account_Team_Members` vì B2C có thể không có Account.

Tư cách thành viên không mặc nhiên được đọc mọi ghi âm, hợp đồng, tài chính hoặc workspace người tiêu dùng của khách. Kết quả quyền là tổng hợp vai trò + phạm vi + mục đích + độ nhạy cảm, với Deny thắng Allow theo SRS.

Tạo chi nhánh mặc định cho giao dịch ngay từ đầu là tiện lợi; nhưng Contact/Account dùng chung toàn tổ chức cần chính sách chia sẻ riêng. Account không nhất thiết trùng chi nhánh với tất cả deal. Công nợ theo pháp nhân hạch toán, không chỉ theo branch.

Người được giao liên hệ có thể đọc số/email theo quyền đang hiệu lực mà không nhập lý do lặp lại mỗi 5 phút. Ngoại lệ nhạy cảm mới dùng reveal có TTL/lý do. Chặn export, audit và cảnh báo truy cập bất thường vẫn cần nhưng không thay thế authorization; ngưỡng 30 hồ sơ/giờ phải đo và cấu hình, không coi là chuẩn chống thất thoát.

## 6. Kiến trúc và phạm vi triển khai khuyến nghị

### Ranh giới nguồn dữ liệu chính

| Miền | Nguồn chính | CRM giữ gì |
| --- | --- | --- |
| Khách, nhu cầu, deal, next action | CRM | Hồ sơ và lịch sử có quyền |
| Hợp đồng/SOW/approval | Kho tài liệu và workflow được chỉ định | ID phiên bản, checksum/bản chụp khi phù hợp, người duyệt, liên kết |
| Tiền giao dịch | Ngân hàng/provider hoặc sao kê đã kiểm tra | Khoản thu xác thực, mapping và reconciliation |
| Chứng từ và số liệu kế toán | ERP/kế toán | Bản chiếu có thời điểm đồng bộ, không sửa thay ERP |
| Task delivery | Một PMS hoặc module được chọn | Milestone, deliverable, acceptance, trạng thái và cost tổng hợp |
| Kênh giao tiếp | Tài khoản/kênh được cấp quyền | Thread, identity, evidence và health sync |

### MVP cần làm

Hồ sơ B2B/B2C; lead/deal; activity/next action; quyền và scope; brief; quote/SOW có phiên bản; hợp đồng/kỳ thanh toán; ghi nhận và phân bổ tiền có kiểm tra; commission preview nếu đã có chính sách; handoff/deliverable/acceptance; ticket cơ bản; nhắc gia hạn đơn giản; audit/consent; backup và restore. Một nguồn lead và một kênh giao tiếp trước.

Đối soát có thể thủ công có kiểm soát ở pilot. Không cần tự động hóa hết để đảm bảo đúng tiền. RFM, journey builder tổng quát, loyalty, AI tự hành, chấm điểm nhân sự, time tracking chi tiết, multi-touch và năm connector đồng loạt để sau khi nhu cầu được chứng minh.

### Cách chọn nền tảng

Không đủ dữ kiện để kết luận Odoo, Frappe, EspoCRM hay sản phẩm khác là tốt nhất. Không lặp lại benchmark hoặc tính năng trong tài liệu cũ như kết quả PoC mới. Chọn 2 ứng viên đáp ứng ngân sách sơ bộ rồi chạy cùng dữ liệu ẩn danh và các ca nghiệm thu ở mục 7.

Các điều kiện loại ngay: không cô lập được dữ liệu cần bảo vệ; không giữ lịch sử và xuất dữ liệu đầy đủ; không hỗ trợ/reconcile tiền và điều chỉnh theo mô hình đã chọn; connector chính không được cấp quyền; không có phương án backup/khôi phục phù hợp. Sau các điều kiện đó mới so TCO, thao tác người dùng, khả năng cấu hình và chi phí vận hành.

TCO phải gồm license, tích hợp, triển khai, dữ liệu, đào tạo, support, API usage, backup, nâng cấp và chuyển nhà cung cấp. Bảng giá trong SRS là giả định, không dùng làm báo giá đã xác minh. Nếu nền tảng có sẵn vượt PoC mà không cần nhiều custom, ưu tiên cấu hình. Hybrid chỉ xây phần thiếu; custom toàn bộ cần business case riêng và người chịu trách nhiệm bảo trì.

## 7. Các ca nghiệm thu quyết định chất lượng phương án

| Mã | Tình huống | Kết quả bắt buộc |
| --- | --- | --- |
| T01 | Khách chuyển trước khi dữ liệu hóa đơn có trong CRM | Tiền được ghi nhận; xác định/phân bổ đúng kỳ; nghĩa vụ hóa đơn còn được theo dõi |
| T02 | Hóa đơn đồng bộ sau phần tiền đã phân bổ | Không tăng thực thu hay hoa hồng lần hai |
| T03 | Hai worker cùng phân bổ phần dư cuối của payment | Chỉ tổng hợp lệ được commit, không vượt số dư |
| T04 | Sao kê thủ công và API chứa cùng giao dịch | Phát hiện/đối chiếu trùng; không cộng tiền hai lần |
| T05 | Hoàn một phần service rồi replay refund | Đảo đúng phần base/commission, không đảo lặp; không kéo media vào service |
| T06 | Thiếu tiền, fee có chứng từ, write-off không có fee | Ba tình huống phân loại đúng; không tăng cash thực thu bằng write-off |
| T07 | Form có consent, identity chưa xác minh | Giữ evidence/timestamp và scope; không mất event, không tự mở rộng consent |
| T08 | Hai workspace có cùng email/điện thoại | Không chia sẻ dữ liệu/owner chỉ vì trùng giá trị |
| T09 | Cùng hotline nhưng hai contact/nhu cầu | Chỉ cảnh báo nghi trùng; không tự merge hoặc hoàn thành chung SLA |
| T10 | Owner đang họp, người trực dự phòng phản hồi | Giữ chủ deal/công lao; audit bàn giao; không reset nghĩa vụ khách hàng |
| T11 | Một contact có quote A và ticket B; gọi về A | Chỉ episode liên quan A được xem xét hoàn thành |
| T12 | NoAnswer, busy, autoack, cuộc gọi kết nối | Phân biệt attempt với human response; không lách bằng đổi trạng thái |
| T13 | Merge nhầm, sau đó có tin mới và revoke rồi unmerge | Provenance còn đủ; outbound bị kiểm lại; phần mơ hồ chờ xét; chứng từ không tự đổi chủ thể |
| T14 | B2C không có Account được bàn giao Sales→AM | Quyền theo hồ sơ được giao; không buộc tạo công ty giả |
| T15 | Deal tạm hoãn rồi quay lại | Giữ lịch sử và thời gian tổng; forecast và cohort theo định nghĩa công bố |
| T16 | Vượt quota sửa do agency làm sai SOW | Không tự tính phí khách; sửa lỗi khác yêu cầu thay đổi |
| T17 | Khách chậm duyệt trong dự án có sự kiện cố định | Ghi trách nhiệm/chờ; không tự dời ngày sự kiện hoặc cộng trùng thời gian |
| T18 | Ngoại lệ kickoff hết hạn khi chưa đủ tiền | Cảnh báo và hạn chế theo mức rủi ro được duyệt, không chỉ kiểm có bất kỳ allocation |
| T19 | Retainer ngắn hạn mới ký; scheduler replay | Không nhắc lại mốc quá khứ hàng loạt; mỗi mốc hợp lệ chỉ một tác vụ |
| T20 | Ticket nghiêm trọng chờ khách rồi reopen | Không tự đóng như ticket thường; không reset/xóa lịch sử breach |
| T21 | Sales nghỉ việc, link tệp cũ còn lưu | Revoke phiên và kiểm quyền truy cập; người nhận bàn giao đủ lịch sử |
| T22 | Restore backup và replay webhook/outbound timeout | Dữ liệu khôi phục được; không nhân tiền, lead hoặc gửi lại mù |

Các ca trên là đề xuất nghiệm thu, chưa được chạy trong lần phân tích này.

## 8. Thứ tự thực hiện và quyết định còn thiếu

**Bước 1 — Chốt dữ kiện vận hành:** làm rõ 50 khách/tháng là khách mới hay đang phục vụ; dịch vụ/gói hợp đồng; công cụ và tài khoản kênh hiện có; chính sách hoa hồng; ngân sách và người bảo trì. Đây là biến quyết định lựa chọn nền tảng, không nên tự suy diễn.

**Bước 2 — Sửa baseline:** ưu tiên scope workspace, schema chồng lấn, cash/allocation/invoice, SLA completion, chia sẻ quyền, snapshot hợp đồng và lịch sử trạng thái. Lập decision log cho mỗi thay đổi với FR/UC/schema/UAT bị ảnh hưởng.

**Bước 3 — PoC một luồng hoàn chỉnh:** tiếp nhận → qualified → quote → hợp đồng → tiền → handoff → nghiệm thu; thêm các nhánh sai/đảo/ngoại lệ. So hai nền tảng theo cùng tiêu chí, không chỉ demo màn hình đẹp.

**Bước 4 — Pilot cá nhân rồi nhóm nhỏ:** đo thời gian nhập liệu, lead bị bỏ sót, thao tác trùng, số dư đối soát, tỷ lệ next action và số cảnh báo sai. Ngưỡng SLA và notification được điều chỉnh bằng dữ liệu; không khẳng định thống kê mạnh từ mẫu nhỏ.

**Bước 5 — Mở rộng khi qua gate:** kiểm quyền chi nhánh, restore, offboarding, ledger, consent và vận hành connector. Lộ trình 90 ngày là mục tiêu có điều kiện theo nguồn lực và phạm vi; không cam kết hoàn thành toàn bộ nền tảng bằng việc cắt số bảng.

**Quyết định đề xuất:** dùng báo cáo Gemini làm danh sách vấn đề để kiểm chứng; dùng SRS hiện tại làm khung nghiệp vụ; bổ sung các chỉnh sửa trong bản phản biện này để tạo baseline triển khai mới. Chưa triển khai nguyên trạng một trong hai tài liệu.
