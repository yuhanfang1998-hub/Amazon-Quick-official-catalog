"""Tests for the agent extension to scripts.skills_checksum.

Verifies that agent assets get a per-asset checksum, that --check validates
them, and that the skillsChecksum roll-up stays skills-only (adding an agent
must not change the roll-up value for an unchanged skill set).
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.skills_checksum import (
    AgentManifest,
    ChecksumStatus,
    ManifestDigest,
    SkillsChecksumService,
)
from tests._fixtures import SAFE_SVG, CatalogBuilder, valid_agent


class ChecksumAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _skill_only_rollup(self) -> str:
        """Roll-up over just the single skill, computed independently."""
        skill_dir = self.root / "skills" / "amazon-quick" / "agent-to-quick-skill"
        from scripts.skills_checksum import SkillManifest

        digest = ManifestDigest(SkillManifest(skill_dir).collect()).compute()
        return SkillsChecksumService(self.root)._roll_up(
            {"skills/amazon-quick/agent-to-quick-skill": digest}
        )

    def _build(self) -> None:
        b = CatalogBuilder(self.root)
        b.add_skill("amazon-quick/agent-to-quick-skill")
        b.add_agent(
            "amazon-quick/test-agent",
            valid_agent(
                skills=["amazon-quick/agent-to-quick-skill"], icon="assets/icon.svg"
            ),
            icon_bytes=SAFE_SVG,
        )
        b.write_catalog()

    def test_write_sets_agent_checksum_and_check_passes(self) -> None:
        self._build()
        service = SkillsChecksumService(self.root)
        service.write()

        catalog = json.loads((self.root / "catalog.json").read_text())
        agent_asset = next(
            a
            for cat in catalog["categories"]
            for a in cat["assets"]
            if a["type"] == "agent"
        )
        self.assertRegex(agent_asset["checksum"], r"^sha256:[0-9a-f]{64}$")
        self.assertNotEqual(agent_asset["checksum"], "sha256:" + "0" * 64)

        self.assertIs(service.check().status, ChecksumStatus.MATCHED)

    def test_rollup_stays_skills_only(self) -> None:
        self._build()
        service = SkillsChecksumService(self.root)
        response = service.write()
        self.assertEqual(response.rollup, self._skill_only_rollup())

    def test_check_detects_agent_drift(self) -> None:
        self._build()
        SkillsChecksumService(self.root).write()
        # Tamper with the agent file after checksums were written.
        agent_json = self.root / "agents" / "amazon-quick" / "test-agent" / "agent.json"
        data = json.loads(agent_json.read_text())
        data["description"] = "changed after checksum"
        agent_json.write_text(json.dumps(data, indent=2))

        response = SkillsChecksumService(self.root).check()
        self.assertIs(response.status, ChecksumStatus.MISMATCHED)
        self.assertTrue(any("test-agent" in p for p in response.problems))

    def test_agent_manifest_includes_icon(self) -> None:
        self._build()
        agent_dir = self.root / "agents" / "amazon-quick" / "test-agent"
        manifest = AgentManifest(agent_dir).collect()
        self.assertIn("agent.json", manifest)
        self.assertIn("assets/icon.svg", manifest)


if __name__ == "__main__":
    unittest.main()
