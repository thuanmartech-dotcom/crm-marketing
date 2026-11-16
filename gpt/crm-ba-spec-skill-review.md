# Rà soát skill crm-ba-spec

Ngày 16/11/2026. Phạm vi gồm SKILL.md và toàn bộ 7 tệp trong references, đối chiếu AGENTS.md, MODULE-SPEC.md, CONTRACT.md, ADR-004/005, DECOMPOSITION-PLAN.md và mã kiểm tra verify_module_spec.py.

## Kết luận

Skill có **9 vấn đề cần xử lý**, gồm **3 HIGH và 6 MEDIUM**. Các điểm HIGH liên quan tới tác dụng ghi của chế độ review, hướng dẫn ownership outbox đã cũ và đường cập nhật tài liệu có thể bỏ qua Change Proposal.

Skill đã có các kiểm soát hữu ích như Documentation-Only, phân loại MASTER/PROPOSED/OPEN-GAP, hỏi quyết định ranh giới, giữ test ứng dụng Not Run và yêu cầu duyệt CR trước Apply. Các phát hiện dưới đây chỉ ra những chỗ các kiểm soát này chưa bao phủ nhất quán mọi nhánh workflow.

Mọi giải pháp là **[PROPOSED]**. Chưa thay đổi skill hoặc tệp dự án. Test ứng dụng **Not Run**.

| ID | Mức độ | Vấn đề | Ưu tiên xử lý |
|---|---|---|---|
| SK-01 | HIGH | Analyze gọi validator ghi vào dự án, thiếu chế độ review chỉ đọc | Trước phiên audit tiếp theo |
| SK-02 | HIGH | Workflow vẫn hướng outbox nội bộ về M19 | Trước bóc tách module/slice mới |
| SK-03 | MEDIUM | Chỉ dẫn kế thừa 10 cột chung lệch ADR-004 | Cùng đợt đồng bộ kiến trúc |
| SK-04 | HIGH | Nhánh questionnaire/hoàn thiện module chưa khóa đường thay đổi Reviewed qua CR | Trước lần sửa spec đã chốt |
| SK-05 | MEDIUM | Bộ lệnh cuối module chỉ kiểm một file, khác gate tổng | Trước bàn giao module/contract |
| SK-06 | MEDIUM | Checklist semantic và tiêu chuẩn chứng minh finding chưa đủ cụ thể | Trước mở rộng audit |
| SK-07 | MEDIUM | Phạm vi/lens/ví dụ Wave 1 đã lệch danh mục hiện hành | Trước review M21–M24 |
| SK-08 | MEDIUM | Phụ thuộc tên tool cụ thể nhưng thiếu fallback | Trước dùng trên host khác |
| SK-09 | MEDIUM | Sao chép hash/registry mà chưa khóa kiểm tra freshness | Trước trích trace và kết luận coverage |

## SK-01 — Analyze có tác dụng ghi ngoài ý định review chỉ đọc

**Bằng chứng.** Luồng A bước 2 tại review-change-workflow.md dòng 12–15 yêu cầu chạy `python 05-tools/verify_module_spec.py`. Script dòng 343–344 ghi `03-planning/evidence/module-spec-validation.json`. Nhánh `--file` dòng 285–301 xuất kết quả ra stdout rồi kết thúc trước đoạn ghi này. [Playbook review](../.agents/skills/crm-ba-spec/references/review-change-workflow.md), [validator](../05-tools/verify_module_spec.py).

**Tình huống.** Người dùng chỉ cho đọc và yêu cầu lưu báo cáo trong gpt/. Agent tuân theo Analyze mặc định sẽ làm thay đổi evidence dự án trước khi hoàn tất review. Việc này không phải sửa spec nhưng vẫn nằm ngoài phạm vi ghi đã được người dùng cho phép.

**Kiểm soát hiện có.** Skill phân biệt Apply và review, nhưng chưa phân loại tác dụng của các lệnh kiểm tra. Trong phiên này, chỉ dẫn của người dùng được ưu tiên nên lệnh ghi evidence tổng không được chạy.

**[PROPOSED]** Thêm xác định chế độ ở đầu phiên gồm audit-only, propose và apply. Với audit-only, nhận output directory từ yêu cầu và kiểm write footprint của tool trước khi chạy. Dùng `--file` cho các tệp được chọn khi cần kiểm cấu trúc. Nếu cần kiểm tổng nhưng công cụ chưa hỗ trợ output directory hoặc stdout-only, ghi giới hạn và giữ review thủ công. Không yêu cầu bộ lệnh có ghi dữ liệu cho mọi lần audit.

**Nghiệm thu skill.** Prompt yêu cầu “chỉ đọc, lưu gpt/” phải tạo đầu ra đúng thư mục, không đổi hash của các tệp ngoài gpt/ và không cập nhật GAPS/PROGRESS.

## SK-02 — Hướng dẫn outbox đã lệch quyết định phân chia M19/M23

**Bằng chứng.** Module workflow dòng 95 coi “bỏ qua M19 outbox” là ví dụ vi phạm invariant. Slice workflow mục Pha 3.3 dẫn luồng qua M19 outbox/inbox. Checklist dòng 39 gom cả tạo task chéo vào nhóm side effects M19. ADR-004 dòng 23 và ADR-005 phân công internal outbox cho M23-F12, external integration cho M19. [Module workflow](../.agents/skills/crm-ba-spec/references/module-workflow.md), [slice workflow](../.agents/skills/crm-ba-spec/references/slice-workflow.md), [checklist](../.agents/skills/crm-ba-spec/references/ears-and-checklists.md), [ADR-005](../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md).

**Tình huống.** Agent tách một domain mới có event nội bộ và làm theo checklist, đưa event đó vào M19. Slice chỉ cần tác vụ nội bộ cũng có thể bị thêm dependency external adapter. Đây là nguồn phát sinh drift lặp lại ngay trong quy trình viết tài liệu.

**Kiểm soát hiện có.** Pha Grounding yêu cầu đọc ADR liên quan. Tuy vậy, workflow không giải quyết mâu thuẫn giữa ADR mới và ví dụ bắt buộc cũ.

**[PROPOSED]** Đồng bộ cả ba vị trí, mô tả riêng transaction ghi domain + internal outbox M23, và dispatch external effect qua M19. Dẫn tới ADR/C23/C19 hiện hành làm nguồn ownership. Ví dụ slice nên lựa chọn dependency theo capability đang bật.

**Nghiệm thu skill.** Tách task nội bộ phải chọn M23/M24 theo SL01. Gửi qua provider phải chọn M19 và kiểm M14/M20. Không tạo dependency external connector chỉ vì có domain event.

## SK-03 — Kế thừa schema chung chưa phản ánh các nhóm thực thể

**Bằng chứng.** Module workflow dòng 17 hướng dẫn “kế thừa 10 cột chuẩn”. ADR-004 mục 2 định nghĩa Nhóm A gồm 12 cột, phân biệt B-Catalog/B-Governance-Sensitive và Nhóm C append-only không có các cột updated_at/updated_by/row_version/archived_at. [Module workflow](../.agents/skills/crm-ba-spec/references/module-workflow.md), [ADR-004](../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md).

**Tác động.** Nếu áp một bộ cột cho mọi bảng, spec mới có thể thiếu scope hoặc đưa cơ chế cập nhật vào ledger bất biến. Chỉ sửa số 10 thành 12 vẫn chưa giải quyết khác biệt Nhóm C và các biến thể tenant-wide.

**[PROPOSED]** Yêu cầu phân loại từng entity theo ADR trước khi mô tả cột. Ghi rõ nullability của workspace, scope pháp nhân/chi nhánh và quyền trên bảng tenant-wide. Với ledger, yêu cầu lịch sử bù trừ và ngoại lệ được phê duyệt thay vì sao chép bộ cột mutable.

**Nghiệm thu skill.** Cho ba ví dụ task, catalog tenant-wide và audit ledger. Agent phải tạo ba mô tả có scope/lifecycle phù hợp, không áp một bộ cột chung.

## SK-04 — Có đường cập nhật spec đã chốt chưa đi qua CR

**Bằng chứng.** Review workflow Luồng C dòng 34 yêu cầu khi người dùng gửi câu trả lời stakeholder thì cập nhật GAPS và module. Đoạn này không phân nhánh theo trạng thái Reviewed/Ready hoặc dẫn về Luồng B. Trong khi Luồng B dòng 50–51 và AGENTS.md yêu cầu duyệt CR trước Apply. SKILL.md còn cho chọn chế độ module để “hoàn thiện” module, nhưng chưa có guard ở đầu route chuyển module đã Reviewed sang review-change. [Review workflow](../.agents/skills/crm-ba-spec/references/review-change-workflow.md), [SKILL.md](../.agents/skills/crm-ba-spec/SKILL.md), [AGENTS.md](../AGENTS.md).

**Tình huống.** Stakeholder trả lời một tham số có tác động state machine của spec Reviewed. Agent thực hiện Luồng C và sửa ngay tài liệu, bỏ qua đánh giá tác động consumer và hồ sơ thay đổi.

**Kiểm soát hiện có.** Luồng B đã quy định CR đúng. Đây là thiếu chuyển hướng giữa các nhánh, không phải hoàn toàn thiếu quy trình phê duyệt.

**[PROPOSED]** Đặt một guard chung trước mọi mutation. Xác định trạng thái tài liệu, phạm vi đã được người dùng cho phép và quyết định/CR đã có. Với spec Reviewed/Ready, chuyển delta vào CR và áp dụng theo authorization hiện hành. Câu trả lời stakeholder chỉ đóng quyết định tương ứng, không tự chứng minh toàn bộ impact đã được xét. Nếu người dùng đã phê duyệt đúng CR/phạm vi thì tiếp tục, tránh hỏi lại.

**Nghiệm thu skill.** Questionnaire trả lời cho Draft được xử lý theo phạm vi cho phép. Cùng câu trả lời cho Reviewed phải có đường CR. Lệnh đã duyệt Apply phải được thực hiện đầy đủ mà không xin lại cùng một quyền.

## SK-05 — Lệnh cuối module không kiểm toàn bộ contract vừa tạo

**Bằng chứng.** SKILL.md mục 4 và AGENTS.md yêu cầu `python 05-tools/verify_module_spec.py` trong bộ kiểm tổng. Module workflow Pha 4 dòng 104–110 dùng `--file` cho Worker, nhưng cũng dùng `--file` ở lệnh thứ tư của nhánh đơn lẻ/Coordinator. Nhánh này chỉ kiểm module đích, trong khi Pha 3 có thể tạo public contract và ảnh hưởng consumer. [SKILL.md](../.agents/skills/crm-ba-spec/SKILL.md), [module workflow](../.agents/skills/crm-ba-spec/references/module-workflow.md), [validator](../05-tools/verify_module_spec.py).

**Tác động.** Agent chọn bộ lệnh của playbook có thể bỏ qua phần kiểm chuyên biệt contract mới, dù báo đã chạy đủ bốn lệnh. Các validator khác không thay cho kiểm contract của verify_module_spec.

**[PROPOSED]** Có một bảng kiểm chuẩn làm nguồn duy nhất. Worker kiểm tất cả tệp mình thay đổi gồm module và contract. Coordinator/phiên chỉnh sửa được cho phép chạy kiểm tổng đúng quy chuẩn. Audit-only dùng phương thức an toàn ở SK-01 và báo rõ phạm vi thực sự đã kiểm.

**Nghiệm thu skill.** Module hợp lệ nhưng contract thiếu phần bắt buộc phải làm gate phát hiện lỗi. Chạy một module không được báo là đã kiểm toàn bộ kho.

## SK-06 — Gate semantic và bằng chứng finding còn quá khái quát

**Bằng chứng.** Analyze có 5 nhóm kiểm ở review workflow dòng 17–23. Checklist chung có concurrency/idempotency và UI, nhưng chưa yêu cầu kịch bản lease cũ chạy lại, delta event đảo thứ tự, ACK từng consumer, privacy/replay race hoặc binding preview/approval. Báo cáo chỉ được yêu cầu phân mức độ, chưa có mẫu bắt buộc nguồn, tình huống và bằng chứng phản bác. Validator dòng 115–145 kiểm dấu hiệu văn bản/ID/heading và các cấu trúc, phần contract dòng 195–229 kiểm đủ phần và JSON parse. [Review workflow](../.agents/skills/crm-ba-spec/references/review-change-workflow.md), [checklist](../.agents/skills/crm-ba-spec/references/ears-and-checklists.md), [validator](../05-tools/verify_module_spec.py).

**Tác động.** Đủ ID hoặc có câu “idempotent” vẫn có thể bỏ sót hành vi sai. Ngược lại, review cũng có thể kết luận quá mức khi không tìm guard trong tài liệu phụ thuộc. Các finding ở báo cáo trước là đầu vào để bổ sung ca kiểm, cần được kiểm chứng độc lập khi dùng.

**Kiểm soát hiện có.** CONTRACT.md đã nói rõ schema pass không thay semantics pass và yêu cầu negative/replay/race. Điểm thiếu là cách biến nguyên tắc đó thành bước review và bằng chứng đầu ra có thể kiểm lại.

**[PROPOSED]** Bổ sung ma trận tình huống theo loại luồng, tiêu chuẩn finding gồm nguồn/dòng, trigger, expected/actual theo đặc tả, guard đã kiểm, tác động, confidence, giải pháp và nghiệm thu. Bắt buộc tìm bằng chứng phản bác và tách lỗi xác nhận khỏi câu hỏi chưa đủ nguồn. Dùng bản [master prompt BA](master-prompt-ba-documentation-review.md) làm tài liệu tham khảo để chọn các tiêu chí phù hợp, tránh sao chép toàn bộ vào mọi playbook.

**Nghiệm thu skill.** Đưa vào một spec đủ ID nhưng chỉ xử lý delta bằng MAX(version), và một spec có guard ở contract liên quan. Review phải phát hiện khoảng trống của ví dụ đầu và tránh báo sai ví dụ sau.

## SK-07 — Lens và ví dụ Wave 1 không theo danh mục hiện hành

**Bằng chứng.** SKILL.md dòng 40 và module workflow dòng 44 yêu cầu đọc đúng một cụm M01–M20. Domain-lenses chưa có cụm riêng cho M21/M22/M23/M24. Usage-guide dòng 36 gọi Sóng 1 là M14/M19/M20/M01, trong khi DECOMPOSITION-PLAN dòng 10 xác định Wave 1 gồm M14/M20/M19/M16 và M01 ở Wave 2. [Domain lenses](../.agents/skills/crm-ba-spec/references/domain-lenses.md), [usage guide](../.agents/skills/crm-ba-spec/references/usage-guide.md), [kế hoạch](../03-planning/DECOMPOSITION-PLAN.md).

**Tác động.** Người dùng sao chép prompt mẫu có thể chọn sai phạm vi wave. Review nền tảng hoặc HR/partner có thể thiếu lens tương ứng. Quy định “đúng một cụm” cũng không phù hợp với audit một giao diện cắt qua nhiều cụm.

**[PROPOSED]** Giữ một lens chính cho module, cho phép đọc bổ sung theo dependency. Bổ sung lens partner/HR/governance/platform và dẫn wave từ kế hoạch hiện hành. Không yêu cầu đọc mọi lens trong mọi phiên.

**Nghiệm thu skill.** Yêu cầu review Wave 1 phải ra đúng danh mục hiện hành. Review M22 phải có lens HR và các giao diện M14/M16/M19/M20 cần thiết.

## SK-08 — Tool name phụ thuộc host chưa có phương án thay thế

**Bằng chứng.** Module workflow yêu cầu `read_file` với StartLine/EndLine và `ask_question`; slice/review cũng dùng ask_question. Các tên tool đó không có trong danh sách công cụ khả dụng của phiên Codex đang rà. Có cơ chế đọc file và hỏi người dùng khác đáp ứng được mục đích. [Module workflow](../.agents/skills/crm-ba-spec/references/module-workflow.md), [slice workflow](../.agents/skills/crm-ba-spec/references/slice-workflow.md).

**Tác động.** Agent có thể dừng vì thiếu một tên tool, hoặc giả đã hỏi/đọc đúng cách. Đây là vấn đề portability ở host hiện tại, không khẳng định các tool đó thiếu ở mọi host.

**[PROPOSED]** Định nghĩa theo capability như đọc đoạn tệp, hỏi quyết định và chạy validation. Kiểm tool khả dụng đầu phiên, ánh xạ sang công cụ tương đương. Nếu không có UI hỏi thì đặt câu hỏi rõ trong hội thoại và chờ câu trả lời cho quyết định thật sự blocking. Giữ nguyên nguyên tắc không tự quyết thay stakeholder.

**Nghiệm thu skill.** Host không có ask_question/read_file vẫn thực hiện grounding và clarification đúng mục đích, không tạo API/tool giả.

## SK-09 — Hash và registry có thể cũ nhưng vẫn được dùng làm căn cứ

**Bằng chứng.** Module workflow dòng 67 yêu cầu lấy SHA-256 từ active-task.json. Change proposal template dòng 11 có hash cố định. Grounding lấy requirement từ registry nhưng chưa yêu cầu xác minh registry được sinh từ cùng bản Master đang đọc. Validator dòng 116 chấp nhận có hash đúng hoặc chỉ có chuỗi `1.9`. [Module workflow](../.agents/skills/crm-ba-spec/references/module-workflow.md), [CR template](../.agents/skills/crm-ba-spec/references/change-proposal-template.md), [validator](../05-tools/verify_module_spec.py).

**Tình huống.** Sau thay đổi baseline hoặc một lần đồng bộ chưa đầy đủ, Agent sao chép hash cũ và tính coverage trên registry cũ. Tệp vẫn có chữ 1.9 nên một phần kiểm baseline của validator có thể đạt. Các script tổng khác có thể phát hiện lệch về sau, nhưng grounding và audit đơn lẻ đã dùng nguồn chưa xác minh.

**[PROPOSED]** Tính hash Master thực tế bằng thao tác đọc, so manifest và metadata registry trước trace harvest. Nếu lệch, báo rõ và kiểm nguồn trực tiếp trong phạm vi cần thiết, không tự rebuild khi chưa có quyền ghi. Template dùng placeholder có yêu cầu điền hash đã kiểm. Phân biệt baseline mismatch với lỗi nội dung requirement.

**Nghiệm thu skill.** Với bản fixture có Master và manifest lệch hash nhưng cùng nhãn 1.9, grounding phải nhận diện lệch trước khi kết luận trace đầy đủ.

## Thứ tự đề xuất sửa skill

1. Thêm guard về chế độ và quyền ghi, xử lý SK-01/SK-04.
2. Đồng bộ ownership/schema và phạm vi từ ADR/kế hoạch, xử lý SK-02/SK-03/SK-07.
3. Thống nhất validation và freshness, xử lý SK-05/SK-09.
4. Bổ sung review semantic và tool fallback, xử lý SK-06/SK-08.

Chỉ dẫn kỹ thuật nên tham chiếu nguồn chuẩn có phiên bản và ghi thời điểm đối chiếu. Các con số/scope dễ thay đổi không nên được chép thành nhiều quy định độc lập trong các playbook.

## Kiểm chứng đã thực hiện

- Đọc đủ 8 tệp Markdown trong skill và các nguồn đối chiếu nêu đầu báo cáo.
- Kiểm tra đường dẫn local của Markdown link trong 8 tệp, không phát hiện đường dẫn tệp bị thiếu. Kiểm này không xác nhận anchor hoặc ý nghĩa link.
- Kiểm số code fence chẵn, đạt trên cả 8 tệp. Đây là kiểm cú pháp tối thiểu, không thay render Markdown.
- Lưu SHA-256 của từng tệp skill và kết quả tại [crm-ba-spec-review-checks.json](crm-ba-spec-review-checks.json).
- Đọc mã validator để xác định write footprint và giới hạn checks. Không chạy validator tổng ghi evidence vào dự án.
- Chưa chạy các tình huống nghiệm thu skill nêu trên. Chúng là đề xuất kiểm chứng cho phiên cải tiến sau khi được phép.

Các phát hiện xác nhận sự lệch hoặc thiếu trong chỉ dẫn, không chứng minh mọi agent sẽ mắc lỗi đó. Chỉ ghi báo cáo/kết quả kiểm trong gpt/, giữ nguyên skill gốc.
