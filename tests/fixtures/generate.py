"""Creates explicit MOCK extraction outputs for contract testing only.

Never use these fixture events as actual model predictions or in live prompts.
"""
import json
from pathlib import Path
D = Path(__file__).resolve().parent

def e(key, topic, kind, typ, source, val=None, owner=None, supporter=None, cond=None, due=None):
    return dict(issue_key=key, topic=topic, kind=kind, event_type=typ, source_ids=[source],
                value=val, owner=owner, supporter=supporter, due_raw=due, condition=cond)

cases = {
'T01': [
 e('option','Lựa chọn phương án','decision','proposal','L002','Phương án B'),
 e('option','Lựa chọn phương án','decision','agreement','L003','Phương án B'),
 e('testing','Kiểm thử B','action','assignment','L004','Kiểm thử B','Lan','Minh'),
 e('testing_access','Quyền môi trường kiểm thử','issue','issue_reported','L005','Thiếu quyền truy cập môi trường'),
 e('setup_guide','Hướng dẫn cấu hình','request','request_made','L006','Bổ sung hướng dẫn cấu hình'),
 e('screen_latency','Màn hình tải chậm','feedback','feedback_given','L007','Khách hàng phản hồi màn hình tải chậm'),
 e('release_date','Ngày phát hành','decision','unresolved','L008','Ngày phát hành chưa chốt'),
],
'T02': [
 e('option','Lựa chọn phương án','decision','proposal','L001','Phương án A'),
 e('option','Lựa chọn phương án','decision','counterproposal','L003','Phương án B'),
 e('option','Lựa chọn phương án','decision','agreement','L004','Phương án B'),
],
'T03': [
 e('option','Lựa chọn phương án giao diện','decision','proposal','L001','Phương án B'),
 e('option','Lựa chọn phương án giao diện','decision','agreement','L002','Phương án B'),
 e('option','Lựa chọn phương án giao diện','decision','reopen','L003'),
],
'T04': [
 e('option','Lựa chọn phương án','decision','proposal','L001','Phương án B'),
 e('option','Lựa chọn phương án','decision','agreement','L002','Phương án B'),
 e('option','Lựa chọn phương án','decision','execution_blocked','L003',cond='Chờ pháp chế phê duyệt'),
],
'T05': [
 e('test_B','Kiểm thử B','action','assignment','L001','Kiểm thử B','Minh'),
 e('login','Kiểm thử đăng nhập','request','request_made','L002','Kiểm thử thêm luồng đăng nhập'),
 e('test_B','Kiểm thử B','action','reassignment','L003','Kiểm thử B','Lan','Minh'),
],
'T06': [
 e('ui','Lựa chọn giao diện','decision','proposal','L001','Phương án A'),
 e('server_account','Tài khoản máy chủ','issue','issue_reported','L002','Chưa có tài khoản máy chủ'),
 e('ui','Lựa chọn giao diện','decision','counterproposal','L003','Phương án B'),
 e('server_access_task','Cấp quyền máy chủ','action','assignment','L004','Cấp quyền máy chủ','Hương'),
 e('menu_feedback','Menu khó tìm','feedback','feedback_given','L005','Menu đang khó tìm'),
 e('ui','Lựa chọn giao diện','decision','agreement','L006','Phương án B'),
 e('server_account','Tài khoản máy chủ','issue','issue_reported','L007','Chưa có tài khoản máy chủ'),
],
'T07': [
 e('filter_speed','Bộ lọc chậm','feedback','feedback_given','L001','Khách hàng phản hồi bộ lọc tìm kiếm chậm'),
 e('filter_fields','Bổ sung trường lọc','request','request_made','L002','Bổ sung lọc theo ngày và vị trí'),
 e('filter_date','Ngày lọc','decision','unresolved','L003','Chưa rõ ngày tạo hay ngày cập nhật'),
 e('vpn','VPN bị ngắt','issue','issue_reported','L004','VPN bị ngắt liên tục'),
 e('api_cursor','Cách phân trang API','knowledge','knowledge_shared','L005','API sử dụng cursor pagination; cần kiểm tra tài liệu mới nhất'),
 e('filter_date','Ngày lọc','decision','unresolved','L006','Chưa chốt cách tính ngày lọc'),
],
}
for case, events in cases.items():
    (D / (case+'.json')).write_text(json.dumps({'events':events},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
