import sys
from types import SimpleNamespace

import agent
import storage


def test_hint_generation_falls_back_between_models(monkeypatch):
    calls = []

    def fake_chat(model, messages):
        calls.append(model)
        if model == "primary":
            raise RuntimeError("model unavailable")
        return SimpleNamespace(
            message=SimpleNamespace(
                content=(
                    "Use a smaller step. Avoid revealing the answer directly. And check the tags."
                )
            )
        )

    monkeypatch.setenv("LUX_OLLAMA_MODEL", "primary")
    monkeypatch.setenv("LUX_OLLAMA_MODELS", "fallback")
    monkeypatch.setitem(sys.modules, "ollama", SimpleNamespace(chat=fake_chat))

    hint = agent.ask_hint_via_ollama(
        {
            "id": "1",
            "title": "Test",
            "description": "Desc",
            "category": "Linux",
            "difficulty": "easy",
            "tags": ["shell"],
        },
        state=storage.default_state(),
    )

    assert calls == ["primary", "fallback"]
    assert hint.startswith("Use a smaller step")
    assert "answer" in hint.lower()


def test_hint_generation_raises_when_all_models_fail(monkeypatch):
    def fake_chat(model, messages):
        raise RuntimeError(f"{model} down")

    monkeypatch.delenv("LUX_OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("LUX_OLLAMA_MODELS", raising=False)
    monkeypatch.setitem(sys.modules, "ollama", SimpleNamespace(chat=fake_chat))

    try:
        agent.ask_hint_via_ollama(
            {
                "id": "1",
                "title": "Test",
                "description": "Desc",
                "category": "Linux",
                "difficulty": "easy",
                "tags": [],
            },
            state=storage.default_state(),
        )
    except RuntimeError as exc:
        assert "Unable to generate a hint" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")
