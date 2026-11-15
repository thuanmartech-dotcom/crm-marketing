# Kho lưu trữ lịch sử (`99-archive/`)

> [!CAUTION]
> **Không dùng làm đặc tả hiện hành.** Toàn bộ tệp trong thư mục này là ảnh chụp lịch sử (v1.2–v1.8), bản nháp trung gian và script hợp nhất/kiểm định cũ trước khi hoàn tất cấu trúc Master v1.9.

## Cấu trúc lưu trữ

- `master-versions/`: Các bản Master đóng băng trước mỗi đợt nâng cấp lớn (`v1.6`, `v1.7`, `v1.8`). Trong đó bản `v1.8` vẫn được [verify_hrm_integration.py](../05-tools/verify_hrm_integration.py) kiểm tra sự tồn tại để đối chiếu tính toàn vẹn.
- `research-2026-10-15/`: Các bản Master cũ `v1.2–v1.5`, báo cáo nghiên cứu CEO/CMO/CX ban đầu, báo cáo kiểm định `v1.3` (`gemini-code-1792078127639.html`) và các manifest kiểm chứng cũ.
- `legacy-build-scripts/`: Các script Python từng dùng để biên soạn/vá từng phiên bản `v1.0–v1.8` (lưu ý một số script như `verify_work_integration.py` có lệnh ghi sửa trực tiếp file Master nên **tuyệt đối không chạy lại**).
- `legacy-working-drafts/`: Các tệp trung gian (`.md`, `.json`, `.txt`) sinh ra trong quá trình kiểm định và hợp nhất `v1.3–v1.9` (tệp `hrm_sections.md` vẫn được script đối chiếu nội dung đọc chỉ-đọc).

Nguồn chuẩn hiện hành duy nhất nằm tại [00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md](../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md).
