import json
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


class ChatLLMClient:
    """Generate answers with a local LM Studio server or an OpenAI-compatible endpoint."""

    def __init__(self, provider=None, base_url=None, model=None, timeout=60):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "lmstudio")).lower()
        self.base_url = base_url or self._default_base_url()
        self.model = model or self._default_model()
        self.timeout = timeout

    def _default_base_url(self):
        if self.provider == "openai":
            return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        return os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")

    def _default_model(self):
        if self.provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        return os.getenv("LM_STUDIO_MODEL", "local-model")

    def generate(self, question, context, citations):
        system_prompt, user_prompt = self._build_rag_prompts(question, context, citations)
        return self.complete(system_prompt, user_prompt)

    def complete(self, system_prompt, user_prompt):
        if self.provider == "openai":
            return self._complete_openai(system_prompt, user_prompt)

        return self._complete_lmstudio(system_prompt, user_prompt)

    def _complete_lmstudio(self, system_prompt, user_prompt):
        payload = self._build_payload(system_prompt, user_prompt)
        request = Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))

        return body["choices"][0]["message"]["content"].strip()

    def _complete_openai(self, system_prompt, user_prompt):
        payload = self._build_payload(system_prompt, user_prompt)
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        request = Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        with urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))

        return body["choices"][0]["message"]["content"].strip()

    def _build_rag_prompts(self, question, context, citations):
        system_prompt = (
            "You are a precise document assistant. Answer only from the provided context. "
            "If the context is insufficient, say so clearly. Include inline citations like [1], [2]."
        )
        user_prompt = (
            f"Question: {question}\n\n"
            f"Context:\n{context}\n\n"
            f"Available citations:\n{citations}"
        )
        return system_prompt, user_prompt

    def _build_payload(self, system_prompt, user_prompt):
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }