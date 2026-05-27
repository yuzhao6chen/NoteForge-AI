from pathlib import Path
from datetime import datetime
import json
import re
import shutil
from typing import Optional
from app.core.config import settings


class LocalStorageTool:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = self._resolve_base_dir(base_dir)
        self.materials_dir = self.base_dir / "materials"
        self.articles_dir = self.base_dir / "articles"
        self.exports_dir = self.base_dir / "exports"
        self.agent_runs_dir = self.base_dir / "agent_runs"
        self.profile_dir = self.base_dir / "profile"
        self.style_profile_path = self.profile_dir / "style_profile.json"

        for d in [
            self.materials_dir,
            self.articles_dir,
            self.exports_dir,
            self.agent_runs_dir,
            self.profile_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def _resolve_base_dir(self, base_dir: Optional[str]) -> Path:
        configured = base_dir or settings.storage_dir
        path = Path(configured)
        if path.is_absolute():
            return path

        if base_dir is None and configured == "storage":
            return Path(__file__).resolve().parents[3] / "storage"

        return (Path.cwd() / path).resolve()

    def _now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _file_time(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def _safe_name(self, name: str) -> str:
        name = re.sub(r'[\\/:*?"<>|]+', "_", name)
        name = name.strip()
        return name[:60] or "untitled"

    def _frontmatter(self, metadata: dict) -> str:
        lines = ["---"]
        for key, value in metadata.items():
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            lines.append(f"{key}: {value}")
        lines.append("---")
        return "\n".join(lines)

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _resolve_existing_file(self, base_dir: Path, item_id: str, suffix: str) -> Path:
        path = (base_dir / f"{item_id}{suffix}").resolve()
        try:
            path.relative_to(base_dir.resolve())
        except ValueError as exc:
            raise FileNotFoundError(f"Invalid storage id: {item_id}") from exc
        if not path.exists():
            raise FileNotFoundError(f"Storage item not found: {item_id}")
        return path

    def save_material(
        self,
        title: str,
        content: str,
        source_type: str = "idea",
        source_name: str = "",
        tags: str = "",
        summary: str = "",
    ) -> dict:
        material_id = f"{self._file_time()}_{self._safe_name(title)}"
        md_path = self.materials_dir / f"{material_id}.md"
        meta_path = self.materials_dir / f"{material_id}.meta.json"

        metadata = {
            "id": material_id,
            "title": title,
            "source_type": source_type,
            "source_name": source_name,
            "tags": tags,
            "summary": summary,
            "created_at": self._now(),
        }

        md = self._frontmatter(metadata) + "\n\n" + content
        md_path.write_text(md, encoding="utf-8")
        meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "id": material_id,
            "path": str(md_path),
            "meta_path": str(meta_path),
        }

    def save_article(
        self,
        title: str,
        content: str,
        platform: str = "wechat",
        outline: str = "",
        status: str = "draft",
    ) -> dict:
        article_id = f"{self._file_time()}_{self._safe_name(title)}"
        md_path = self.articles_dir / f"{article_id}.md"
        meta_path = self.articles_dir / f"{article_id}.meta.json"

        metadata = {
            "id": article_id,
            "title": title,
            "platform": platform,
            "status": status,
            "created_at": self._now(),
        }

        md = self._frontmatter(metadata)

        if outline:
            md += "\n\n## 文章大纲\n\n"
            md += outline

        md += "\n\n## 正文\n\n"
        md += content

        md_path.write_text(md, encoding="utf-8")
        meta_path.write_text(
            json.dumps({**metadata, "outline": outline}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "id": article_id,
            "path": str(md_path),
            "meta_path": str(meta_path),
        }

    def save_agent_run(self, task_type: str, input_data: dict, output_data: dict) -> dict:
        run_id = f"{self._file_time()}_{self._safe_name(task_type)}"
        path = self.agent_runs_dir / f"{run_id}.json"

        data = {
            "id": run_id,
            "task_type": task_type,
            "created_at": self._now(),
            "input": input_data,
            "output": output_data,
        }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "id": run_id,
            "path": str(path),
        }

    def export_article(self, article_id: str) -> dict:
        source_path = self._resolve_existing_file(self.articles_dir, article_id, ".md")

        export_path = self.exports_dir / f"{article_id}.md"
        shutil.copyfile(source_path, export_path)

        return {
            "id": article_id,
            "path": str(export_path),
        }

    def export_article_content(
        self,
        article_id: str,
        title: str,
        content: str,
        platform: str = "wechat",
        outline: str = "",
        status: str = "edited",
    ) -> dict:
        export_id = f"{article_id}_edited_{self._file_time()}"
        export_path = self.exports_dir / f"{export_id}.md"

        metadata = {
            "id": export_id,
            "source_article_id": article_id,
            "title": title,
            "platform": platform,
            "status": status,
            "created_at": self._now(),
        }

        md = self._frontmatter(metadata)
        if outline:
            md += "\n\n## 文章大纲\n\n"
            md += outline
        md += "\n\n## 正文\n\n"
        md += content

        export_path.write_text(md, encoding="utf-8")

        return {
            "id": export_id,
            "path": str(export_path),
        }

    def read_style_profile(self) -> dict:
        data = self._read_json(self.style_profile_path)
        if data:
            return {
                "profile": data.get("profile", {}),
                "updated_at": data.get("updated_at", ""),
                "sample_count": data.get("sample_count", 0),
                "last_source": data.get("last_source", {}),
                "path": str(self.style_profile_path),
            }

        return {
            "profile": {},
            "updated_at": "",
            "sample_count": 0,
            "last_source": {},
            "path": str(self.style_profile_path),
        }

    def save_style_profile(self, profile: dict, last_source: Optional[dict] = None) -> dict:
        current = self.read_style_profile()
        data = {
            "profile": profile,
            "updated_at": self._now(),
            "sample_count": int(current.get("sample_count", 0)) + 1,
            "last_source": last_source or {},
        }

        self.style_profile_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            **data,
            "path": str(self.style_profile_path),
        }

    def reset_style_profile(self) -> dict:
        if self.style_profile_path.exists():
            self.style_profile_path.unlink()
        return self.read_style_profile()

    def list_articles(self) -> list[dict]:
        items = []
        for path in sorted(self.articles_dir.glob("*.md"), reverse=True):
            metadata = self._read_json(path.with_suffix(".meta.json"))
            items.append({
                "id": path.stem,
                "title": metadata.get("title", path.stem),
                "created_at": metadata.get("created_at", ""),
                "path": str(path),
            })
        return items

    def list_materials(self) -> list[dict]:
        items = []
        for path in sorted(self.materials_dir.glob("*.md"), reverse=True):
            metadata = self._read_json(path.with_suffix(".meta.json"))
            items.append({
                "id": path.stem,
                "title": metadata.get("title", path.stem),
                "created_at": metadata.get("created_at", ""),
                "path": str(path),
            })
        return items

    def read_article(self, article_id: str) -> dict:
        path = self._resolve_existing_file(self.articles_dir, article_id, ".md")
        metadata = self._read_json(path.with_suffix(".meta.json"))
        return {
            "id": article_id,
            "title": metadata.get("title", article_id),
            "content": path.read_text(encoding="utf-8"),
            "path": str(path),
            "metadata": metadata,
        }

    def read_material(self, material_id: str) -> dict:
        path = self._resolve_existing_file(self.materials_dir, material_id, ".md")
        metadata = self._read_json(path.with_suffix(".meta.json"))
        return {
            "id": material_id,
            "title": metadata.get("title", material_id),
            "content": path.read_text(encoding="utf-8"),
            "path": str(path),
            "metadata": metadata,
        }
