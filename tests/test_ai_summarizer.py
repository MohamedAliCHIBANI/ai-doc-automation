from unittest.mock import MagicMock, patch


def _mock_openai(content: str) -> MagicMock:
    mock = MagicMock()
    mock.chat.completions.create.return_value.choices[0].message.content = content
    return mock


def test_summarize_returns_parsed_dict():
    payload = (
        '{"Summary":"A doc.","Key Points":["p1","p2"],'
        '"Document Type":"Report","Sentiment":"neutral","Word Count":100}'
    )
    with patch("app.services.ai_summarizer.client", _mock_openai(payload)):
        from app.services.ai_summarizer import summarize
        result = summarize("some text", "PDF")

    assert result["Summary"] == "A doc."
    assert result["Sentiment"] == "neutral"
    assert len(result["Key Points"]) == 2


def test_summarize_strips_markdown_code_fences():
    # The model sometimes wraps the response in ```json ... ```
    payload = (
        "```json\n"
        '{"Summary":"s","Key Points":[],"Document Type":"TXT","Sentiment":"positive","Word Count":3}'
        "\n```"
    )
    with patch("app.services.ai_summarizer.client", _mock_openai(payload)):
        from app.services.ai_summarizer import summarize
        result = summarize("hi", "TXT")

    assert result["Sentiment"] == "positive"
