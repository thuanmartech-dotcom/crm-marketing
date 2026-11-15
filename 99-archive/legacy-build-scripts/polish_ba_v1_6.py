from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
s=p.read_text(encoding='utf-8')
for old,new in {
 'phiên bản1.6':'phiên bản 1.6','Danh mục20 module':'Danh mục 20 module','Chương2–9':'Chương 2–9',
 'Đây là20':'Đây là 20','không phải20':'không phải 20','kiểm định1.5':'kiểm định 1.5',
 'Chương3':'Chương 3','Chương4':'Chương 4','Chương5':'Chương 5','Chương6':'Chương 6','Chương9':'Chương 9',
 'bắt đầu từ danh mục module tại3.0':'bắt đầu từ danh mục module tại 3.0',
 'ở9.14':'ở 9.14','nằm ởA.6':'nằm ở A.6','Nội dung1.6':'Nội dung 1.6','hiện hành1.6':'hiện hành 1.6',
 'qua9.5/9.11':'qua 9.5/9.11','theo3.13.5':'theo 3.13.5','theo3.13.4/4.13':'theo 3.13.4/4.13',
 '| M09-F02 Nhận evidence |':'| M09-F02 Nhận bằng chứng giao dịch |',
 '| M09-F03 Verify/match |':'| M09-F03 Xác minh và ghép khoản thu |',
 '| M09-F04 Allocate |':'| M09-F04 Phân bổ tiền |',
 '| M09-F05 Map invoice |':'| M09-F05 Đối chiếu hóa đơn |',
 '| M09-F06 Refund |':'| M09-F06 Hoàn tiền |',
 '| M09-F07 Close/reconcile |':'| M09-F07 Đối soát và khóa kỳ |',
 '| Trigger/đầu vào |':'| Kích hoạt/đầu vào |',
 '| Trigger / đầu vào |':'| Kích hoạt / đầu vào |',
}.items(): s=s.replace(old,new)
p.write_text(s,encoding='utf-8',newline='\n')
