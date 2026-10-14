"""OpenAI-compatible Chat Completions adapter with safe error reporting.

All calls need explicit API credentials. No silent synthetic response or mock
fallback is used in production/API mode. Only HTTPS or loopback HTTP allowed.
"""
from __future__ import annotations
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from .config import load_local_config

class LLMError(RuntimeError):
    def __init__(self, message, *, status_code=None, provider_code=None, diagnostics=None):
        super().__init__(message)
        self.status_code = status_code
        self.provider_code = provider_code
        self.diagnostics = diagnostics or {}


def strict_schema(schema):
    """Convert Pydantic's schema to the strict provider subset, without mutation.

    All object properties are required; nullable fields remain nullable.
    Local Pydantic validation still enforces constraints and event semantics.
    """
    if isinstance(schema, list):
        return [strict_schema(item) for item in schema]
    if not isinstance(schema, dict):
        return schema
    result = {key: strict_schema(value) for key, value in schema.items()
              if key not in {'default', 'minLength', 'maxLength', 'minItems', 'maxItems'}}
    if result.get('type') == 'object':
        result['additionalProperties'] = False
        result['required'] = list(result.get('properties', {}))
    return result

class LLMClient:
    def __init__(self, *, api_key: str | None = None, base_url: str | None = None,
                 model: str | None = None, timeout: int = 60,
                 json_mode: bool | None = None, max_retries: int = 1,
                 max_retry_wait: float = 60, min_call_interval: float = 0,
                 structured_mode: str | None = None, max_completion_tokens: int | None = None,
                 temperature: float | None = None, reasoning_effort: str | None = None):
        load_local_config()
        self.api_key = api_key or os.environ.get('LLM_API_KEY', '')
        self.base_url = (base_url or os.environ.get('LLM_BASE_URL', '')).rstrip('/')
        self.model = model or os.environ.get('LLM_MODEL', '')
        self.timeout = timeout
        self.max_retries = max(0, min(3, max_retries))
        self.max_retry_wait = max(0, max_retry_wait)
        self.min_call_interval = max(0, min_call_interval)
        self.last_call_at = 0.0
        self.json_mode = (os.environ.get('LLM_JSON_MODE', 'true').lower() not in {'0','false','no'}
                          if json_mode is None else json_mode)
        self.structured_mode = structured_mode or os.environ.get('LLM_STRUCTURED_OUTPUTS', 'auto')
        if self.structured_mode not in {'auto', 'strict', 'off'}:
            raise LLMError('LLM_STRUCTURED_OUTPUTS phải là auto, strict hoặc off.')
        self.call_count = 0
        self.token_usage: dict[str, int] = {}
        if not all([self.api_key, self.base_url, self.model]):
            raise LLMError('Thiếu LLM_API_KEY, LLM_BASE_URL hoặc LLM_MODEL; không giả lập kết quả LLM thật.')
        from urllib.parse import urlparse
        addr = urlparse(self.base_url)
        secure = addr.scheme == 'https' and bool(addr.hostname)
        local = addr.scheme == 'http' and addr.hostname in {'localhost', '127.0.0.1', '::1'}
        if not (secure or local) or addr.username or addr.password or addr.query or addr.fragment:
            raise LLMError('LLM_BASE_URL cần là HTTPS, ngoại trừ máy chủ localhost; không chứa thông tin đăng nhập.')
        groq_oss = addr.hostname == 'api.groq.com' and self.model in {'openai/gpt-oss-20b','openai/gpt-oss-120b'}
        try:
            self.temperature = float(temperature if temperature is not None else
                                     os.environ.get('LLM_TEMPERATURE', '0.6' if groq_oss else '0'))
            if not math.isfinite(self.temperature) or not 0 <= self.temperature <= 2:
                raise ValueError()
        except (ValueError,TypeError):
            raise LLMError('LLM_TEMPERATURE phải nằm trong khoảng 0 đến 2.') from None
        self.reasoning_effort = reasoning_effort or os.environ.get('LLM_REASONING_EFFORT') or ('low' if groq_oss else None)
        if self.reasoning_effort not in {None,'low','medium','high'}:
            raise LLMError('LLM_REASONING_EFFORT phải là low, medium hoặc high.')
        configured_budget = (max_completion_tokens if max_completion_tokens is not None
                             else os.environ.get('LLM_MAX_COMPLETION_TOKENS'))
        if configured_budget is None and addr.hostname == 'api.groq.com' and self.model in {
            'openai/gpt-oss-20b', 'openai/gpt-oss-120b'
        }:
            configured_budget = 2560
        try:
            self.max_completion_tokens = int(configured_budget) if configured_budget is not None else None
            if self.max_completion_tokens is not None and self.max_completion_tokens < 1:
                raise ValueError()
        except (ValueError, TypeError):
            raise LLMError('LLM_MAX_COMPLETION_TOKENS phải là số nguyên dương.') from None

    def completion_typed(self, system: str, user: str, response_model, *, max_completion_tokens=None) -> dict:
        from urllib.parse import urlparse
        supported = (urlparse(self.base_url).hostname == 'api.groq.com'
                     and self.model in {'openai/gpt-oss-20b', 'openai/gpt-oss-120b'})
        use_strict = self.json_mode and (self.structured_mode == 'strict' or
                                        (self.structured_mode == 'auto' and supported))
        if use_strict:
            return self.completion_json(system, user, max_completion_tokens=max_completion_tokens, response_schema={
                'name': response_model.__name__, 'strict': True,
                'schema': strict_schema(response_model.model_json_schema()),
            })
        return self.completion_json(system, user, max_completion_tokens=max_completion_tokens)

    def completion_json(self, system: str, user: str, *, response_schema=None, max_completion_tokens=None) -> dict:
        endpoint = self.base_url
        if not endpoint.endswith('/chat/completions'):
            endpoint += '/chat/completions'
        payload = {
            'model': self.model,
            'temperature': self.temperature,
            'messages': [{'role': 'system', 'content': system},
                         {'role': 'user', 'content': user}],
        }
        budget = max_completion_tokens if max_completion_tokens is not None else self.max_completion_tokens
        if budget is not None:
            payload['max_completion_tokens'] = budget
        if self.reasoning_effort is not None:
            payload['reasoning_effort'] = self.reasoning_effort
        if response_schema is not None:
            payload['response_format'] = {'type': 'json_schema', 'json_schema': response_schema}
        elif self.json_mode:
            payload['response_format'] = {'type': 'json_object'}
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json',
                     'Accept': 'application/json', 'User-Agent': 'MeetingIntelligence/0.1'},
            method='POST',
        )
        for attempt in range(self.max_retries + 1):
            try:
                remaining = self.min_call_interval - (time.monotonic() - self.last_call_at)
                if remaining > 0:
                    time.sleep(remaining)
                self.last_call_at = time.monotonic()
                self.call_count += 1
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    # Avoid unlimited memory use for malformed provider responses.
                    body = response.read(8_000_001)
                if len(body) > 8_000_000:
                    raise LLMError('LLM phản hồi quá lớn')
                data = json.loads(body)
                usage = data.get('usage') if isinstance(data, dict) else None
                if isinstance(usage, dict):
                    for k in ['prompt_tokens', 'completion_tokens', 'total_tokens']:
                        if isinstance(usage.get(k), int):
                            self.token_usage[k] = self.token_usage.get(k, 0) + usage[k]
                choice = data['choices'][0]
                if choice.get('finish_reason') not in {None, 'stop'}:
                    reason = choice.get('finish_reason')
                    safe_reason = reason if reason in {'length','content_filter','tool_calls','function_call'} else 'unknown'
                    raise LLMError('LLM chưa hoàn tất phản hồi hoặc bị chặn; không dùng kết quả thiếu '
                                   f'(finish_reason={safe_reason})', diagnostics={'finish_reason':safe_reason})
                content = choice['message']['content']
                if not isinstance(content, str):
                    raise ValueError('LLM content is not text')
                decoded = json.loads(content)
                if not isinstance(decoded, dict):
                    raise ValueError('LLM response must be a JSON object')
                return decoded
            except urllib.error.HTTPError as exc:
                if exc.code in {429, 500, 502, 503, 504} and attempt < self.max_retries:
                    wait = min(2 ** attempt, 2)
                    retry_header = exc.headers.get('Retry-After') if exc.headers else None
                    if retry_header:
                        try:
                            retry_seconds = float(retry_header)
                            if math.isfinite(retry_seconds) and retry_seconds >= 0:
                                wait = max(wait, retry_seconds)
                        except ValueError:
                            pass
                    if wait > self.max_retry_wait:
                        raise LLMError(f'API HTTP {exc.code}; cần chờ {wait:g} giây trước khi thử lại') from exc
                    time.sleep(wait)
                    continue
                # Never expose provider messages/failed_generation: they can echo
                # credentials or meeting content. Only allow known error codes.
                code = None
                diagnostics = {}
                try:
                    error = json.loads(exc.read(64000)).get('error', {})
                    candidate = error.get('code')
                    if candidate in {'json_validate_failed', 'rate_limit_exceeded',
                                     'context_length_exceeded', 'invalid_api_key',
                                     'model_not_found', 'insufficient_quota'}:
                        code = candidate
                    if code == 'rate_limit_exceeded':
                        message = error.get('message', '')
                        if isinstance(message,str):
                            unit = re.search(r'\b(TPM|TPD|RPM|RPD)\b',message)
                            if unit: diagnostics['rate_limit_unit'] = unit.group(1)
                            for label in ('Limit','Used','Requested'):
                                match = re.search(r'\b'+label+r'[: ]+([\d,]+)',message)
                                if match: diagnostics[label.lower()] = int(match.group(1).replace(',',''))
                except (ValueError, AttributeError, TypeError):
                    pass
                detail = f' ({code})' if code else ''
                if diagnostics:
                    detail += ' '+json.dumps(diagnostics,ensure_ascii=False)
                raise LLMError(f'API HTTP {exc.code}{detail}; kiểm tra giới hạn, model và chế độ đầu ra',
                               status_code=exc.code, provider_code=code, diagnostics=diagnostics) from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < self.max_retries:
                    time.sleep(min(2 ** attempt, 2))
                    continue
                raise LLMError('Không thể kết nối API hoặc hết thời gian chờ') from exc
            except (ValueError, TypeError, IndexError, KeyError, AttributeError) as exc:
                raise LLMError('API không trả về JSON object hợp lệ theo hợp đồng') from exc
        raise LLMError('Không thể hoàn thành gọi API')
