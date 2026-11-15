# Kiểm định bổ sung Security/Privacy — Master 1.4

Ngày rà soát: 15/10/2026. Đầu vào: `CRM_MASTER_BRD_SRS_HOP_NHAT.md`, phiên bản 1.4, 2.799 dòng. Đây là báo cáo làm việc cho lần kiểm định, không phải Master thứ hai. Các dòng bên dưới thuộc bản 1.4 trước các thay đổi của vòng audit này.

## Phạm vi và kết luận có điều kiện

Đã đối chiếu FR02/08/09/13/21/30–40, UC11/12/14/18/19/21, Chương 5–7, các UAT liên quan và các quyết định đã sửa trong Phụ lục F. Không báo lại các điểm đã được sửa: transaction-scoped RLS, consent provenance, no-OR consent, same-workspace và bridge có kiểm quyền, AI training khác retention, DSAR không dùng một hạn 72h, legal incident không đợi Confirmed.

Có sáu điểm Major còn thiếu hợp đồng kỹ thuật hoặc mâu thuẫn có thể tái hiện bằng kịch bản thiết kế. Không có bằng chứng để tuyên bố hệ thống đã bị khai thác hoặc vi phạm pháp luật: chưa có implementation, PoC hay kiểm thử chạy thật. Cho phép tiếp tục thiết kế/coding nền; chưa nghiệm thu các capability bị ảnh hưởng trước khi chốt và kiểm các bản vá. Không cấp chứng nhận tuân thủ pháp lý 100% từ việc đọc SRS.

| Mã | Mức | Vị trí chính | Vấn đề còn lại | Điều kiện áp dụng |
| --- | --- | --- | --- | --- |
| SEC01 | Major | 2.6 dòng226; 2.7 dòng267–275; FR30 dòng727–736; 5.16 dòng1539 | Chưa ràng buộc callback OAuth với người khởi tạo, scope đích và tài khoản ngoài được xác minh | Trước bật connector OAuth |
| SEC02 | Major | 5.16 dòng1539; 2.7 dòng273; UC17 dòng1167–1171 | Unique connection gồm workspace cho phép một tài khoản nguồn đồng thời thuộc hai workspace; thiếu quy tắc chủ quyền/routing | Trước dùng hơn một workspace hoặc reconnect account |
| SEC03 | Major | FR37 dòng814; 6.2 dòng1655; UC12 dòng1108; U16 dòng1890 | ACL chỉ ở lúc cấp URL không bảo đảm URL storage cũ hết quyền sau offboarding | Trước chia sẻ file bảo mật |
| SEC04 | Major | 2.7 dòng273; FR40 dòng847; 5.16 dòng1545; 6.2 dòng1655 | Quét malware không ngăn SSRF ở bước fetch remote attachment/preview | Khi adapter/backend fetch URL |
| SEC05 | Major | FR09 dòng439; FR34 dòng771–780; FR40 dòng847; 6.3 dòng1675/1682 | Email marketing có consent gate nhưng chưa có unsubscribe delivery path, trạng thái deliverability và sender activation gate | Khi bật email marketing; không bắt xây campaign engine cho email giao dịch |
| SEC06 | Major | FR21 dòng617; 5.18 dòng1580; 6.1 dòng1644–1651 | Quyền cấp/sửa role và team grant chưa có người cấp, giới hạn ủy quyền, kiểm tự nâng quyền | Trước bật nhiều user/quản trị phân quyền |

## SEC01 — OAuth callback không được coi là yêu cầu cấu hình bình thường

**Bằng chứng:** 2.6 quản lý token/vault/refresh; 2.7 mô tả authorization lifecycle và inbound mapping. Không có quy định chống callback CSRF/account-linking, token code injection hoặc binding phiên khởi tạo với workspace đích. `Channel_Connections` có `external_account_id` nhưng chưa bắt xác minh giá trị qua provider trước ghi Active.

**Kịch bản:** Operator mở kết nối CLIENT A, callback mang state/session khác hoặc dữ liệu đích do trình duyệt sửa sang CLIENT B. Lưu token an toàn trong vault vẫn không sửa được việc gắn nhầm tài khoản và chuyển tin nhắn vào phạm vi sai.

**Căn cứ bên ngoài:** RFC 9700 §2.1 yêu cầu chống CSRF và mix-up cho redirect flows; public client phải dùng PKCE; confidential client được khuyến nghị PKCE. Provider cụ thể có thể có flow/khả năng khác, phải ghi rõ. [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html).

**Bổ sung sau đoạn đầu Mục 2.6:**

> **Authorization binding:** Khởi tạo/reconnect chỉ bởi principal có quyền quản trị connection trong scope đích. Authorization attempt lưu server-side actor/session, tenant/workspace, connection, provider, expiry và trạng thái dùng một lần. Callback kiểm CSRF binding và provider; redirect đích được cấu hình trước. Dùng PKCE S256 khi flow/provider hỗ trợ theo hợp đồng đã xác minh; không fallback âm thầm bỏ kiểm bảo vệ. Sau exchange, server đọc external account/scopes từ provider và so với account dự kiến trước Active. Callback sai/đã dùng/hết hạn bị từ chối; reconnect không tự đổi chủ workspace. Không tin tenant/workspace/account do query hoặc form khách gửi.

**Bổ sung dòng tại Mục 9.13:**

| SEC-U01 | Callback khác phiên/scope/provider, callback replay; reconnect chọn account khác | Reject, không sửa connection/token hiện hữu; account/scopes được xác minh trước Active. Provider không hỗ trợ cơ chế yêu cầu phải có flow thay thế đã review, không tắt kiểm tra. |

## SEC02 — Một external account cần một chủ quyền nguồn rõ ràng

**Bằng chứng:** Unique tại 5.16 dòng1539 là `tenant/workspace/provider/external_account_id`. Do workspace ở trong key, cùng account ngoài có thể tồn tại hai connection ở hai workspace của cùng tenant. 2.7 dòng273 chỉ nói suy scope từ connection; chưa xác định khi cùng subscription/account phát event tới nhiều connection hoặc khi reassignment account.

**Kịch bản:** Page P của khách A được nối vào CLIENT A; operator nối lại P vào CLIENT B. Cả hai row thỏa unique. Nếu cùng subscription/event được nhận hai lần theo hai mapping, mỗi `Inbound_Events.connection_id` có key riêng nên dedup không ngăn nhập chéo. Đây là đường thiết kế có thể xảy ra, không khẳng định provider luôn fanout như vậy.

**Quyết định thiết kế đề xuất:** Quy mô hiện tại dùng một connection sở hữu một account trong một workspace; nhiều inbox của connection vẫn hợp lệ. Không cần xây multiplexing engine. Namespace phải theo định nghĩa provider/app, không ép một ID toàn cầu khi provider cấp ID theo app/region.

**Thay ô Ràng buộc/ý nghĩa của `Channel_Connections` tại Mục 5.16 bằng:**

> Connection giữ một owner workspace bất biến khi Active. Trong một tenant, tại một thời điểm chỉ một connection Active/Degraded/ReauthorizationRequired sở hữu `(provider, provider_namespace, external_account_id)`; `provider_namespace` gồm app/region hoặc phần namespace provider thực sự dùng. Cưỡng chế bằng key/registry unique và transaction khi activate/reconnect; không chỉ unique theo workspace. Nhiều Inbox nội bộ được dùng chung một connection. Muốn chuyển chủ phải pause ingest/send, kiểm ủy quyền/account, chốt cursor và pending intents, revoke grant cũ rồi chuyển có audit/migration; không tự chép lịch sử sang khách mới. Multiplexing nhiều workspace chỉ mở khi có routing/publish policy riêng đã kiểm isolation; mặc định không hỗ trợ. Secret giữ trong vault; capability có checked_at/evidence.

**Bổ sung vào Mục 2.7:**

> Webhook resolver kiểm chữ ký và account/subscription nằm trong connection mapping được sở hữu; không dùng riêng callback URL hoặc connection ID do người gọi tự khai để quyết định workspace. Chuyển mapping không làm raw event cũ thay workspace; event giữ scope nguồn ban đầu.

> **Error envelope:** API không trả raw PostgreSQL DETAIL, tên constraint, giá trị field, ID hoặc số lượng bản ghi ngoài scope qua lỗi unique/FK. Với tài nguyên không được phép xác nhận tồn tại, dùng phản hồi nhất quán theo chính sách404/403 đã chốt; thông báo account nguồn đã được quản lý không nêu workspace/người sở hữu không có quyền xem. Log kỹ thuật chứa diagnostic được hạn chế theo quyền hỗ trợ và redact. Các key/FK vẫn kiểm toàn vẹn; không coi RLS là cơ chế che mọi thông tin từ lỗi ràng buộc. [PostgreSQL Row Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) lưu ý unique/FK checks bypass row security để bảo toàn integrity, có thể tạo covert channel.

**Bổ sung dòng tại Mục 9.13:**

| SEC-U02 | Đồng thời activate cùng Page/OA/mailbox vào hai CLIENT workspace, rồi reconnect/move account; gửi ID/key target ngoài quyền | Một activation thắng; activation còn lại conflict rõ nhưng không lộ owner/workspace ngoài quyền. Không nhập hai bản event khác scope; move có quy trình, lịch sử giữ scope gốc; lỗi FK/unique không trả raw DETAIL. |

## SEC03 — URL ký là bearer capability, khác session của nhân viên

**Bằng chứng:** FR37 và6.2 kiểm ACL khi cấp URL, dùng URL ký ngắn hạn. UC12 dòng1108 lại yêu cầu URL cũ không đọc được sau revoke. App session revoke không tự vô hiệu một URL được storage ký bằng service principal.

**Kịch bản:** Sales lấy URL 5 phút, nghỉ việc một phút sau. API đã trả403 nhưng storage còn chấp nhận URL đã ký; sao chép link cho người khác cũng không đi qua API ACL. “Ngắn hạn” chưa có số và chưa có cơ chế revoke tương ứng.

**Căn cứ:** AWS mô tả presigned URL là bearer token; hiệu lực gắn expiry và credentials/policy ký. Việc revoke app user tự nó không tương đương revoke credentials của storage signer. [AWS S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).

**Bổ sung cuối đoạn đầu Mục 6.2; cập nhật mô tả URL tại FR37 theo cùng quy tắc:**

> **Download và revoke:** File PII, hợp đồng, ghi âm, dữ liệu tài chính và export nội bộ đi qua download gateway kiểm session/principal, object ACL, scan status và grant hiện tại ở mỗi request, kể cả Range/resume. Không trả raw storage presigned URL cho nhóm này; không cache public nội dung bảo vệ. URL gateway mang token không thay session/ACL và không mở rộng scope. Sau commit revoke, request download mới hoặc Range mới phải bị từ chối; byte đã tải hoặc stream đã được cấp trước revoke không thể thu hồi chắc chắn. Asset publish cho khách dùng share grant riêng đúng recipient/resource/expiry; nếu chọn bearer link phải hiển thị rõ tính chất có thể chuyển tiếp và có cơ chế revoke ở gateway. Hệ lưu trữ chỉ chấp nhận yêu cầu từ gateway/service được phép.

**Thay ô Tiêu chí nghiệm thu UC12 tại Mục4.12 bằng:**

> Sau commit khóa user/revoke grant, token phiên cũ và mọi request download mới qua URL gateway cũ bị từ chối; thử cả Range/resume, cache, tab khác và link copy. Lịch sử actor giữ nguyên. Không yêu cầu thu hồi byte người dùng đã tải.

**Thay kết quả U16 và bổ sung SEC-U03 tại9.13:**

| SEC-U03 | Cấp link file nhạy cảm, revoke user/grant, thử GET/Range/link copy không session | Request mới bị từ chối; cache không trả nội dung. Tài liệu publish chỉ đọc qua share grant riêng còn hiệu lực. |

## SEC04 — Fetch attachment cần kiểm mạng trước quét nội dung

**Bằng chứng:** Mục2.7 có fetch; FR40/6.2 kiểm MIME, nén và malware nhưng không có contract cho URL từ provider/payload. Antivirus chỉ kiểm nội dung sau khi HTTP request đã được gửi.

**Kịch bản:** Payload hoặc URL attachment trỏ cloud metadata/localhost, hoặc host hợp lệ redirect sang mạng riêng. Worker có credentials/network nội bộ bị dùng làm proxy. Không khẳng định provider cụ thể cho tùy chỉnh mọi URL; áp cho mọi nhánh có backend fetch.

**Căn cứ:** OWASP SSRF Prevention khuyến nghị kiểm địa chỉ đích và kiểm soát redirect; input URL có thể vượt validation qua redirect/DNS. [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).

**Bổ sung sau đoạn FR40 tại Mục3.12.11:**

> **Remote fetch:** Dùng media endpoint/provider SDK được xác minh và allowlist endpoint theo connector; không cho khách tự chọn endpoint fetch tổng quát. Worker chỉ dùng HTTPS phù hợp provider, kiểm host/IP sau resolve và từng redirect; chặn loopback, link-local/metadata, mạng riêng và reserved ranges trừ integration nội bộ đã được thiết kế riêng. Redirect mặc định tắt; trường hợp provider cần redirect phải kiểm lại từng hop, không forward token sang host mới. Egress/network policy bảo vệ bổ sung chống DNS rebinding; không dựa kiểm chuỗi URL đơn lẻ. Giới hạn timeout, số redirect, byte tải và decompression; lỗi đưa quarantine, không cho preview/download. Credential provider chỉ gửi tới host/endpoint được phép. Chốt allowlist/quota cụ thể trong connector manifest trước bật; không cần crawler hoặc proxy URL tùy ý.

**Bổ sung dòng tại Mục9.13:**

| SEC-U04 | URL localhost/metadata/private IPv4+IPv6, redirect từ host hợp lệ sang private, DNS đổi IP và file quá cỡ | Không chạm đích mạng bị cấm/không lộ token; quarantine hoặc reject có audit metadata; worker tiếp tục xử lý event hợp lệ. |

## SEC05 — Suppression có gate nhưng chưa có đường vào từ email recipient/provider

**Bằng chứng:** 6.3 có suppression chung; chưa có cấu hình unsubscribe URL/action, inbound yêu cầu từ chối email, bounce/complaint reducer hoặc điều kiện sender authentication. Consent hợp lệ không bảo đảm endpoint vẫn có thể nhận thư; người nhận có thể hủy qua email header/body/provider và không đăng nhập CRM.

**Kịch bản:** Recipient hủy nhận email bằng phương thức provider hỗ trợ; event chưa được ánh xạ sang suppression nên journey vẫn gửi. Hoặc SMTP tiếp tục retry hard-bounced address, làm xấu reputation cho cả mailbox phục vụ khách.

**Căn cứ:** Gmail yêu cầu SPF hoặc DKIM cho mọi sender tới tài khoản Gmail cá nhân; nhóm bulk sender có yêu cầu bổ sung, gồm SPF+DKIM/DMARC và one-click unsubscribe cho marketing/subscribed mail. Không áp ngưỡng bulk 5.000 thư/ngày cho mọi email báo giá ở quy mô pilot. [Google sender guidelines](https://support.google.com/mail/answer/81126?hl=en). NĐ91/2020 có quy tắc riêng cho email quảng cáo và từ chối, phải được pháp lý kiểm văn bản hiện hành/tình huống áp dụng; không dùng riêng Luật dữ liệu cá nhân thay toàn bộ luật chống spam. [NĐ91/2020 bản Chính phủ](https://vanban.chinhphu.vn/default.aspx?docid=200773&pageid=27160), [bản Công báo](https://congbao.chinhphu.vn/tai-ve-van-ban-so-91-2020-nd-cp-31908-32282?format=pdf).

**Bổ sung vào FR34 tại Mục3.12.5:**

> **Email eligibility:** Manifest phân biệt email giao dịch/phục vụ yêu cầu và email marketing; sender domain/From/Reply-To được xác minh và có bằng chứng DNS/provider authentication phù hợp nơi nhận. Không tự bật marketing từ mailbox dùng báo giá. Trước mở marketing, chốt quy tắc chống spam hiện hành, nội dung nhận diện và cách từ chối; triển khai unsubscribe trong body và one-click headers khi luật/provider/product yêu cầu. Unsubscribe token ràng buộc endpoint/purpose/sender scope, không chứa PII rõ và không đòi đăng nhập CRM; không cung cấp hồ sơ cá nhân. Yêu cầu từ chối qua các kênh hợp lệ và provider unsubscribe event cùng đi vào suppression authoritative idempotent tại6.3. Không dùng bước xác minh tài khoản nặng như DSAR để cản từ chối.
>
> Bounce/complaint được xác minh từ provider, dedup và lưu delivery event theo connection/message/endpoint. Hard bounce chặn endpoint; soft bounce có retry/backoff/expiry theo provider policy đã chốt; complaint chặn marketing theo phạm vi xác định. Đây là delivery/safety suppression, không tự giả thành consent Revoke của mọi mục đích hoặc mọi khách dùng chung địa chỉ. Mọi dispatch kiểm cả consent và delivery suppression hiện tại. Reimport/replay không tự xóa suppression; khôi phục endpoint có workflow/evidence. Thông báo giao dịch chỉ tiếp tục khi còn cơ sở và endpoint gửi được; không lách nhãn Transactional để gửi quảng cáo.

**Bổ sung dữ liệu tối thiểu tại Mục5.18 (có thể ánh xạ ESP):**

| Email_Delivery_Events, Endpoint_Suppressions | connection/message/contact_point refs; provider event ID; event_type; reason; purpose/sender scope; occurred/received; source/evidence; effective/released_at | Event append-only và idempotent; suppression current-state có provenance; từ chối khác hard-bounce khác consent; cập nhật atomically trước dispatch tiếp. |

**Bổ sung dòng tại Mục9.13:**

| SEC-U05 | Unsubscribe qua body/header/provider khi journey đang đợi; hard-bounce/complaint trùng rồi import lại | Marketing không gửi tiếp; không lộ hồ sơ hoặc đòi login; không tự hồi sinh endpoint khi import. Soft bounce tuân retry/expiry; provider/sender authentication đạt trước bật gửi. |

## SEC06 — Bảo vệ quyền cấp quyền

**Bằng chứng:** Entity_Team_Grants có user/team/actions/time, và6.1 hạn chế Admin đọc nghiệp vụ. Chưa có contract ai được cấp/sửa role binding, team membership, grant, field policy, break-glass; thay role/config có thể làm vô hiệu tuyên bố “Admin không mặc nhiên đọc”. Đây là thiếu authorization của control plane, không phải khẳng định mọi Admin chắc chắn nâng quyền được.

**Kịch bản:** Admin không đọc bảng hợp đồng nhưng có quyền cấu hình; tự thêm role Finance hoặc thêm mình vào Project team. Worker/search tuân ACL mới hoàn toàn, nên các lớp row policy không phát hiện việc cấp quyền trái thẩm quyền.

**Bổ sung sau đoạn Mục6.1 dòng1651:**

> **Thẩm quyền cấp quyền:** Quản lý users/teams/role bindings, resource grants, field policies và break-glass là các action riêng, không suy từ quyền cấu hình connector hoặc sửa bản ghi. Mỗi grant/policy change lưu grantor, authority/approval, resource/actions/fields, thời hạn và reason; server kiểm quyền cấp trên đúng scope. Người cấp không được tự cấp thêm quyền nhạy cảm hoặc ủy quyền vượt authority đã được phê duyệt; membership update không là đường vòng. Khi có đội ngũ, thay quyền tenant-wide, tài chính, privacy/export và break-glass cho chính mình cần người có thẩm quyền khác duyệt; chế độ cá nhân được khai báo rõ, owner chấp nhận kiêm nhiệm và giữ audit, không giả có separation of duties. Revoke/cấp mới cập nhật permission version và consumer theo contract hiện có. Technical Admin chỉ triển khai policy đã duyệt, không mặc nhiên được tự cấp business access. Dữ liệu support khi cần dùng grant TTL đúng phạm vi.

**Bổ sung vào ô Ràng buộc của Entity_Team_Grants tại5.18:**

> Có grantor_id, authority/approval_ref, reason, created/revoked_at; command kiểm quyền grant riêng, không chỉ quyền U resource. Cấm cấp lại grant trùng chỉ để né expiry/deny; membership và policy changes dùng cùng quy trình.

**Bổ sung dòng tại Mục9.13:**

| SEC-U06 | Admin connector tự gán role Finance, manager cấp quyền ngoài branch, user tự thêm team, tự kéo dài break-glass | Từ chối nếu thiếu grant authority/approval; grant hợp lệ có TTL/actor/evidence. Test bản pilot một owner và bản nhiều user với separation khác nhau. |

## Các điểm chưa có bằng chứng để kết luận sai

- **Meta/Zalo/TikTok:** 1.4 đã gate capability/version/account và có giới hạn cửa sổ theo provider; không phát hiện một con số cửa sổ dùng chung còn sót trong phần chức năng hiện hành. Eligibility thực tế của TikTok Việt Nam và quyền từng account vẫn chưa kiểm trên tài khoản. Không khẳng định có hay không có quyền từ một trang giới thiệu API.
- **Privacy deadlines:** 1.4 đã bỏ DSAR72h. Cần legal owner xác nhận policy matrix đúng loại quyền/vai trò/nhánh theo Điều5 trước Active. Đây là gate đã có; không báo lại như lỗi mới hoặc tự thay bằng hạn do auditor nghĩ ra.
- **RLS/merge/search/AI:** Nhiều quy tắc nguyên tắc đã rõ; vẫn phải xuất DDL và chạy fixtures role thật. “Chưa chạy” là giới hạn chứng cứ, không tự chứng minh thiết kế đang leak. Không lập thêm lỗi chỉ vì chưa có implementation.
- **Quy mô:** Sáu bản vá là điều kiện đúng khi bật capability, không bắt pilot xây riêng sáu engine. OAuth/egress/mail/unsubscribe có thể dựa SDK, platform hoặc ESP có bằng chứng; governance có thể là approval/config hiện có. File gateway đơn giản phù hợp lưu lượng thấp; không cần dịch vụ riêng.

