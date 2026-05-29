import json
import re
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Optional

import requests
from requests import Response

from app.core.config import settings
from app.core.errors import LLMClientError


_model_override: ContextVar[str] = ContextVar("llm_model_override", default="")


DEEPSEEK_MODEL_OPTIONS = [
    {
        "id": "deepseek-v4-flash",
        "label": "DeepSeek V4 Flash",
        "description": "速度更快，适合草稿生成、标题候选和轻量检查。",
        "provider": "deepseek",
        "deprecated": False,
    },
    {
        "id": "deepseek-v4-pro",
        "label": "DeepSeek V4 Pro",
        "description": "质量更高，适合文章体检、事实风险审查和深度打磨。",
        "provider": "deepseek",
        "deprecated": False,
    },
]


@contextmanager
def use_llm_model(model: Optional[str]):
    token = _model_override.set((model or "").strip())
    try:
        yield
    finally:
        _model_override.reset(token)


def get_llm_model_options() -> dict:
    options = _model_options()
    default_model = settings.openai_model.strip()

    return {
        "provider": settings.llm_provider,
        "base_url": _display_base_url(),
        "default_model": default_model,
        "models": [
            {
                **option,
                "is_default": option["id"] == default_model,
            }
            for option in options
        ],
    }


class LLMClient:
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> str:
        provider = settings.llm_provider.lower().strip()
        if provider != "openai":
            raise LLMClientError(
                "LLM_PROVIDER 目前只支持 openai。",
                status_code=400,
                code="invalid_llm_provider",
                hint="这里的 openai 表示 OpenAI-compatible Chat Completions API，例如 OpenAI、DeepSeek 或 Qwen。",
            )
        if not settings.openai_api_key.strip():
            raise LLMClientError(
                "OPENAI_API_KEY 为空，无法调用模型服务。",
                status_code=400,
                code="missing_openai_api_key",
                hint="请在 backend/.env 中配置真实 API key，然后重启后端服务。",
            )
        if not self._model_name():
            raise LLMClientError(
                "OPENAI_MODEL 为空，无法调用模型服务。",
                status_code=400,
                code="missing_openai_model",
                hint="请在 backend/.env 中填写模型名，例如 gpt-4o-mini、deepseek-chat 或服务商后台提供的模型名。",
            )

        return self._openai_chat(system_prompt, user_prompt, temperature, json_mode)

    def generate_json(self, system_prompt: str, user_prompt: str) -> Any:
        text = self.generate(system_prompt, user_prompt, temperature=0.2, json_mode=True)
        try:
            return self._safe_json_loads(text)
        except ValueError:
            repaired = self.generate(
                "你是 JSON 修复器。只输出合法 JSON，不要解释。",
                f"请把下面内容修复为合法 JSON，保持原字段含义：\n\n{text}",
                temperature=0,
                json_mode=True,
            )
            try:
                return self._safe_json_loads(repaired)
            except ValueError as exc:
                raise LLMClientError(
                    "模型返回的 JSON 无法解析。",
                    code="llm_invalid_json",
                    hint="可以重试一次；如果持续出现，请换一个更稳定支持 JSON 输出的模型。",
                    detail={"sample": repaired[:500]},
                ) from exc

    def _openai_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool,
    ) -> str:
        url = self._chat_url()
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model_name(),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = self._post_chat(url, headers, payload)
        except LLMClientError as exc:
            if not json_mode or exc.code not in {"llm_ssl_error", "llm_connection_error"}:
                raise
            payload.pop("response_format", None)
            resp = self._post_chat(url, headers, payload)

        if json_mode and resp.status_code in {400, 422}:
            payload.pop("response_format", None)
            resp = self._post_chat(url, headers, payload)

        self._raise_for_bad_response(resp)
        data = self._response_json(resp)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError(
                "模型服务返回格式不符合 Chat Completions 规范。",
                code="llm_bad_response_shape",
                hint="请检查 OPENAI_BASE_URL 是否指向 OpenAI-compatible Chat Completions 服务。",
                detail={"body": data},
            ) from exc

    def _chat_url(self) -> str:
        base_url = settings.openai_base_url.strip().rstrip("/")
        if not base_url:
            raise LLMClientError(
                "OPENAI_BASE_URL 为空，无法调用模型服务。",
                status_code=400,
                code="missing_openai_base_url",
                hint="请在 backend/.env 中填写服务商 base URL，例如 https://api.openai.com/v1 或 https://api.deepseek.com。",
            )
        if base_url.lower().endswith("/chat/completions"):
            raise LLMClientError(
                "OPENAI_BASE_URL 不要包含 /chat/completions。",
                status_code=400,
                code="invalid_openai_base_url",
                hint="请只填写 base URL，例如 https://api.deepseek.com；代码会自动拼接 /chat/completions。",
            )
        return f"{base_url}/chat/completions"

    def _model_name(self) -> str:
        return self._resolve_model_name(_model_override.get())

    def _resolve_model_name(self, requested_model: str = "") -> str:
        model = (requested_model or settings.openai_model).strip()
        if not model:
            return ""

        allowed_models = {option["id"] for option in _model_options()}
        if requested_model and allowed_models and model not in allowed_models:
            raise LLMClientError(
                f"当前后端未配置可选模型：{model}",
                status_code=400,
                code="invalid_llm_model",
                hint=(
                    "请在 backend/.env 的 LLM_MODEL_OPTIONS 中加入该模型，"
                    "或在前端选择后端返回的模型选项。DeepSeek 常用模型是 "
                    "deepseek-v4-flash 和 deepseek-v4-pro。"
                ),
                detail={
                    "requested_model": model,
                    "allowed_models": sorted(allowed_models),
                    "default_model": settings.openai_model,
                },
            )

        return model

    def _post_chat(self, url: str, headers: dict, payload: dict) -> Response:
        try:
            return requests.post(url, headers=headers, json=payload, timeout=settings.llm_request_timeout)
        except requests.exceptions.SSLError as exc:
            raise LLMClientError(
                "无法和模型服务建立稳定的 HTTPS 连接。",
                code="llm_ssl_error",
                hint="TCP 443 能通只代表端口可达；SSL 错误通常和代理/VPN、防火墙、证书包或服务商网关有关。请检查代理设置，或稍后重试。",
                detail={"base_url": settings.openai_base_url, "model": self._model_name()},
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise LLMClientError(
                "模型服务请求超时。",
                code="llm_timeout",
                hint=(
                    f"当前单次模型请求超时时间为 {settings.llm_request_timeout} 秒。"
                    "可以稍后重试，或换用响应更快的模型；长文本生成时也可以降低输入长度。"
                ),
                detail={
                    "base_url": settings.openai_base_url,
                    "model": self._model_name(),
                    "timeout_seconds": settings.llm_request_timeout,
                },
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise LLMClientError(
                "无法连接到模型服务。",
                code="llm_connection_error",
                hint="请检查网络、代理/VPN、防火墙，以及 OPENAI_BASE_URL 是否能被当前后端进程访问。",
                detail={"base_url": settings.openai_base_url, "model": self._model_name()},
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise LLMClientError(
                "模型服务请求失败。",
                code="llm_request_error",
                hint="请检查服务商地址、网络环境和本机代理配置。",
                detail={"base_url": settings.openai_base_url, "model": self._model_name()},
            ) from exc

    def _raise_for_bad_response(self, resp: Response) -> None:
        if resp.status_code < 400:
            return

        provider_message = self._extract_api_error(resp)
        detail = {
            "status_code": resp.status_code,
            "provider_message": provider_message,
            "base_url": settings.openai_base_url,
            "model": self._model_name(),
        }

        if resp.status_code in {401, 403}:
            raise LLMClientError(
                "模型服务鉴权失败。",
                status_code=resp.status_code,
                code="llm_auth_error",
                hint="请检查 OPENAI_API_KEY 是否正确、是否属于当前服务商，以及账号是否有模型调用权限。",
                detail=detail,
            )
        if resp.status_code == 404:
            raise LLMClientError(
                "模型接口地址或模型名不存在。",
                status_code=404,
                code="llm_not_found",
                hint="请检查 OPENAI_BASE_URL 和 OPENAI_MODEL。DeepSeek 常见 base URL 是 https://api.deepseek.com。",
                detail=detail,
            )
        if resp.status_code == 429:
            raise LLMClientError(
                "模型服务限流、额度不足或并发过高。",
                status_code=429,
                code="llm_rate_limited",
                hint="请稍后重试，或检查服务商后台的额度、余额和并发限制。",
                detail=detail,
            )
        if resp.status_code in {400, 422}:
            raise LLMClientError(
                "模型服务拒绝了当前请求参数。",
                status_code=400,
                code="llm_bad_request",
                hint="请检查 OPENAI_MODEL 是否存在、base URL 是否正确，以及当前模型是否支持 Chat Completions。",
                detail=detail,
            )
        if resp.status_code >= 500:
            raise LLMClientError(
                "模型服务暂时不可用。",
                status_code=502,
                code="llm_provider_error",
                hint="这是服务商侧错误或网关异常，可以稍后重试或临时切换模型服务。",
                detail=detail,
            )

        raise LLMClientError(
            "模型服务返回错误。",
            status_code=502,
            code="llm_http_error",
            hint="请查看 error_detail 中的服务商返回信息。",
            detail=detail,
        )

    def _response_json(self, resp: Response) -> Any:
        try:
            return resp.json()
        except ValueError as exc:
            raise LLMClientError(
                "模型服务返回了非 JSON 响应。",
                code="llm_non_json_response",
                hint="请检查 OPENAI_BASE_URL 是否指向 API 服务，而不是网页或代理错误页。",
                detail={"status_code": resp.status_code, "body": resp.text[:500]},
            ) from exc

    def _extract_api_error(self, resp: Response) -> str:
        try:
            data = resp.json()
        except ValueError:
            return resp.text[:500]

        error = data.get("error") if isinstance(data, dict) else None
        if isinstance(error, dict):
            return str(error.get("message") or error)
        if isinstance(error, str):
            return error
        if isinstance(data, dict):
            return str(data.get("message") or data.get("detail") or data)
        return str(data)

    def _safe_json_loads(self, text: str) -> Any:
        cleaned = self._strip_json_fences(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            candidate = self._extract_json_candidate(cleaned)
            if candidate:
                return json.loads(candidate)
            raise ValueError(f"LLM did not return valid JSON: {cleaned[:300]}")

    def _strip_json_fences(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def _extract_json_candidate(self, text: str) -> Optional[str]:
        decoder = json.JSONDecoder()
        starts = [idx for idx in (text.find("{"), text.find("[")) if idx >= 0]
        for start in sorted(starts):
            try:
                _, end = decoder.raw_decode(text[start:])
                return text[start:start + end]
            except json.JSONDecodeError:
                continue
        return None


def _model_options() -> list[dict]:
    configured = _parse_configured_model_options(settings.llm_model_options)
    if configured:
        return _ensure_default_model(configured)

    if _is_deepseek_base_url(settings.openai_base_url):
        return _ensure_default_model(DEEPSEEK_MODEL_OPTIONS)

    default_model = settings.openai_model.strip()
    if not default_model:
        return []

    return [
        {
            "id": default_model,
            "label": default_model,
            "description": "backend/.env 当前默认模型。",
            "provider": settings.llm_provider,
            "deprecated": False,
        }
    ]


def _parse_configured_model_options(raw: str) -> list[dict]:
    items = []
    seen = set()
    for chunk in (raw or "").split(","):
        parts = [part.strip() for part in chunk.split("|")]
        model_id = parts[0] if parts else ""
        if not model_id or model_id in seen:
            continue
        seen.add(model_id)
        items.append({
            "id": model_id,
            "label": parts[1] if len(parts) > 1 and parts[1] else model_id,
            "description": parts[2] if len(parts) > 2 and parts[2] else "自定义模型。",
            "provider": _provider_name_for_model(model_id),
            "deprecated": model_id in {"deepseek-chat", "deepseek-reasoner"},
        })
    return items


def _ensure_default_model(options: list[dict]) -> list[dict]:
    default_model = settings.openai_model.strip()
    if not default_model:
        return options
    if any(option["id"] == default_model for option in options):
        return options
    return [
        {
            "id": default_model,
            "label": default_model,
            "description": "backend/.env 当前默认模型。",
            "provider": _provider_name_for_model(default_model),
            "deprecated": default_model in {"deepseek-chat", "deepseek-reasoner"},
        },
        *options,
    ]


def _is_deepseek_base_url(base_url: str) -> bool:
    return "api.deepseek.com" in (base_url or "").lower()


def _provider_name_for_model(model_id: str) -> str:
    if model_id.startswith("deepseek-"):
        return "deepseek"
    return settings.llm_provider


def _display_base_url() -> str:
    base_url = settings.openai_base_url.strip()
    if not base_url:
        return ""
    return re.sub(r"(?<=//)[^/@]+@", "", base_url)
