"""Helpers that build a throwaway catalog project tree for validator tests.

Each test gets a temp dir containing the real agent.schema.json and
catalog.schema.json (copied from the repo), plus whatever skills, agents and
catalog.json the test writes. This keeps the tests hermetic — they never touch
the repo's own catalog.json or skills.
"""

import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# A minimal, safe SVG well under the 5 KB cap.
SAFE_SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
    b'<path d="M12 2 L22 22 L2 22 Z" fill="#6b4fbb"/></svg>'
)


class CatalogBuilder:
    """Builds a catalog project under ``root`` for a single test."""

    def __init__(self, root: Path) -> None:
        self.root = root
        (root / "skills").mkdir(parents=True, exist_ok=True)
        (root / "agents").mkdir(parents=True, exist_ok=True)
        for schema in ("agent.schema.json", "catalog.schema.json"):
            shutil.copy(REPO_ROOT / schema, root / schema)
        self._categories: dict[str, list[dict]] = {}

    # -- skills ---------------------------------------------------------------
    def add_skill(
        self,
        path: str,
        *,
        frontmatter_name: str | None = None,
        in_catalog: bool = True,
    ) -> "CatalogBuilder":
        """Create skills/<path>/SKILL.md; optionally register it in catalog."""
        category, name = path.split("/", 1)
        skill_dir = self.root / "skills" / category / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        fm_name = frontmatter_name if frontmatter_name is not None else name
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {fm_name}\ndescription: test skill\n"
            f'checksum: "sha256:{"0" * 64}"\n---\n\n# {name}\n',
            encoding="utf-8",
        )
        if in_catalog:
            self._categories.setdefault(category, []).append(
                {
                    "path": f"skills/{category}/{name}",
                    "type": "skill",
                    "checksum": "sha256:" + "0" * 64,
                }
            )
        return self

    # -- agents ---------------------------------------------------------------
    def add_agent(
        self,
        path: str,
        agent: dict,
        *,
        icon_bytes: bytes | None = None,
        in_catalog: bool = True,
        on_disk: bool = True,
    ) -> "CatalogBuilder":
        """Write agents/<path>/agent.json (+ optional icon); register in catalog."""
        category, name = path.split("/", 1)
        if on_disk:
            agent_dir = self.root / "agents" / category / name
            agent_dir.mkdir(parents=True, exist_ok=True)
            (agent_dir / "agent.json").write_text(
                json.dumps(agent, indent=2), encoding="utf-8"
            )
            if icon_bytes is not None:
                (agent_dir / "assets").mkdir(exist_ok=True)
                (agent_dir / "assets" / "icon.svg").write_bytes(icon_bytes)
        if in_catalog:
            self._categories.setdefault(category, []).append(
                {
                    "path": f"agents/{category}/{name}",
                    "type": "agent",
                    "checksum": "sha256:" + "0" * 64,
                }
            )
        return self

    # -- finalize -------------------------------------------------------------
    def write_catalog(self) -> Path:
        catalog = {
            "skillsChecksum": "sha256:" + "0" * 64,
            "categories": [
                {"name": slug.title(), "assets": assets}
                for slug, assets in self._categories.items()
            ]
            or [{"name": "Empty", "assets": []}],
        }
        (self.root / "catalog.json").write_text(
            json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
        )
        return self.root


def valid_agent(**overrides: object) -> dict:
    """A schema-valid agent dict; override individual fields per test."""
    agent = {
        "schema_version": 1,
        "name": "Test Agent",
        "description": "A test agent.",
        "system_prompt": "You are a helpful test agent.",
        "welcome_message": "Hello!",
        "starter_prompts": ["Do a thing"],
        "capabilities": [],
        "skills": [],
        "author": "Amazon",
        "connectors": [],
        "spaces": [],
        "files": [],
    }
    agent.update(overrides)
    return agent
