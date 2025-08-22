from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class TagFile:
    path: Path
    category: str
    rating: str
    tags: List[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.stem
