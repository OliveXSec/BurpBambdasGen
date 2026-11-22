"""Tests for type detection and prompt building."""

from src.config.prompts import RetrievedContext, build_generation_prompt, detect_bambda_type


def test_detects_a_filter_request():
    assert detect_bambda_type("filtrar requests con JWT") == "VIEW_FILTER"


def test_detects_a_passive_scan_request():
    assert detect_bambda_type("passive scan for a missing CSP header") == "SCAN_CHECK_PASSIVE"


def test_returns_none_when_nothing_matches():
    assert detect_bambda_type("zzz qqq") is None


def test_prompt_includes_the_request_and_the_examples():
    context = RetrievedContext(
        examples=[{"name": "Ex1", "bambda_type": "VIEW_FILTER", "location": "PROXY_HTTP_HISTORY",
                   "description": "d", "source": "return true;"}],
        documentation=[{"section": "s", "content": "doc body"}],
    )
    prompt = build_generation_prompt("show 403s", "VIEW_FILTER", context)
    assert "show 403s" in prompt
    assert "Ex1" in prompt
    assert "doc body" in prompt
    assert "Return type: boolean" in prompt


def test_prompt_is_still_usable_with_no_retrieved_context():
    prompt = build_generation_prompt("show 403s", None, RetrievedContext(examples=[], documentation=[]))
    assert "No examples retrieved." in prompt
    assert "No specific documentation retrieved." in prompt
