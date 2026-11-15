# Kiểm định còn tồn tại — schema và tài chính trên Master 1.4

Phạm vi: đọc đối chiếu Chương 1–10 và các phụ lục của `CRM_MASTER_BRD_SRS_HOP_NHAT.md`, tập trung FR14–17, UC05–08/13, Chương 5 và các ca tiền. Đây là kiểm định đặc tả, chưa chạy PostgreSQL/ứng dụng/provider. Các bất biến đã có tại 3.13.4, 5.1, 5.14, 5.18–19 được tính là đã có; không báo lại thiếu obligation, refund reservation, cross-workspace bridge hoặc rounding largest remainder. Không có Blocker tuyệt đối ngăn mọi công việc phát triển; các Major dưới chặn đóng băng phần tài chính để code không phải tự đoán.

## Finding inventory

| ID | Mức | Vị trí và bằng chứng | Phản ví dụ / tác động | Quyết định |
| --- | --- | --- | --- | --- |
| FS-F01 | Major | 5.5 dòng1368: `Deals.commission_policy_id` FK `CommissionPolicies`, mô tả Snapshot. 5.12 dòng1478 và 5.18 dòng1585 lại định nghĩa `Policy_Snapshots`, `Commission_Pools`; không có dictionary cho `CommissionPolicies`. FR17, UC07/13. | Developer phải chọn tạo bảng không có hợp đồng, trỏ live policy hoặc snapshot. Sửa policy sau quote có thể khiến entitlement mới đọc rule khác nếu chọn sai. Đây là FK/semantics chưa thống nhất, không khẳng định phần mềm đang crash. | Chuẩn hóa pointer tới snapshot và giao policy cho từng line/pool; Deal chỉ giữ default, không thay attribution đã khóa. |
| FS-F02 | Major | 5.13 dòng1517 chỉ có `Finance_Periods.start/end/closed_at`; 5.12 dòng1481 có period_id; 5.14 dòng1523 chỉ nêu lock payment/obligation. 6.1 có close-period command nhưng chưa có contract atomic giữa post và close. U12/CEO-U23 chỉ thử sau khóa, không thử đồng thời. | T1 kiểm kỳ mở; T2 khóa kỳ, commit; T1 post bằng kết quả kiểm cũ. Một journal vào kỳ đã khóa vẫn đúng các mô tả lock payment hiện tại. Cũng chưa định nghĩa period có scope sổ/pháp nhân nào, ngày posting vs ngày sự kiện. | Bổ sung lock cùng hàng kỳ, scope kỳ, cutoff/outbox gate và UAT race. |
| FS-F03 | Major | 3.13.4 dòng944: công thức trừ mọi active refund reservation khỏi số dư đã trừ allocation. 5.18 dòng1601 cho reservation có allocation linkage; UC13 dòng1117–1118 bắt hợp đồng và luôn reversal allocation/commission negative. | Receipt100, allocated100, yêu cầu hoàn20 từ allocated: công thức đang cho `100−0−100−20=−20`, dù đây là hoàn hợp lệ và chưa trừ lần hai tại confirmation. Receipt100 chưa allocated và chưa biết contract lại không thỏa UC13, dù 3.13.4 cho hoàn dư không reversal. | Tách reserve tiền chưa phân bổ và reserve phần allocation đã có; đồng bộ UC13. Không cần lập hệ sổ kép mới. |
| FS-F04 | Major | 5.1 dòng1236 và Payments5.10 dòng1448 dùng numeric(18,2), char(3), amount>0; 5.11 dòng1464–65 chỉ >0/>=0; Commission5.12 dòng1479–80 dùng numeric không scale. Không có finite-number domain, supported-currency/quantum contract. | PostgreSQL cho numeric NaN và xếp NaN lớn hơn mọi số thường: CHECK amount>0 chưa loại NaN; NaN còn lan vào tổng. numeric có scale tự làm tròn input nhiều chữ số; currency bất kỳ được chấp nhận dù precision chỉ2. Đây là đặc tính DB trong tài liệu chính thức, chưa chạy DDL dự án. | P0 hỗ trợ VND rõ; validate số hữu hạn/quantum trước cast, finite domain/check và explicit rounding. Muốn thêm currency phải migration/PoC theo precision. |
| FS-F05 | Minor | U08 dòng1882 ghi Won chưa ứng trước → kickoff pending, không nói hợp đồng có yêu cầu cọc hay không; FR15 dòng531 cho credit/ngoại lệ hợp lệ. | QA có thể fail một kickoff hợp lệ bằng approved credit vì fixture không phân biệt. | Làm rõ tiền điều kiện và thêm nhánh credit, không đổi FR15. |

Không tính PipelineStages/Pipeline_Stages thành Major độc lập: có thể cùng ánh xạ snake_case, nhưng dictionary/OpenAPI phải dùng đúng một alias. UAT chưa có script/actual là trạng thái công việc phải thực hiện, không tự là lỗi phần mềm.

## Patch FS-F01 — pointer policy thống nhất

**Thay thế dòng `commission_policy_id` trong bảng Deals tại Mục5.5 bằng:**

| commission_policy_snapshot_id | uuid | FK Policy_Snapshots, NULL khi PendingPolicy hoặc chưa áp commission | Snapshot default được duyệt cho cơ hội; không trỏ rule live. Chính sách cuối áp dụng theo từng Order_Line/pool/eligible allocation; không đổi người hưởng lịch sử theo owner hiện tại. |

**Bổ sung sau bảng Commission_Entries tại Mục5.12:**

`Policy_Definitions` là định danh chính sách; `Policy_Versions` là phiên bản cấu hình Draft/Reviewed/Active; `Policy_Snapshots` đóng băng phiên bản và tham số đã duyệt tại sự kiện nghiệp vụ. Snapshot lưu `policy_version_id`, `snapshot_hash`, `effective_at`, `approved_by/at`, basis/rate/rounding/eligibility và scope áp dụng; đã được ledger tham chiếu thì không sửa. Không có bảng song song tên `CommissionPolicies`. Pointer mặc định trên Deal không thay snapshot gắn với line/pool/commission entry. Chưa có policy cho dòng/pool thì giữ `PendingPolicy`, không phát Earned/Payable hoặc tự tính0/full. Migration đổi tên field cũ giữ mapping và không tự chụp policy hiện hành để thay snapshot lịch sử chưa xác định.

**Bổ sung ca sau RV20 tại Mục9.13:**

| FA01 | Quote/line dùng snapshot A; policy version B có hiệu lực sau thu tiền hoặc owner đổi | Ledger cũ giữ A và người hưởng cũ; dòng chưa khóa policy vào PendingPolicy; FK đích tồn tại đúng scope, không trỏ bảng alias chưa định nghĩa |

## Patch FS-F02 — khóa kỳ và post cùng contract

**Thay thế dòng gộp Audit_Logs, Finance_Periods tại Mục5.13 bằng hai dòng:**

| Audit_Logs | actor_id uuid, action text, target_id uuid, correlation_id uuid, reason/evidence | Append-only, redact PII; không xóa/sửa để thay correction nghiệp vụ. |
| Finance_Periods | legal_entity_id uuid NN, ledger_kind text NN, period_start/period_end date NN, status Open/Closed, closed_at timestamptz NULL, closed_by uuid NULL, close_watermark text NULL, row_version bigint NN | Kỳ `[period_start,period_end)` theo timezone pháp nhân, end>start; không chồng lấn trong tenant/workspace/legal entity/ledger_kind. `Closed` phải có actor/time và đối soát đóng kỳ. |

**Bổ sung sau đoạn transaction tại Mục5.14:**

Mọi lệnh post/adjust/reverse/payout và close-period thuộc cùng sổ phải khóa cùng `Finance_Periods` row trong transaction, kiểm trạng thái sau lấy lock rồi mới ghi ledger/outbox hoặc đóng kỳ. Thứ tự lock thống nhất là kỳ theo khóa scope/ID ổn định → receipt → obligation/allocation → commission/payout aggregate; lệnh nhiều kỳ khóa theo cùng thứ tự. Không giữ lock khi gọi provider. `close-period` chỉ commit khi các đối soát bắt buộc và financial events tới `close_watermark` đã xử lý hoặc được lập danh sách ngoại lệ có thẩm quyền; không đóng dựa vào read model có thể trễ.

Ledger post có `period_id`, `posting_date` theo timezone kỳ và `source_occurred_at/received_at` riêng; `posting_date` phải trong kỳ đã chọn và kỳ còn Open tại commit theo lock contract. Sự kiện đến muộn/refund sau khóa ghi adjustment ở kỳ mở được Finance chọn, giữ link entry/kỳ/sự kiện gốc; không đổi ngày sự kiện hoặc tự mở lại kỳ đóng. Period selection không được dùng ngày nhận webhook để viết đè lịch sử kinh tế. Bảng ERP sở hữu thì mapping và quyền đóng kỳ theo ERP; CRM không tạo bản kỳ đối lập.

**Bổ sung ca tại Mục9.13:**

| FA02 | T1 chuẩn bị post, T2 close-period cùng kỳ; đổi thứ tự lấy lock hai lần | Chỉ một thứ tự commit hợp lệ: post trước rồi close có đối soát, hoặc close trước làm post từ chối/route adjustment kỳ mở; không có entry chèn vào kỳ đã đóng |
| FA03 | Allocation đã commit nhưng consumer commission còn pending ở cutoff | Close kiểm watermark và xử lý/ngoại lệ có audit; event tới muộn không âm thầm post về kỳ đóng; kỳ khác pháp nhân không chặn hoặc nhận nhầm entry |

## Patch FS-F03 — tiền hoàn chưa và đã phân bổ

**Thay thế bullet bắt đầu “Hoàn tiền dư chưa phân bổ” tại Mục3.13.4 bằng:**

- Hoàn tiền khóa receipt và phần số dư/allocations gốc, giữ reservation theo từng phần tiền trước khi gọi provider. Gọi `C` là confirmed incoming của receipt, `R` là confirmed refunds, `A` là tổng Allocate trừ Reverse còn hiệu lực, `Ru` là active reservations cho tiền chưa phân bổ và `Ra(a)` là active reservations giữ phần của allocation `a`. `AvailableToAllocate = C − R − A − Ru >=0`. Không trừ `Ra` lần nữa vì tiền đó vẫn nằm trong `A`. Mỗi `Ra(a)` không vượt phần hiệu lực chưa được reserve của allocation `a`; mọi reverse/reallocate phải bảo vệ phần đang reserve. Tổng refund đã xác nhận cộng toàn bộ reservation đang hiệu lực không vượt receipt còn được hoàn, cùng currency/pháp nhân/party authority.
- Reservation hoàn dư có allocation_id NULL và chỉ được tạo nếu `Ru_new <= C−R−A−Ru_existing`. Reservation hoàn phần đã phân bổ trỏ allocation gốc và cấu phần trả lại, không giải phóng allocation trước khi có kết quả xác thực. Một yêu cầu hoàn nhiều allocation có nhiều reservation lines cùng operation_id, mỗi line có item_key duy nhất; không cần bảng tài chính tổng quát mới. Khóa idempotency có scope receipt/operation/item và request hash; cùng key khác amount/beneficiary/body trả409.
- Confirmation hoàn dư cập nhật một Refund canonical, kết thúc reservation dư trong cùng transaction, không tạo Reverse allocation hoặc commission reversal nếu chưa phát sinh. Confirmation hoàn allocated cùng transaction ghi Refund, Reverse đúng allocation/components và kết thúc reservation: `R` tăng x, `A` giảm x nên available không đổi. Phát outbox để đảo đúng commission gốc đủ điều kiện theo policy/kỳ; không đảo media/tax thành service commission. Nếu giảm nghĩa vụ thương mại thì dùng Obligation_Adjustment/ERP credit có căn cứ riêng; refund không tự quyết định nghĩa vụ đã hết.
- Timeout/provider unknown giữ reservation và case reconcile; TTL đến hạn chỉ tạo cảnh báo/review, không tự giải phóng khoản có thể đã chi. Release chỉ sau kết quả xác thực không chi hoặc quyết định giải quyết có evidence/authority; retry cùng operation không tạo khoản hoàn mới. Provider call luôn ngoài DB transaction.

**Thay thế dòng Refund_Reservations tại Mục5.18 bằng:**

| Refund_Reservations | original_payment_id NN, operation_id/item_key NN, allocation_id NULL khi hoàn dư, amount>0, currency, component snapshot, beneficiary/evidence, request_hash, state Reserved/Dispatching/Unknown/Confirmed/Released/Rejected, expires/reconcile_at | Unique tenant/workspace/receipt/operation/item; allocated reservation giữ phần allocation chưa được reserve, unallocated reservation giữ available cash. Chuyển Confirmed cùng ghi Refund/reversal áp dụng, không double-subtract. Unknown quá hạn không tự nhả. |

**Thay thế các dòng Đầu vào/Luồng chính/Đậu rớt của UC13 tại Mục4.13 bằng:**

| Đầu vào và tiền điều kiện | Receipt Confirmed và evidence, số còn được hoàn, beneficiary đã xác minh, reason và refund authority; Contract/obligation/allocations chỉ bắt buộc theo phần hoàn tương ứng. Khoản chuyển nhầm/unidentified có thể hoàn qua case xác minh tài chính mà không tạo Contract giả. |
| Luồng chính | Xác định hoàn dư/hoàn phần allocation hoặc hỗn hợp → lock và kiểm số dư/components → reserve theo3.13.4 → duyệt theo authority → dispatch ngoài transaction → xác thực kết quả → ghi Refund và kết thúc reservations atomic; chỉ phần đã allocate mới Reverse allocation và phát commission adjustment đủ điều kiện → đối soát. |
| Đậu rớt và rẽ nhánh | Unknown giữ reservation và reconcile. Hoàn dư không có allocation/commission thì không tạo reversal giả. Kỳ khóa ghi adjustment kỳ mở có link, không sửa payout/kỳ cũ. Thiếu beneficiary/authority hoặc không đủ refund headroom thì giữ case, không dispatch. |

**Bổ sung ca tại Mục9.13:**

| FA04 | Receipt100, allocated100; reserve allocated refund20; đồng thời lệnh allocate/reverse khác | Available vẫn0, không−20; phần20 đã reserve không được dùng lại. Confirmed refund làm R=20/A=80; available0; replay không nhân refund/reversal |
| FA05 | Receipt100 chưa allocated, không có Contract, reserve hoàn20 và allocate90 đồng thời | Chỉ kết quả giữ bất biến được commit; refund hợp lệ không cần Contract giả và không sinh commission negative giả; Unknown không tự nhả khi hết TTL |

## Patch FS-F04 — monetary domain và giới hạn currency thực dụng

**Bổ sung cuối đoạn đầu Mục5.1:**

P0 chỉ kích hoạt currency `VND`; đây là ranh giới MVP được đề xuất để chốt, không phải hệ thống đã hỗ trợ mọi mã char(3). Chỉ bật currency khác sau CR có precision/minor-unit exponent, rounding/cap, connector/ERP mapping, DDL migration và UAT tương ứng. Không cộng tiền khác currency hoặc chuyển FX ngầm.

Mọi amount/quantity/rate/share tính tiền phải là số hữu hạn; API/import/connector từ chối NaN và ±Infinity trước ghi. Tại PostgreSQL dùng domain hoặc CHECK rõ `value NOT IN ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)` bên cạnh NULL/range policy; không coi `amount>0` là đã chặn NaN. Với cột numeric(18,2), Infinity bị giới hạn precision cũng không thay việc validate finite xuyên API và các cột numeric không ràng precision. Trước cast sang kiểu storage, parse Decimal chính xác, kiểm range/quantum và reject dữ liệu không hợp lệ; không để phép coercion của cột âm thầm làm tròn chứng từ nhập.

Giá/quantity/rate trung gian có precision do pricing policy quy định; các amount đã post VND phải là số nguyên đồng. Rounding chỉ diễn ra tại bước nghiệp vụ được snapshot theo3.13.4; khi đã post, các cấu phần và tổng phải khớp integer units. Invoice ERP giữ nguyên số nguồn, sai quantum được reconcile, không tự sửa chứng từ. Mở rộng currency có quantum nhỏ hơn khả năng storage hiện tại bắt buộc sửa schema trước enable; không chỉ thêm mã currency.

**Bổ sung ca tại Mục9.13:**

| FA06 | Import/API gửi NaN/Infinity, số vượt range hoặc amount VND phân số không được policy cho phép; currency chưa bật | Từ chối trước cast/post với mã lỗi rõ; không tạo ledger NaN hoặc silently round. Giá/rate trung gian hợp lệ vẫn được tính bằng Decimal rồi round đúng bước; currency chưa supported không bị nhận chỉ vì char(3) hợp lệ |

## Patch FS-F05 — fixture UAT (Minor, có thể áp cùng)

**Thay dòng U08 tại9.5 bằng:**

| U08 | UC06 | Won; điều khoản bắt buộc ứng trước; chưa đủ cọc và không có approved credit/start exception | Order có thể tạo; Paid không bật; kickoff pending. Nhánh approved credit/ngoại lệ còn hiệu lực chỉ mở đúng công việc được duyệt, không tự cho chi media. | P0 |

## Căn cứ kỹ thuật và mức chứng minh

[PostgreSQL Numeric Types](https://www.postgresql.org/docs/current/datatype-numeric.html) mô tả declared scale tự round input, numeric hỗ trợ NaN và thứ tự so sánh đặc biệt; đây là lý do cần finite/quantum validation, không phải kết quả test DB dự án. [PostgreSQL Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html) mô tả row locks và yêu cầu thứ tự nhất quán; contract post/close ở trên là thiết kế đề xuất cho bất biến kỳ của dự án. Phản ví dụ100/100/20 là phép số học trên chính công thức1.4. Cần integration test với hai connection/transaction thực sau khi xuất DDL; không ghi pass vào Master từ kiểm định này.
