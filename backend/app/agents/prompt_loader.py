from pathlib import Path


def load_prompt(filename: str) -> str:
    """
    从 app/prompts/ 目录读取 prompt 文件。
    例如：
    load_prompt("article_writer.md")
    """
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / filename

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")