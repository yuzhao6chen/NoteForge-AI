def strip_model_preamble(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped

    preamble_starts = ("好的", "以下是", "根据你的", "根据您的", "收到")
    if not stripped.startswith(preamble_starts):
        return stripped

    heading_index = stripped.find("\n#")
    if heading_index >= 0:
        return stripped[heading_index + 1:].strip()

    paragraphs = stripped.split("\n\n", 1)
    if len(paragraphs) == 2:
        return paragraphs[1].strip()

    return stripped
