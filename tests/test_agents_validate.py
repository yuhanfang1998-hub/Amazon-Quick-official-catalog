"""Tests for scripts.agents_validate — one case per validation rule."""

import tempfile
import unittest
from pathlib import Path

from scripts.agents_validate import AgentValidator, Severity, is_safe_svg
from tests._fixtures import SAFE_SVG, CatalogBuilder, valid_agent


class ValidatorTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.builder = CatalogBuilder(self.root)
        self.addCleanup(self._tmp.cleanup)

    def run_validator(self) -> list:
        self.builder.write_catalog()
        return AgentValidator(self.root).validate()

    def errors(self, findings: list) -> list[str]:
        return [f.message for f in findings if f.severity is Severity.ERROR]

    def warnings(self, findings: list) -> list[str]:
        return [f.message for f in findings if f.severity is Severity.WARNING]


class ValidAgentTests(ValidatorTestBase):
    def test_fully_valid_agent_has_no_findings(self) -> None:
        self.builder.add_skill("amazon-quick/agent-to-quick-skill")
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(
                skills=["amazon-quick/agent-to-quick-skill"],
                capabilities=["WEB_SEARCH"],
                icon="assets/icon.svg",
            ),
            icon_bytes=SAFE_SVG,
        )
        findings = self.run_validator()
        self.assertEqual([], self.errors(findings))
        self.assertEqual([], self.warnings(findings))


class SchemaTests(ValidatorTestBase):
    def test_name_over_limit_fails(self) -> None:
        self.builder.add_agent("amazon-quick/test-agent", valid_agent(name="x" * 51))
        self.assertTrue(any("schema" in m for m in self.errors(self.run_validator())))

    def test_non_empty_connectors_fails(self) -> None:
        self.builder.add_agent(
            "amazon-quick/test-agent", valid_agent(connectors=["something"])
        )
        self.assertTrue(any("schema" in m for m in self.errors(self.run_validator())))

    def test_wrong_schema_version_fails(self) -> None:
        self.builder.add_agent("amazon-quick/test-agent", valid_agent(schema_version=2))
        self.assertTrue(any("schema" in m for m in self.errors(self.run_validator())))

    def test_too_many_starter_prompts_fails(self) -> None:
        self.builder.add_agent(
            "amazon-quick/test-agent", valid_agent(starter_prompts=["a", "b", "c", "d"])
        )
        self.assertTrue(any("schema" in m for m in self.errors(self.run_validator())))


class NoIdTests(ValidatorTestBase):
    def test_arn_anywhere_fails(self) -> None:
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(
                system_prompt="Call arn:aws:bedrock:us-east-1:123456789012:agent/x"
            ),
        )
        self.assertTrue(any("ARN" in m for m in self.errors(self.run_validator())))

    def test_uuid_anywhere_fails(self) -> None:
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(description="agent 1b4e28ba-2fa1-11d2-883f-0016d3cca427 here"),
        )
        self.assertTrue(any("UUID" in m for m in self.errors(self.run_validator())))


class SkillReferenceTests(ValidatorTestBase):
    def test_missing_skill_path_fails(self) -> None:
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(skills=["amazon-quick/does-not-exist"]),
        )
        self.assertTrue(
            any("no skills/" in m for m in self.errors(self.run_validator()))
        )

    def test_skill_on_disk_but_not_in_catalog_fails(self) -> None:
        self.builder.add_skill("amazon-quick/orphan-skill", in_catalog=False)
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(skills=["amazon-quick/orphan-skill"]),
        )
        self.assertTrue(
            any("not a published" in m for m in self.errors(self.run_validator()))
        )

    def test_dir_name_mismatch_frontmatter_fails(self) -> None:
        self.builder.add_skill(
            "amazon-quick/renamed-skill", frontmatter_name="old-name"
        )
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(skills=["amazon-quick/renamed-skill"]),
        )
        self.assertTrue(
            any("frontmatter name" in m for m in self.errors(self.run_validator()))
        )


class IconTests(ValidatorTestBase):
    def test_icon_missing_file_fails(self) -> None:
        self.builder.add_agent(
            "amazon-quick/test-agent", valid_agent(icon="assets/icon.svg")
        )
        self.assertTrue(
            any("does not exist" in m for m in self.errors(self.run_validator()))
        )

    def test_icon_over_cap_fails(self) -> None:
        big = (
            b'<svg xmlns="http://www.w3.org/2000/svg">'
            + b"<!-- "
            + b"x" * 6000
            + b" -->"
            + b"</svg>"
        )
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(icon="assets/icon.svg"),
            icon_bytes=big,
        )
        self.assertTrue(any("byte cap" in m for m in self.errors(self.run_validator())))

    def test_unsafe_svg_fails(self) -> None:
        evil = (
            b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        )
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(icon="assets/icon.svg"),
            icon_bytes=evil,
        )
        self.assertTrue(
            any("not a safe SVG" in m for m in self.errors(self.run_validator()))
        )


class WebSearchWarningTests(ValidatorTestBase):
    def test_web_search_phrase_without_capability_warns_not_errors(self) -> None:
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(
                system_prompt="Use web search to gather public intelligence.",
                capabilities=[],
            ),
        )
        findings = self.run_validator()
        self.assertEqual([], self.errors(findings))
        self.assertTrue(any("WEB_SEARCH" in m for m in self.warnings(findings)))

    def test_web_search_phrase_with_capability_no_warning(self) -> None:
        self.builder.add_agent(
            "amazon-quick/test-agent",
            valid_agent(
                system_prompt="Use web search to gather public intelligence.",
                capabilities=["WEB_SEARCH"],
            ),
        )
        self.assertEqual([], self.warnings(self.run_validator()))


class CatalogParityTests(ValidatorTestBase):
    def test_catalog_agent_without_disk_dir_fails(self) -> None:
        self.builder.add_agent(
            "amazon-quick/ghost-agent", valid_agent(), on_disk=False, in_catalog=True
        )
        self.assertTrue(
            any("no agents/" in m for m in self.errors(self.run_validator()))
        )

    def test_disk_agent_without_catalog_entry_fails(self) -> None:
        self.builder.add_agent(
            "amazon-quick/unlisted", valid_agent(), on_disk=True, in_catalog=False
        )
        self.assertTrue(
            any("not registered" in m for m in self.errors(self.run_validator()))
        )


class IsSafeSvgUnitTests(unittest.TestCase):
    def test_safe_svg_accepted(self) -> None:
        self.assertTrue(is_safe_svg(SAFE_SVG))

    def test_script_rejected(self) -> None:
        self.assertFalse(
            is_safe_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><script/></svg>')
        )

    def test_event_handler_rejected(self) -> None:
        self.assertFalse(
            is_safe_svg(b'<svg xmlns="http://www.w3.org/2000/svg" onload="x()"></svg>')
        )

    def test_animate_rejected(self) -> None:
        self.assertFalse(
            is_safe_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><animate/></svg>')
        )

    def test_remote_href_rejected(self) -> None:
        self.assertFalse(
            is_safe_svg(
                b'<svg xmlns="http://www.w3.org/2000/svg">'
                b'<image href="https://evil.example/x.png"/></svg>'
            )
        )

    def test_remote_css_url_rejected(self) -> None:
        self.assertFalse(
            is_safe_svg(
                b'<svg xmlns="http://www.w3.org/2000/svg">'
                b'<rect fill="url(https://evil.example/x)"/></svg>'
            )
        )

    def test_non_svg_root_rejected(self) -> None:
        self.assertFalse(is_safe_svg(b"<html></html>"))

    def test_malformed_rejected(self) -> None:
        self.assertFalse(is_safe_svg(b"<svg>"))


if __name__ == "__main__":
    unittest.main()
