from pathlib import Path
from typing import List, Set
from .model import TagFile
import json
import re
import sys

def load_tags_from_file(path: Path) -> List[str]:
    tags: List[str] = []
    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        text = re.sub(r'\\\n[ \t]*', '', text)
        tags = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    except Exception as e:
        print(f"failed to load file!: {path} ({e})")
    return tags

def load_template(template_path: Path):
    try:
        with template_path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"failed to load template file {template_path}: {e}")
        return {}

def scan_dir(directory, known_categories) -> List[TagFile]:
    files: List[TagFile] = []
    for p in directory.rglob("*.txt"):
        tags = load_tags_from_file(p)
        if tags:
            cat = decide_category(p, known_categories)
            rate = decide_rating(p.stem)
            files.append(TagFile(p, cat, rate, tags))
    return files

def decide_category(path: Path, known_categories: Set[str]) -> str:
    for ancestor in path.parents:
        if ancestor.name in known_categories:
            return ancestor.name
    return "none"

def decide_rating(file_stem: str) -> str:
    s = file_stem.lower()
    if s.endswith("_r"):
        return "r"
    elif s.endswith("_p"):
        return "p"
    else:
        return "g"

def discover_categories(directory: Path) -> Set[str]:
    if not directory.exists():
        return {"none"}
    categories = {d.name for d in directory.iterdir() if d.is_dir()}
    if not categories:
        categories = {"none"}
    return categories
