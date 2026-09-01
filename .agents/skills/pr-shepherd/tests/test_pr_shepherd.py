from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts/pr_shepherd.py"
SPEC = importlib.util.spec_from_file_location("pr_shepherd", SCRIPT)
assert SPEC and SPEC.loader
shepherd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shepherd)


class ShepherdTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.state = Path(self.temporary.name) / "state"
        self.environment = mock.patch.dict(
            os.environ,
            {"XDG_STATE_HOME": str(self.state), "CODEX_THREAD_ID": "thread-123"},
            clear=False,
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def register(self) -> None:
        args = argparse.Namespace(
            url="https://github.com/example/project/pull/7",
            trusted_user="owner",
            thread_id=None,
            cwd=self.temporary.name,
        )
        with mock.patch.object(
            shepherd,
            "current_pr",
            return_value={
                "repo": "example/project",
                "number": 7,
                "url": args.url,
                "state": "OPEN",
            },
        ), mock.patch.object(
            shepherd,
            "feedback",
            return_value=[{"kind": "conversation", "id": 1, "body": "already here"}],
        ):
            shepherd.register(args)

    def test_register_baselines_feedback_and_records_task(self) -> None:
        self.register()
        entry = shepherd.load_registry()["entries"][0]
        self.assertEqual(entry["thread_id"], "thread-123")
        self.assertEqual(entry["trusted_user"], "owner")
        self.assertEqual(entry["cwd"], str(Path(self.temporary.name).resolve()))
        self.assertEqual(
            entry["feedback_fingerprint"],
            shepherd.fingerprint([{"kind": "conversation", "id": 1, "body": "already here"}]),
        )

    def test_unchanged_feedback_does_not_wake_codex(self) -> None:
        self.register()
        baseline = [{"kind": "conversation", "id": 1, "body": "already here"}]
        with mock.patch.object(shepherd, "pr_state", return_value="OPEN"), mock.patch.object(
            shepherd, "feedback", return_value=baseline
        ), mock.patch.object(shepherd, "run_command") as command:
            shepherd.run_entries(argparse.Namespace(dry_run=False))
        command.assert_not_called()

    def test_new_trusted_feedback_wakes_original_task_once(self) -> None:
        self.register()
        changed = [{"kind": "conversation", "id": 2, "body": "please fix this"}]
        completed = subprocess.CompletedProcess([], 0, "", "")
        with mock.patch.object(shepherd, "pr_state", return_value="OPEN"), mock.patch.object(
            shepherd, "feedback", return_value=changed
        ), mock.patch.object(shepherd, "run_command", return_value=completed) as command:
            shepherd.run_entries(argparse.Namespace(dry_run=False))
        invocation = command.call_args.args[0]
        self.assertEqual(invocation[:4], ["codex", "exec", "resume", "thread-123"])
        self.assertIn("https://github.com/example/project/pull/7", invocation[4])

        with mock.patch.object(shepherd, "pr_state", return_value="OPEN"), mock.patch.object(
            shepherd, "feedback", return_value=changed
        ), mock.patch.object(shepherd, "run_command") as second_command:
            shepherd.run_entries(argparse.Namespace(dry_run=False))
        second_command.assert_not_called()

    def test_closed_pr_is_removed_without_waking_codex(self) -> None:
        self.register()
        with mock.patch.object(shepherd, "pr_state", return_value="MERGED"), mock.patch.object(
            shepherd, "run_command"
        ) as command:
            shepherd.run_entries(argparse.Namespace(dry_run=False))
        command.assert_not_called()
        self.assertEqual(shepherd.load_registry()["entries"], [])

    def test_cron_block_is_central_idempotent_and_preserves_other_jobs(self) -> None:
        existing = "15 4 * * * backup\n"
        first = shepherd.replace_cron(existing, "/bin/shepherd run")
        second = shepherd.replace_cron(first, "/bin/shepherd run")
        self.assertEqual(first, second)
        self.assertIn(existing.strip(), second)
        self.assertEqual(second.count(shepherd.BEGIN), 1)
        self.assertEqual(second.count(shepherd.SCHEDULE), 1)

    def test_launchd_fallback_has_the_same_eight_weekday_times(self) -> None:
        schedule = shepherd.launchd_schedule()
        self.assertEqual(len(schedule), 40)
        self.assertEqual({item["Weekday"] for item in schedule}, {1, 2, 3, 4, 5})
        self.assertEqual(
            {item["Hour"] for item in schedule},
            {8, 10, 12, 14, 16, 18, 20, 22},
        )

    def test_installed_executable_uses_personal_skill_as_its_source(self) -> None:
        personal = Path(self.temporary.name) / ".agents/skills/pr-shepherd"
        personal.mkdir(parents=True)
        (personal / "SKILL.md").write_text("skill")
        with mock.patch.object(shepherd, "__file__", str(Path(self.temporary.name) / ".local/bin/codex-pr-shepherd")):
            self.assertEqual(shepherd.skill_source(personal), personal)


if __name__ == "__main__":
    unittest.main()
