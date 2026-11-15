"""One-time authorized integration of M21 into Master 1.8; archives exact 1.7."""
from pathlib import Path
import re, hashlib, json, sys

sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
master=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
doc=root/'docs/delivery-plan/specs/modules/M21-PARTNER-BUSINESS-RESULTS.md'
archive=root/'docs/archive/CRM_MASTER_v1.7_BEFORE_PARTNER_RESULTS_2026-10-18.md'
raw=master.read_bytes()
before=hashlib.sha256(raw).hexdigest()
if before!='70c190232df3416680f3ee768288fa53230aa4b8cc131609fa4d9a933a97affb':
    raise SystemExit('Master differs from reviewed 1.7; do not re-run or overwrite changes.')
text=raw.decode('utf-8-sig')
spec=doc.read_text(encoding='utf-8')
blocks={k:v.strip()+'\n\n' for k,v in re.findall(r'<!-- MASTER:([^>]+) -->\s*(.*?)(?=<!-- MASTER:|<!-- END:MASTER -->)',spec,re.S)}
expected=['3.15','4.24','5.21','6.7','7.8','8.6','9.17','A.8']
assert set(blocks)==set(expected)
def replace_once(old,new):
    global text
    if text.count(old)!=1: raise AssertionError((old[:90],text.count(old)))
    text=text.replace(old,new,1)

replace_once('Phiên bản 1.7 — Hợp nhất quản lý công việc cá nhân, đội nhóm, tổ chức và dự án',
 'Phiên bản 1.8 — Hợp nhất kết quả kinh doanh đối tác, chia sẻ dữ liệu theo mức và lead công ty')
replace_once('Ngày 16 tháng 10 năm 2026  ', 'Ngày 18 tháng 10 năm 2026  ')
replace_once('Khối lượng đầu vào khoảng 100 lead và 50 khách hàng mỗi tháng, có khả năng tăng trưởng.',
 'Lead B2C của công ty hiện là đầu vào chưa phân loại/chuyển đổi; số lượng chính xác cần chuẩn hóa theo A.8. Đơn TikTok Shop/Shopee/Facebook thuộc đối tác dùng dịch vụ và đang dùng Pancake; kịch bản tạm 2.000–5.000 đơn/tháng chưa rõ mỗi đối tác hay tổng, không tính thành lead/doanh thu agency.')
replace_once('`CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản 1.7.', '`CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản 1.8.')
replace_once('Danh mục 20 module ở đầu Chương 3;', 'Danh mục 21 module ở đầu Chương 3;')
replace_once('Đây là 20 ranh giới nghiệp vụ logic, không phải 20 ứng dụng/dịch vụ phải xây.',
 'Đây là 21 ranh giới nghiệp vụ logic, không phải 21 ứng dụng/dịch vụ phải xây.')
replace_once('Đặc tả thiết kế BA hiện hành 1.7;', 'Đặc tả thiết kế BA hiện hành 1.8;')
needle='**Phiên bản 1.7 (16/10/2026):**'
replace_once(needle,'**Phiên bản 1.8 (18/10/2026):** CR-PARTNER-RESULTS-20261018 bổ sung FR41/M21; NONE/SUMMARY/FILE/API_READ theo quyền từng đối tác, source provenance/coverage/reconciliation/report versioning; giữ Pancake làm hệ thống vận hành đối tác. Baseline1.7 lưu archive. Có UC-P01–10, BR-P01–20, P-T01–40, P-NFR01–08 và A.8; chưa có code/UAT thực thi.\n\n'+needle)
replace_once('## Mục lục', '**Hợp nhất 1.8:** lead của công ty chưa chuyển đổi thuộc AGENCY; kết quả bán hàng của đối tác thuộc CLIENT được cấp quyền. M21 áp dụng theo mức chia sẻ: không cấp API vẫn có FILE/SUMMARY/NONE; không có dữ liệu không giả số0, không làm gián đoạn nghiệp vụ công ty. Core M21 ở3.15/4.24/5.21/6.7/7.8/8.6/9.17/A.8. M21 là quyết định thiết kế theo yêu cầu tích hợp, không phê duyệt mọi tham số/live connector.\n\n## Mục lục')
replace_once('- [Danh mục module và điều hướng BA](#danh-muc-module)', '- [Danh mục module và điều hướng BA](#danh-muc-module)\n- [M21 — Kết quả kinh doanh đối tác](#module-m21)')
replace_once('| A01 | 100 lead/tháng; 50 khách/tháng | Phân biệt khách đang phục vụ, khách mới và khách thanh toán. Không suy ra conversion 50% trước khi xác định cohort. |',
 '| A01 | Lead B2C công ty chưa phân loại; khối lượng mới chưa chuẩn hóa; đối tác có kịch bản2.000–5.000 đơn/tháng trên TikTok Shop/Shopee/Facebook | Không giữ100 lead/50 khách làm baseline; không suy conversion hoặc gộp đơn đối tác vào khách công ty; A.8/P-O01. |')
replace_once('| A03 | Kênh chưa được chỉ định | Đề xuất website/form, email công ty, Zalo OA, Facebook Page và tổng đài; chưa coi là hệ thống đang dùng. |',
 '| A03 | Đối tác dùng Pancake, có đơn TikTok Shop/Shopee/Facebook; sản phẩm/quyền/kết nối cụ thể chưa verified | Kênh lead công ty và kênh shop đối tác tách biệt; M21 nhận dữ liệu theo thỏa thuận, không coi mọi kênh đã có API/inbox. |')
replace_once('Chưa cần Kafka, Kubernetes hoặc lakehouse với 100 lead/tháng.',
 'Chưa có căn cứ thêm Kafka, Kubernetes hoặc lakehouse chỉ từ số đơn/tháng; đo peak, sốshop/event/backfill và quyền nguồn trước sizing.')
replace_once('| TikTok Shop và Shopee | Đơn/sản phẩm của khách thuê agency khi có ủy quyền | P2, pack thương mại điện tử riêng; không trộn GMV của khách với doanh thu agency [S07](#s07), [S08](#s08). |',
 '| Pancake và dữ liệu đơn TikTok Shop/Shopee/Facebook của đối tác | M21 nhận kết quả theo mức NONE/SUMMARY/FILE/API_READ, đối tác giữ vận hành đơn/kho | Core M21 P0 theo release; API_READ P1 hoặc CR mở sớm sau verified. Quản lý fulfillment/inventory riêng vẫn P2 khi có nhu cầu; không trộn GMV với doanh thu agency [S07](#s07), [S08](#s08). |')
catalog='| [M20](#module-m20) |'
line=next(l for l in text.splitlines() if l.startswith(catalog))
replace_once(line,line+'\n| [M21](#module-m21) | Kết quả kinh doanh đối tác và chia sẻ dữ liệu theo mức | AM, Analytics, partner reporter, data owner | Sharing profile/source binding/dataset/import/reconciliation/report snapshot/exception | M08/M14/M16/M18/M19/M20 | P0 NONE/SUMMARY/FILE và controls; API_READ/detail P1 theo quyền; không thay OMS đối tác |')
replace_once('không suy rằng20 module phải triển khai đủ trong MVP.', 'không suy rằng21 module phải triển khai đủ trong MVP.')
replace_once('100 lead/tháng chia 30 Sales chỉ khoảng 3,3 lead/người nếu phân đều, nên không mở cả 30 người nhận inbound ngay. Pilot pool 5 người, phân theo capacity và giữ nhóm chuyên ngành; tính toán capacity từ thời gian xử lý thật.',
 'Giả định100 lead/tháng không còn là baseline; chưa phân loại/conversion và volume mới chưa chuẩn hóa. Chọn pool pilot theo phút xử lý, follow-up, lịch/skill và tải đo được, không chia đều cho30 Sales hoặc lấy số đơn đối tác làm inbound công ty.')
for key,anchor in [('3.15','<a id="chuong-4"></a>'),('4.24','<a id="chuong-5"></a>'),('5.21','<a id="chuong-6"></a>'),('6.7','<a id="chuong-7"></a>'),('7.8','<a id="chuong-8"></a>'),('8.6','<a id="chuong-9"></a>'),('9.17','<a id="chuong-10"></a>'),('A.8','<a id="phu-luc-b"></a>')]:
    replace_once(anchor,blocks[key]+anchor)
trace='| NFR01–12 | Mọi luồng |'
line=next(l for l in text.splitlines() if l.startswith(trace))
replace_once(line,'| FR41 / M21 | UC-P01–10; chia sẻ dữ liệu theo mức | Partner profiles/datasets/imports/reports;6.7; BR-P01–20; scope M14/M20 | P-T01–40; P-NFR01–08;9.17; trạng thái Not Run |\n'+line)
replace_once('### 10.6 TCO bổ sung cho hợp nhất năm kênh',
 '### 10.6 TCO bổ sung cho hợp nhất năm kênh') if False else None
# Keep historical estimates but explicitly remove the obsolete workload assumption as a current commitment.
replace_once('Mô hình volume: 100 inquiry/tháng × 30 message/inquiry',
 '**Kịch bản lịch sử1.7, không là sizing baseline1.8:** Mô hình volume: 100 inquiry/tháng × 30 message/inquiry')
text+='\n\n## PHỤ LỤC I — Nguồn và kiểm soát thay đổi M21 ngày18/10/2026\n\n'+spec.split('## Nguồn đối chiếu và giới hạn\n',1)[1]+'\n\nBản module triển khai dẫn xuất: `docs/delivery-plan/specs/modules/M21-PARTNER-BUSINESS-RESULTS.md`. Master vẫn là nguồn chuẩn nghiệp vụ. Chuỗi tích hợp: CR-PARTNER-RESULTS-20261018 → FR41/M21 → UC-P/BR-P/schema/API/quyền/NFR/KPI → P-T. Bằng chứng kiểm tài liệu không thay kết quả UAT ứng dụng.\n'
if archive.exists(): raise SystemExit('Archive already exists; inspect before continuing')
assert all(f'### {k} ' in text for k in expected)
archive.write_bytes(raw)
master.write_text(text,encoding='utf-8',newline='\n')
print(json.dumps({'archived':str(archive),'before_sha256':before,'after_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'sections_integrated':expected},ensure_ascii=False,indent=2))
