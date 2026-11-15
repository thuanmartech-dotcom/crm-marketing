# Rà soát chuyên sâu CRM agency — góc CEO, tài chính và quản trị vận hành

Ngày nghiên cứu: 15/10/2026, múi giờ Việt Nam. Phạm vi: FR14–17, FR20–21, luồng lead-to-cash, lợi nhuận, hoa hồng, nguồn dữ liệu và phân quyền. Đọc đối chiếu `CRM_MASTER_BRD_SRS_HOP_NHAT.md` và `PHAN_TICH_PHAN_BIEN_CRM_2026-10-15.md`; không sửa hai tài liệu đó.

## 1. Kết luận điều hành

SRS có định hướng đúng: tách phí dịch vụ/media, giữ SOW có phiên bản, xác minh tiền từ nguồn đáng tin, không đồng nhất Won với Paid, có bút toán đảo, tách vai trò và chỉ bắt đầu với MVP. Tuy nhiên, các quy tắc trên chưa kết nối thành mô hình đủ chặt để triển khai sản xuất. Không nên xác nhận “đã chuẩn” chỉ vì các tên module đã có.

**Các điểm phải sửa trước khi lập trình phần tài chính:**

1. Phân biệt tiền đã xác thực, tiền đã nhận diện chủ thể, tiền đã phân bổ và nghĩa vụ đã thanh toán. `Payments.status = Pending/Confirmed/Reversed/Unmatched` đang gộp nhiều chiều trạng thái.
2. `Payment_Allocations.invoice_line_id NOT NULL` chưa hỗ trợ phân bổ theo nghĩa vụ hợp đồng khi hóa đơn chưa có trong CRM. Không chữa bằng cách cho mọi đích rỗng.
3. Bổ sung pháp nhân hạch toán, tài khoản ngân hàng nhận tiền và quan hệ người trả/người mua. Tenant, workspace và chi nhánh không thay thế pháp nhân.
4. Chuẩn hóa một giao dịch ngân hàng xuất hiện qua API và sao kê thành một khoản thu; unique theo connector chưa giải quyết được trùng xuyên nguồn.
5. Cố định thẩm quyền phê duyệt, phiên bản, đơn vị và công thức của giá/cost/margin/hoa hồng; bổ sung điều chỉnh, kết chuyển và quyết toán.
6. Có đối soát giữa CRM, ERP và ngân hàng với người chịu trách nhiệm xử lý sai lệch. Một webhook “thành công” không chứng minh số dư ba hệ thống khớp.
7. Liên kết media được phép chi với hợp đồng, ngân sách duyệt và nguồn tiền/credit được phép sử dụng; không coi toàn bộ số dư ngân hàng là tiền sẵn sàng chi cho mọi khách.

Các đề xuất chi tiết dưới đây là **thiết kế của người rà soát**, suy ra từ rủi ro và quy trình agency. Những ngưỡng như 5%, 30%, 60 giây, 90 ngày trong SRS là chính sách/giả định nội bộ cần xác nhận; không phải chuẩn ngành đã được chứng minh.

## 2. Bằng chứng nghiên cứu và giới hạn

Ký hiệu: **T** = tài liệu sản phẩm/chuẩn chính thức; **C** = đã đọc đoạn mã nguồn thực tế; **L** = nguồn cơ quan nhà nước; **ĐX** = đề xuất thiết kế. Không cài ERPNext/Odoo, không chạy test upstream và không kiểm chứng môi trường CRM đang hoạt động. Nguồn mã đọc từ branch; đã thử GitHub API/commit history nhưng không lấy được SHA ổn định qua công cụ web. Vì vậy các URL branch có thể thay đổi sau ngày nghiên cứu.

| ID | Nguồn và vị trí | Quan sát được xác nhận | Giới hạn áp dụng |
| --- | --- | --- | --- |
| CEO-S01 T | [ERPNext Payment Entry](https://docs.frappe.io/erpnext/payment-entry), phần overview/advance/unallocated | Payment có thể tham chiếu hóa đơn hoặc đơn hàng; tiền ứng trước/độc lập có thể để chưa phân bổ rồi đối soát sau | Không chứng minh tuân thủ hóa đơn Việt Nam; không chứng minh đã đáp ứng split commission của agency |
| CEO-S02 T | [ERPNext Payment Reconciliation](https://docs.frappe.io/erpnext/payment-reconciliation), Before you begin/What changes | Đối soát kiểm Company, party và tài khoản; điều chỉnh liên kết/số dư, không ghi lại bank posting; hỗ trợ quan hệ nhiều payment–nhiều invoice | FIFO là lựa chọn sản phẩm, không phải chính sách phù hợp mọi hợp đồng |
| CEO-S03 C | [ERPNext version-15 payment_entry.py](https://github.com/frappe/erpnext/blob/version-15/erpnext/accounts/doctype/payment_entry/payment_entry.py): `validate_allocated_amount_with_latest_data`, `validate_reference_documents`, `validate_duplicate_entry`, `get_valid_reference_doctypes`; đọc thêm [raw](https://raw.githubusercontent.com/frappe/erpnext/version-15/erpnext/accounts/doctype/payment_entry/payment_entry.py) | Có kiểm số dư mới nhất, tham chiếu party/chứng từ và loại reference; `validate_duplicate_entry` ở đây kiểm trùng các dòng References trong một payment | Tên hàm “duplicate” không chứng minh chống ghi trùng giao dịch ngân hàng xuyên connector; đọc đoạn này không chứng minh an toàn khi nhiều transaction chạy đồng thời |
| CEO-S04 C | [Odoo 18 sale_order.py](https://github.com/odoo/odoo/blob/18.0/addons/sale/models/sale_order.py): `action_confirm`, `_confirmation_error_message`, `_prepare_confirmation_values`; đọc [raw](https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order.py) | Luồng confirm kiểm trạng thái rồi chuyển sang sale, có điểm mở rộng cho chứng từ liên quan | Không đồng nghĩa có kiểm đủ ứng trước, thẩm quyền ký hay SOW riêng của agency; không được suy “bấm confirm = đủ điều kiện kickoff” |
| CEO-S05 T | [Odoo 19 Invoice project milestones](https://www.odoo.com/documentation/19.0/applications/sales/sales/invoicing/milestone.html), How milestone invoicing works | Milestone liên kết Sales và Project; đạt milestone cập nhật lượng có thể lập hóa đơn, không mặc nhiên tạo invoice | Đây là workflow sản phẩm. Không dùng để trì hoãn nghĩa vụ lập hóa đơn theo quy định địa phương |
| CEO-S06 T | [Odoo 19 project profitability — bản tiếng Tây Ban Nha chính thức](https://www.odoo.com/documentation/19.0/es_419/applications/services/project/project_management/project_profitability.html) | Báo cáo tập hợp bản ghi liên kết project/analytic account; tách expected, to invoice/to bill và invoiced/billed; bao gồm nhiều loại cost | Tài liệu không xác nhận edition/module cài tại doanh nghiệp; dashboard không tự sửa chi phí thiếu hoặc mapping sai |
| CEO-S07 T | [PostgreSQL Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) | Table owner thường bypass RLS; superuser/BYPASSRLS cũng có ngoại lệ; FORCE RLS xử lý trường hợp owner | Không bảo vệ tự động search engine, object storage, bản export, cache hoặc vector index |
| CEO-S08 L | [Chính phủ: Nghị định 70/2025/NĐ-CP về hóa đơn](https://xaydungchinhsach.chinhphu.vn/nghi-dinh-70-2025-nd-cp-sua-doi-bo-sung-quy-dinh-ve-hoa-don-chung-tu-11925032321512617.htm) | Có nguyên tắc thời điểm lập hóa đơn dịch vụ khi thu tiền trước/trong quá trình cung cấp và các ngoại lệ được liệt kê | Không thể suy mọi “tạm ứng marketing” đều thuộc ngoại lệ. Đây là đối chiếu điểm thiết kế; chưa là bản rà soát pháp luật toàn diện đến ngày go-live |
| CEO-S09 T | [IFRS Foundation, IFRIC Update November 2021 — principal versus agent](https://www.ifrs.org/news-and-events/updates/ifric/2021/ifric-update-november-2021/) | Khi nhiều bên cung cấp hàng/dịch vụ, đánh giá bản chất lời hứa và quyền kiểm soát quan trọng hơn tên khoản thu | Là tham chiếu khái niệm IFRS; không khẳng định mọi agency Việt Nam áp dụng IFRS hoặc mọi media đều phải hạch toán thu hộ |

Không dùng bài quảng cáo bán CRM làm bằng chứng tính đúng đắn tài chính. Facebook có thể cho ví dụ pain point vận hành nhưng không thay thế nguồn pháp lý, sổ kế toán hoặc mã nguồn. Nghiên cứu Facebook nằm ngoài phân công chuyên đề CEO này.

## 3. Rà từng module: tại sao cần và liên kết bắt buộc

### FR14 — Danh mục dịch vụ, báo giá và phê duyệt

**Kết luận: giữ ở P0, sửa phần giá/cost/version và thẩm quyền.** Một agency bán sản phẩm vô hình nên tranh chấp thường bắt đầu từ kỳ vọng, số lượng và phạm vi. Catalog không chỉ để chọn giá; nó phải mô tả chính xác thứ khách mua và cách agency ước lượng khả năng giao.

| Thành phần | Lý do phải có | Đầu vào → đầu ra | Liên kết |
| --- | --- | --- | --- |
| Service catalog versioned | Gói cũ đã bán không được thay đổi âm thầm khi bảng giá mới cập nhật | Mã dịch vụ, đơn vị, số lượng, điều kiện, hiệu lực → phiên bản dòng báo giá | FR04 deal, FR22 brief, FR15 SOW, FR25 capacity |
| Quote lines tách service/production/media và thuế | Sales cần thấy giá trị công sức thực; kế toán cần bản chất khoản thu; không cho media làm phồng biên và commission | Scope, giá, giảm giá, cost basis, tax code → tổng và cấu phần giá | FR16, FR17, FR26, FR28–29 |
| Margin preview theo phiên bản cost | Giá bán lớn chưa chứng minh lời nếu ekip/thuê ngoài/sửa lại quá tốn | Giá thuần, chi phí trực tiếp dự kiến → contribution amount/rate và cảnh báo | FR25 nguồn lực, FR26 cost, FR27 báo cáo nguồn lực |
| Approval theo loại ngoại lệ | Phê duyệt giảm giá không đồng thời cấp phép kéo dài công nợ hoặc cam kết KPI ngoài khả năng | Discount/margin/payment term/SOW exceptions → quyết định có phạm vi, thời hạn | FR15 hợp đồng, FR21 quyền |
| Quote revision + customer acceptance evidence | Khách chấp thuận bản nào phải truy được; nội bộ duyệt bản A không được gửi bản B như đã duyệt | Hash/version, người duyệt/khách nhận → bản đã phát hành và trạng thái | Assets/Approvals, FR07 inbox, FR15 |

**Bổ sung vào đặc tả:**

- Tách `contribution_amount = net_service_fee - defined_direct_cost` và `contribution_rate = contribution_amount / net_service_fee`. Nếu mẫu số bằng 0, trả N/A; không chia theo tổng service+media. Đây là định nghĩa quản trị đề xuất, phải ghi rõ cost bao gồm gì và có gồm commission hay chưa.
- Cost dự kiến có `cost_version`, `effective_at`, `estimate_confidence`, người xác nhận. Chưa có cost phải hiển thị “chưa đủ dữ liệu”, không mặc định bằng 0 để đạt margin 100%.
- Thuế là cấu phần/treatment của dòng, không nên bị trộn lẫn tùy tiện với nhóm nghiệp vụ service/media trong cùng một enum. Catalog có category nghiệp vụ, từng dòng có net/tax/gross và quy tắc làm tròn.
- Phê duyệt riêng ít nhất: giá/giảm giá, biên thấp, điều khoản tín dụng, cam kết đặc biệt, chi phí hoặc scope vượt quyền. Một người có thể giữ nhiều quyền, nhưng quyền phải được khai báo.
- Khách chấp nhận báo giá hết hiệu lực: yêu cầu revalidate và phát hành/duyệt lại theo policy; không im lặng sửa ngày hết hạn.
- Không bắt lập báo giá/SOW nhiều trang cho mọi dịch vụ B2C nhỏ. Có thể dùng gói chuẩn/đơn xác nhận với phiên bản điều khoản, nhưng vẫn giữ bằng chứng phạm vi và chấp thuận.

**Bất biến:** bản được gửi phải đúng version đã qua gate; sửa giá/scope/điều khoản ảnh hưởng phải làm mất hiệu lực approval tương ứng; không xóa revision đã phát hành; hoàn toàn tách nội bộ approve và khách accept.

### FR15 — Hợp đồng, SOW, handoff và kỳ dịch vụ

**Kết luận: giữ P0; không chỉ có upload hợp đồng và nút Won.** Đây là cầu nối giữa thứ Sales hứa, thứ Delivery giao và thứ kế toán thu. Thiếu cầu nối này tạo scope creep, mất margin và khách thất vọng dù CRM có đủ dữ liệu lead.

| Chức năng | Lý do | Đầu vào → đầu ra | Liên kết |
| --- | --- | --- | --- |
| Contract/SOW version và thẩm quyền người duyệt | Contact trong CRM chưa chắc có quyền ký hoặc nghiệm thu | Quote accepted, signer/authority, điều kiện hiệu lực → cam kết có căn cứ | FR01 quan hệ contact–account, FR14, FR21 |
| Start authorization | Deal thắng chưa chứng minh đã có asset, người làm và tiền được phép dùng | Contract effective + điều kiện tiền + capacity + handoff accepted → phép khởi động | FR16, FR20, FR25, FR26 |
| Milestone/deliverable/acceptance | Khách và agency cần cùng hiểu thế nào là hoàn thành | SOW version → deliverable version, QA, feedback, acceptance | FR18 ticket, FR25 task, FR16 billing request |
| Change request | Yêu cầu mới cần đánh giá chi phí/lịch; tránh ghi thêm việc mà không ai chịu trách nhiệm | Scope delta, impact, quote delta → approved amendment/baseline mới | FR14, FR26 ngân sách, FR20 lịch |
| Retainer periods/renewal/termination | Kỳ dịch vụ khác kỳ thu; hủy giữa kỳ phải chốt phần còn phải thực hiện/trả lại | Điều khoản kỳ và thay đổi → service periods, payment schedule, renewal event | FR09 nhắc, FR16, FR17, FR19, FR28 |

**Sửa và làm rõ:**

- `Won`, contract effective, start authorized, service started, delivered, accepted, invoiced và paid là các mốc riêng. Khách có thể ký nhưng chưa trả; có thể trả nhưng thiếu tài sản; có thể được giao một phần nhưng chưa nghiệm thu toàn bộ.
- Một hợp đồng khung có thể có nhiều SOW, order và project. UAT “một contract chỉ sinh một project từ cùng handoff event” đúng ở ý idempotency, không được biến thành unique toàn cục `contract_id` trên Projects. Khóa tạo phải theo lệnh/handoff hoặc gói giao hàng cụ thể.
- Ngoại lệ cho kickoff phải có `approved_limit`, phạm vi công việc được bắt đầu, thời hạn, người chịu rủi ro và điều kiện dừng/escalate. Duyệt bắt đầu soạn nội dung không tự cho phép chi 100 triệu media.
- Thời gian chờ khách ảnh hưởng lịch dự kiến; không tự sửa deadline cam kết. Phân biệt ngày sự kiện cố định, deadline hợp đồng và lịch nội bộ.
- Số vòng sửa theo SOW; một vòng là tập phản hồi hợp nhất được chốt. Sửa lỗi không đạt tiêu chuẩn ban đầu khác yêu cầu đổi ý. Không khóa khả năng khắc phục lỗi chỉ vì quota sửa đã hết.
- Retainer phải quyết định xử lý kỳ đầu/cuối không tròn tháng, tạm dừng, tăng giá, rollover quota, hết hạn không gia hạn và thanh lý sớm. Không tự pro-rata nếu hợp đồng không quy định.
- Nghiệm thu được gắn với đúng asset/SOW version, người có thẩm quyền và evidence. Không tự suy nghiệm thu chỉ vì task đã Done hoặc khách không trả lời.

CEO-S05 cho thấy mối nối milestone–order–invoice là một pattern có trong sản phẩm thật; nó không thay thế điều khoản hợp đồng hay thời điểm hóa đơn địa phương.

### FR16 — Tiền, công nợ, phân bổ và đối soát

**Kết luận: phải sửa P0 trước khi triển khai.** CRM không cần trở thành sổ kế toán tổng hợp, nhưng không được báo khách nợ sai hoặc trả commission từ tiền chưa thật sự nhận. CEO cần biết thu được tiền gì, của ai, còn nghĩa vụ nào và có phần nào đang dùng để tài trợ delivery/media.

**Mô hình tối thiểu đề xuất:**

1. `PaymentEvidence`: event API/sao kê đã nhập, nguồn, external ID, thời gian nhận, trạng thái kiểm tra, tham chiếu bản gốc. Nhiều evidence có thể chứng minh cùng một payment.
2. `Payment`: giao dịch kinh tế canonical, `legal_entity_id`, tài khoản nhận, tiền tệ, amount/direction, bank reference, thời điểm giao dịch/xác nhận, chủ thể trả và party được hưởng khi đã xác định.
3. `ContractPaymentObligation`/kỳ thu: số tiền phải thu theo hợp đồng/đơn, ngày đến hạn, phân rã service/media/tax được phê duyệt, trạng thái điều chỉnh. Không thay thế khoản phải thu đã hạch toán trong ERP.
4. `PaymentAllocation`: phân bổ có đích xác định đến nghĩa vụ/dòng kỳ hoặc đối tượng tài chính được thiết kế rõ; reverse bằng dòng liên kết. Không cho một bản ghi vừa trỏ hai đích không kiểm soát; có thể dùng supertype hoặc bảng riêng tùy nền tảng.
5. `InvoiceProjection`/`InvoiceLineProjection` + mapping: bản chiếu chứng từ ERP; liên kết với nghĩa vụ và allocation theo amount. Hóa đơn đến sau chỉ bổ sung mapping, không phát sinh cash lần hai.
6. `ReconciliationCase`: chênh lệch, ảnh hưởng, người xử lý, due date, evidence và resolution. Cần có trạng thái chênh lệch chưa xử lý nhìn thấy được.

Mô hình này là ĐX; CEO-S01/S02 xác nhận nguyên tắc nhận tiền trước/phân bổ sau tồn tại trong phần mềm ERP, không phải chứng minh schema đề xuất này đã chạy được.

**Tách các chiều trạng thái:**

- `verification_state`: pending/confirmed/rejected (và cơ chế ghi nhận reversal riêng).
- `matching_state`: unidentified/identified/ambiguous.
- `allocation_state`: unallocated/partially_allocated/fully_allocated, tính từ ledger.
- `reconciliation_state`: open/reconciled/disputed hoặc thiết kế tương đương.

Một khoản tiền có thể đồng thời confirmed, ambiguous và unallocated. Không đổi confirmed thành unmatched rồi làm dashboard tưởng chưa có tiền. Partial refund không được đánh dấu toàn bộ payment là đã hoàn hết.

**Luồng:** xác thực nguồn → ghi evidence bền vững → nhận diện payment canonical → xác định legal entity/party → khớp nghĩa vụ → phân bổ trong transaction → outbox → cập nhật projections/commission candidate → đối soát ERP → đóng case. Thông tin từ ảnh chuyển khoản hoặc VietQR chỉ hỗ trợ tìm kiếm, không chứng minh cash.

**Tại sao cần liên kết các module:** FR01/02 xác định khách nhưng merge contact không được tự đổi bên trên chứng từ; FR14/15 cho biết nghĩa vụ/cấu phần thu; FR17 nhận cơ sở service đã đủ điều kiện; FR26 nhận phép sử dụng ngân sách; FR18 ghi tranh chấp ảnh hưởng dunning; FR21 kiểm quyền kế toán/pháp nhân; FR28/29 sử dụng chỉ số tiền cùng định nghĩa.

**Các bất biến:**

- Tổng phân bổ hiệu lực không vượt tiền khả dụng và nghĩa vụ hợp lệ; kiểm dưới lock/atomic transaction, có retry được thiết kế cho conflict.
- Không phân bổ chéo tenant, workspace tài chính, pháp nhân, party hoặc currency khi chưa có nghiệp vụ chuyển/ủy quyền/chuyển đổi hợp lệ. Một người trả hộ chỉ mở case để xác nhận quan hệ, không tự merge payer với buyer.
- Fingerprint ngày+số tiền+nội dung chỉ là candidate dedup khi không có ID ngân hàng ổn định: hai giao dịch thật có thể giống các thuộc tính đó. Không tự bỏ một dòng chỉ vì hash trùng.
- Replay API, nhập lại file hoặc hóa đơn đồng bộ muộn không được tăng tiền/commission. Idempotency key còn phải kiểm payload: cùng key khác nội dung là conflict.
- Refund/chargeback/reversal phải liên kết phần gốc, có quyền và không đảo lặp phần đã đảo. Credit note, xóa nợ, chiết khấu và bank fee không tự tạo cash receipt.
- Kỳ khóa không sửa số lịch sử; sửa bằng adjustment trong kỳ cho phép với audit. Trạng thái chi trả/approval có thể tiến triển nhưng giá trị ledger đã ghi phải có lịch sử bất biến.
- ERP sở hữu chứng từ/khoản phải thu hạch toán. CRM có thể hiển thị nghĩa vụ hợp đồng vận hành nhưng phải đặt tên khác và đối soát; không có hai nơi cùng tự sửa “công nợ chính thức”.

**Hóa đơn:** CEO-S08 cho thấy không thể mặc định dịch vụ marketing nhận tiền trước luôn được chờ nghiệm thu mới lập hóa đơn. Cần `invoice_required_at`, căn cứ/treatment được kế toán duyệt và hàng chờ chứng từ thiếu. Tách technical sync lag khỏi legal due date. Nghiên cứu này không xác nhận đầy đủ mọi thay đổi pháp luật đến ngày triển khai.

### FR17 — Hoa hồng

**Kết luận: giữ tính minh bạch P0 nếu agency trả hoa hồng; hoãn engine linh hoạt tổng quát.** Hoa hồng phải hướng Sales bán hợp đồng có giá trị và thu tiền đúng; công thức sai khuyến khích bán media lớn, giảm giá mạnh hoặc nhận hết công của người trực inbox.

Đầu vào: allocation đủ điều kiện, loại dòng dịch vụ, chính sách áp dụng, attribution share, tiêu chí chất lượng có bằng chứng và các điều chỉnh. Đầu ra: preview có giải thích → earned/approved/payable theo quy chế → payout và lịch sử điều chỉnh. Liên kết FR14 margin; FR15 SOW/nghiệm thu; FR16 cash/refund; FR18/19 dữ kiện chất lượng; FR21 người duyệt; FR28 báo cáo.

**Các sửa đổi bắt buộc:**

- Định nghĩa rõ eligible base là gì, gross/net, có VAT/thu hộ/chiết khấu/thuê ngoài hay không, và thời điểm đủ điều kiện. “Thực thu” không có nghĩa toàn bộ transfer thuộc service.
- Share tổng bằng 1 nên áp dụng cho **một pool hoa hồng/chính sách/phạm vi và phiên bản hiệu lực**. Nếu có pool hunter, renewal hoặc referral riêng, không gom tất cả người hưởng vào một tổng duy nhất ở Deal.
- Không thay đổi quyền hưởng chỉ vì đổi owner Deal, chuyển chi nhánh hay người trực inbox trả lời. Có lịch sử attribution riêng và thẩm quyền sửa tương lai/điều chỉnh quá khứ.
- Quality factor nếu chưa có kết quả phải thể hiện pending; không tự lấy 1 để chi. Với MVP nên tách base commission và quality bonus nếu quy chế có thể chấp nhận, giúp không làm mơ hồ tiền lương/hoa hồng đã được hưởng.
- Mỗi entry giữ policy version, allocation gốc, base, rate, share, rounding và lý do adjustment. Chỉ `policy_version` dạng text mà không truy được snapshot là chưa đủ.
- `Preview`, `Approved`, `Payable`, `Paid` cần bảng điều kiện chuyển và người có quyền. Payout có batch, bằng chứng chuyển tiền và số dư phải trả; một entry có thể cần nhiều payout/adjustment, không chỉ status đơn.
- Refund sau payout tạo khoản điều chỉnh theo quy chế đã được rà soát; không sửa entry Paid thành chưa từng trả và không tự khấu trừ lương ngoài quy trình hợp lệ.

**Ví dụ không thuế để kiểm tra logic:** nghĩa vụ 20 triệu service + 80 triệu media, nhận 50 triệu. Nếu kỳ đã duyệt thu theo tỷ lệ 20/80 thì service thực thu 10 triệu; commission rate 5% tạo pool 500.000; split A/B 70/30 cho 350.000/150.000. Nếu kỳ đầu được định nghĩa thu media trước thì base service bằng 0. Khi thiếu bằng chứng phân bổ, preview pending. Hai kết quả khác nhau đều có thể đúng theo điều khoản; không có một pro-rata mặc định đúng cho mọi hợp đồng.

### FR20 — Lịch hẹn, ekip và check-in

**Kết luận: lịch hẹn/capacity cơ bản P0; GPS check-in chỉ làm khi có nhu cầu thực địa chứng minh.** Giá trị là giữ lời hẹn với khách và không bán trùng ekip. GPS không chứng minh chất lượng tư vấn, quay chụp hoặc nghiệm thu.

- Đầu vào: khách/người tham dự, mục đích, tài nguyên, khoảng thời gian, timezone, location và buffer di chuyển. Đầu ra: tentative hold/confirmed/cancelled/no-show/rescheduled, người chịu trách nhiệm và thông báo phù hợp.
- Liên kết FR04 discovery; FR15 kickoff/delivery/acceptance; FR05 ca trực; FR25 availability; FR18 đặt lịch xử lý; FR09 reminder; FR21 chia sẻ lịch theo quyền.
- “Chặn trùng lịch” cần phân biệt người bắt buộc/người tùy chọn, tài nguyên độc quyền và slot dự kiến. Phải kiểm concurrency ở backend, không chỉ lọc ô lịch UI.
- Hai người đặt cùng ekip vào cùng thời gian chỉ một hold/confirmation hợp lệ; hold có TTL. Thêm buffer và lịch nghỉ; lưu timezone chuẩn chứ không chỉ chuỗi giờ.
- External calendar sync phải có external ID/version, conflict policy, chống vòng lặp và xử lý deletion/reschedule. Nếu chưa tích hợp, chỉ có một nguồn lịch được tuyên bố chính thức.
- Check-in có độ chính xác/timestamp; quyền từ chối vị trí và bằng chứng thay thế. Không coi GPS sai là vi phạm tự động. Không triển khai geotracking liên tục cho agency chỉ để “có đủ tính năng”.

### FR21 — Chi nhánh, cộng tác và quyền

**Kết luận: quyền/scope P0, tính năng điều hành nhiều chi nhánh mở theo nhu cầu.** Khách hàng không nên phải kể lại toàn bộ khi chuyển team, nhưng người không được giao không được nhìn mọi hồ sơ chỉ vì cùng một CEO.

| Khái niệm | Vai trò | Không được đồng nhất với |
| --- | --- | --- |
| Tenant | Tổ chức/vùng cô lập cấp cao của hệ thống | Pháp nhân hạch toán trong mọi trường hợp |
| Legal entity | Bên ký/hạch toán/tài khoản tài chính | Chi nhánh vận hành |
| Branch | Queue, lịch, mục tiêu và trách nhiệm quản lý | Chủ thể hóa đơn hoặc ranh giới tenant mặc định |
| Workspace | Phạm vi dữ liệu agency hoặc xử lý thay khách | Một chiến dịch, một công ty mua, hoặc quyền xem tiền của agency |
| Team/grant | Quyền cộng tác có vai trò, phạm vi, thời hạn | Đổi ownership hay đổi hoa hồng |

- SRS 5.1 dùng `client_workspace_id nullable` nhưng 5.16 dùng `workspace_id NOT NULL`; cần một mô hình scope thống nhất hoặc mapping chính thức trước viết FK/policy. Khuyến nghị workspace AGENCY và CLIENT rõ ràng cho dữ liệu có scope; danh mục dùng chung cấp tenant được khai báo riêng.
- Hợp đồng, invoice và tiền của agency thường thuộc workspace nghiệp vụ agency, dù phục vụ project/campaign của một CLIENT workspace. Cần quan hệ kiểm soát rõ giữa tài chính agency và delivery khách; không ép chia sẻ toàn bộ số tiền/commission cho người làm trong client workspace.
- Account có thể dùng chung, nhưng Deal/Project/Ticket vẫn có quyền riêng. B2C không có Account cần grant ở Contact/Deal/Project; chỉ có Account Team chưa đủ.
- Phân quyền approver tách create/edit/view. CEO thấy tổng hợp không mặc nhiên có quyền sửa ledger; Admin kỹ thuật không mặc nhiên đọc tất cả tài liệu. Audit cần cả hành động break-glass và thời hạn quyền.
- Chuyển chi nhánh là workflow bàn giao active obligations, owner/backup, lịch hẹn, ticket và quyền; các khoản phải thu giữ đúng pháp nhân. Không sửa branch để “di chuyển công nợ”.
- Offboarding thu hồi phiên, refresh token, API token, connector grant cá nhân và file access; kiểm cả link download cũ, các task scheduler đang chạy và quyền inherited. Job đang chạy cũng phải kiểm quyền tại thời điểm hành động nhạy cảm.
- CEO-S07 hỗ trợ cảnh báo rằng RLS chỉ là một lớp. Cần tests theo role thực và các bề mặt API/search/export/storage/AI.

## 4. Các khoảng trống điều hành agency còn thiếu

### 4.1 Media funding và trách nhiệm chi

ĐX thêm quy trình nhẹ, liên kết FR15–16–23–26. Đầu vào: ngân sách khách đã duyệt, kỳ/dòng media, tiền được phép dùng hoặc hạn mức tín dụng đã duyệt, số đã commit và actual. Đầu ra: headroom được phép tiếp tục chi và case chênh lệch.

Lý do: agency có thể thu 100 triệu nhưng phải giữ phần lớn để chạy media; số dư ngân hàng dương chưa nói agency có lãi hoặc đủ tiền cho mọi khách. Cần theo dõi ngân sách duyệt, nguồn funding và spend ba chiều riêng. Nếu ad spend chưa đồng bộ, ghi freshness và dự phòng theo policy; không hiện số khả dụng chính xác giả.

Không gọi mọi media là “thu hộ” chỉ vì CRM đặt line_type như vậy. Bản chất principal/agent cần được kế toán xác định từ hợp đồng; CEO-S09 chỉ là tham chiếu khái niệm. Không dùng nhãn để tự kết luận thuế hoặc ghi nhận doanh thu.

### 4.2 Dunning và tranh chấp công nợ

ĐX thêm owner thu hồi, aging theo due date, promise-to-pay, lý do dispute, reminder schedule và policy hold. Liên kết FR16 với FR18, FR15 và FR07. Lý do: gửi nhắc nợ tự động trong lúc khách đang khiếu nại hóa đơn sai có thể gây tổn hại quan hệ; nhưng dispute không được âm thầm xóa khoản phải thu. Bản projection cần nêu rõ outstanding từ ERP, contract obligation, disputed amount và freshness.

### 4.3 Lợi nhuận và forecast

Tách sáu thước đo: pipeline kỳ vọng, booked service value, delivered/recognized theo nguồn được phê duyệt, invoiced, cash received và contribution. Không dùng “doanh thu” chung cho tất cả.

Khi đánh giá dự án cần ít nhất estimated direct cost, committed cost, actual cost đã được xác nhận, cost-to-complete và estimate-at-completion. Nếu cùng một khoản chuyển từ committed sang actual, giảm committed tương ứng để không đếm hai lần. Liên kết FR14 dự toán → FR15 baseline → FR25 effort → FR26 cost → FR28 dictionary. CEO-S06 cung cấp pattern báo cáo theo các trạng thái khác nhau; công thức và cách hạch toán cụ thể vẫn phải do doanh nghiệp chốt.

Tỷ lệ margin 30% chỉ có ý nghĩa khi nói rõ trước hay sau commission, cost lao động được phân bổ bằng giờ thực tế hay định mức, có phân bổ overhead hay chưa. MVP có thể dùng tổng cost đã kiểm tra thay cho timesheet chi tiết; thiếu cost không được coi bằng 0.

### 4.4 Retention và quyết định tái ký

Nhắc hết hạn chỉ giải quyết lịch. CEO/AM còn cần health review có nguồn: mức hoàn thành cam kết, ticket nghiêm trọng, feedback, adoption/engagement phù hợp, công nợ, kết quả kinh doanh trong phạm vi đo được và kế hoạch kỳ sau. Liên kết FR15/18/19/22/26/28. Health score phải giải thích các thành phần; không tự suy một khách có NPS thấp chắc chắn rời bỏ, hoặc nhiều ticket luôn là khách xấu.

### 4.5 Handoff và operating cadence

| Nhịp vận hành | Owner | Quyết định dựa trên CRM | Đầu ra bắt buộc |
| --- | --- | --- | --- |
| Hằng ngày | Sales/AM/Delivery | Lead/next action trễ, handoff thiếu, delivery/ticket cần cứu | Owner, việc kế tiếp, deadline và escalation cụ thể |
| Hằng ngày hoặc theo khối lượng | Kế toán | Unmatched, duplicate candidates, cash–ERP differences, invoice due | Case xử lý, bằng chứng, số dư đối soát |
| Hằng tuần | CEO + Sales + Delivery | Pipeline có năng lực giao, margin at risk, media funding, client risk | Ưu tiên nguồn lực, quyết định ngoại lệ có hạn mức |
| Theo kỳ chi trả | Kế toán + người duyệt | Commission payable/refund/quality pending | Batch payout, dấu vết phê duyệt, reconciliation |
| Hằng tháng | CEO/CMO/AM | Revenue mix, contribution, concentration, renewals và hiệu quả acquisition | Quyết định danh mục dịch vụ/ngân sách, owner thay đổi |

Không bắt cá nhân làm thêm nhiều cuộc họp: có thể là checklist review. Điều bắt buộc là dữ liệu dẫn đến quyết định và có người đóng vòng xử lý.

## 5. Bộ nghiệm thu riêng cho góc CEO/tài chính

Các ca dưới **chưa được chạy**; đây là tiêu chí lựa chọn/triển khai. P0 = sai có thể gây tiền/scope/quyền sai, phải qua trước mở chức năng tương ứng.

| ID | Tình huống | Kết quả đạt | FR |
| --- | --- | --- | --- |
| CEO-U01 P0 | Cost chưa nhập hoặc hết hiệu lực | Không hiển thị biên 100%; yêu cầu xác nhận/review đúng quyền | 14,26,28 |
| CEO-U02 P0 | Quote đã approved, sửa SOW hoặc lịch trả | Approval ảnh hưởng mất hiệu lực; bản cũ không bị viết đè | 14,15 |
| CEO-U03 P0 | Người liên hệ chấp thuận nhưng không có quyền nghiệm thu | Giữ evidence; không tự chuyển accepted khi chưa đủ thẩm quyền | 01,15,21 |
| CEO-U04 P0 | Hợp đồng khung có hai SOW; replay handoff của một SOW | Hai gói delivery hợp lệ; replay không tạo bản thứ ba | 15,25 |
| CEO-U05 P0 | Chỉ được duyệt kickoff sáng tạo, chưa duyệt chi media | Cho đúng phần công việc; không mở ngân sách quảng cáo ngoài quyền | 15,23,26 |
| CEO-U06 P0 | Tiền xác thực nhưng chưa biết hóa đơn/chủ thể | Tiền vẫn tồn tại confirmed; case match mở; không tạo commission vô căn cứ | 16,17 |
| CEO-U07 P0 | Cùng giao dịch xuất hiện qua bank API và file sao kê | Hai evidence, một payment canonical; không tăng thực thu hai lần | 16 |
| CEO-U08 P0 | Hai giao dịch thật cùng ngày/số tiền/nội dung | Không tự bỏ một giao dịch chỉ do fingerprint | 16 |
| CEO-U09 P0 | Hai worker phân bổ 70 triệu từ cùng số dư 100 triệu | Không commit tổng 140 triệu; transaction thua nhận conflict/retry rõ | 16 |
| CEO-U10 P0 | Phân bổ payment của pháp nhân A sang nghĩa vụ pháp nhân B | Chặn hoặc đi nghiệp vụ hợp lệ riêng; không sửa scope để lách | 16,21 |
| CEO-U11 P0 | Invoice đến sau khoản ứng trước đã phân bổ | Mapping cập nhật; cash và commission không nhân đôi | 15,16,17 |
| CEO-U12 P0 | Hợp đồng service/media, kỳ đầu chỉ thu media | Commission service bằng 0 hoặc pending theo dữ kiện; không pro-rata tùy tiện | 16,17 |
| CEO-U13 P0 | Refund một phần service sau payout; callback replay | Đảo đúng phần một lần; giữ payout cũ và adjustment theo quy chế | 16,17 |
| CEO-U14 P0 | Write-off 1 triệu thay vì khách thực trả | AR giảm theo ERP nhưng cash-based commission không tăng | 16,17,28 |
| CEO-U15 P0 | Đổi Sales/chi nhánh giữa dự án | Không tự chuyển quyền hưởng lịch sử; handoff task/ticket/ACL có audit | 17,21 |
| CEO-U16 P0 | Quality chưa có và kỳ trả tới hạn | Hiện pending theo policy; không mặc định factor=1 | 17,18,19 |
| CEO-U17 P0 | Client workspace user mở link hợp đồng/commission agency | Chỉ truy cập phần đã được publish/grant; chặn dữ liệu nội bộ | 15,17,21 |
| CEO-U18 P0 | Thu hồi quyền sau khi job export đã xếp hàng | Recheck tại execution/download; không xuất nhờ snapshot quyền cũ | 21 |
| CEO-U19 P0 | Khách chậm feedback nhưng ngày khai trương cố định | Ghi thời gian chờ/rủi ro; không tự dời cam kết | 15,20,25 |
| CEO-U20 P0 | Hết quota sửa nhưng deliverable lỗi so với SOW | Đi quy trình defect; không tự bắt mua thêm vòng sửa | 15,18 |
| CEO-U21 P0 | Hai booking đồng thời cho một ekip độc quyền | Chỉ một reservation hợp lệ; hold hết hạn nhả tài nguyên | 20,25 |
| CEO-U22 P0 | Chuyển committed cost thành actual | Tổng forecast cost không cộng trùng; truy được nguồn | 26,28 |
| CEO-U23 P0 | Kỳ tài chính đã khóa, ERP điều chỉnh sau | Adjustment kỳ cho phép + lịch sử, báo cáo đã công bố truy được | 16,17,28 |
| CEO-U24 P0 | Khách dispute invoice và automation đang nhắc nợ | Route theo policy; không xóa nợ, không gửi nội dung sai/ngược lịch xử lý | 07,09,16,18 |
| CEO-U25 | Retainer hủy giữa kỳ hoặc rollover chưa dùng | Kết quả theo đúng điều khoản version, không pro-rata/rollover ngầm | 15,16,28 |
| CEO-U26 P0 | Restore DB rồi replay payment/invoice/outbox | Không tạo thêm cash, commission, project hay thông báo đã gửi; reconciliation còn thực hiện được | 15,16,17 |

## 6. Phạm vi khuyến nghị và gate quyết định

**P0:** catalog đủ dữ liệu, quote/SOW revision, approval, contract/order/kỳ thu, handoff, milestone/acceptance, payment canonical + allocation + reconciliation, quyền/scope, lịch cơ bản, contribution có nguồn, commission minh bạch nếu có quy chế. Có thể nhập/đối soát thủ công có kiểm soát; không bắt buộc tự động mọi bước ngay.

**P1 khi có nghiệp vụ:** calendar sync, retainer amendment/rollover phức tạp, media funding monitor, automated dunning, commission batch integration, client portal, nhiều chi nhánh.

**Hoãn:** GPS mọi nhân viên, game hóa/chấm hạng từ activity count, engine thuế/kế toán tự viết, commission DSL tổng quát, allocation AI tự chốt, hệ thống HR/payroll riêng. Những phần này tăng vận hành và rủi ro trước khi chứng minh giá trị.

Không đủ dữ kiện để tuyên bố nền tảng duy nhất tốt nhất. Dùng ERPNext/Odoo và CRM đang có làm ứng viên PoC khi phù hợp; xác minh edition, license/module, tích hợp VN, migration, backup, nâng cấp và TCO. Mã nguồn mở cho phép kiểm chứng và tùy biến, không tự làm triển khai rẻ/an toàn hơn.

Gate chọn nền tảng: chạy cùng dữ liệu ẩn danh và CEO-U01–26; các ca P0 sai phải sửa/loại trước mở chức năng. Chỉ so tốc độ thao tác, cấu hình và chi phí sau khi tiền, quyền và nghĩa vụ khách hàng đúng. Bộ ca này không thay thế kiểm thử tải, bảo mật và nghiên cứu connector của nhóm kỹ thuật.

## 7. Dữ kiện doanh nghiệp cần chốt để biến thành baseline triển khai

1. Pháp nhân nào ký hợp đồng, xuất hóa đơn, nhận tiền; branch nào chỉ quản lý vận hành?
2. Dịch vụ thực tế: retainer/one-off, mua media theo mô hình nào, ai sở hữu tài khoản quảng cáo, khách trả trực tiếp hay agency ứng?
3. Hệ thống kế toán/PMS hiện có; ai là nguồn chuẩn cho công nợ/cost; tần suất đồng bộ và độ trễ chấp nhận?
4. Commission có thực trả không; thời điểm earned/payable; pool, split, refund, quality và người duyệt?
5. Quyền ký/duyệt/nghiệm thu của khách được xác minh thế nào; có MSA nhiều SOW không?
6. Cost trực tiếp có dữ liệu nào; có cần time entry hay tổng hợp theo dự án là đủ; công thức margin nào dùng ra quyết định?
7. Nguồn lực và năng lực hỗ trợ hệ thống, ngân sách triển khai/vận hành, kế hoạch tăng team và trách nhiệm quản trị dữ liệu?

Đây là dữ kiện cần để chốt cấu hình, không phải lý do dừng việc rà soát. Với dữ kiện hiện có, phương án phù hợp nhất là CRM cấu hình được hoặc hybrid nhẹ, có một chuỗi giao dịch nhất quán và giữ ERP là nguồn chứng từ chính thức. Chưa đủ bằng chứng để chọn custom toàn bộ hoặc cam kết ROI/thời hạn chính xác.
