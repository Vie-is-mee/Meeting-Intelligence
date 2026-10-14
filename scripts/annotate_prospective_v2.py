"""Apply explicit same-assistant semantic labels requested by user; never call LLM."""
import copy
import json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.parser import parse_transcript
from scripts.prepare_prospective_eval import validate_annotations

def main():
    pool=json.loads((ROOT/'datasets/prospective_eval_v2.json').read_text(encoding='utf8'))
    path=ROOT/'datasets/prospective_eval_v2_annotations.json'
    annotations=json.loads(path.read_text(encoding='utf8'))
    if any(r['annotation_status']!='pending' for r in annotations['cases']):raise SystemExit('Annotations already reviewed; do not overwrite.')
    sources={c['id']:{u.id:u.text for u in parse_transcript(c['transcript'])} for c in pool['cases']}
    def quotes(cid,ids):return [{'source_id':f'L{i:03d}','quote':sources[cid][f'L{i:03d}']} for i in ids]
    def record(cid,lid,kind,meaning,status,ids,*,field_sources=None,owner=None,supporter=None,due=None,condition=None,execution=None,review=False,counter=(),note=''):
        fields={'content':quotes(cid,ids),'meeting_status':quotes(cid,[ids[-1]])}
        for key,value in (field_sources or {}).items():fields[key]=quotes(cid,value)
        return {'label_id':lid,'kind':kind,'meaning':meaning,'meeting_status':status,
            'execution_status':execution or ('unknown' if kind in {'decision','action'} else 'not_applicable'),
            'authority_status':'unknown','owner':owner,'supporter':supporter,'due_raw':due,'due_iso':None,'condition':condition,
            'evidence':quotes(cid,ids),'field_evidence':fields,'counter_evidence':quotes(cid,counter),
            'must_flag_for_review':review,'semantic_note':note}
    def alternative(aid,replaces,records,note):return {'id':aid,'replaces_label_ids':replaces,'expected_records':records,'note':note}
    required={};extras={};alternatives={};notes={};forbidden={}

    required['N01']=[record('N01','south_carrier','decision','Dùng đơn vị Mây cho đợt bán thử miền Nam','agreed',[1,4,5],field_sources={'content':[1,5],'meeting_status':[5]},counter=[2],note='Sao là đề xuất cũ đã rút; Mây chỉ áp dụng đợt thử miền Nam.')]
    extras['N01']=[record('N01','north_carrier_open','decision','Chưa chọn đơn vị giao hàng miền Bắc, để cuộc họp khác','open',[5,6],field_sources={'meeting_status':[5]})]
    forbidden['N01']=['Sao là đơn vị đang được chọn','Mây đã được chọn cho mọi miền/mọi đợt','Có một người đã nhận liên hệ đơn vị giao hàng']
    notes['N01']='Miền Bắc nằm ngoài phạm vi chọn hôm nay: chấp nhận open riêng nhưng không bắt buộc model phải tạo record ngoài phạm vi. Không chấm proposal Sao thành quyết định còn hiệu lực.'

    required['N02']=[record('N02','activation_guide','action','Làm bản hướng dẫn kích hoạt tài khoản','assigned',[1,4,5,6],owner='Uyên',due='chiều thứ Sáu',field_sources={'content':[1,4,5],'meeting_status':[5,6],'owner':[4,5,6],'supporter':[6],'due_raw':[4,5]},counter=[1,2],note='Phương là owner cũ, không còn là owner/supporter; không tự chuẩn hóa thứ Sáu thành ngày lịch.')]
    forbidden['N02']=['Phương vẫn là người phụ trách hoặc người hỗ trợ','Hạn hiện hành là sáng thứ Tư','Hai action đang giao cùng việc cho Phương và Uyên']
    notes['N02']='Một vòng đời công việc, không phải hai công việc độc lập. L004 thay người và hạn; L005 xác nhận nhận việc; L006 nói chưa giao supporter.'

    required['N03']=[record('N03','registration_many_fields','feedback','Khách dùng thử phản hồi trang đăng ký có quá nhiều ô nhập','recorded',[1]),record('N03','required_registration_fields','request','Bước đăng ký đầu chỉ bắt buộc số điện thoại và mã xác nhận','recorded',[2,4],field_sources={'content':[2],'meeting_status':[4]}),record('N03','picture_instructions_positive','feedback','Khách khen hướng dẫn bằng hình dễ hiểu','recorded',[3])]
    extras['N03']=[record('N03','registration_design_open','decision','Chưa chốt thiết kế đăng ký thay thế','open',[4])]
    alternatives['N03']=[alternative('combined_registration_feedback',['registration_many_fields','picture_instructions_positive'],[record('N03','registration_feedback_combined','feedback','Khách phản hồi đăng ký quá nhiều ô nhập và khen hướng dẫn bằng hình dễ hiểu','recorded',[1,3],field_sources={'meeting_status':[1,3]})],'Một feedback gộp được chấp nhận nếu giữ đủ ý tiêu cực và tích cực; request giảm trường vẫn riêng.')]
    forbidden['N03']=['Khách yêu cầu thêm hình','Đã chốt thiết kế thay thế hoặc giao người triển khai','Khách yêu cầu bỏ đăng ký bằng số điện thoại để dùng email']
    notes['N03']='Chưa chốt thiết kế là thông tin có nguồn, chấp nhận open riêng. Câu hỏi email chưa phải yêu cầu bỏ số điện thoại. Không tạo task chỉ từ request.'

    required['N04']=[record('N04','xlsx_need','request','Bộ phận vận hành cần tải danh sách đơn dưới dạng XLSX; nhu cầu vẫn giữ','recorded',[1,5],field_sources={'content':[1,5],'meeting_status':[5]}),record('N04','try_tool_k','action','Thử xuất danh sách đơn bằng công cụ K (đã hủy)','cancelled',[2,3,4,6],owner='Trúc',field_sources={'content':[2,4],'meeting_status':[4,6],'owner':[2,3],'due_raw':[4]},counter=[2],note='Trúc là owner lịch sử; hạn trưa mai đã bị bỏ. Lý do hủy không là condition để tiếp tục.'),record('N04','xlsx_method_open','decision','Chưa chọn cách xuất XLSX thay thế','open',[5])]
    forbidden['N04']=['Nhu cầu XLSX đã bị rút','Trúc đang tiếp tục thử K hoặc đang làm cách mới','Hạn trưa mai vẫn hiện hành','Không phù hợp chính sách dữ liệu là condition hiện hành để thử K','Sinh request thử K độc lập còn hiệu lực từ câu giao việc đã hủy']
    notes['N04']='Giữ ba vai trò: nhu cầu, công việc triển khai đã hủy, lựa chọn thay thế chưa chốt. Owner lịch sử không tự bị xóa; không ghép hạn của task vào request XLSX.'

    required['N05']=[record('N05','scanner_connectivity','issue','Lỗi máy quét quầy số hai được Oanh báo hết trong lượt thử, chưa được kiểm tra độc lập hoặc xác nhận không tái phát','reported_resolved',[1,2,3,4,5],field_sources={'content':[1,4,5],'meeting_status':[4,5]},review=True)]
    extras['N05']=[record('N05','scanner_trial_report','knowledge','Oanh báo ba lượt thử gửi được sau thay dây mạng; chưa xác minh cả ca','unverified',[2,3,4],review=True)]
    forbidden['N05']=['Lỗi đã được xác minh độc lập hết hoàn toàn hoặc không tái phát','Đã giao Oanh/Nam làm nhiệm vụ kiểm tra sau họp']
    notes['N05']='reported_resolved là lời báo kết quả giới hạn, không là verified. Việc Oanh đã làm trước câu nói không tự trở thành action assigned sau họp. Cần thể hiện rõ giới hạn kiểm chứng; không chỉ ghi "đã xử lý xong".'

    required['N06']=[record('N06','launch_condition','decision','Mở chương trình ưu đãi khi đủ 100 cửa hàng tham gia VÀ kiểm thử thanh toán không có lỗi nghiêm trọng','conditional',[3,4,5],condition='đủ 100 cửa hàng tham gia và kiểm thử thanh toán không có lỗi nghiêm trọng',execution='pending_condition',field_sources={'content':[3],'meeting_status':[3,5],'condition':[3],'execution_status':[4,5]},counter=[1],review=True)]
    forbidden['N06']=['Mốc hiện hành là 80 cửa hàng','Chỉ cần một trong hai điều kiện','Các điều kiện đã đạt hoặc được phép mở ngay','Quyết định có điều kiện đã bị hủy/mở lại','Có ngày mở đã chốt']
    notes['N06']='Điều kiện chưa đạt không biến conditional thành reopened. Ngưỡng 100 và kiểm thử không lỗi là quan hệ AND. Có thể biểu diễn chặn mở ngay bằng blocked nếu nói rõ cùng trạng thái chờ; phương án dưới đây được chốt trước đầu ra.'
    alt_launch=copy.deepcopy(required['N06'][0]);alt_launch['label_id']='launch_condition_blocked';alt_launch['execution_status']='blocked';alt_launch['semantic_note']='Cách thể hiện tương đương: chưa được mở ngay do các điều kiện chưa đạt, không bịa một lệnh cấm độc lập.'
    alternatives['N06']=[alternative('blocked_until_conditions',['launch_condition'],[alt_launch],'Chấp nhận blocked thay pending_condition chỉ khi giữ đầy đủ điều kiện và không đổi meeting_status conditional.')]

    required['N07']=[record('N07','check_event_exit','request','Kiểm tra đường thoát khu sự kiện trước lượt diễn tập tiếp theo; chưa xác định người nhận','recorded',[1,4,6],due='trước lượt diễn tập tiếp theo',field_sources={'content':[1,6],'meeting_status':[6],'owner':[4],'due_raw':[1,6]},review=True),record('N07','rehearsal_date_open','decision','Chưa chọn ngày diễn tập; thứ Hai/thứ Ba mới là gợi ý','open',[5,6],field_sources={'content':[5,6],'meeting_status':[6]})]
    extras['N07']=[record('N07','ask_organizer_schedule','request','Cần hỏi thêm lịch ban tổ chức trước khi bàn người và ngày','recorded',[7])]
    forbidden['N07']=['Đã giao Khánh/Mai hoặc một người cụ thể kiểm tra','Đã chốt diễn tập thứ Hai hoặc thứ Ba','Yêu cầu kiểm tra không có ràng buộc thời gian vì chưa biết ngày lịch']
    notes['N07']='Request có thời điểm tương đối dù chưa có owner/action. Đại từ trong câu hỏi L002 không chứng minh nhận việc. L007 là nhu cầu bổ trợ có thể tách, không tự gán Mai làm.'

    required['N08']=[record('N08','venue_reopened','decision','Lựa chọn địa điểm hội thảo đã mở lại; hôm nay chưa chọn phòng A hay B','reopened',[1,3,6],field_sources={'content':[3],'meeting_status':[3,6]},counter=[1]),record('N08','suitable_venue_request','request','Có phương án phòng phù hợp trước lần xác nhận vé tiếp theo','recorded',[4,5],due='trước lần xác nhận vé tiếp theo',field_sources={'content':[4],'meeting_status':[5],'owner':[5],'due_raw':[4]})]
    extras['N08']=[record('N08','room_a_electric_repair','issue','Phòng A đang sửa điện, ảnh hưởng lựa chọn địa điểm','open',[2])]
    forbidden['N08']=['Phòng A đã được chốt lại hôm nay','Phòng B đã được chọn','Thu/Dũng đã nhận tìm phòng hoặc có ngày xác nhận vé cụ thể']
    notes['N08']='Có thể giữ content phòng A như nội dung lịch sử của reopened nếu ghi rõ không còn kết luận cuối. L006 nhắc câu cũ không là agreement mới.'

    required['N09']=[]
    forbidden['N09']=['Tạo quyết định kinh doanh hoặc công việc sau họp từ thử mic/camera','Hà/Bình nhận một nhiệm vụ sau cuộc họp','Coi kết quả thử âm thanh là tri thức nghiệp vụ cần dùng tiếp']
    notes['N09']='Negative control: chỉ thử thiết bị trước họp, không có nội dung nghiệp vụ/cam kết dùng sau họp. required_records=[] có chủ ý; không cần suy diễn thiếu transcript hoặc bịa cảnh báo hỏng dữ liệu.'

    required['N10']=[record('N10','retention_uncertain','knowledge','Có lời nhớ 45 ngày và tài liệu cũ ghi 30 ngày; thời gian lưu dấu vết hiện tại chưa được xác minh','unverified',[1,2,5],field_sources={'content':[1,2,5],'meeting_status':[1,2,5]},review=True),record('N10','verify_retention_config','request','Đối chiếu tài liệu cấu hình mới trước khi trả lời khách','recorded',[3,4],due='trước khi trả lời khách',field_sources={'content':[3],'meeting_status':[3],'owner':[4],'due_raw':[3]})]
    alternatives['N10']=[alternative('separate_uncertain_retention_claims',['retention_uncertain'],[record('N10','retention_45_unverified','knowledge','Nga nhớ thời gian lưu 45 ngày nhưng chưa chắc là cấu hình hiện tại','unverified',[1,5],field_sources={'content':[1],'meeting_status':[1,5]},review=True),record('N10','retention_30_old_doc','knowledge','Tài liệu cũ Vũ đọc ghi 30 ngày, chưa xác minh cấu hình hiện tại','unverified',[2,5],field_sources={'content':[2],'meeting_status':[2,5]},review=True)],'Hai knowledge đều phải giữ nguồn và độ chưa chắc chắn. Không chấm hai con số thành hai facts verified.')]
    forbidden['N10']=['Cấu hình hiện tại chắc chắn là 30 hoặc 45 ngày','Cuộc họp quyết định đổi thời gian lưu','Nga/Vũ đã nhận việc đối chiếu','Không có ràng buộc trước khi trả lời khách chỉ vì không có ngày lịch']
    notes['N10']='Tri thức là phát biểu có mức tin cậy, không là sự thật bên ngoài đã xác minh. L004 chưa chốt hạn lịch không xóa thứ tự "trước khi trả lời khách" ở L003.'

    required['N11']=[record('N11','cold_inventory_schedule','decision','Kiểm kê khu lạnh chiều thứ Sáu, thay lịch sáng thứ Năm','agreed',[2,3,62,63,64,66,72],field_sources={'content':[62,64,72],'meeting_status':[64,72]},counter=[2,3]),record('N11','cold_map_document','action','Sửa sơ đồ khu lạnh trong tài liệu; Linh phụ trách, gửi sáng thứ Sáu','assigned',[11,12,36,58,59,60,66,69,72],owner='Linh',due='sáng thứ Sáu',field_sources={'content':[36,58,60],'meeting_status':[59,60,72],'owner':[58,59,60,69],'due_raw':[59,60,66]},counter=[11,12]),record('N11','arrival_button_feedback','feedback','Ca tối dùng máy bàn phản hồi màn hình hàng về khó tìm nút xác nhận; chưa xử lý','recorded',[4,7,26,43,56,67],field_sources={'content':[4,7,26,56],'meeting_status':[43,67]}),record('N11','small_text_feedback','feedback','Chữ ở màn hình xác nhận nhỏ trên màn hình cũ; không quy kết mọi máy đều như vậy','recorded',[18,19,67],field_sources={'content':[18,19],'meeting_status':[67]})]
    extras['N11']=[record('N11','normal_zone_schedule_open','decision','Chưa chọn lịch kiểm kê khu thường, ngoài phạm vi chốt khu lạnh','open',[37,64],field_sources={'meeting_status':[64]}),record('N11','obscured_shelf_code','issue','Mã kệ phía đông trên sơ đồ hiện tại bị chú thích che; chưa có lời báo đã sửa','open',[13,14]),record('N11','button_visibility_request','request','Người dùng muốn nhìn thấy nút xác nhận rõ hơn, chưa đề nghị vị trí cụ thể','recorded',[30])]
    alternatives['N11']=[alternative('combined_arrival_ui_feedback',['arrival_button_feedback','small_text_feedback'],[record('N11','arrival_ui_feedback_combined','feedback','Ca tối/máy bàn khó tìm nút xác nhận; chữ nhỏ trên màn hình cũ; chưa có phương án sửa','recorded',[4,7,18,19,26,67],field_sources={'content':[4,7,18,19,26],'meeting_status':[67]})],'Feedback gộp được chấp nhận nếu giữ cả hai ý và phạm vi thiết bị; không mất một ý rồi vẫn tính đủ recall.')]
    forbidden['N11']=['Kiểm kê khu lạnh sáng thứ Năm còn là lịch cuối','Bình còn phụ trách sơ đồ hoặc được gán supporter','Hạn sơ đồ là chiều thứ Tư hoặc chiều thứ Sáu','Linh/Vy/Bình đã được giao sửa giao diện hay lịch xe','Đã chốt kiểm kê toàn kho/đổi cảm biến/dịch tài liệu']
    notes['N11']='Lịch kiểm kê chiều thứ Sáu nằm trong nội dung decision, không gán thành due của tài liệu. Tài liệu gửi sáng thứ Sáu theo L066. Hai feedback có phạm vi, không tự đổi thành task. Khu thường ngoài phạm vi nên open có nguồn là extra hợp lệ.'

    required['N12']=[record('N12','english_guide_need','request','Khách cần hướng dẫn tiếng Anh cho cả tuyến Bắc và Nam; nhu cầu còn giữ','recorded',[2,20,46,61,69,72],field_sources={'content':[2,20,72],'meeting_status':[46,69,72],'due_raw':[61]}),record('N12','try_tool_m','action','Thử làm hướng dẫn bằng công cụ M (đã hủy)','cancelled',[3,4,44,45,49,60,73],owner='Hòa',field_sources={'content':[3,44],'meeting_status':[44,45,73],'owner':[3,4,73],'due_raw':[44,60,73]},counter=[3]),record('N12','guide_method_open','decision','Chưa chọn công cụ/cách làm hướng dẫn thay thế và chưa giao người làm','open',[47,48,64,74,75],field_sources={'content':[47,48,74],'meeting_status':[48,74,75]}),record('N12','north_departure_reopened','decision','Lựa chọn giờ tuyến Bắc được mở lại; không còn chốt 8 giờ hay 7 giờ, ngày chạy thử chưa chắc chắn','reopened',[5,6,55,66,67,68,71,78,79],field_sources={'content':[67,68,71,79],'meeting_status':[67,68,71,78]},counter=[5,55]),record('N12','south_departure_open','decision','Chưa chốt giờ khởi hành tuyến Nam','open',[25,26,59,71],field_sources={'content':[25,59,71],'meeting_status':[59,71]}),record('N12','south_bus_late_feedback','feedback','Tuyến Nam có phản hồi xe đến điểm đón trễ, chưa có lời báo hết trễ','recorded',[7,8,24,38,65,76],field_sources={'content':[7,8,65,76],'meeting_status':[65,76]}),record('N12','confirm_south_departure','request','Cần xác nhận giờ tuyến Nam với nhà xe; chưa có người nhận liên hệ','recorded',[57,58,59],field_sources={'content':[57,59],'meeting_status':[59],'owner':[58]})]
    extras['N12']=[record('N12','south_lateness_issue','issue','Vướng mắc xe tuyến Nam trễ chưa được báo khắc phục','open',[7,24,38,76])]
    forbidden['N12']=['Giờ tuyến Bắc hiện đã chốt 7 hoặc 8 giờ','Lấy 8 giờ của Bắc làm giờ Nam','Hòa còn đang thử M/làm hướng dẫn mới hoặc còn hạn tối mai','Yêu cầu tiếng Anh bị hủy khi công cụ M hoặc lịch Bắc bị mở lại','Lý do công cụ không cho dùng thương mại thành condition tiếp tục triển khai M','Đã chọn công cụ thay thế hoặc giao người làm/liên hệ nhà xe','Xe tuyến Nam được báo khắc phục hoặc xác minh hết trễ']
    notes['N12']='Giữ riêng vòng đời hai tuyến, request tài liệu và task M. Giờ 8 chỉ từng agreed trong ngày thử rồi bị reopened ở L067; các giờ được nhắc lại là history. Hòa là owner lịch sử của task cancelled, hạn null. Request xác nhận giờ Nam khác với một action liên hệ được nhận. Extra issue Nam có căn cứ nhưng không tự chứng minh feedback đã được trích đủ.'

    stamp=datetime.now(timezone.utc).isoformat()
    for row in annotations['cases']:
        cid=row['id'];row.update(annotation_status='assistant_reviewed',reviewer='coding_assistant_same_author_not_independent_human',reviewed_at=stamp,labels_finalized_before_outputs=True,
            required_records=required[cid],allowed_additional_records=extras.get(cid,[]),forbidden_claims=forbidden[cid],representation_alternatives=alternatives.get(cid,[]),annotation_notes=notes[cid],case_review_required=cid in {'N05','N07','N10'})
        if cid=='N09':row['no_required_records_reason']='Chỉ thử mic/camera trước phần họp chính; không có thông tin nghiệp vụ hoặc cam kết dùng sau họp.'
    annotations.update(status='assistant_semantically_reviewed_before_outputs',review_method='Internal same-author semantic review against the full transcript; user explicitly requested assistant annotation, not human signoff.',independence_claim=False,llm_execution_performed=False)
    validate_annotations(pool,annotations,allow_assistant_review=True)
    path.write_text(json.dumps(annotations,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    stats=Counter(r['kind'] for rows in required.values() for r in rows)
    report='# Rà soát nhãn bộ prospective v2\n\nTheo yêu cầu ứng viên, trợ lý tự đọc và gán nhãn trước đầu ra model. **Không có human signoff, không độc lập, chưa chạy API và chưa có điểm model.** Transcript giữ nguyên hash. Quote lấy nguyên văn từ parser; việc quote tồn tại không tự chứng minh mọi diễn giải là đúng.\n\n'
    report+=f"Tổng {sum(stats.values())} nhãn cốt lõi; {sum(len(v) for v in extras.values())} extras tham chiếu; {len(alternatives)} cách biểu diễn thay thế. Nhãn theo loại: `{dict(stats)}`. Các alternative là lựa chọn biểu diễn trước matching, không cộng đôi recall.\n\n"
    for case in pool['cases']:
        cid=case['id'];report+=f"## {cid} — {case['title']}\n\n| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |\n|---|---|---|---|---|\n"
        for r in required[cid]:
            values='; '.join(f'{k}: {r[k]}' for k in ['owner','due_raw','condition'] if r[k] is not None) or 'Không tự điền'
            ids=', '.join(q['source_id'] for q in r['field_evidence']['meeting_status'])
            report+=f"| {r['kind']} | {r['meaning']} | {r['meeting_status']} | {values} | {ids} |\n"
        if not required[cid]:report+='| Không có | Không có bản ghi nghiệp vụ bắt buộc | — | — | L001–L005 |\n'
        report+=f"\n**Lý do/ranh giới:** {notes[cid]}\n\n"
        if extras.get(cid):report+='**Extras có thể chấp nhận:** '+'; '.join(r['meaning'] for r in extras[cid])+'.\n\n'
        if alternatives.get(cid):report+='**Biểu diễn tương đương:** '+'; '.join(a['note'] for a in alternatives[cid])+'.\n\n'
        report+='**Không được kết luận như thông tin hiện hành:** '+'; '.join(forbidden[cid])+'. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.\n\n'
    report+='## Quy tắc chấm\n\nGold là tập cốt lõi, không giả là danh sách vét cạn mọi thông tin. Xét thêm từng output theo nghĩa/nguồn/độ trùng lặp, không tự gọi output ngoài danh sách extras là bịa. Chọn đúng một representation cho mỗi case rồi matching một-một. Không dùng kết quả model để sửa nhãn nhằm làm tăng điểm. Nếu phát hiện lỗi gold trước lượt chạy, sửa có lịch sử và tạo frozen version mới.\n'
    (ROOT/'docs/PROSPECTIVE_LABEL_REVIEW.md').write_text(report,encoding='utf8')
    print('Annotated all 12 cases:',sum(stats.values()),'required records;',dict(stats),'No model/API calls.')

if __name__=='__main__':main()
