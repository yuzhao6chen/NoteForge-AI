from pathlib import Path
from datetime import datetime
import re


class MarkdownExporterTool:
    def __init__(self, export_dir: str = "storage/exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export(self, title: str, content: str) -> str:
        safe_title = re.sub(r'[\/:*?"<>|]+', "_", title).strip()
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{date}_{safe_title[:40]}.md"
        path = self.export_dir / filename
        path.write_text(content, encoding="utf-8")
        return str(path)
