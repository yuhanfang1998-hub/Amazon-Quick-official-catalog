"""Validate official agent definitions for the Amazon Quick Official Catalog.

Checks every ``agents/{category}/{name}/agent.json`` and its relationship to
``catalog.json`` and the ``skills/`` tree. Run in CI before publish:

    uv run python -m scripts.agents_validate            # validate
    uv run python -m scripts.agents_validate --quiet     # errors only

Rules (ERROR unless noted):

  schema      agent.json conforms to agent.schema.json (field presence,
              limits, schema_version == 1, connectors/spaces/files empty).
  catalog     every agents/ dir on disk has a matching ``type: agent`` asset
              in catalog.json, and every agent asset in catalog.json resolves
              to a dir with an agent.json (both directions).
  no-ids      no field in agent.json contains an ARN or a UUID.
  skills      each entry in ``skills`` resolves to skills/<path>/SKILL.md on
              disk AND to a ``type: skill`` ``path`` in catalog.json; the
              skill's directory name equals its SKILL.md frontmatter ``name``.
              A removed or moved skill therefore fails here.
  icon        if ``icon`` is set, the file exists inside the agent folder, is
              <= 5 KB, and passes the same SVG-safety rules as skill icons
              (no script/animation/remote references).
  web-search  WARNING (not error) when system_prompt reads like it needs web
              search but ``WEB_SEARCH`` is not in ``capabilities``.

The SVG-safety check mirrors the app's icon_image.is_safe_svg so a catalog
icon that CI accepts is the same icon the app will render.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import click
import yaml
from jsonschema import Draft7Validator
from loguru import logger

try:  # Prefer the hardened parser the app uses; fall back to stdlib + DTD guard.
    from defusedxml import ElementTree as _SafeET

    def _parse_xml(data: bytes) -> ET.Element:
        return _SafeET.fromstring(data, forbid_dtd=True)
except ImportError:  # pragma: no cover - defusedxml is a locked dependency

    def _parse_xml(data: bytes) -> ET.Element:
        if _SVG_DOCTYPE_RE.search(data):
            raise ValueError("DTD not allowed")
        return ET.fromstring(data)


CATALOG_FILE = "catalog.json"
CATALOG_SCHEMA_FILE = "catalog.schema.json"
AGENT_SCHEMA_FILE = "agent.schema.json"
AGENTS_DIR = "agents"
SKILLS_DIR = "skills"
AGENT_FILE = "agent.json"
SKILL_FILE = "SKILL.md"
AGENT_ASSET_TYPE = "agent"
SKILL_ASSET_TYPE = "skill"
WEB_SEARCH_CAPABILITY = "WEB_SEARCH"
MAX_ICON_BYTES = 5 * 1024

# An ARN or a UUID anywhere in agent.json means an environment-specific id
# leaked into a portable, catalog-shipped file. Both are rejected.
ARN_RE = re.compile(r"arn:[a-z0-9][a-z0-9-]*:[a-z0-9-]*:", re.IGNORECASE)
UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
# A prompt that reads like it needs the web but has no WEB_SEARCH capability.
WEB_SEARCH_PHRASE_RE = re.compile(
    r"web[\s-]*search|search\s+the\s+(web|internet)|browse\s+the\s+web|"
    r"search\s+online|search\s+the\s+net",
    re.IGNORECASE,
)

# --- SVG safety, mirrored from the app's icon_image.py -----------------------
_SVG_FORBIDDEN_TAGS = {
    "script", "foreignobject", "iframe", "object", "embed",
    "animate", "animatetransform", "animatemotion", "set", "handler", "listener",
}  # fmt: skip
_SVG_EVENT_ATTR_RE = re.compile(r"^on[a-z]+$", re.IGNORECASE)
_SVG_CSS_REMOTE_RE = re.compile(
    r"@import|javascript:|expression\s*\(|image-set\s*\(|\\", re.IGNORECASE
)
_SVG_PI_RE = re.compile(rb"<\?(?!xml[\s?])", re.IGNORECASE)
_SVG_DOCTYPE_RE = re.compile(rb"<!DOCTYPE|<!ENTITY", re.IGNORECASE)
_SVG_URL_RE = re.compile(r"url\s*\(\s*['\"]?\s*([^'\")\s]*)", re.IGNORECASE)


def _has_remote_css(value: str) -> bool:
    if _SVG_CSS_REMOTE_RE.search(value):
        return True
    return any(not target.startswith("#") for target in _SVG_URL_RE.findall(value))


def _local_name(tag: str) -> str:
    """Strip an XML namespace: ``{http://www.w3.org/2000/svg}svg`` -> ``svg``."""
    return tag.rsplit("}", 1)[-1].lower()


def is_safe_svg(data: bytes) -> bool:
    """True if ``data`` is an SVG with no script, remote references or animation."""
    if _SVG_PI_RE.search(data):
        return False
    try:
        root = _parse_xml(data)
    except (ET.ParseError, ValueError):
        return False
    if _local_name(root.tag) != "svg":
        return False
    for el in root.iter():
        if _local_name(el.tag) in _SVG_FORBIDDEN_TAGS:
            return False
        if (el.text and _has_remote_css(el.text)) or (
            el.tail and _has_remote_css(el.tail)
        ):
            return False
        for attr, val in el.attrib.items():
            name = _local_name(attr)
            if _SVG_EVENT_ATTR_RE.match(name):
                return False
            if _has_remote_css(val):
                return False
            if name == "href":
                v = val.strip().lower()
                if not (v.startswith("#") or v.startswith("data:image/")):
                    return False
    return True


# --- Findings ----------------------------------------------------------------
class Severity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True)
class Finding:
    """One validation result, scoped to an agent path."""

    severity: Severity
    where: str
    message: str

    def render(self) -> str:
        return f"[{self.severity}] {self.where}: {self.message}"


class AgentValidator:
    """Validates all official agents in a catalog project directory."""

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self.agents_dir = project_dir / AGENTS_DIR
        self.skills_dir = project_dir / SKILLS_DIR
        self.catalog_file = project_dir / CATALOG_FILE
        self._agent_schema = self._load_json(project_dir / AGENT_SCHEMA_FILE)
        self._catalog_schema = self._load_json(project_dir / CATALOG_SCHEMA_FILE)
        self._agent_validator = Draft7Validator(self._agent_schema)

    # -- public ---------------------------------------------------------------
    def validate(self) -> list[Finding]:
        findings: list[Finding] = []
        catalog = self._load_json(self.catalog_file)

        findings.extend(self._validate_catalog_schema(catalog))
        catalog_agent_paths = {
            a["path"] for a in self._assets(catalog, AGENT_ASSET_TYPE)
        }
        skill_paths = {a["path"] for a in self._assets(catalog, SKILL_ASSET_TYPE)}
        disk_agent_paths = {self._rel(d): d for d in self._iter_agent_dirs()}

        findings.extend(
            self._validate_catalog_disk_parity(catalog_agent_paths, disk_agent_paths)
        )

        for path, agent_dir in sorted(disk_agent_paths.items()):
            findings.extend(self._validate_agent(path, agent_dir, skill_paths))

        return findings

    # -- catalog <-> disk -----------------------------------------------------
    def _validate_catalog_schema(self, catalog: dict) -> list[Finding]:
        errors = sorted(
            Draft7Validator(self._catalog_schema).iter_errors(catalog),
            key=lambda e: e.path,
        )
        return [
            Finding(
                Severity.ERROR,
                CATALOG_FILE,
                f"schema: {self._loc(e.absolute_path)}{e.message}",
            )
            for e in errors
        ]

    def _validate_catalog_disk_parity(
        self, catalog_paths: set[str], disk_paths: dict[str, Path]
    ) -> list[Finding]:
        findings: list[Finding] = []
        for path in sorted(catalog_paths - set(disk_paths)):
            findings.append(
                Finding(
                    Severity.ERROR,
                    path,
                    "listed as a type:agent asset in catalog.json but no "
                    f"{AGENTS_DIR}/.../{AGENT_FILE} exists on disk",
                )
            )
        for path in sorted(set(disk_paths) - catalog_paths):
            findings.append(
                Finding(
                    Severity.ERROR,
                    path,
                    "agent directory on disk is not registered as a type:agent "
                    "asset in catalog.json",
                )
            )
        return findings

    # -- per-agent ------------------------------------------------------------
    def _validate_agent(
        self, path: str, agent_dir: Path, skill_paths: set[str]
    ) -> list[Finding]:
        findings: list[Finding] = []
        agent_file = agent_dir / AGENT_FILE
        try:
            agent = json.loads(agent_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return [Finding(Severity.ERROR, path, f"cannot read {AGENT_FILE}: {exc}")]

        for err in sorted(
            self._agent_validator.iter_errors(agent), key=lambda e: e.path
        ):
            findings.append(
                Finding(
                    Severity.ERROR,
                    path,
                    f"schema: {self._loc(err.absolute_path)}{err.message}",
                )
            )

        findings.extend(self._validate_no_ids(path, agent))
        findings.extend(self._validate_skills(path, agent, skill_paths))
        findings.extend(self._validate_icon(path, agent_dir, agent))
        findings.extend(self._validate_web_search(path, agent))
        return findings

    def _validate_no_ids(self, path: str, agent: dict) -> list[Finding]:
        findings: list[Finding] = []
        for field, value in self._iter_strings(agent):
            if ARN_RE.search(value):
                findings.append(
                    Finding(
                        Severity.ERROR,
                        path,
                        f"{field} contains an ARN (no ids allowed)",
                    )
                )
            if UUID_RE.search(value):
                findings.append(
                    Finding(
                        Severity.ERROR,
                        path,
                        f"{field} contains a UUID (no ids allowed)",
                    )
                )
        return findings

    def _validate_skills(
        self, path: str, agent: dict, skill_paths: set[str]
    ) -> list[Finding]:
        findings: list[Finding] = []
        skills = agent.get("skills")
        if not isinstance(skills, list):
            return findings  # schema already reported a non-list
        for entry in skills:
            if not isinstance(entry, str):
                continue
            skill_dir = self.skills_dir / entry
            skill_md = skill_dir / SKILL_FILE
            catalog_path = f"{SKILLS_DIR}/{entry}"
            if not skill_md.is_file():
                findings.append(
                    Finding(
                        Severity.ERROR,
                        path,
                        f"skill '{entry}' has no {SKILLS_DIR}/{entry}/{SKILL_FILE} "
                        "(removed or moved?)",
                    )
                )
                continue
            if catalog_path not in skill_paths:
                findings.append(
                    Finding(
                        Severity.ERROR,
                        path,
                        f"skill '{entry}' is not a published type:skill asset "
                        f"(no '{catalog_path}' in catalog.json)",
                    )
                )
            frontmatter_name = self._skill_frontmatter_name(skill_md)
            if frontmatter_name is not None and frontmatter_name != skill_dir.name:
                findings.append(
                    Finding(
                        Severity.ERROR,
                        path,
                        f"skill '{entry}': directory name '{skill_dir.name}' != "
                        f"{SKILL_FILE} frontmatter name '{frontmatter_name}'",
                    )
                )
        return findings

    def _validate_icon(self, path: str, agent_dir: Path, agent: dict) -> list[Finding]:
        icon = agent.get("icon")
        if not isinstance(icon, str) or not icon:
            return []  # optional; absence is fine
        rel = icon[2:] if icon.startswith("./") else icon
        icon_path = agent_dir / rel
        if not icon_path.is_file():
            return [Finding(Severity.ERROR, path, f"icon '{icon}' does not exist")]
        data = icon_path.read_bytes()
        if len(data) > MAX_ICON_BYTES:
            return [
                Finding(
                    Severity.ERROR,
                    path,
                    f"icon '{icon}' is {len(data)} bytes, over the {MAX_ICON_BYTES} "
                    "byte cap",
                )
            ]
        if not is_safe_svg(data):
            return [
                Finding(
                    Severity.ERROR,
                    path,
                    f"icon '{icon}' is not a safe SVG (script, animation, event "
                    "handler, or remote reference)",
                )
            ]
        return []

    def _validate_web_search(self, path: str, agent: dict) -> list[Finding]:
        prompt = agent.get("system_prompt")
        caps = agent.get("capabilities")
        if not isinstance(prompt, str) or not isinstance(caps, list):
            return []
        if WEB_SEARCH_PHRASE_RE.search(prompt) and WEB_SEARCH_CAPABILITY not in caps:
            return [
                Finding(
                    Severity.WARNING,
                    path,
                    "system_prompt reads like it needs web search but "
                    f"{WEB_SEARCH_CAPABILITY} is not in capabilities",
                )
            ]
        return []

    # -- helpers --------------------------------------------------------------
    def _iter_agent_dirs(self) -> Iterator[Path]:
        if not self.agents_dir.exists():
            return
        for entry in sorted(self.agents_dir.iterdir()):
            if not entry.is_dir():
                continue
            if (entry / AGENT_FILE).is_file():
                yield entry
            else:
                for child in sorted(entry.iterdir()):
                    if child.is_dir() and (child / AGENT_FILE).is_file():
                        yield child

    def _rel(self, p: Path) -> str:
        return p.relative_to(self.project_dir).as_posix()

    @staticmethod
    def _assets(catalog: dict, asset_type: str) -> Iterator[dict]:
        for category in catalog.get("categories", []):
            for asset in category.get("assets", []):
                if asset.get("type") == asset_type and "path" in asset:
                    yield asset

    def _iter_strings(
        self, value: object, prefix: str = ""
    ) -> Iterator[tuple[str, str]]:
        """Yield (dotted-field, string) for every string in a nested JSON value."""
        if isinstance(value, str):
            yield (prefix or "<root>", value)
        elif isinstance(value, dict):
            for key, item in value.items():
                child = f"{prefix}.{key}" if prefix else str(key)
                yield from self._iter_strings(item, child)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                yield from self._iter_strings(item, f"{prefix}[{idx}]")

    def _skill_frontmatter_name(self, skill_md: Path) -> str | None:
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return None
        parts = text.split("---", 2)
        if len(parts) < 3:
            return None
        try:
            data = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            return None
        if isinstance(data, dict) and isinstance(data.get("name"), str):
            return data["name"]
        return None

    @staticmethod
    def _loc(absolute_path) -> str:
        parts = list(absolute_path)
        return f"{'.'.join(str(p) for p in parts)}: " if parts else ""

    @staticmethod
    def _load_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


@click.command()
@click.option("--quiet", is_flag=True, help="Only print errors, not warnings.")
def main(quiet: bool) -> None:
    """Validate every official agent in the catalog; exit 1 on any error."""
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{message}")

    project_dir = Path(__file__).resolve().parent.parent
    findings = AgentValidator(project_dir).validate()

    errors = [f for f in findings if f.severity is Severity.ERROR]
    warnings = [f for f in findings if f.severity is Severity.WARNING]

    for finding in warnings if not quiet else []:
        logger.warning(finding.render())
    for finding in errors:
        logger.error(finding.render())

    if errors:
        logger.error(
            f"Agent validation FAILED: {len(errors)} error(s), {len(warnings)} warning(s)."
        )
        sys.exit(1)

    logger.success(f"Agent validation passed ({len(warnings)} warning(s)).")
    sys.exit(0)


if __name__ == "__main__":
    main()
