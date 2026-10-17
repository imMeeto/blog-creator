"""Exercise saved workflow evidence, approvals and offline research states."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_artifact", ROOT / "skills/blog-launch/scripts/check_artifact.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class AgentStateTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads((ROOT / "skills/blog-launch/assets/project-state.example.json").read_text(encoding="utf-8"))

    def test_initial_and_legacy_states_remain_usable(self):
        self.assertEqual(checker.check_state(self.state), [])
        legacy = copy.deepcopy(self.state)
        legacy.pop("workflow")
        legacy.pop("research")
        legacy["schema_version"] = "1.0.0"
        self.assertEqual(checker.check_state(legacy), [])

    def test_completed_stage_needs_result_and_cannot_also_be_skipped(self):
        self.state["workflow"]["completed_stages"] = [{"stage": 1, "artifact_refs": []}]
        self.assertTrue(checker.check_state(self.state))
        self.state["workflow"]["completed_stages"][0]["artifact_refs"] = ["blog-passport.md#direction"]
        self.assertEqual(checker.check_state(self.state), [])
        self.state["workflow"]["skipped_stages"] = [{"stage": 1, "reason": "not needed"}]
        self.assertTrue(checker.check_state(self.state))

    def test_optional_format_can_be_skipped_with_reason(self):
        self.state["workflow"]["skipped_stages"] = [{"stage": 7, "reason": "Only short videos requested"}]
        self.assertEqual(checker.check_state(self.state), [])
        self.state["workflow"]["skipped_stages"][0]["reason"] = ""
        self.assertTrue(checker.check_state(self.state))

    def test_waiting_requires_specific_dependency(self):
        self.state["status"] = "awaiting_input"
        self.assertTrue(checker.check_state(self.state))
        self.state["pending_questions"] = ["Which market and language?"]
        self.assertEqual(checker.check_state(self.state), [])

    def test_offline_research_does_not_count_as_completed(self):
        self.state["research"]["status"] = "unavailable"
        self.state["research"]["gaps"] = ["Web search unavailable"]
        self.assertEqual(checker.check_state(self.state), [])
        self.state["research"]["status"] = "completed"
        self.assertTrue(checker.check_state(self.state))

    def test_research_sources_must_resolve_to_dated_urls(self):
        self.state["research"].update(status="completed", checked_at="2026-10-17", source_ids=["R001"])
        self.assertTrue(checker.check_state(self.state))
        self.state["sources"] = [{"id": "R001", "url": "https://example.org/source", "checked_at": "2026-10-17"}]
        self.assertEqual(checker.check_state(self.state), [])
        self.state["sources"][0]["url"] = "not-a-url"
        self.assertTrue(checker.check_state(self.state))

    def test_week_approval_must_match_current_revision(self):
        self.state.update(status="week_approved", week=1, revision=2)
        self.state["approvals"] = [{"kind": "week", "target": 1, "revision": 1, "user_text": "Утверждаю неделю 1"}]
        self.assertTrue(checker.check_state(self.state))
        self.state["approvals"][0]["revision"] = 2
        self.assertEqual(checker.check_state(self.state), [])

    def test_scope_completion_requires_checked_deliverable(self):
        self.state["status"] = "complete"
        self.assertTrue(checker.check_state(self.state))
        self.state["workflow"]["artifacts"] = [{"id": "S001", "ref": "week-1.md", "checked": True}]
        self.assertEqual(checker.check_state(self.state), [])

    def test_ready_to_publish_is_not_published(self):
        self.state["workflow"]["launch_status"] = "ready_to_publish"
        self.assertEqual(checker.check_state(self.state), [])
        self.state["workflow"]["launch_status"] = "published"
        self.assertTrue(checker.check_state(self.state))
        self.state["workflow"]["publication_evidence"] = {"ref": "user message: publication confirmed", "confirmed_at": "2026-10-17"}
        self.assertEqual(checker.check_state(self.state), [])

    def test_bad_field_types_produce_errors_without_crashing(self):
        for key in ("scope", "launch_status"):
            state = copy.deepcopy(self.state)
            state["workflow"][key] = []
            self.assertTrue(checker.check_state(state))
        self.state["research"]["status"] = []
        self.assertTrue(checker.check_state(self.state))


if __name__ == "__main__":
    unittest.main()
