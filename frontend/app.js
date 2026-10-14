'use strict';

const $ = id => document.getElementById(id);
const kinds = {decision:'Quyết định',action:'Công việc',issue:'Vướng mắc',request:'Yêu cầu',feedback:'Phản hồi',knowledge:'Tri thức'};
const statuses = {proposed:'Chỉ mới đề xuất',agreed:'Đã thống nhất',conditional:'Chốt có điều kiện',reopened:'Chưa chốt lại',withdrawn:'Đã rút',assigned:'Đã phân công',cancelled:'Đã hủy',open:'Chưa chốt / còn mở',reported_resolved:'Được báo đã xử lý',recorded:'Đã ghi nhận',unverified:'Chưa xác định chắc chắn'};
const events = {proposal:'Đề xuất',counterproposal:'Đề xuất thay thế',agreement:'Thống nhất',conditional_agreement:'Thống nhất có điều kiện',reopen:'Mở lại kết luận',unresolved:'Chưa chốt',withdrawal:'Rút quyết định',execution_blocked:'Chặn triển khai',assignment:'Phân công',reassignment:'Đổi người phụ trách',deadline_change:'Thay đổi thời hạn',action_cancelled:'Hủy công việc',issue_reported:'Ghi nhận vướng mắc',issue_reported_resolved:'Báo đã xử lý',request_made:'Đưa ra yêu cầu',request_changed:'Sửa yêu cầu',request_withdrawn:'Rút yêu cầu',feedback_given:'Ghi nhận phản hồi',knowledge_shared:'Chia sẻ tri thức'};
const fields = {content:'Nội dung',meeting_status:'Trạng thái',execution_status:'Trạng thái triển khai',owner:'Người phụ trách',supporter:'Người hỗ trợ',due_raw:'Thời hạn',condition:'Điều kiện'};
let sampleData = [], result = null, selected = -1, filter = 'all', busy = false;
let demoData = null, backendAvailable = false;
let currentReview = null;
const reviewSessions = new Map(), resultSessionIds = new WeakMap();
const REVIEW_STORAGE_KEY = 'meeting-intelligence-review-last-v1';

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined && text !== null) element.textContent = text;
  return element;
}
function statusBadge(status) {
  const tone = ['agreed','assigned','recorded','reported_resolved'].includes(status) ? 'green' : status === 'unverified' ? 'red' : 'amber';
  return node('span', `badge ${tone}`, statuses[status] || status);
}
function recordPresentation(record) {
  const content = record.content || 'Nội dung chưa được xác định.';
  if (record.kind === 'action' && record.meeting_status === 'cancelled') return {title:'Công việc đã bị hủy',context:`Công việc trước đó: ${content}. Không còn là việc đang được giao.`};
  if (record.kind !== 'decision') return {title: content, context: ''};
  switch (record.meeting_status) {
    case 'reopened': {
      const previous = [...(record.history || [])].reverse().find(event =>
        ['agreement','conditional_agreement'].includes(event.event_type) && event.value);
      return {title: 'Chưa có quyết định cuối — đã mở lại',
        context: previous ? `Từng ${previous.event_type === 'conditional_agreement' ? 'chốt có điều kiện' : 'chốt'}: ${previous.value}. Kết luận đó đã được mở lại.`
          : `Nội dung đang được xem xét: ${content}`};
    }
    case 'open': return {title: 'Chưa có quyết định cuối', context: `Nội dung còn bỏ ngỏ: ${content}`};
    case 'proposed': return {title: 'Mới là đề xuất — chưa chốt', context: `Đề xuất: ${content}`};
    case 'withdrawn': return {title: 'Quyết định đã bị rút', context: `Nội dung đã rút: ${content}`};
    case 'unverified': return {title: 'Chưa xác định chắc chắn kết luận cuối', context: `Nội dung cần kiểm tra: ${content}. Chưa được coi là quyết định đã chốt.`};
    case 'conditional': return {title: `Thống nhất có điều kiện: ${content}`, context: 'Không coi đây là quyết định vô điều kiện.'};
    case 'agreed': return {title: `Đã thống nhất: ${content}`, context: record.execution_status === 'blocked'
      ? 'Đã chốt trong cuộc họp, nhưng chưa được triển khai.' : ''};
    default: return {title: content, context: ''};
  }
}
function conclusionBlock(record) {
  const presentation = recordPresentation(record);
  const block = node('div', `conclusion${record.kind === 'decision' ? ' decision-conclusion' : ''}`);
  block.append(node('span','conclusion-label',record.kind === 'decision' ? 'KẾT LUẬN HỆ THỐNG GHI NHẬN' : 'NỘI DUNG HỆ THỐNG GHI NHẬN'));
  block.append(node('p','conclusion-title',presentation.title));
  if (presentation.context) block.append(node('p','conclusion-context',presentation.context));
  return block;
}
function reviewLabel(status) {
  return status === 'reviewed' ? 'Đã được người dùng kiểm tra' : status === 'needs_review'
    ? 'Cần người kiểm tra' : 'Chờ người dùng xác nhận';
}
function showError(message) { $('error').textContent = message; $('error').hidden = false; }
function countText() { $('text-count').textContent = `${$('transcript').value.length.toLocaleString('vi-VN')} ký tự`; }
function markChanged() { if (result) $('stale').hidden = false; countText(); }
function engineSettings() {
  const live = $('engine').value === 'llm_api';
  const recorded = $('engine').value === 'recorded';
  $('audit').disabled = !live || busy;
  $('transcript').readOnly = recorded;
  $('file').disabled = recorded || busy;
  $('recorded-notice').hidden = !recorded;
  const available = demoData?.cases.some(c => c.id === $('sample').value);
  $('analyze').disabled = busy || (recorded ? !available : !backendAvailable);
  $('engine-note').textContent = recorded ? 'Xem đầu ra nguyên bản của lượt hồi quy. Không phân tích mới; đổi sang LLM API để nhập transcript của bạn.' : live ? 'Transcript được gửi tới API đã cấu hình. Kết quả mới có thể khác lượt demo và vẫn cần đối chiếu bằng chứng.' : 'Offline chỉ nhận diện một số mẫu quyết định; không đại diện cho năng lực LLM.';
  if (!busy) $('analyze').replaceChildren(node('span','',recorded ? 'Xem kết quả đã lưu' : 'Phân tích cuộc họp'));
}
function setBusy(value) {
  busy = value;
  ['sample','transcript','engine','file','analyze'].forEach(id => $(id).disabled = value);
  $('download').disabled = value || !result;
  engineSettings();
  const button = $('analyze');
  button.replaceChildren();
  if (value) button.append(node('span','spinner'));
  button.append(node('span','',value ? 'Đang phân tích…' : 'Phân tích cuộc họp'));
  $('run-state').classList.toggle('running', value);
}
function chooseSample(id) {
  const sample = sampleData.find(item => item.id === id);
  if (sample) {
    $('transcript').value = sample.transcript;
    $('sample-description').textContent = sample.description;
  } else {
    $('sample-description').textContent = 'Dán transcript của bạn. Không có đáp án tham chiếu cho dữ liệu tùy chỉnh.';
  }
  markChanged();
  engineSettings();
}

function renderFilters() {
  const container = $('filters');
  container.replaceChildren();
  const records = result.analysis.records;
  const options = [['all',`Tất cả · ${records.length}`], ...Object.entries(kinds)
    .filter(([kind]) => records.some(record => record.kind === kind))
    .map(([kind, label]) => [kind, `${label} · ${records.filter(r => r.kind === kind).length}`])];
  for (const [value, label] of options) {
    const button = node('button', `filter${filter === value ? ' active' : ''}`, label);
    button.setAttribute('aria-pressed', String(filter === value));
    button.addEventListener('click', () => { filter = value; renderFilters(); renderRecords(); });
    container.append(button);
  }
  container.hidden = records.length === 0;
}

function renderRecords() {
  const container = $('records');
  container.replaceChildren();
  const records = result.analysis.records;
  let visible = 0;
  records.forEach((record, index) => {
    if (filter !== 'all' && filter !== record.kind) return;
    visible++;
    const button = node('button', `record${selected === index ? ' selected' : ''}`);
    button.setAttribute('aria-pressed', String(selected === index));
    const top = node('div','record-top');
    top.append(node('span','record-kind',kinds[record.kind] || record.kind), statusBadge(record.meeting_status));
    button.append(top, node('h3','',record.topic), conclusionBlock(record));
    const details = node('div','record-fields');
    if (record.kind === 'action') {
      const cancelled = record.meeting_status === 'cancelled';
      details.append(node('span','',`${cancelled ? 'Người từng phụ trách' : 'Phụ trách'}: ${record.owner || 'Chưa nêu / cần làm rõ'}`));
      details.append(node('span','',`${cancelled ? 'Hạn còn lưu trong bản ghi' : 'Hạn'}: ${record.due_raw || (cancelled ? 'Không có' : 'Chưa nêu')}`));
    }
    if (record.supporter) details.append(node('span','',`Hỗ trợ: ${record.supporter}`));
    if (record.condition) details.append(node('span','',`Điều kiện: ${record.condition}`));
    if (record.execution_status === 'blocked') details.append(node('span','', 'Chưa được triển khai'));
    if (details.childNodes.length) button.append(details);
    const bottom = node('div','record-bottom');
    const review = record.review_status === 'needs_review';
    bottom.append(node('span',review ? 'review' : '', `Rà soát bản ghi: ${reviewLabel(record.review_status)}`),
      node('span','',`${record.history.length} sự kiện · ${record.evidence_ids.length} câu nguồn`), node('span','arrow','↗'));
    const human=currentReview?.records[index];
    if(human && human.decision!=='pending') bottom.append(node('span',human.decision==='rejected'?'human-rejected':'human-confirmed',human.decision==='rejected'?'Bản người dùng: đã từ chối, không xuất CSV':'Bản người dùng: đã xác nhận nội dung (AI gốc vẫn giữ nguyên)'));
    button.append(bottom);
    button.addEventListener('click', () => { selected = index; renderRecords(); renderDetail(); renderHumanReview(); });
    container.append(button);
  });
  if (!visible) {
    const empty = node('div','empty-state');
    empty.append(node('h3','', 'Không có bản ghi được trích xuất'),
      node('p','',result.analysis.engine === 'offline_rules' ? 'Baseline offline có phạm vi hẹp. Thử T02/T03/T04 hoặc chuyển sang LLM API.' : 'Đọc transcript và cảnh báo để kiểm tra liệu hệ thống đã bỏ sót thông tin.'));
    container.append(empty);
  }
}

function showEvidenceTab(view) {
  $('timeline').hidden = view !== 'history';
  $('source-view').hidden = view !== 'transcript';
  $('show-history').classList.toggle('active', view === 'history');
  $('show-transcript').classList.toggle('active', view === 'transcript');
}
function focusSource(id) {
  showEvidenceTab('transcript');
  document.querySelectorAll('.source-line.focused').forEach(line => line.classList.remove('focused'));
  const line = document.getElementById(`source-${id}`);
  if (line) { line.classList.add('focused'); line.scrollIntoView({behavior: 'smooth', block: 'nearest'}); }
}
function sourceLink(id) {
  const button = node('button','source-link',id);
  button.setAttribute('aria-label',`Xem câu nguồn ${id}`);
  button.addEventListener('click',() => focusSource(id));
  return button;
}

const eventRules = {
  proposal:'Ghi nhận đề xuất, chưa coi là đã chốt. Đề xuất mới sau phát biểu chốt được giữ để rà soát.',
  counterproposal:'Ghi nhận phương án khác được đề xuất; chưa tự coi là đồng thuận.',
  agreement:'Cập nhật thành đã thống nhất trong họp; không tự suy ra quyền phê duyệt của tổ chức.',
  conditional_agreement:'Giữ lựa chọn đã thống nhất có điều kiện và bộ điều kiện được trích; chưa coi điều kiện đã đạt.',
  reopen:'Mở lại lựa chọn, xóa điều kiện hiện hành; giữ nội dung cũ trong lịch sử.',
  unresolved:'Giữ mục còn mở, chưa có lựa chọn cuối; không tự chọn một đề xuất.',
  withdrawal:'Rút lựa chọn khỏi trạng thái hiện hành, giữ lịch sử để truy lại.',
  execution_blocked:'Ghi nhận chưa được triển khai; không tự mở lại quyết định đã thống nhất.',
  assignment:'Cập nhật phân công và các trường được trích; trường không có dữ liệu không tự được điền.',
  reassignment:'Cập nhật phân công mới; nếu chưa rõ người nhận thì giữ để rà soát.',
  deadline_change:'Chỉ cập nhật hoặc xóa hạn, không tự đổi người hoặc kích hoạt lại việc đã hủy.',
  action_cancelled:'Đánh dấu công việc đã hủy. Giữ thông tin lịch sử trừ những trường được yêu cầu xóa rõ ràng.',
  request_made:'Ghi nhận yêu cầu; không tự biến thành công việc đã giao cho một người.',
  request_changed:'Cập nhật nội dung yêu cầu theo sự kiện được trích.',
  request_withdrawn:'Đánh dấu yêu cầu đã rút, giữ nội dung cũ trong lịch sử.',
  issue_reported:'Giữ vướng mắc ở trạng thái còn mở.',
  issue_reported_resolved:'Chỉ ghi được báo đã xử lý; không coi đã xác minh ngoài thực tế.',
  feedback_given:'Ghi nhận phản hồi, không tự biến thành quyết định hoặc nhiệm vụ.',
  knowledge_shared:'Giữ tri thức chưa xác minh, không coi là sự thật đã được kiểm chứng.'
};
function sourceQuote(id, utterances) {
  const source = utterances.get(id), cell = node('div','trace-quote');
  cell.append(sourceLink(id),node('span','trace-speaker',source?.speaker || 'Chưa rõ người nói'),
    node('p','',source ? `“${source.text}”` : 'Không tìm thấy câu nguồn.'));
  return cell;
}
function makeTraceTable(headers, rows) {
  const table = node('table','trace-table'), head = node('thead'), tr = node('tr');
  headers.forEach(label => { const th = node('th','',label); th.scope = 'col'; tr.append(th); });
  head.append(tr); table.append(head);
  const body = node('tbody');
  rows.forEach(cells => { const row = node('tr'); cells.forEach(value => { const td = node('td'); td.append(typeof value === 'string' ? document.createTextNode(value) : value); row.append(td); }); body.append(row); });
  table.append(body); return table;
}
function renderExplanation(record, utterances) {
  $('explanation-panel').hidden = !record;
  if (!record) return;
  $('explanation-title').textContent = `${kinds[record.kind]} · ${record.topic}`;
  const execution = {unknown:'Chưa xác định',blocked:'Chưa được triển khai',pending_condition:'Chờ đáp ứng điều kiện',not_applicable:'Không áp dụng'};
  const provenance = record.field_evidence_ids || {};
  const fieldRows = Object.entries(provenance).map(([field,ids]) => {
    const sources = node('div'); ids.forEach(id => sources.append(sourceQuote(id,utterances)));
    if (!ids.length) sources.append(node('p','','Chưa có câu nguồn riêng cho trường này.'));
    const raw = record[field];
    const value = field === 'meeting_status' ? statuses[raw] || raw : field === 'execution_status' ? execution[raw] || raw : raw ?? 'Không có giá trị hiện hành';
    const label = field === 'owner' && record.meeting_status === 'cancelled' ? 'Người từng phụ trách' : fields[field] || field;
    return [label,String(value),sources];
  });
  $('conclusion-table').replaceChildren(makeTraceTable(['Trường kết quả','Giá trị hiện tại','Câu nguồn được hệ thống gắn'],fieldRows));
  const cuePattern = /chưa\s+(?:chốt|chọn|quyết\s+định|nhận)|không\s+(?:chốt|tiếp\s+tục)|mở\s+lại|rút\s+(?:lời\s+chốt|đề\s+xuất)|chốt|đồng\s+ý|thống\s+nhất|đề\s+xuất|đề\s+nghị|nếu|cho\s+đến\s+khi|hủy|bỏ\s+hạn|yêu\s+cầu|phản\s+hồi|tôi\s+nhận|phụ\s+trách|hạn/giu;
  const eventRows = [];
  for (const event of record.history) {
    const cleared = (event.clear_fields || []).filter(f => event.event_type !== 'deadline_change' || f === 'due_raw');
    const rule = (eventRules[event.event_type] || 'Xem sự kiện được trích và JSON gốc.') + (cleared.length ? ` Trường được đánh dấu xóa: ${cleared.map(f => fields[f] || f).join(', ')}.` : '');
    for (const id of event.source_ids) {
      const quote = utterances.get(id)?.text || '';
      const cues = [...new Set(quote.match(cuePattern) || [])];
      const classification = node('div'); classification.append(node('strong','',events[event.event_type] || event.event_type));
      if (event.value) classification.append(node('p','',event.value));
      eventRows.push([sourceQuote(id,utterances),cues.length ? cues.map(c => `“${c}”`).join(', ') : 'Không có cụm gợi ý trong danh sách hiển thị; cần đọc ngữ cảnh.',classification,rule]);
    }
  }
  $('event-table').replaceChildren(makeTraceTable(['Phát biểu nguyên văn','Cụm gợi ý xuất hiện trong câu','Phân loại hệ thống đã trích','Quy tắc xử lý tương ứng'],eventRows));
  const findings = result.analysis.audit_findings.filter(f => f.issue_key === record.issue_key && (!f.kind || f.kind === record.kind));
  $('audit-explanation').hidden = !findings.length;
  $('audit-table').replaceChildren(makeTraceTable(['Nguồn audit dẫn','Nhận xét của LLM audit','Cách sử dụng nhận xét'],findings.map(f => {
    const source = node('div'); f.source_ids.forEach(id => source.append(sourceLink(id))); source.append(node('p','',`“${f.source_quote}”`));
    return [source,f.explanation,'Đây là cảnh báo cần rà soát, không phải kết luận thay thế hay bằng chứng audit luôn đúng.'];
  })));
}

function renderDetail() {
  const record = result.analysis.records[selected];
  $('detail').hidden = !record;
  $('detail-empty').hidden = !!record;
  $('explanation-panel').hidden = !record;
  if (!record) return;
  $('detail-kind').textContent = `${kinds[record.kind]} · ${record.issue_key}`;
  $('detail-title').textContent = record.topic;
  $('detail-status').replaceChildren(statusBadge(record.meeting_status));
  $('detail-conclusion').replaceChildren(conclusionBlock(record),
    node('p','detail-review',`Rà soát bản ghi: ${reviewLabel(record.review_status)}. Đây là bước kiểm tra bản ghi, không phải trạng thái chốt của cuộc họp.`));
  const jump = node('button','button secondary trace-jump','Xem bảng câu nguồn → kết luận');
  jump.addEventListener('click',() => $('explanation-panel').scrollIntoView({behavior:'smooth',block:'start'}));
  $('detail-conclusion').append(jump);
  const utterances = new Map(result.analysis.utterances.map(u => [u.id,u]));
  const timeline = $('timeline');
  timeline.replaceChildren();
  record.history.forEach(event => {
    const item = node('div','timeline-event');
    const top = node('div','event-top');
    top.append(node('strong','',events[event.event_type] || event.event_type),node('span','source-id',event.source_ids.join(', ')));
    item.append(top);
    if (event.value) item.append(node('p','',event.value));
    const values = [];
    for (const field of ['owner','supporter','due_raw','condition']) {
      if (event[field]) values.push(`${fields[field]}: ${event[field]}`);
    }
    if (event.clear_fields?.length) values.push(`Thu hồi: ${event.clear_fields.map(f => fields[f] || f).join(', ')}`);
    if (values.length) item.append(node('p','',values.join(' · ')));
    for (const id of event.source_ids) {
      const source = utterances.get(id);
      const quote = node('button','quote',source ? `${source.speaker ? source.speaker + ': ' : ''}“${source.text}”` : `Không tìm thấy ${id}`);
      quote.addEventListener('click',() => focusSource(id));
      item.append(quote);
    }
    timeline.append(item);
  });
  for (const finding of result.analysis.audit_findings.filter(f => f.issue_key === record.issue_key && (!f.kind || f.kind === record.kind))) {
    const item = node('div','timeline-event');
    item.append(node('div','event-top','Audit · phát hiện cần rà soát'),node('p','',finding.explanation));
    const quote = node('button','quote',`“${finding.source_quote}”`);
    quote.addEventListener('click',() => focusSource(finding.source_ids[0]));
    item.append(quote); timeline.append(item);
  }
  if (record.warnings.length) {
    const warnings = node('div','engine-note');
    warnings.append(node('strong','','Lưu ý của bản ghi'));
    record.warnings.forEach(warning => warnings.append(node('p','',warning)));
    timeline.append(warnings);
  }
  const sourceLines = $('source-lines');
  sourceLines.replaceChildren();
  for (const utterance of result.analysis.utterances) {
    const tone = record.counter_evidence_ids.includes(utterance.id) ? 'changed' : record.evidence_ids.includes(utterance.id) ? 'cited' : '';
    const line = node('article',`source-line ${tone}`);
    line.id = `source-${utterance.id}`;
    const header = node('header');
    header.append(node('span','source-id',utterance.id),node('span','',[utterance.speaker,utterance.timestamp].filter(Boolean).join(' · ') || 'Không có người nói / thời gian'));
    line.append(header,node('p','',utterance.text));
    sourceLines.append(line);
  }
  const provenance = $('field-evidence');
  provenance.replaceChildren(node('h4','','Nguồn theo từng trường'));
  for (const [field, ids] of Object.entries(record.field_evidence_ids || {})) {
    const row = node('div','field-row');
    row.append(node('span','',fields[field] || field));
    const links = node('span');
    ids.forEach((id,index) => { if(index) links.append(document.createTextNode(' · ')); links.append(sourceLink(id)); });
    row.append(links); provenance.append(row);
  }
  provenance.append(node('p','','Nguồn có thật chưa bảo đảm cách diễn giải đúng. Hãy đọc cả ngữ cảnh.'));
  renderExplanation(record,utterances);
  showEvidenceTab('history');
}

function renderEvaluation() {
  const evaluation = result.evaluation;
  $('evaluation').hidden = !evaluation;
  if (!evaluation) return;
  $('evaluation-summary').textContent = `${evaluation.case} · ${evaluation.status === 'PASS' ? 'Đạt' : 'Chưa đạt'} theo đáp án tham chiếu`;
  $('evaluation-summary').className = evaluation.status === 'PASS' ? 'eval-pass' : 'eval-fail';
  const body = $('evaluation-body');
  body.replaceChildren(node('p','',evaluation.label));
  if (evaluation.errors.length) {
    const list = node('ul');
    evaluation.errors.forEach(error => list.append(node('li','',error)));
    body.append(list);
  }
  body.append(node('h4','','Kỳ vọng trước khi chạy'));
  for (const expected of evaluation.expectations) {
    const item = node('div','expectation');
    item.append(node('strong','',`${kinds[expected.kind]} · ${statuses[expected.status] || expected.status}`));
    const parts = [];
    if (expected.content_contains) parts.push(`Có nội dung: ${expected.content_contains}`);
    for (const field of ['owner','supporter','due_raw','condition']) {
      if (field in expected) parts.push(`${fields[field]}: ${expected[field] ?? 'Chưa nêu'}`);
    }
    if (expected.must_cite?.length) parts.push(`Nguồn: ${expected.must_cite.join(', ')}`);
    if (expected.counter_cite?.length) parts.push(`Nguồn thay đổi: ${expected.counter_cite.join(', ')}`);
    item.append(node('p','',parts.join(' · '))); body.append(item);
  }
  body.append(node('p','','PASS chỉ kiểm tra các trường đã gán nhãn; vẫn cần đọc bằng chứng để đánh giá ngữ nghĩa.'));
  $('evaluation').open = true;
}

function renderResult() {
  const {analysis} = result;
  const recorded = result.source_mode === 'recorded';
  if (!resultSessionIds.has(result)) resultSessionIds.set(result,recorded ? `recorded:${result.provenance.run_sha256}:${result.provenance.case}` : `live:${crypto.randomUUID()}`);
  const id = resultSessionIds.get(result);
  if (!reviewSessions.has(id)) reviewSessions.set(id,MeetingReview.create(analysis,id,{source_mode:result.source_mode||'live',model:result.model||null,provenance:result.provenance||null}));
  currentReview = reviewSessions.get(id);
  if(!result.restored_from_local)$('recorded-notice').textContent='Kết quả LLM thật đã lưu · Không gọi API hoặc phân tích transcript mới. Giữ nguyên cả kết quả sai để đối chiếu.';
  $('metric-records').textContent = analysis.records.length;
  $('metric-review').textContent = analysis.records.filter(r => r.review_status === 'needs_review').length;
  $('metric-time').textContent = recorded || result.restored_from_local ? 'Đã lưu' : `${result.duration_s}s`;
  $('result-engine').textContent = result.restored_from_local ? 'Phiên đã lưu trên máy' : recorded ? 'Bản ghi LLM đã lưu' : analysis.engine === 'llm_api' ? 'LLM API mới' : 'Offline · theo luật';
  $('result-engine').className = `badge ${analysis.engine === 'llm_api' ? 'green' : 'amber'}`;
  $('api-metrics').textContent = recorded || result.restored_from_local ? 'Lượt xem này: 0 API call' : `${result.api_calls} API call${result.token_usage.total_tokens ? ' · ' + result.token_usage.total_tokens.toLocaleString('vi-VN') + ' token' : ''}`;
  $('demo-review').hidden = !recorded;
  if (recorded) {
    const review = result.review;
    $('demo-review').open = false;
    $('demo-review-summary').textContent = `Đánh giá bộ kiểm thử ${review.id}: ${review.verdict === 'PASS' ? 'đạt' : 'chưa đạt đầy đủ'} · Mở để xem`;
    const panel = $('demo-review-body');
    panel.replaceChildren(node('p','review-explainer','Đây là nhận xét đối chiếu với đáp án do trợ lý chuẩn bị, không phải nội dung cuộc họp hoặc kết quả LLM mới. “Đạt/chưa đạt” đánh giá chất lượng trích xuất, không nói cuộc họp đã chốt hay chưa.'));
    for (const [label,key] of [['Đáp án mong đợi','expectation'],['Nhận xét về đầu ra hệ thống','observed'],['Điều học được khi kiểm thử','lesson']]) {
      const p = node('p'); p.append(node('b','',label + ': '), document.createTextNode(review[key])); panel.append(p);
    }
    const date = new Date(result.provenance.created_utc).toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh'});
    panel.append(node('small','',`Review cùng trợ lý, chưa độc lập · Lượt hồi quy bắt đầu ${date} ICT · ${result.model}. Thời gian gốc ${result.duration_s}s gồm khoảng nghỉ; không phải thời gian xem hiện tại.`));
    $('footer-model').textContent = `Đang xem kết quả đã lưu · SHA-256 ${result.provenance.run_sha256.slice(0,12)}…`;
  } else {
    $('footer-model').textContent = result.restored_from_local ? 'Đang xem phiên lưu trên máy · không gọi API.' : result.model ? `Lượt phân tích mới · ${result.model}` : 'Baseline offline · không gọi LLM.';
  }
  $('raw-json').textContent = JSON.stringify(result, null, 2);
  $('warnings-list').replaceChildren();
  analysis.warnings.forEach(warning => $('warnings-list').append(node('li','',warning)));
  $('warnings').hidden = analysis.warnings.length === 0;
  $('warnings-summary').textContent = `${analysis.warnings.length} lưu ý của lượt chạy`;
  filter = 'all'; selected = analysis.records.length ? 0 : -1;
  renderFilters(); renderRecords(); renderDetail(); renderEvaluation();
  renderHumanReview();
  setResultTab('records');
}

function reviewKindSettings(preferred) {
  const kind = $('review-kind').value, select = $('review-meeting-status');
  select.replaceChildren();
  MeetingReview.statuses[kind].forEach(value => { const option = node('option','',statuses[value]); option.value = value; select.append(option); });
  select.value = MeetingReview.statuses[kind].includes(preferred) ? preferred : 'unverified';
  for (const [id,allowed] of [['review-owner',kind==='action'],['review-supporter',kind==='action'],['review-due',['action','request'].includes(kind)],['review-condition',['decision','action'].includes(kind)]]) {
    $(id).disabled = !allowed; if(!allowed) $(id).value = '';
  }
}
function renderHumanReview() {
  $('review-message').textContent='';
  $('human-review-panel').hidden = !currentReview;
  if (!currentReview) return;
  const counts = {pending:0,confirmed:0,rejected:0}; currentReview.records.forEach(r=>counts[r.decision]++);
  $('review-counts').textContent = `${counts.pending} chờ rà soát · ${counts.confirmed} đã xác nhận nội dung · ${counts.rejected} bị từ chối`;
  $('export-review-csv').disabled = !counts.confirmed;
  const selector = node('select'); selector.setAttribute('aria-label','Chọn bản ghi để rà soát');
  currentReview.records.forEach((r,i)=>{const option=node('option','',`${i+1}. ${result.analysis.records[i].topic} · ${{pending:'Chờ rà soát',confirmed:'Đã xác nhận',rejected:'Đã từ chối'}[r.decision]}`);option.value=i;selector.append(option);});
  selector.value=selected;
  selector.addEventListener('change',()=>{selected=Number(selector.value);renderRecords();renderDetail();renderHumanReview();});
  $('review-record-selector').replaceChildren(node('label','','Chọn bản ghi (lưu chỉnh sửa trước khi chuyển)'),selector);
  const entry=currentReview.records[selected];
  $('human-review-form').hidden=!entry;
  $('review-record-title').textContent=entry ? `Bản rà soát ${selected+1}: ${result.analysis.records[selected].topic}` : 'Không có bản ghi để rà soát.';
  $('review-original').replaceChildren(); $('review-history').replaceChildren();
  if(entry){
    const original=currentReview.original_analysis.records[selected];
    $('review-original').append(node('strong','','AI gốc (không thay đổi)'),node('p','',`${kinds[original.kind]} · ${statuses[original.meeting_status]} · ${original.content||'Chưa có nội dung'}`));
    $('review-kind').replaceChildren();Object.entries(kinds).forEach(([value,label])=>{const option=node('option','',label);option.value=value;$('review-kind').append(option);});
    $('review-kind').value=entry.draft.kind;
    for(const [id,field] of [['review-content','content'],['review-owner','owner'],['review-supporter','supporter'],['review-due','due_raw'],['review-condition','condition']])$(id).value=entry.draft[field]||'';
    reviewKindSettings(entry.draft.meeting_status);
    $('review-sources').value=entry.source_ids.join(', ');$('review-reason').value='';$('review-checked').checked=false;
    if(!entry.history.length)$('review-history').append(node('p','','Chưa có thao tác của người dùng.'));
    entry.history.forEach(h=>{const detail=node('details');detail.append(node('summary','',`${new Date(h.at).toLocaleString('vi-VN')} · ${h.actor} · ${{confirmed:'Xác nhận',edited:'Chỉnh sửa, chờ xác nhận',rejected:'Từ chối',reopened:'Mở lại'}[h.action]}`));detail.append(node('p','',h.reason||'Xác nhận nội dung sau đối chiếu.'),node('pre','',JSON.stringify(h,null,2)));$('review-history').append(detail);});
  }
  const ready=MeetingReview.confirmed(currentReview);
  $('confirmed-records').replaceChildren(node('h3','','Bản đã xác nhận để xuất dữ liệu'));
  if(!ready.length)$('confirmed-records').append(node('p','','Chưa có bản được xác nhận. Bản chờ hoặc bị từ chối không vào CSV.'));
  ready.forEach(r=>$('confirmed-records').append(node('article','confirmed-item',`${kinds[r.kind]} · ${statuses[r.meeting_status]} · ${r.content}`)));
}
function applyHumanReview(confirm=false) {
  if(busy||!currentReview||!$('stale').hidden)throw new Error('Kết quả đang cũ hoặc đang chạy. Hãy mở đúng kết quả trước khi rà soát.');
  if(confirm&&!$('review-checked').checked)throw new Error('Hãy đánh dấu đã đối chiếu câu nguồn trước khi xác nhận.');
  const patch={kind:$('review-kind').value,content:$('review-content').value.trim(),meeting_status:$('review-meeting-status').value};
  for(const [id,key] of [['review-owner','owner'],['review-supporter','supporter'],['review-due','due_raw'],['review-condition','condition']])patch[key]=$(id).value.trim()||null;
  const ids=$('review-sources').value.split(',').map(v=>v.trim()).filter(Boolean);
  MeetingReview.update(currentReview,selected,patch,ids,$('review-actor').value,$('review-reason').value,confirm);
  renderRecords();renderHumanReview();$('review-message').textContent=confirm?'Đã xác nhận bản rà soát. Đầu ra AI và điểm kiểm thử gốc vẫn giữ nguyên.':'Đã lưu chỉnh sửa trong phiên, cần xác nhận lại để đưa vào CSV.';
}
function downloadText(text,filename,type){const url=URL.createObjectURL(new Blob([text],{type}));const link=node('a');link.href=url;link.download=filename;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function reviewAction(action){try{action();}catch(error){$('review-message').textContent=error.message;}}
$('review-kind').addEventListener('change',()=>reviewKindSettings($('review-meeting-status').value));
$('human-review-form').addEventListener('submit',event=>{event.preventDefault();reviewAction(()=>applyHumanReview(true));});
$('review-edit').addEventListener('click',()=>reviewAction(()=>applyHumanReview(false)));
for(const [id,decision] of [['review-reject','rejected'],['review-reopen','pending']])$(id).addEventListener('click',()=>reviewAction(()=>{
  if(busy||!$('stale').hidden)throw new Error('Hãy mở đúng kết quả trước khi rà soát.');
  MeetingReview.decide(currentReview,selected,decision,$('review-actor').value,$('review-reason').value);renderRecords();renderHumanReview();$('review-message').textContent=decision==='rejected'?'Đã từ chối; giữ bản gốc và lý do, không đưa bản này vào CSV.':'Đã mở lại; bản này không còn trong danh sách đã xác nhận.';
}));
$('export-review-json').addEventListener('click',()=>reviewAction(()=>downloadText(JSON.stringify(MeetingReview.exportJSON(currentReview),null,2),'meeting-human-review.json','application/json;charset=utf-8')));
$('export-review-csv').addEventListener('click',()=>reviewAction(()=>downloadText(MeetingReview.exportCSV(currentReview),'meeting-confirmed.csv','text/csv;charset=utf-8')));
$('save-review').addEventListener('click',()=>reviewAction(()=>{
  if(busy||!$('stale').hidden)throw new Error('Mở đúng kết quả trước khi lưu phiên; transcript/tùy chọn đã thay đổi.');
  localStorage.setItem(REVIEW_STORAGE_KEY,JSON.stringify({session:currentReview,result,input_transcript:$('transcript').value,saved_at:new Date().toISOString()}));
  $('review-save-status').textContent=`Đã lưu phiên gần nhất (${result.provenance?.case||'phân tích mới'}) trên trình duyệt này. Không gửi dữ liệu lên server.`;
}));
$('restore-review').addEventListener('click',()=>{
  try{
    if(busy)throw new Error('Chờ lượt phân tích hoàn tất trước khi mở phiên.');
    const raw=localStorage.getItem(REVIEW_STORAGE_KEY);if(!raw)throw new Error('Chưa có phiên đã lưu trên trình duyệt này.');
    const saved=JSON.parse(raw);const session=MeetingReview.restore(saved.session,saved.result.analysis,saved.session.id);
    result=structuredClone(saved.result);result.restored_from_local=true;resultSessionIds.set(result,session.id);reviewSessions.set(session.id,session);
    $('transcript').value=saved.input_transcript;$('sample').value=demoData?.cases.some(c=>c.id===result.provenance?.case)?result.provenance.case:'custom';
    countText();renderResult();$('stale').hidden=true;
    $('recorded-notice').hidden=false;$('recorded-notice').textContent='Đang xem phiên rà soát đã lưu trên máy; không chạy LLM mới. Nội dung AI gốc và chỉnh sửa người dùng được giữ riêng.';
    $('review-save-status').textContent=`Đã mở phiên lưu ${new Date(saved.saved_at).toLocaleString('vi-VN')}.`; $('download').disabled=false;
  }catch(error){$('review-save-status').textContent=error.message;}
});

function setResultTab(view) {
  for (const name of ['records','json']) {
    $(`${name}-view`).hidden = name !== view;
    $(`tab-${name}`).classList.toggle('active', name === view);
    $(`tab-${name}`).setAttribute('aria-selected',String(name === view));
    $(`tab-${name}`).tabIndex = name === view ? 0 : -1;
  }
}

async function runAnalysis() {
  if (busy) return;
  if ($('engine').value === 'recorded') {
    const saved = demoData?.cases.find(c => c.id === $('sample').value);
    if (!saved || $('transcript').value !== saved.transcript) { showError('Chọn tình huống demo nguyên bản. Transcript mới cần chế độ LLM API.'); return; }
    $('error').hidden = true;
    result = structuredClone(saved.result);
    renderResult(); $('stale').hidden = true;
    $('download').disabled = false;
    $('run-state').textContent = 'Đã mở kết quả LLM lưu từ trước · không gọi API';
    return;
  }
  const text = $('transcript').value;
  if (!text.trim()) { showError('Hãy nhập transcript hoặc chọn một tình huống mẫu.'); $('transcript').focus(); return; }
  $('error').hidden = true;
  setBusy(true);
  const start = Date.now();
  const update = () => { $('run-state').textContent = `Đang chạy ${$('engine').value === 'llm_api' ? 'LLM và kiểm chứng' : 'baseline offline'} · ${Math.floor((Date.now()-start)/1000)}s`; };
  update(); const timer = setInterval(update,1000);
  try {
    const response = await fetch('/api/analyze', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({transcript:text,engine:$('engine').value,audit:$('audit').checked,sample_id:$('sample').value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể hoàn tất phân tích.');
    result = data;
    renderResult();
    $('stale').hidden = true;
    $('run-state').textContent = `Hoàn tất · ${data.duration_s}s · chọn bản ghi để xem nguồn`;
  } catch(error) {
    showError(error.message === 'Failed to fetch' ? 'Không kết nối được Python. Kiểm tra terminal đang chạy python web.py.' : error.message);
    $('run-state').textContent = 'Lượt chạy chưa hoàn tất. Kiểm tra thông báo lỗi.';
    if (result) $('stale').hidden = false;
  } finally { clearInterval(timer); setBusy(false); }
}

$('sample').addEventListener('change',event => chooseSample(event.target.value));
$('transcript').addEventListener('input',markChanged);
$('engine').addEventListener('change',() => {
  if ($('engine').value === 'recorded' && !demoData?.cases.some(c => c.id === $('sample').value)) {
    $('sample').value = demoData?.cases[0]?.id || 'custom'; chooseSample($('sample').value);
  }
  engineSettings(); markChanged();
});
$('audit').addEventListener('change',markChanged);
$('analyze').addEventListener('click',runAnalysis);
$('show-history').addEventListener('click',() => showEvidenceTab('history'));
$('show-transcript').addEventListener('click',() => showEvidenceTab('transcript'));
for (const view of ['records','json']) {
  $(`tab-${view}`).addEventListener('click',() => setResultTab(view));
  $(`tab-${view}`).addEventListener('keydown',event => {
    if (['ArrowLeft','ArrowRight'].includes(event.key)) {
      event.preventDefault(); const next = view === 'records' ? 'json' : 'records'; setResultTab(next); $(`tab-${next}`).focus();
    }
  });
}
$('file').addEventListener('change',async event => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    if (file.size > 600000) throw new Error('Tệp quá lớn. Hãy chọn transcript dưới 600 KB.');
    const text = await file.text();
    if (text.length > 100000) throw new Error('Tệp vượt giới hạn 100.000 ký tự.');
    $('transcript').value = text; $('sample').value = 'custom'; chooseSample('custom');
  } catch(error) { showError(error.message); }
  event.target.value = '';
});
$('download').addEventListener('click',() => {
  if (!result) return;
  const blob = new Blob([JSON.stringify(result,null,2)],{type:'application/json;charset=utf-8'});
  const url = URL.createObjectURL(blob), link = node('a');
  link.href = url; link.download = `meeting-analysis-${new Date().toISOString().replace(/[:.]/g,'-')}.json`;
  document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url),1000);
});

function populateSamples(samples) {
  sampleData = samples;
  $('sample').replaceChildren();
  sampleData.forEach(sample => {
    const option = node('option','',`${sample.id} · ${sample.description}`);
    option.value = sample.id; $('sample').append(option);
  });
  const custom = node('option','','Transcript của bạn'); custom.value = 'custom'; $('sample').append(custom);
  $('sample').value = sampleData.some(sample => sample.id === 'D01') ? 'D01' : sampleData.some(sample => sample.id === 'T03') ? 'T03' : 'custom';
  chooseSample($('sample').value);
  $('sample').disabled = false;
}

async function staticPreview() {
  $('static-preview').hidden = false;
  $('config-status').textContent = 'Demo tĩnh đã sẵn sàng; phân tích transcript mới cần backend Python.';
  $('footer-model').textContent = 'Demo tĩnh · kết quả LLM đã lưu · không gọi API.';
  $('run-state').textContent = 'Chọn tình huống để xem kết quả đã lưu.';
  $('engine').value = 'recorded';
  [...$('engine').options].forEach(option => option.disabled = option.value !== 'recorded');
  if (demoData) { populateSamples(demoData.cases); engineSettings(); await runAnalysis(); return; }
  const loaded = await Promise.allSettled(['T01','T02','T03','T04','T05','T06','T07'].map(async id => {
    const responses = await Promise.all([fetch(`../samples/expected/${id}.json`), fetch(`../samples/${id}.txt`)]);
    if (responses.some(response => !response.ok)) throw new Error('Không tải được mẫu');
    const [expected, transcript] = await Promise.all([responses[0].json(), responses[1].text()]);
    return {...expected, transcript};
  }));
  populateSamples(loaded.filter(item => item.status === 'fulfilled').map(item => item.value));
}

async function initialize() {
  try {
    const response = await fetch('./demo-data.json');
    if (!response.ok) throw new Error('Thiếu dữ liệu demo');
    demoData = await response.json();
    const stats = demoData.summary;
    $('demo-summary').replaceChildren(node('strong','','Bộ demo đã lưu · 8 tình huống cùng phiên bản'),node('span','',`${stats.strict_case_passed}/8 đạt đầy đủ · ${stats.core_data_passed}/8 đúng dữ liệu lõi · Có cả lỗi thật để đối chiếu`));
    $('demo-summary').hidden = false;
  } catch { $('engine').querySelector('[value="recorded"]').disabled = true; $('engine').value = 'offline_rules'; }
  try {
    const responses = await Promise.all([fetch('/api/config'),fetch('/api/samples')]);
    if (responses.some(response => !response.ok)) throw new Error('Backend chưa sẵn sàng.');
    const [config,data] = await Promise.all(responses.map(response => response.json()));
    backendAvailable = true;
    populateSamples([...(demoData?.cases || []),...data.samples]);
    $('config-status').textContent = config.api_configured ? `Đã có cấu hình · ${config.provider} · ${config.model}` : 'Chưa có khóa API hợp lệ trong .env. Bạn vẫn chạy được chế độ offline.';
    $('footer-model').textContent = config.model ? `Model cấu hình: ${config.model}` : 'Chế độ offline không gọi API.';
    $('sample').disabled = false;
    $('run-state').textContent = 'Sẵn sàng · chưa gọi API';
    engineSettings();
    if (demoData && $('engine').value === 'recorded') await runAnalysis();
  } catch(error) {
    await staticPreview();
  }
}
initialize();
