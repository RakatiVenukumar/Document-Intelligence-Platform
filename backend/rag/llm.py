import json
import os
import ssl
import re
from collections import Counter
from urllib.request import Request, urlopen

import certifi


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

        if self.provider == "groq":
            return os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

        return os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")

    def _default_model(self):
        if self.provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if self.provider == "groq":
            return os.getenv("GROQ_MODEL", "llama3-8b-8192")

        return os.getenv("LM_STUDIO_MODEL", "local-model")

    def generate(self, question, context, citations):
        system_prompt, user_prompt = self._build_rag_prompts(question, context, citations)
        return self.complete(system_prompt, user_prompt)

    def complete(self, system_prompt, user_prompt):
        if self.provider == "offline":
            return self._complete_offline(system_prompt, user_prompt)

        if self.provider == "openai":
            return self._complete_openai(system_prompt, user_prompt)

        if self.provider == "groq":
            return self._complete_groq(system_prompt, user_prompt)

        return self._complete_lmstudio(system_prompt, user_prompt)

    def _complete_lmstudio(self, system_prompt, user_prompt):
        payload = self._build_payload(system_prompt, user_prompt)
        request = Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self._open_request(request) as response:
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

        with self._open_request(request) as response:
            body = json.loads(response.read().decode("utf-8"))

        return body["choices"][0]["message"]["content"].strip()

    def _complete_groq(self, system_prompt, user_prompt):
        payload = self._build_payload(system_prompt, user_prompt)
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required when LLM_PROVIDER=groq")

        request = Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        with self._open_request(request) as response:
            body = json.loads(response.read().decode("utf-8"))

        return body["choices"][0]["message"]["content"].strip()

    def _complete_offline(self, system_prompt, user_prompt):
        question = self._extract_section(user_prompt, "Question:", "Context:")
        context = self._extract_section(user_prompt, "Context:", "Available citations:")
        citations = self._extract_section(user_prompt, "Available citations:", None)

        if not context.strip():
            return "I could not find enough indexed book context to answer this question."

        sentences = self._split_sentences(context)
        if not sentences:
            return f"Based on the available context, {context.strip()}"

        keywords = self._extract_keywords(question)
        ranked_sentences = sorted(
            sentences,
            key=lambda sentence: (self._sentence_score(sentence, keywords), len(sentence)),
            reverse=True,
        )
        best_sentences = [sentence for sentence in ranked_sentences[:3] if sentence.strip()]
        summary = " ".join(best_sentences) if best_sentences else context.strip()

        citation_ids = self._extract_citation_ids(citations)
        citation_suffix = f" Citations: {', '.join(citation_ids)}." if citation_ids else ""
        return f"Based on the indexed book context, {summary}{citation_suffix}"

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

    def _open_request(self, request):
        context = self._ssl_context()
        return urlopen(request, timeout=self.timeout, context=context)

    def _ssl_context(self):
        # Emergency local override only. Keep disabled in normal usage.
        if os.getenv("LLM_SKIP_TLS_VERIFY", "false").lower() == "true":
            return ssl._create_unverified_context()

        ca_bundle = os.getenv("LLM_CA_BUNDLE", "").strip()
        if ca_bundle:
            return ssl.create_default_context(cafile=ca_bundle)

        return ssl.create_default_context(cafile=certifi.where())

    def _extract_section(self, text, start_marker, end_marker):
        start_index = text.find(start_marker)
        if start_index == -1:
            return ""

        start_index += len(start_marker)
        if end_marker is None:
            return text[start_index:].strip()

        end_index = text.find(end_marker, start_index)
        if end_index == -1:
            return text[start_index:].strip()

        return text[start_index:end_index].strip()

    def _split_sentences(self, text):
        parts = re.split(r"(?<=[.!?])\s+|\n+", text)
        return [part.strip() for part in parts if part.strip()]

    def _extract_keywords(self, text):
        words = re.findall(r"[a-z0-9]+", text.lower())
        stop_words = {
            "a",
            "an",
            "and",
            "are",
            "about",
            "book",
            "do",
            "does",
            "for",
            "from",
            "how",
            "i",
            "in",
            "is",
            "it",
            "main",
            "of",
            "on",
            "question",
            "the",
            "this",
            "to",
            "what",
            "which",
            "with",
        }
        return [word for word in words if word not in stop_words]

    def _sentence_score(self, sentence, keywords):
        if not keywords:
            return len(sentence.split())

        sentence_words = re.findall(r"[a-z0-9]+", sentence.lower())
        counts = Counter(sentence_words)
        return sum(counts.get(keyword, 0) for keyword in keywords)

    def _extract_citation_ids(self, citations_text):
        return re.findall(r"\[(\d+)\]", citations_text or "")