#!/usr/bin/env python3
"""What `sweep.py` claims about `PRS/` notes, as tests rather than as prose.

Run: python3 -m unittest discover -s .agents/skills/sweep -p 'test_*.py'
"""
import os
import pathlib
import tempfile
import unittest

import sweep


class Notes(unittest.TestCase):
    """`notes` is the whole rule: one file per open AGENT-owned head, deleted
    when the head is not open any more."""

    def test_agreement_is_silent(self):
        self.assertEqual(sweep.notes({489, 443}, {443, 489}), ([], []))

    def test_a_head_with_no_note_is_missing(self):
        self.assertEqual(sweep.notes({489}, {489, 443}), ([443], []))

    def test_a_note_with_no_head_is_an_orphan(self):
        self.assertEqual(sweep.notes({489, 676}, {489}), ([], [676]))

    def test_both_at_once_and_sorted(self):
        self.assertEqual(sweep.notes({9, 2}, {3, 1}), ([1, 3], [2, 9]))

    def test_nothing_open_makes_every_note_an_orphan(self):
        self.assertEqual(sweep.notes({1, 2}, set()), ([], [1, 2]))


class MemoryClone(unittest.TestCase):
    """A sweep run without the memory clone beside it says so, rather than
    reporting every open head as missing its note."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = pathlib.Path(self.directory.name)
        self.setup = {"MEMORY_REPO": "someone/memory"}

    def override(self, path):
        os.environ["AGENTS_MEMORY"] = str(path)
        self.addCleanup(os.environ.pop, "AGENTS_MEMORY", None)

    def test_a_clone_carrying_PRS_is_found(self):
        (self.root / "PRS").mkdir()
        self.override(self.root)
        self.assertEqual(sweep.memory_clone(self.setup), self.root)

    def test_a_directory_without_PRS_is_not_a_memory_clone(self):
        self.override(self.root)
        self.assertIsNone(sweep.memory_clone(self.setup))

    def test_a_path_that_does_not_exist_is_none(self):
        self.override(self.root / "nowhere")
        self.assertIsNone(sweep.memory_clone(self.setup))


class Config(unittest.TestCase):
    """`config.env` is the one file naming USER, AGENT and the repos, so a
    malformed line raises rather than parsing to a key nobody reads."""

    def parse(self, text):
        path = pathlib.Path(tempfile.mkdtemp()) / "config.env"
        path.write_text(text)
        return sweep.config(path)

    def test_values_keep_everything_after_the_first_equals(self):
        self.assertEqual(self.parse("AGENT_EMAIL=a=b@c\n")["AGENT_EMAIL"],
                         "a=b@c")

    def test_work_repos_is_a_list(self):
        self.assertEqual(self.parse("WORK_REPOS=a/b,c/d\n")["WORK_REPOS"],
                         ["a/b", "c/d"])

    def test_adopted_prs_maps_repo_to_numbers(self):
        self.assertEqual(self.parse("ADOPTED_PRS=a/b:1,2 c/d:3\n")
                         ["ADOPTED_PRS"], {"a/b": [1, 2], "c/d": [3]})

    def test_an_empty_adopted_prs_is_no_repo(self):
        self.assertEqual(self.parse("ADOPTED_PRS=\n")["ADOPTED_PRS"], {})

    def test_a_line_with_no_key_raises(self):
        with self.assertRaises(ValueError):
            self.parse("USER=toumix\nnot a setting\n")


if __name__ == "__main__":
    unittest.main()
