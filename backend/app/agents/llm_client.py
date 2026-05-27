import json
import re
import requests
from typing import Any, Optional
from app.core.config import settings


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
            raise ValueError("LLM_PROVIDER 仅支持 openai。项目已移除本地 mock 降级逻辑，请在 backend/.env 中配置真实 OpenAI-compatible API。")
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY 为空。项目已移除本地 mock 降级逻辑，请配置真实 API key。")
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
            return self._safe_json_loads(repaired)

    def _openai_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool,
    ) -> str:
        url = settings.openai_base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            if json_mode and resp.status_code in {400, 422}:
                payload.pop("response_format", None)
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                resp.raise_for_status()
            else:
                raise
        data = resp.json()
        return data["choices"][0]["message"]["content"]

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
