# Đề xuất điều chỉnh CRM cho B2C và bán lẻ trên sàn

**Cập nhật bàn giao:** CR-PARTNER-RESULTS-20261018 đã được hợp nhất vào Master1.8 theo yêu cầu chủ dự án. Phần đề xuất/kịch bản bên dưới là lịch sử; quy tắc hiện hành là Master3.15/4.24/5.21/6.7/7.8/8.6/9.17/A.8 và file M21 trong delivery-plan/specs/modules. Không hiểu các câu “Master chưa sửa” lịch sử là trạng thái hiện tại.

Ngày 18/10/2026. Trạng thái: change proposal đang làm rõ đầu vào; chưa thay baseline Master 1.7 hoặc phê duyệt scope mới. Mã đề xuất: CR-SCALE-RETAIL-20261018.

## Cập nhật sau xác nhận của chủ dự án — đọc trước phần kịch bản bên dưới

Đối tác là bên sở hữu hoạt động bán lẻ và đang dùng Pancake. Công ty chủ dự án cung cấp dịch vụ cho đối tác. Các kênh có TikTok Shop, Shopee và đơn Facebook. Lead đầu vào chưa phân loại; chưa có số khách chuyển đổi tin cậy. Chủ dự án viết “2000-5000 ngàn đơn”; trong phân tích tiếp tục dùng mốc 2.000–5.000 của trao đổi trước như cách hiểu tạm, không nhân thêm 1.000 hoặc coi đơn vị đã được chuẩn hóa. Chưa rõ quy mô cho mỗi đối tác hay tổng các đối tác. Mốc “500–100” B2C chưa được sửa rõ và chưa rõ lead này thuộc pipeline công ty hay chiến dịch của đối tác.

**Điều chỉnh khuyến nghị:** giữ CRM agency làm trung tâm quản trị khách hàng doanh nghiệp, hợp đồng, chiến dịch, công việc và hiệu quả dịch vụ. Pancake/POS hoặc hệ thống đối tác tiếp tục vận hành đơn/kho theo nguồn chuẩn đã xác minh. Không mặc định chuyển dự án thành OMS bán lẻ hoặc nâng toàn bộ retail fulfillment lên P0.

**Xác nhận tiếp theo:** lead B2C là lead của chính công ty chủ dự án, chưa chuyển đổi; không phải người tiêu dùng đối tác. Vì vậy pipeline lead trực tiếp thuộc AGENCY workspace và có trạng thái chưa phân loại/chưa liên hệ/đang xử lý theo thiết kế được chốt; không gọi tất cả lead là khách đã mua. Chỉ con số chính xác của dải B2C còn chưa rõ. Dữ liệu đơn hàng của đối tác là miền CLIENT riêng; không cộng hai tập thành một phễu hoặc lấy số đơn đối tác chia lead công ty để tính conversion.

Số đơn đối tác là dữ kiện workload tích hợp và outcome dịch vụ; không phải số lead, số khách mua dịch vụ hoặc doanh thu agency. Một đối tác có nhiều shop/chiến dịch/đơn; mỗi đơn là dữ kiện nguồn trong CLIENT workspace được cấp quyền. Phí dịch vụ và khoản phải thu agency ở AGENCY workspace/miền tài chính riêng. Attribution chỉ ghi confirmed/inferred/unknown theo bằng chứng; không nhận toàn bộ đơn shop là do chiến dịch agency tạo ra.

Mức tích hợp đề xuất:

1. **P0 nếu cần đo hiệu quả dịch vụ:** báo cáo tổng hợp theo đối tác/shop/kênh/kỳ, nguồn và freshness; nhập file có kiểm hoặc API đọc được cấp. Không bắt nhận PII hoặc mọi order nếu mục tiêu chỉ cần tổng hợp.
2. **Tiếp theo khi cần drill-down/đối soát:** bản chiếu order chỉ đọc, scoped external IDs, trạng thái/giá trị/hoàn-hủy và campaign link có evidence; dedup một đơn xuất hiện qua nhiều nguồn. Xác minh đối tác dùng sản phẩm Pancake nào và các kênh đã thực sự nằm trong đó; không suy mọi đơn sàn đều đã đồng bộ POS.
3. **Chỉ khi phạm vi hợp đồng yêu cầu:** task xử lý ngoại lệ/CSKH và thao tác ghi trở lại, có authority/approval/audit. Kho, đóng gói, vận chuyển và hoàn tiền không trở thành chức năng CRM agency chỉ vì biết số đơn.

Nguồn chính thức [Pancake POS — trạng thái đơn và luồng xử lý](https://docs.pancake.biz/pos/st-f13/st-p3?lang=vi) mô tả trạng thái dùng cho tích hợp Open API và phân biệt đơn bán với đơn hoàn/đổi. Đây là căn cứ khảo sát connector, chưa chứng minh tài khoản đối tác có API/quyền/webhook cụ thể. Cần PoC dữ liệu thật được phép, không mặc định webhook có sẵn.

Các mục 2–9 bên dưới giữ vai trò phân tích kịch bản trước khi biết quyền sở hữu shop. Những đề xuất tự quản lý fulfillment/inventory chỉ áp dụng nếu sau này công ty nhận trách nhiệm đó; không còn là hướng mặc định. SL01/SL02 cần xem lại theo quản lý dịch vụ và tích hợp kết quả chiến dịch, không tự thay bằng pipeline retailer. Master vẫn chưa sửa.

## 1. Dữ kiện và điều chưa rõ

Người dùng nêu “tối thiểu 500 - 100” lead B2C/tháng và “2000-5000 lead đơn hàng” trên TikTok Shop/Shopee. Cần xác nhận mốc B2C (có phải 500–1.000 không) và đơn vị trên sàn là lead/hội thoại/đơn hàng. Không chuyển số nhập mơ hồ thành baseline đã xác nhận.

Cần xác định shop do công ty sở hữu hàng và nhận tiền hay vận hành cho khách; phần mềm OMS/kho/ERP đang dùng; số shop, SKU, kho; đỉnh livestream/campaign; tỷ lệ hoàn/hủy; số người xử lý và số hội thoại/tin nhắn. Các dữ kiện này quyết định source ownership, capacity và phạm vi mua/tích hợp/tự xây.

## 2. Kết luận kiến trúc đề xuất

Thay đổi quan trọng trước hết là bổ sung miền bán lẻ giao dịch, không chỉ tăng thông số lead. Giữ Modular Monolith/PostgreSQL làm ứng viên nền; tách worker và hàng đợi theo loại tải để sự cố sàn không chặn sales hoặc finance. Chưa có căn cứ chọn microservices/sharding từ số đơn tháng.

Tách hai luồng vận hành:

- B2C cần tư vấn: intake → dedup đúng scope → phân công → tư vấn/follow-up → chốt hoặc mất → chăm sóc theo quyền/mục đích hợp lệ.
- Retail: order từ sàn → chuẩn hóa → xử lý fulfillment → tracking → hủy/hoàn/refund khi phát sinh → đối soát settlement. Một đơn mới không bắt buộc đi qua lead/deal, báo giá, SOW và project của agency.

Retail cần năng lực OMS nhưng CRM không nhất thiết phải tự xây OMS. Nếu đã có nền tảng vận hành đơn/kho đủ tốt, CRM nhận projection có nguồn và xử lý khách hàng/ngoại lệ; tránh nhân đôi nơi ghi tồn kho/trạng thái giao hàng. Nếu chưa có, PoC nền tảng OMS hoặc pack tối thiểu trước khi quyết định xây kho/fulfillment đầy đủ.

## 3. Source of truth và loại dữ liệu

| Đối tượng | Đề xuất owner |
|---|---|
| B2C lead, owner, next action | CRM sales |
| Shop authorization, capability, cursor | Integration M19 |
| External order và trạng thái nền tảng | Sàn là nguồn dữ kiện; CRM/OMS lưu snapshot/version/mapping |
| Fulfillment operation nội bộ | Một OMS được chỉ định; command tới sàn phải theo capability |
| Tồn khả dụng và reservation | Một inventory authority được chỉ định; không cho CRM/OMS/Excel cùng ghi tự do |
| Case khiếu nại, task xử lý ngoại lệ | CRM service/task, liên kết order/line/package |
| Settlement/fees/refund của sàn | Dữ liệu sàn + reconciliation; ERP sở hữu chứng từ đã hạch toán |

Giữ cả raw platform status và trạng thái nội bộ có mapping/version; không ép tất cả sàn dùng một enum mất ý nghĩa. Order/payment/fulfillment/return/settlement là các chiều trạng thái riêng. Delivered không tự nghĩa đã nhận tiền; refund status không tự nghĩa hàng đã nhập lại kho.

Identity nguồn có namespace platform/shop/buyer ID khi được cấp. Không gộp khách từ tên hiển thị hoặc số điện thoại bị che; không coi mua hàng là consent marketing. Quyền đọc order không tự cấp quyền nhắn tin hoặc lấy mọi dữ liệu khách. Các trường thực sự truy cập được cần xác minh trên từng app/shop/market.

## 4. Pack bán lẻ đề xuất, chưa cấp ID canonical mới

Giữ M01–M20; dùng namespace đề xuất `retail-commerce` cho năng lực chuyên ngành. Không đổi nghĩa bảng Orders dịch vụ hiện có thành đơn sàn bằng vài cột bổ sung chưa review.

| Capability | Nội dung | Mức đề xuất |
|---|---|---|
| Shop & SKU mapping | Shop/account grant; sản phẩm/biến thể và external IDs | P0 nếu vận hành retail trong release |
| Order intake | Webhook/poll theo API được cấp, dedup, backfill, reconcile | P0 |
| Order operations | Trạng thái, package, tracking, pending/canceled và exceptions | P0 theo mô hình tự vận hành/tích hợp OMS |
| Inventory | Availability/reservation/sync theo nguồn chuẩn | P0 nếu hệ thống nhận trách nhiệm tồn; nếu OMS ngoài thì mapping/sync controls P0 |
| After-sales | Return/refund/dispute, evidence và thời hạn nguồn | P0 cho phần nghiệp vụ được bật |
| Settlement | Phí, hoàn/điều chỉnh, khoản được thanh toán, discrepancy | P0 nhập/đối soát có kiểm soát; tự động hóa theo capability |
| Customer/work | Order history có ACL, task ngoại lệ, queue/SLA | P0 |
| Advanced planning | Forecast, tối ưu mua hàng, AI/attribution nâng cao | Sau baseline ổn định |

Không tạo task thủ công cho mọi order event. Đơn bình thường xử lý theo automation; task dành cho tình huống cần người quyết định, ví dụ thiếu mapping SKU, sắp trễ xử lý, hoàn hàng, lệch đối soát. Dedup theo exception key/episode để cùng lỗi không tạo nhiều việc.

## 5. Tác động M01–M20

M01 thêm identity/customer projection theo shop, bảo toàn ACL. M02 ưu tiên pool B2C, routing theo availability/capacity/skill, phân biệt lead mới và khách mua lại. M03 không trộn TikTok DM với TikTok Shop; order API không tự chứng minh inbox capability. M07 tách catalog dịch vụ và retail SKU/variant. M08 giữ contract/order dịch vụ riêng và typed retail link. M09 thêm reconciliation settlement nhưng không hòa GMV shop khách vào doanh thu agency. M10 commission nội bộ khác affiliate/platform fee. M11 thêm case order/return. M14 thêm shop grants và warehouse scope theo tổ chức thực. M16 làm hàng đợi công việc ngoại lệ. M17/M18 tách unit economics retail và agency. M19 thêm connector/order events/poll recovery. M20 kiểm dữ liệu được cấp, purpose và retention. M04/05/06 chỉ mở automation/loyalty/AI khi đủ điều kiện.

Nếu shop thuộc khách, giữ CLIENT workspace/ủy quyền, báo cáo GMV khách tách doanh thu agency. Nếu shop thuộc công ty, phải xác định chủ hàng/pháp nhân/kho và kế toán của công ty. Không tự đồng nhất shop với branch hoặc tenant; một doanh nghiệp có thể có nhiều shop trong một scope quản trị với grants riêng.

## 6. Quy mô và vận hành

Nếu 2.000–5.000 là đơn/tháng: trung bình khoảng 67–167 đơn/ngày theo tháng 30 ngày; 5.000/tháng tương đương 60.000 đơn/năm nếu giữ đều. Đây là phép tính số lượng, không phải benchmark hiệu năng.

Một đơn có nhiều line, package, message, event, return và settlement rows. Ví dụ giả định 10–30 event/đơn cho kiểm nhạy cảm tạo 20.000–150.000 event/tháng; con số này chưa đo và chưa gồm replay/backfill/chat/file. Đỉnh livestream và thời gian phục hồi sau downtime quyết định tải ngắn hạn hơn trung bình tháng.

Profile test cần: orders/minute peak theo shop; events/order; duplicate/out-of-order; backlog sau mất kết nối; concurrent users; line/package count; attachment; retention; provider quota. Test xử lý trong deadline với tải đo được và headroom đã quyết định. Chưa tự sửa NFR bằng cách nhân 10 mọi chỉ số.

Công thức staffing: tổng phút xử lý = số case × tỷ lệ cần người × số lượt × phút/lượt + việc follow-up/exception; chia phút làm việc hữu ích/người. Ví dụ 5.000 đơn × 10% ngoại lệ × 8 phút = khoảng 66,7 giờ/tháng riêng xử lý ngoại lệ. Chỉ là minh họa, không kết luận số nhân viên cần tuyển. Không dùng 30 Sales hoặc inbound chia đều như giả định 100 lead/tháng cũ.

## 7. KPI tách biệt

B2C: unique lead đủ điều kiện, FRT theo lịch, contact rate, qualified/win theo cohort, next-action overdue và cost per qualified outcome. Retail: orders theo trạng thái, cancel/return/refund rate với mẫu số rõ, xử lý/giao đúng hạn, inventory discrepancy, settlement discrepancy/age, contribution theo policy chi phí. Task: queue age, SLA của case, review age; không thưởng theo số task sinh ra.

Phân biệt gross order value, GMV theo định nghĩa sàn, net sales, settlement receivable và tiền đã nhận. Không chốt công thức doanh thu/lợi nhuận kế toán khi chưa có định nghĩa và chứng từ; bảng quản trị phải ghi nguồn, version, exclusions và freshness.

## 8. Lộ trình điều chỉnh

1. Chốt đơn vị khối lượng và sở hữu shop, kiểm kê hệ thống đang dùng; cập nhật change impact.
2. Chạy song song về mặt kế hoạch hai luồng ưu tiên: B2C intake/routing/follow-up và một shop order ingestion/read-only/reconcile; không cần hoàn thiện tất cả agency trước.
3. Bật xử lý ngoại lệ + task/SLA; kiểm ngày cao điểm và replay/downtime.
4. Bật command fulfillment/inventory/return theo ownership và quyền thực; tránh dual-write.
5. Hoàn thiện settlement reconciliation và báo cáo tách mảng; mở shop/sàn tiếp theo khi gate đạt.

SL01 internal work trước đây có thể thu hẹp thành nền task/review phục vụ ngoại lệ; không còn mặc định là ưu tiên giá trị đầu tiên. SL02 inbox phải tách message integration và commerce order integration. Các slice agency hợp đồng/SOW vẫn giữ nếu còn hoạt động nhưng xếp lại theo giá trị thực.

## 9. Thay đổi tài liệu sau khi đầu vào được xác nhận

Master: mục tiêu/volume 1.2–1.6; architecture 2.1; tích hợp 2.4 (Shop/Shopee hiện P2); domain catalog; UC/schema cho retail; scope grants; NFR/peak/recovery; dashboard; release profile/UAT; staffing/TCO và A.6. Không chỉ sửa con số ở đầu tài liệu.

Sau khi hợp nhất có CR và version mới: rebuild registry theo hash mới, cập nhật ownership/entity/contracts, roadmap/SL01/SL02 và active manifest. Các số 634/221 hiện là snapshot Master 1.7, không tái sử dụng như coverage của baseline retail mới. Các test ứng dụng vẫn Not Run.

## 10. Nguồn đối chiếu và giới hạn

- [TikTok Shop — OMS](https://partner.tiktokshop.com/docv2/page/order-management-system-oms): kết quả tài liệu chính thức mô tả OMS cho hoạt động sau khi đơn được tạo, có tham chiếu order APIs/webhook và phạm vi fulfillment. Phần trang mở trực tiếp yêu cầu JavaScript; chưa xác minh quyền tài khoản cụ thể.
- [TikTok Shop — transactions by order](https://partner.tiktokshop.com/docv2/page/get-transactions-by-order): tham chiếu tài chính riêng theo order; không tự đồng nhất trạng thái đơn với settlement. Trang đầy đủ yêu cầu JavaScript.
- [Shopee Open Platform](https://open.shopee.com/faq/92): công cụ đọc trang gặp HTTP 403 ngày 18/10/2026; chưa xác minh chi tiết endpoint, scope, quota hoặc quyền chat. Mọi capability Shopee trong báo cáo là nhu cầu cần PoC, không là lời xác nhận tài khoản đã hỗ trợ.

Đề xuất trên không đổi Master hoặc thực hiện kết nối/live command. Hai câu hỏi khối lượng và sở hữu shop đang chờ người dùng làm rõ.
