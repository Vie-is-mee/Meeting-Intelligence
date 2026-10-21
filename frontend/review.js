/* Human review is a separate layer. It never rewrites the original prediction. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MeetingReview=api;})(globalThis,()=>{
  const clone=value=>JSON.parse(JSON.stringify(value));
  const statuses={decision:['proposed','agreed','conditional','reopened','withdrawn','open','unverified'],action:['assigned','cancelled','unverified'],issue:['open','reported_resolved','unverified'],request:['recorded','withdrawn','unverified'],feedback:['recorded','unverified'],knowledge:['unverified']};
  const editable=['kind','content','meeting_status','owner','supporter','due_raw','condition'];
  function create(analysis,id,source={}){return {version:1,id,source_metadata:clone(source),original_analysis:clone(analysis),records:analysis.records.map((r,index)=>({index,decision:'pending',draft:Object.fromEntries(editable.map(k=>[k,r[k]??null])),source_ids:[...r.evidence_ids],history:[]}))};}
  function actorName(actor){if(!String(actor||'').trim())throw new Error('Hãy nhập tên người rà soát.');return actor.trim();}
  function validate(session,draft,ids){
    if(!statuses[draft.kind]?.includes(draft.meeting_status))throw new Error('Loại thông tin và trạng thái không phù hợp.');
    if(!String(draft.content||'').trim())throw new Error('Nội dung bản ghi không được trống.');
    if(draft.kind!=='action'&&(draft.owner||draft.supporter))throw new Error('Chỉ công việc có người phụ trách/người hỗ trợ; hãy đổi loại hoặc để trống.');
    if(!['action','request'].includes(draft.kind)&&draft.due_raw)throw new Error('Chỉ công việc/yêu cầu có trường hạn trong bản rà soát.');
    if(!['action','decision'].includes(draft.kind)&&draft.condition)throw new Error('Loại này không dùng trường điều kiện.');
    if(draft.meeting_status==='conditional'&&!draft.condition?.trim())throw new Error('Quyết định có điều kiện cần ghi rõ điều kiện.');
    if(!Array.isArray(ids)||!ids.length)throw new Error('Cần ít nhất một mã câu nguồn để lưu/xác nhận bản ghi.');
    const known=new Set(session.original_analysis.utterances.map(u=>u.id));
    if(ids.some(id=>!known.has(id)))throw new Error('Có mã câu nguồn không tồn tại trong transcript.');
  }
  function update(session,index,patch,ids,actor,reason,confirm=false){
    const entry=session.records[index];if(!entry)throw new Error('Không tìm thấy bản ghi.');
    actor=actorName(actor);
    const draft={...entry.draft};for(const key of editable)if(Object.hasOwn(patch,key))draft[key]=patch[key];
    ids=[...new Set(ids)];validate(session,draft,ids);
    const before={draft:clone(entry.draft),source_ids:[...entry.source_ids],decision:entry.decision};
    const edited=JSON.stringify(draft)!==JSON.stringify(entry.draft)||JSON.stringify(ids)!==JSON.stringify(entry.source_ids);
    if((edited||(!confirm&&entry.decision!=='pending')||(confirm&&entry.decision==='rejected'))&&!String(reason||'').trim())throw new Error('Hãy ghi lý do chỉnh sửa/thay đổi xác nhận và câu nguồn hỗ trợ.');
    entry.draft=draft;entry.source_ids=ids;entry.decision=confirm?'confirmed':'pending';entry.assessment=null;
    entry.history.push({at:new Date().toISOString(),actor,action:confirm?'confirmed':'edited',reason:String(reason||'').trim(),before,after:{draft:clone(draft),source_ids:[...ids],decision:entry.decision}});
    return entry;
  }
  function decide(session,index,decision,actor,reason){
    if(!['rejected','pending','insufficient'].includes(decision))throw new Error('Thao tác không hợp lệ.');
    actor=actorName(actor);if(!String(reason||'').trim())throw new Error('Hãy ghi lý do từ chối/mở lại.');
    const entry=session.records[index];if(!entry)throw new Error('Không tìm thấy bản ghi.');
    const before=entry.decision;entry.decision=decision==='insufficient'?'pending':decision;entry.assessment=decision==='insufficient'?'insufficient':null;
    entry.history.push({at:new Date().toISOString(),actor,action:decision==='insufficient'?'insufficient':decision==='rejected'?'rejected':'reopened',reason:reason.trim(),before_decision:before,after_decision:entry.decision});return entry;
  }
  function confirmed(session){return session.records.filter(r=>r.decision==='confirmed').map(r=>{const source=session.original_analysis.records[r.index]||{};const sameKind=source.kind===r.draft.kind;return {original_index:r.index,...clone(r.draft),source_ids:[...r.source_ids],human_review:'confirmed',reviewed_by:r.history.at(-1)?.actor,reviewed_at:r.history.at(-1)?.at,authority_status:'unknown',ai_information_utility:sameKind?(source.information_utility??null):null,ai_utility_note:sameKind?(source.information_utility_note??null):null,confirmation_scope:'Nội dung do người dùng rà soát, không phải phê duyệt tổ chức.',review_history:clone(r.history)};});}
  function exportJSON(session){return {format:'meeting-human-review-v1',session_id:session.id,source_metadata:clone(session.source_metadata||{}),original_analysis:clone(session.original_analysis),review:clone(session.records),confirmed_records:confirmed(session)};}
  function csvCell(value){let text=String(value??'');if(/^[\s]*[=+\-@]/u.test(text)||/^[\t\r\n]/u.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"';}
  function exportCSV(session){
    const rows=confirmed(session);if(!rows.length)throw new Error('Chưa có bản ghi được xác nhận để xuất CSV.');
    const headers=['original_index','kind','content','meeting_status','owner','supporter','due_raw','condition','source_ids','human_review','reviewed_by','reviewed_at','authority_status','ai_information_utility','ai_utility_note'];
    return '\ufeff'+[headers.map(csvCell).join(','),...rows.map(r=>headers.map(k=>csvCell(k==='source_ids'?r.source_ids.join('; '):r[k])).join(','))].join('\r\n');
  }
  function restore(value,analysis,id){
    if(value?.version!==1||value.id!==id||JSON.stringify(value.original_analysis)!==JSON.stringify(analysis)||value.records?.length!==analysis.records.length)throw new Error('Phiên lưu không khớp đầu ra gốc.');
    value.records.forEach((r,i)=>{if(r.index!==i||!['pending','confirmed','rejected'].includes(r.decision)||!Array.isArray(r.history)||!statuses[r.draft?.kind]?.includes(r.draft.meeting_status)||!Array.isArray(r.source_ids))throw new Error('Phiên rà soát không hợp lệ.');if(r.decision==='confirmed')validate(value,r.draft,r.source_ids);});
    return clone(value);
  }
  return {statuses,editable,create,update,decide,confirmed,exportJSON,exportCSV,restore};
});
